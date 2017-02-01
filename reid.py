#!/usr/bin/env python

# TODO: This would be better by using the conll libraries to rewrite
#       trees.
# NOTE: Also assumes that all the sentences have ids. If there is no
#       id on a given sentence then none is added.

import sys

if len(sys.argv) < 4:
    raise TypeError('Not enough arguments provided.')

COMMENT_MARKER = '#'
SENT_ID_MARKER = 'sentid:'

in_filename = sys.argv[1]
out_filename = sys.argv[2]
form = sys.argv[3]

with open(in_filename, 'r') as f1:
    with open(out_filename, 'w') as f2:
        cur_id = 1

        for line in f1:
            if line[0] == COMMENT_MARKER and SENT_ID_MARKER in line:
                new_id = form.format(cur_id)
                id_line = ' '.join([COMMENT_MARKER, SENT_ID_MARKER, new_id])
                f2.write(id_line + '\n')

                cur_id += 1
            else:
                f2.write(line)
