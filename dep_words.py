######################################################################
#
# Finds all occurences of words in a given treebank file that match
# the given dependency. The word counts are then provided based on
# lemma.
#
# Example:
#
#   python dep_words.py treebank.txt nsubj
#
######################################################################

import re
import sys

DEP_REGEX = r'^\d+?\t(\S+)\t(\S+)\t\S+\t_\t\S+\t\S+\t(\S+)\t'

if len(sys.argv) < 3:
    raise TypeError('Too few arguments. Need at least 2.')

filename = sys.argv[1]
desired_dep = sys.argv[2]

found_words = {}

with open(filename) as f:
    for line in f:
        m = re.match(DEP_REGEX, line)
        if m:
            lemma, dep = m.group(2), m.group(3)

            if dep == desired_dep:
                try:
                    found_words[lemma] += 1
                except KeyError:
                    found_words[lemma] = 1

for (key, value) in found_words.iteritems():
    print '{}: {}'.format(key, value)
