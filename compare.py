#!/usr/bin/env python

################################################################################
# A utility script in the UD consistency workflow. This script will compare two
# different outputs from the consistency.py script. The first output file should
# be annotated using the guidelines explained in README. It does not matter if
# the second file is annotated or not. The results will be as follows:
#
#   - The number of total occurences in the first file.
#   - The number of annotated occurences in the first file.
#   - The number of occurences in the first file also in the second.
#   - The number of annotated occurences in the first file also in the second.
#   - The number of annotated occurences that were only in the first file, that
#     were are also correct in the original corpus (i.e. has 'y' annotation).
#
#   Example Usage:
#       ./compare.py errors.txt errors-dep.txt
#
# The idea behind this script is to be able to quantify different heuristics
# and techniques. The results of this script will reveal the relative precision
# and recall for different heuristics.
#
# NOTE: That the comparison right now only works when the occurences in the
#       second output file are a subset of the occurences in the first input
#       file.
################################################################################

import sys

from lib.annotation import Annotation

if len(sys.argv) < 3:
    raise TypeError("Not enough arguments provided")

first = Annotation()
first.from_filename(sys.argv[1])

second = Annotation()
second.from_filename(sys.argv[2])

# The counts to be displayed as results. total and annotated are 2-tuples where
# the first item represents the amount from the first file, and the second item
# represents the amount that are shared between the first and second file.
total = [0, 0]
annotated = [0, 0]
correct = [0, 0]

lemmas_total = [0, 0, False]
lemmas_annotated = [0, 0, False, False]
lemmas_incorrect = [0, 0, False, False]

for lemmas, occurrences in first.annotations.items():
    lemmas_total[2] = False
    lemmas_annotated[2] = False
    lemmas_annotated[3] = False
    lemmas_incorrect[2] = False
    lemmas_incorrect[3] = False

    lemmas_total[0] += 1

    for occ in occurrences:
        total[0] += 1

        shared = second.has_line(lemmas, occ)
        if shared:
            total[1] += 1

            if not lemmas_total[2]:
                lemmas_total[2] = True
                lemmas_total[1] += 1

        if occ.is_annotated():
            if not lemmas_annotated[2]:
                lemmas_annotated[2] = True
                lemmas_annotated[0] += 1

            annotated[0] += 1
            if occ.correct_in_corpus():
                correct[0] += 1
            elif not lemmas_incorrect[2]:
                lemmas_incorrect[2] = True
                lemmas_incorrect[0] += 1

            if shared:
                if not lemmas_annotated[3]:
                    lemmas_annotated[3] = True
                    lemmas_annotated[1] += 1

                annotated[1] += 1
                if occ.correct_in_corpus():
                    correct[1] += 1
                elif not lemmas_incorrect[3]:
                    lemmas_incorrect[3] = True
                    lemmas_incorrect[1] += 1

incorrect = [annotated[0] - correct[0], annotated[1] - correct[1]]
left_out = correct[0] - correct[1]
too_much = incorrect[0] - incorrect[1]

left_out_lemma = lemmas_incorrect[0] - lemmas_incorrect[1]

print '{} / {} of occurrences are annotated in {}'.format(annotated[0], total[0], sys.argv[1])
print '{} / {} of occurences in {} are in also {}'.format(total[1], total[0], sys.argv[1], sys.argv[2])
print '{} / {} of annotated occurences in {} are also in {}'.format(annotated[1], annotated[0], sys.argv[1], sys.argv[2])
print '{} / {} of annotated occurences in {} NOT in {} are correct in the original corpus'.format(left_out, annotated[0] - annotated[1], sys.argv[1], sys.argv[2])
print '{} / {} of incorrect occurences in {} are NOT in {}'.format(too_much, incorrect[0], sys.argv[1], sys.argv[2])
print '{} / {} of lemmas with an incorrect occurrence in {} are NOT in {}'.format(left_out_lemma, lemmas_incorrect[0], sys.argv[1], sys.argv[2])
