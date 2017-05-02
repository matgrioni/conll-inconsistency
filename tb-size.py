#!/usr/bin/env python

################################################################################
#
# A simple script to count the number of sentences and tokens in a given
# TreeBank file. Simply provide the filenames as the input and the number of
# sentences will first be output followed by the number of tokens across all
# TreeBanks.
#
################################################################################

from lib.conll import TreeBank

import os
import sys

if len(sys.argv) < 2:
    raise TypeError('Have to count at least one file!')

filenames = sys.argv[1:]
tb = TreeBank()

s_count = 0
t_count = 0
for fn in filenames:
    for sentence in tb.genr(fn):
        s_count += 1
        t_count += len(sentence.words)

print(s_count)
print(t_count)
