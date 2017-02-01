#!/usr/bin/env python
# TODO: Later try to do with shell

import os
import re
import shutil
import sys

if (sys.argv < 2):
    raise TypeError('Not enough arguments')

TEMP_FILENAME = 'no_spaces.tmp'
SPACES_IN_LEMMA = '^\d+\t[^\W_]*_[^\W_]*\t[^\W_]*_[^\W_]*\t'

with open(sys.argv[1], 'r') as source:
    with open(TEMP_FILENAME, 'w') as dest:
        for line in source:
            m = re.match(SPACES_IN_LEMMA, line)

            if m:
                line = line.replace('_', ' ', 2)

            dest.write(line)

shutil.copyfile(TEMP_FILENAME, sys.argv[1])
os.remove(TEMP_FILENAME)
