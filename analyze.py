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

VariationCountInternal = recordclass('VariationCountInternal', ['correct', 'incorrect', 'unmarked'])
class VariationCount(VariationCountInternal):
    def one_marked(self):
        return self.correct > 0 or self.incorrect > 0

    def annotated_count(self):
        return self.correct + self.incorrect

    def percent_incorrect(self):
        return self.incorrect / self.annotated_count() * 100

DEP_FLAG_ARG = ('-dep', '-d')
LEMMA_FLAG_ARG = ('-lemma', '-l')
FREQ_FLAG_ARG = ('-frequency', '-f')

if len(sys.argv) < 2:
    raise TypeError('Not enough arguments provided')

dep_flag = reduce(lambda acc, arg: acc or arg in DEP_FLAG_ARG, sys.argv, False)
lemma_flag = reduce(lambda acc, arg: acc or arg in LEMMA_FLAG_ARG, sys.argv, False)
freq_flag = reduce(lambda acc, arg: acc or arg in FREQ_FLAG_ARG, sys.argv, False)

total_count = 0
annotated_count = 0

filename = sys.argv[1]
ann = Annotation()
ann.from_filename(filename)

accounted = 0
acc_flag = False

inconsistent_tokens = 0
total_tokens = 0

counted_lemma_incorrect = False
counted_lemma = False
inconsistent_lemmas = 0
annotated_lemmas = 0

by_dep = defaultdict(lambda: VariationCount(0, 0, 0))
by_lemma = defaultdict(lambda: VariationCount(0, 0, 0))
freqs = defaultdict(int)

for lemma_pair, occurrences in ann.annotations.items():
    counted_lemma_incorrect = False
    counted_lemma = False

    num_annotated = 0
    for occ in occurrences:
        if occ.is_annotated():
            num_annotated += 1

            if not counted_lemma:
                counted_lemma = True
                annotated_lemmas += 1

            if not acc_flag:
                acc_flag = True
                accounted += 1

            total_tokens += 1

            if occ.correct_in_corpus():
                by_dep[occ.dep].correct += 1
                by_lemma[lemma_pair].correct += 1
            else:
                inconsistent_tokens += 1
                if not counted_lemma_incorrect:
                    counted_lemma_incorrect = True
                    inconsistent_lemmas += 1

                by_dep[occ.dep].incorrect += 1
                by_lemma[lemma_pair].incorrect += 1
        else:
            by_dep[occ.dep].unmarked += 1
            by_lemma[lemma_pair].unmarked += 1

    freqs[num_annotated] += 1

if dep_flag:
    print 'Data analysis by dependency type'
    print 'Format is as follows:'
    print 'DIR, REL\t# incorrrect\t# total annotated\tpercent incorrect'

    print

    for dep, count in by_dep.items():
        if count.one_marked():
            print '{}, {}\t{}\t{}\t{}%'.format(dep[0], dep[1], count.incorrect, count.annotated_count(), count.percent_incorrect())

    print
    print

if lemma_flag:
    print 'Data analysis by lemma'
    print 'Format is as follows:'
    print 'LEMMA1, LEMMA2\t# incorrrect\t# total annotated\tpercent incorrect'

    print

    for lemmas, count in by_lemma.items():
        if count.one_marked():
            lemma1, lemma2 = lemmas

            print '{}, {}\t{}\t{}\t{}%'.format(lemma1, lemma2, count.incorrect, count.annotated_count(), count.percent_incorrect())

    print
    print

if freq_flag:
    print 'Data analysis by freq'
    print 'Format is as follows:'
    print 'NUMBER ANNOTATED\tFREQUENCY'

    print

    for num, freq in freqs.items():
        print '{}\t{}'.format(num, freq)

if accounted > 0:
    print 'Percent of all occurences that were correct'
    print '{} / {} = {}%'.format(total_tokens - inconsistent_tokens, total_tokens, (total_tokens - inconsistent_tokens) / total_tokens * 100)

    print 'Percent of all occurences that were incorrect'
    print '{} / {} = {}%'.format(inconsistent_tokens, total_tokens, inconsistent_tokens / total_tokens)

    print 'Percent of all lemma pairs with at least one incorrect occurrence'
    print '{} / {} = {}%'.format(inconsistent_lemmas, annotated_lemmas, inconsistent_lemmas / annotated_lemmas * 100)
else:
    print 'No instances were counted because they all had at least'
    print 'one unsure or one unmarked token'
