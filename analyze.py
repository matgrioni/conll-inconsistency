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

from lib.annotation import Annotation

VariationCount = recordclass('VariationCount', ['correct', 'incorrect', 'unmarked'])

if len(sys.argv) < 2:
    raise TypeError('Not enough arguments provided')

total_count = 0
annotated_count = 0

filename = sys.argv[1]
ann = Annotation()
ann.from_filename(filename)

accounted = 0
acc_flag = False
inconsistent_tokens = 0
total_tokens = 0

for lemma_pair, occurrences in ann.annotations.items():
    for occ in occurrences:
        if occ.is_annotated():
            if not acc_flag:
                acc_flag = True
                accounted += 1

            total_tokens += 1

            if not occ.correct_in_corpus():
                inconsistent_tokens += 1

if accounted > 0:
    print 'Percent of all occurences that were correct'
    print '{} / {} = {}%'.format(total_tokens - inconsistent_tokens, total_tokens, (total_tokens - inconsistent_tokens) / total_tokens)

    print 'Percent of all occurences that were incorrect'
    print '{} / {} = {}%'.format(inconsistent_tokens, total_tokens, inconsistent_tokens / total_tokens)
else:
    print 'No instances were counted because they all had at least'
    print 'one unsure or one unmarked token'
