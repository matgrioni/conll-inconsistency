#!/usr/bin/python

######################################################################
# The following is an analysis tool for the output of the results of
# a consistency analysis on a corpus. There are a few requirements
# that must be met in order to ensure accurate results. There must be
# a newline between the nuclei variation occurences, there must be a
# tab character before the annoation, 'y', 'n', or '?', the file
# must end in a newline to ensure the last annotation is counted.
#
# Examples of properly formatted annotations can be found in the
# repo's README.
######################################################################

from __future__ import division
from collections import defaultdict
from recordclass import recordclass

import re
import sys

# Matches a header in the consistency output file. Such as
# -----------------   Nil Context   --------------------.
# This header, Nil Context, will be captured and used to clasify the
# variation occurences that follow it.
HEADER_REGEX = '^-+\s*(.+?)\s*-+$'

VariationCount = recordclass('VariationCount', ['yes', 'no', 'unsure', 'unmarked'])

if len(sys.argv) < 2:
    raise TypeError('Not enough arguments provided')

# The structure of the variations dictionary is such that each key is
# a pair of lemmas that is found in the annotated file. Each value is
# then a 3-namedtuple where the first element is the number of actual
# inconsistencies, the second element is the number of ambiguities,
# and the third number is the number of unsure marks, and the last
# number is the number of unmarked occurences.
variations = defaultdict(lambda: VariationCount(0, 0, 0, 0))

filename = sys.argv[1]
with open(filename, 'r') as f:
    cur_header = None
    cur_lemmas = None

    # A marker for if the current variation in the parser has been
    # marked in the variations dict.
    new_variation = True

    for line in f:
        # Check first if we are starting a next section of errors.
        match = re.match(HEADER_REGEX, line)
        if match:
            cur_header = match.group(1)
        else:
            # Check if we are on the line that tells us if the
            # variation was legitimate or not.
            if line[0] == '\t' and line[1] in ['y', 'n', '?'] and cur_lemmas:
                # Check to make sure that one variation isn't counted
                # twice.
                if new_variation:
                    if line[1] == 'y':
                        variations[cur_lemmas].yes += 1
                    elif line[1] == 'n':
                        variations[cur_lemmas].no += 1
                    elif line[1] == '?':
                        variations[cur_lemmas].unsure += 1

                new_variation = False
            # Otherwise if we have current lemmas, and are on a newline
            # then this variation was unmarked.
            elif line in ['\n', '\r\n'] and cur_lemmas:
                # Check to make sure that one variation isn't coutned
                # twice.
                if new_variation:
                    variations[cur_lemmas].unmarked += 1

                new_variation = False
            # Otherwise, the line might be a line that starts a lemma
            # pair. In which case, they have no whitespace before them
            elif line[0] != '\t':
                # This line is starting off a pair of lemmas, so split
                # it into the two lemmas, ignoring the '\n' in the
                # second lemma.
                comma = line.index(', ')
                first_lemma = line[:comma]
                second_lemma = line[comma + 2:-1]

                cur_lemmas = (first_lemma, second_lemma)
            # Otherwise, if the line starts with a tab, but does not
            # start with a 'y', 'n', '?', then this is a new variation
            # occurence.
            elif line[0] == '\t':
                new_variation = True

# Print the output format
print 'This is the output format'
print 'lemma1, lemma2'
print '\t# inconsistent|# total|% precision'

print
print

fully_inconsistent = 0
accounted = 0
for lemma_pair, count in variations.items():
    # Do not include unfinished counts.
    if count.unsure == 0 and count.unmarked == 0:
        accounted += 1
        print '{}, {}'.format(*lemma_pair)

        total = count.yes + count.no + count.unsure + count.unmarked
        print '\t{}\t{}\t{}%'.format(count.no, total, count.no / total * 100)

        if count.yes == 0:
            fully_inconsistent += 1

if accounted > 0:
    print 'Percent of lemmas where all tokens were inconsistent'
    print '{} / {} = {}%'.format(fully_inconsistent, accounted, fully_inconsistent / accounted * 100)
else:
    print 'No instances were counted'
