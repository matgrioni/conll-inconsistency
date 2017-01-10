#!/usr/bin/python

import sys

from annotation import Annotation, AnnotationLine

# Transfers the given annotations in the source to the destination
# annotations. The assumption is that the source is the annotated
# output of the consistency script without head heuristic while the
# destination annotation is the blank consistency output of the script
# with the head heuristic. Returns a 2-tuple where the first element
# is the number of annotations that could not be transfered to the
# destination, while the second number is the number of annotations
# that were not transferred that were ambigiuous.
def transfer_downstream(source_ann, dest_ann):
    not_transferred = 0
    amb = 0

    for header, lemmas in source_ann.annotations.items():
        for lemma, anns in lemmas.items():
            for ann in anns:
                if dest_ann.has_line(header, lemma, ann.dep, ann.line_num):
                    dest_ann.set_line(header, lemma, ann.dep, ann.line_num, ann.ann)
                else:
                    not_transferred += 1

                    if ann.ann == 'y':
                        amb += 1

    return (not_transferred, amb)

if len(sys.argv) < 3:
    raise TypeError("Not enough arguments provided")

source_filename = sys.argv[1]
dest_filename = sys.argv[2]

source_ann = Annotation()
source_ann.from_filename(source_filename)
dest_ann = Annotation()
dest_ann.from_filename(dest_filename)

results = transfer_downstream(source_ann, dest_ann)
print results
