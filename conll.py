import re

from tree import *

class TreeBank(object):
    def __init__(self, treebank_str):
        self.sentences = []
        lines = treebank_str.splitlines()

        idx = 0
        while idx < len(lines):
            blank_line = idx
            while lines[blank_line] != '':
                blank_line += 1

            annotation = '\n'.join(lines[idx:blank_line])
            self.sentences.append(Sentence(annotation))

            idx = blank_line + 1

    def __iter__(self):
        for sentence in self.sentences:
            yield sentence

    def __getitem__(self, key):
        return self.sentences[key]

class Sentence(object):
    COMMENT_MARKER = '#'
    SENTENCE_ID_REGEX = COMMENT_MARKER + ' sentid: fr-ud-(dev|train|test)_(\d+)'
    CONTRACTION_REGEX = '^\d+-\d+'
    SENTENCE_TEXT_START = 17

    def __init__(self, annotation):
        self.words = []
        lines = annotation.splitlines()

        id_match = re.match(Sentence.SENTENCE_ID_REGEX, lines[0])
        if id_match:
            self.id = (id_match.group(1), id_match.group(2))
        else:
            self.id = (None, -1)

        self.text = lines[1][Sentence.SENTENCE_TEXT_START:]

        lines = filter(self._is_word_line, lines)

        for line in lines:
            self.words.append(Word(line))

        # Construct the sentence tree here.
        self._create_tree()

    def _is_word_line(self, line):
        return line[0] != Sentence.COMMENT_MARKER and not(re.match(Sentence.CONTRACTION_REGEX, line))

    def _create_tree(self):
        for word in self.words:
            if word.dep_index == 0:
                self.tree = Tree(word)
                self._create_tree_helper(self.tree, word.index)
                break

    def _create_tree_helper(self, tree, dep_index):
        child_words = filter(lambda word: word.dep_index == dep_index, self.words)

        for word in child_words:
            t = Tree(word)
            self._create_tree_helper(t, word.index)
            tree.add_children(t)

    def dep(self, word):
        word_index = self.words.index(word)
        return self.words[self.words[word_index].dep_index - 1]

    def context_match(self, value, left, right, callback, context_callback):
        for i, word in enumerate(self.words):
            if callback(word) == value:
                matching = False
                if i - 1 >= 0 and left:
                    matching = left == context_callback(self.words[i - 1])
                else:
                    matching = not(left) or (i - 1 < 0)

                if i + 1 < len(self.words) and right:
                    matching = matching and right == context_callback(self.words[i + 1])
                else:
                    matching = matching and (not(right) or (i + 1 >= len(self.words)))

                if matching:
                    return word

        return None

    def __getitem__(self, key):
        return self.words[key]

    def __len__(self):
        return len(self.words)

class Word(object):
    FIELD_DELIMITER = '\t'
    FEATURE_DELIMITER = '|'

    def __init__(self, annotation):
        fields = annotation.split(Word.FIELD_DELIMITER)

        self.index = int(fields[0])
        self.phon = fields[1]
        self.lemma = fields[2]
        self.pos = fields[3]
        self.features = fields[4]
        self.dep_index = int(fields[6])
        self.dep = fields[7]

    def __str__(self):
        return self.phon

    def __repr__(self):
        return self.phon
