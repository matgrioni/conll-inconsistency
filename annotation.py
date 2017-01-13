import re

from collections import defaultdict
from recordclass import recordclass

AnnotationLine = recordclass('AnnotationLine', ['type', 'dep', 'line_num', 'ann'])

class Annotation(object):
    # A line in the annotation file is a line that can be annotated.
    # Basically this lines that are not headers, lemma pairs or
    # newlines.
    LINE_REGEX = '^\t(context|nil) \| (.+) at (\d+)(\s+(y|n))?\n$'

    def __init__(self):
        self.annotations = defaultdict(list)
        self.lemmas = 0
        self.size = 0

    def from_filename(self, filename):
        with open(filename, 'r') as f:
            cur_header = None
            cur_lemmas = None

            for line in f:
                m = re.match(Annotation.LINE_REGEX, line)
                if m:
                    dep_t = ', '.split(m.group(2))
                    l_n = int(m.group(3))

                    line_ann = AnnotationLine(m.group(1), dep_t, l_n, m.group(5))
                    self.annotations[cur_lemmas].append(line_ann)
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

    def has_line(self, t, lemmas, dep, line_num):
        return self._find_line(t, lemmas, dep, line_num) == None

    def set_ann(self, t, lemmas, dep, line_num, ann):
        l = self._find_line(t, lemmas, dep, line_num)
        if l:
            l.ann = ann

    def _find_line(self, t, lemmas, dep, line_num):
        for line in self.annotations[lemmas]:
            if line.type == t and line.dep == dep and line.line_num == line_num:
                return line

        return None

    def output(self, filename):
        with open(filename, 'w') as f:
            for lemmas, occurences in self.annotations.items():
                f.write(', '.join(lemmas) + '\n')

                for o in occurences:
                    dep_s = ', '.join(o.dep)
                    if o.ann is None:
                        line = '\t{} | {} at {}\n'.format(o.type, dep_s, o.line_num)
                    else:
                        line = '\t{} | {} at {} {}\n'.format(o.type, dep_s, o.line_num, o.ann)

                    f.write(line)

                f.write('\n')
