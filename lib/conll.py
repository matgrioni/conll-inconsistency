import re

from tree import *

class TreeBank(object):
    def from_filename(self, filename):
        self.sentences = []

        with open(filename, 'r') as f:
            lines = []
            sent_start = 1
            for i, line in enumerate(f):
                stripped = line.strip()

                # If the line is not blank then add it to the running
                # list of lines for the current sentence.
                if stripped:
                    lines.append(stripped)
                else:
                    # Otherwise, the line is blank and the end of this
                    # sentence has been reached. So combine the lines
                    # found for this sentence and create Sentence
                    # object.
                    annotation = '\n'.join(lines)
                    self.sentences.append(Sentence(annotation, sent_start))
                    sent_start = i + 2
                    del lines[:]

    def from_string(self, string):
        self.sentences = []
        lines = string.splitlines();

        start = 0
        idx = 0
        while start < len(lines):
            line = lines[idx].strip()

            if not line:
                annotation = '\n'.join(lines[start:idx])
                self.sentences.append(Sentence(annotation, start + 1))

                start = idx + 1

            idx += 1

    def __iter__(self):
        for sentence in self.sentences:
            yield sentence

    def __getitem__(self, key):
        return self.sentences[key]

class Sentence(object):
    COMMENT_MARKER = '#'
    SENTENCE_ID_REGEX = COMMENT_MARKER + ' sentid: ([a-z]{2}-ud-(dev|train|test)_\d+)'
    CONTRACTION_REGEX = '^\d+-\d+'
    SENTENCE_TEXT_MARKER = ':'

    def __init__(self, annotation, line_num=-1):
        self.line_num = line_num
        self.words = []
        self.lines = annotation.splitlines()

        id_match = re.match(Sentence.SENTENCE_ID_REGEX, self.lines[0])
        if id_match:
            self.id = id_match.group(1)
        else:
            self.id = None

        for i, line in enumerate(self.lines):
            if self._is_word_line(line):
                word_line = -1 if line_num == -1 else self.line_num + i
                self.words.append(Word(line, word_line))

        # This is to handle the cases where the format is different
        # from the French corpus.
        # TODO: Comment that for accurate sentence text need space after
        # ':'
        try:
            marker_index = self.lines[1].index(Sentence.SENTENCE_TEXT_MARKER)
            self.text = self.lines[1][marker_index + 2:]
        except:
            self.text = ""

    def _is_word_line(self, line):
        return line[0] != Sentence.COMMENT_MARKER and not re.match(Sentence.CONTRACTION_REGEX, line)

    def __getitem__(self, key):
        return self.words[key]

    def __len__(self):
        return len(self.words)

# A navigable tree created from a provided Sentence object. The
# sentence's root is the root of this tree. The root's dependents are
# then the children of the root node and so on. The SentenceTree also
# actually extends Tree, so look to that for more info, this is just a
# wrapper around the construction of a tree data structure from a
# sentence object.
class SentenceTree(Tree):
    def __init__(self, sentence):
        self.sentence = sentence
        for word in self.sentence:
            if word.dep_index == 0:
                super(Tree, self).__init__(word)
                break

        self._construct_tree()

    def _construct_tree(self):
        self._construct_tree_helper(self, 0)

    def _construct_tree_helper(self, tree, index):
        child_words = filter(lambda word: word.dep_index == index, self.sentence)

        for word in child_words:
            t = Tree(word)
            self._construct_tree_helper(t, word.index)
            tree.add_children(t)

class Word(object):
    FIELD_DELIMITER = '\t'
    FEATURE_DELIMITER = '|'

    def __init__(self, annotation, line_num=-1):
        self.line_num = line_num
        fields = annotation.split(Word.FIELD_DELIMITER)

        self.index = int(fields[0])
        self.phon = fields[1]
        self.lemma = fields[2]
        self.pos = fields[3]
        self.features = fields[4]
        self.dep_index = int(fields[6])
        self.dep = fields[7]
        self.deps = fields[8]
        self.misc = fields[9]

    def __str__(self):
        return self.phon

    def __repr__(self):
        items = [self.index, self.phon, self.lemma, self.pos, self.features,
                 self.dep_index, self.dep, self.deps, self.misc]
        return Word.FIELD_DELIMITER.join(items)
