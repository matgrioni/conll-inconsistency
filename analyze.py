#!/usr/bin/env python

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

VariationCount = recordclass('VariationCount', ['correct', 'incorrect', 'unmarked'])

if len(sys.argv) < 2:
    raise TypeError('Not enough arguments provided')

# The structure of the variations dictionary is such that each key is
# a pair of lemmas that is found in the annotated file. Each value is
# then a 3-namedtuple where the first element is the number of actual
# inconsistencies, the second element is the number of ambiguities,
# and the last number is the number of unmarked occurences.
variations = defaultdict(lambda: VariationCount(0, 0, 0))

total_count = 0
annotated_count = 0

filename = sys.argv[1]
with open(filename, 'r') as f:
    cur_lemmas = None

    for line in f:
        if line[0] == '\t':
            total_count += 1
            annotation = line[-2]

            if annotation == 'y':
                variations[cur_lemmas].correct += 1
                annotated_count += 1
            elif annotation == 'n':
                variations[cur_lemmas].incorrect += 1
                annotated_count += 1
            else:
                variations[cur_lemmas].unmarked += 1
        elif line not in ['\n', '\r\n']:
            # This line is starting off a pair of lemmas, so split
            # it into the two lemmas, ignoring the '\n' in the
            # second lemma.
            comma = line.index(', ')
            first_lemma = line[:comma]
            second_lemma = line[comma + 2:-1]

            cur_lemmas = (first_lemma, second_lemma)

# Print the output format
print 'This is the output format'
print 'lemma1, lemma2'
print '\t# inconsistent|# total|% precision'

print

fully_inconsistent = 0
accounted = 0
inconsistent_tokens = 0
total_tokens = 0
for lemma_pair, count in variations.items():
    # Do not include unfinished counts.
    if count.unsure == 0 and count.unmarked == 0:
        accounted += 1
        print '{}, {}'.format(*lemma_pair)

        total = count.correct + count.incorrect
        inconsistent_tokens += count.incorrect
        total_tokens += total
        print '\t{}\t{}\t{}%'.format(count.incorrect, total, count.incorrect / total * 100)

        if count.correct == 0:
            fully_inconsistent += 1

if accounted > 0:
    print 'Total number of occurrences: {}'.format(total_count)
    print 'Total number of annotated occurrences: {}'.format(annotated_count)

    print 'Percent of lemmas where all tokens were inconsistent'
    print '{} / {} = {}%'.format(fully_inconsistent, accounted, fully_inconsistent / accounted * 100)

    print 'Percent of all tokens that were inconsistent'
    print '{} / {} = {}%'.format(inconsistent_tokens, total_tokens, inconsistent_tokens / total_tokens)
else:
    print 'No instances were counted because they all had at least'
    print 'one unsure or one unmarked token'
