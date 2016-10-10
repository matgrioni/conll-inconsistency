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

class Sentence(object):
    SENTENCE_ID_REGEX = '# sentid: fr-ud-[dev|train|test]_(\d+)'

    def __init__(self, annotation):
        self.words = []
        lines = annotation.splitlines()

        id_match = re.match(Sentence.SENTENCE_ID_REGEX, lines[0])
        if id_match:
            self.id = id_match.group(1)
        else:
            self.id = -1

        for line in lines[2:]:
            self.words.append(Word(line))

class Word(object):
    FIELD_DELIMITER = '\t'
    FEATURE_DELIMITER = '|'

    def __init__(self, annotation):
        fields = annotation.split(Word.FIELD_DELIMITER)

        # TODO: Make features a dictionary
        self.index = fields[0]
        self.text = fields[1]
        self.lemma = fields[2]
        self.pos = fields[3]
        self.features = fields[4]
        self.dep_index = fields[6]
        self.dep = fields[7]
