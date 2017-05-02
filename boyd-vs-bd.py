#!/usr/bin/env python

################################################################################
#
# Compares output from the Boyd et al method with the Big Data approach.
# Specifically, this transforms the Boyd et al output to mark the occurences
# that are in both approaches. This takes as input the Boyd et al output file,
# and the Big Data output file. The output is the Boyd et al output file, with a
# 'x ' in front of the line if it the same lines show up in the Big Data method
# or a '  ' otherwise.
#
################################################################################

from __future__ import division

from lib.annotation import Annotation

import sys

if len(sys.argv) < 3:
    raise TypeError('Give the Boyd et al output first then the Big Data output')

boyd_output = Annotation()
boyd_output.from_filename(sys.argv[1])

with open(sys.argv[2], 'r') as f:
    bd_raw_output = f.read()

count = 0
counted = False
for lemmas, errors in boyd_output.annotations.items():
    counted = False
    for error in errors:
        if str(error.line_nums) not in bd_raw_output:
            if not counted:
                try:
                    print '{}, {}'.format(*lemmas)
                except IndexError:
                    print '{0}, {0}'.format(*lemmas)
            counted = True

            count += 1
            print('\t{}'.format(error))

print(count)
print(boyd_output.size)
print(count / boyd_output.size)
