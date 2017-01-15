#!/usr/bin/env python

import sys

from lib.annotation import Annotation, AnnotationLine

# Transfers the given annotations in the source to the destination
# annotations. The assumption is that the source is the annotated
# output of the consistency script without head heuristic while the
# destination annotation is the blank consistency output of the script
# with the head heuristic. Returns a 2-tuple where the first element
# is the number of annotations that could not be transfered to the
# destination, while the second number is the number of annotations
# that were not transferred that were ambigiuous.

# TODO: Update docs, and account for the fact that nil errors should
# not be counted in the transfer. Maybe a separate compare and
# transfer function.
def transfer_downstream(source_ann, dest_ann):
    not_transferred = 0
    transferred = 0
    amb = 0

    for lemmas, occurences in source_ann.annotations.items():
        for o in occurences:
            if o.ann is not None:
                if dest_ann.has_line(o.type, lemmas, o.dep, o.line_num):
                    dest_ann.set_line(o.type, lemmas, o.dep, o.line_num, o.ann)
                    transferred += 1
                else:
                    not_transferred += 1

                    if o.ann == 'y':
                        amb += 1

    return (transferred, not_transferred, amb)

if len(sys.argv) < 3:
    raise TypeError("Not enough arguments provided")

source_filename = sys.argv[1]
dest_filename = sys.argv[2]

source_ann = Annotation()
source_ann.from_filename(source_filename)
dest_ann = Annotation()
dest_ann.from_filename(dest_filename)

results = transfer_downstream(source_ann, dest_ann)
dest_ann.output(dest_filename)

print '{} / {} annotations were transferred'.format(results[0], results[0] + results[1])
print '{} / {} annotations that were not transferred were also correctly annotated in the original corpus'.format(results[2], results[1])
print 'The closer to 1 this ratio is, the better the head heuristic because it does not include cases that are not inconsistent that are in the less stringent results. The closer to 0 this ratio is, the worse it is because it removes actual inconsistencies from the results'
