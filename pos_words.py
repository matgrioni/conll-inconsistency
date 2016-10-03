######################################################################
#
# Finds all occurences of words in a given treebank file that match
# the given part of speech. The word counts are then provided based on
# lemma.
#
# Example:
#
#   python pos_words.py treebank.txt AUX
#
######################################################################

import re
import sys

POS_REGEX = r'^\d+?\t(\S+)\t(\S+)\t(\S+)\t'

if len(sys.argv) < 3:
    raise TypeError('Too few arguments. Need at least 2.')

filename = sys.argv[1]
desired_pos = sys.argv[2]

found_words = {}

with open(filename) as f:
    for line in f:
        m = re.match(POS_REGEX, line)
        if m:
            lemma, pos = m.group(2), m.group(3)

            if pos == desired_pos:
                try:
                    found_words[lemma] += 1
                except KeyError:
                    found_words[lemma] = 1

for (key, value) in found_words.iteritems():
    print '{}: {}'.format(key, value)
