#!/usr/bin/env python

import sys

from lib.annotation import Annotation, AnnotationLine

################################################################################
# A simply utility to transfer annotations that have been done in one file to
# another file. This would be used for example in a test of stringency. There
# are two outputs, one that used more stringent heuristics and one that used
# less stringent heuristics. The less stringent output is annotated and then
# this script is used to transfer over the annotations. Only annotations which
# are present in both files will be transferred over.
#
#   Example Usage:
#       ./transfer.py errors.txt errors-dep.txt
################################################################################

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

for lemmas, occurences in source_ann.annotations.items():
    for o in occurences:
        if o.is_annotated():
            dest_ann.set_line(lemmas, o, o.ann)
