import re

from collections import defaultdict
from recordclass import recordclass

AnnotationLine = recordclass('AnnotationLine', ['dep', 'line_num', 'ann'])

class Annotation(object):
    # Matches a header in the consistency output file. Such as
    # -----------------   Nil Context   --------------------.
    # This header, Nil Context, will be captured and used to clasify the
    # variation occurences that follow it.
    HEADER_REGEX = '^-+\s*(.+?)\s*-+$'

    # A line in the annotation file is a line that can be annotated.
    # Basically this lines that are not headers, lemma pairs or
    # newlines.
    LINE_REGEX = '^\t(.+) at (\d+)\s+(y|n)?\n$'

    def __init__(self):
        self.annotations = defaultdict(defaultdict(list))
        self.lemmas = 0
        self.size = 0

    def from_filename(self, filename):
        with open(filename, 'r') as f:
            cur_header = None
            cur_lemmas = None

            for line in f:
                # Check first if we are starting a next section of errors.
                match = re.match(Annotation.HEADER_REGEX, line)
                if match:
                    cur_header = match.group(1)
                else:
                    m = re.match(Annotation.LINE_REGEX, line)

                    if m:
                        line_ann = AnnotationLine(m.group(1), m.group(2), m.group(3))
                        self.annotations[cur_header][cur_lemmas].append(line_ann)
                        self.size += 1
                    elif line not in ['\n', '\r\n']:
                        # This line is starting off a pair of lemmas, so split
                        # it into the two lemmas, ignoring the '\n' in the
                        # second lemma.
                        comma = line.index(', ')
                        first_lemma = line[:comma]
                        second_lemma = line[comma + 2:-1]

                        cur_lemmas = (first_lemma, second_lemma)
                        self.lemmas += 1

    def has_line(self, header, lemmas, dep, line_num):
        return self._find_line(header, lemmas, dep, line_num) == None

    def set_ann(self, header, lemmas, dep, line_num, ann):
        l = self._find_line(header, lemmas, dep, line_num)
        if l:
            l.ann = ann

    def _find_line(self, header, lemmas, dep, line_num):
        for line in self.annotations[header][lemmas]:
            if line.dep == dep and line.line_num == line_num:
                return line

        return None

    def output(self):
        pass
