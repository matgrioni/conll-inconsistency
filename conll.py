import re

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

    def pos_word_count(self, pos):
        return self._field_word_count(lambda word: word.pos, pos)

    def dep_word_count(self, dep):
        return self._field_word_count(lambda word: word.dep, dep)

    def _field_word_count(self, callback, field):
        counts = {}

        for sentence in self.sentences:
            for word in sentence.words:
                if callback(word) == field:
                    try:
                        counts[word.lemma] += 1
                    except KeyError:
                        counts[word.lemma] = 1

        return counts

class Sentence(object):
    COMMENT_MARKER = '#'
    SENTENCE_ID_REGEX = COMMENT_MARKER + ' sentid: fr-ud-(dev|train|test)_(\d+)'
    CONTRACTION_REGEX = '^\d+-\d+'

    def __init__(self, annotation):
        self.words = []
        lines = annotation.splitlines()

        id_match = re.match(Sentence.SENTENCE_ID_REGEX, lines[0])
        if id_match:
            self.id = id_match.group(2)
        else:
            self.id = -1

        self.text = lines[1][17:]

        lines = filter(lambda line: line[0] != Sentence.COMMENT_MARKER and not(re.match(Sentence.CONTRACTION_REGEX, line)),
                       lines)

        for line in lines:
            self.words.append(Word(line))

    def context_match(self, value, callback, left_lemma, right_lemma):
        for i, word in enumerate(self.words):
            if callback(word) == value:
                matching = False
                if i - 1 >= 0 and left_lemma:
                    matching = left_lemma == self.words[i - 1].phon
                else:
                    matching = not(left_lemma) or (i - 1 < 0)

                if i + 1 < len(self.words) and right_lemma:
                    matching = matching and right_lemma == self.words[i + 1].phon
                else:
                    matching = matching and (not(right_lemma) or (i + 1 >= len(self.words)))

                if matching:
                    return word

        return None

class Word(object):
    FIELD_DELIMITER = '\t'
    FEATURE_DELIMITER = '|'

    def __init__(self, annotation):
        fields = annotation.split(Word.FIELD_DELIMITER)

        # TODO: Make features a dictionary
        self.index = fields[0]
        self.phon = fields[1]
        self.lemma = fields[2]
        self.pos = fields[3]
        self.features = fields[4]
        self.dep_index = fields[6]
        self.dep = fields[7]
