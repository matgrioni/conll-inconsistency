######################################################################
#
# Algorithm that implements the consistency validations in dependency
# based treebanks outlined in Boyd et al. Provide the file to check
# for inconsistencies in the command line arguments. Further options
# will support the inclusion of different heuristics as explained in
# the second half of the paper.
#
######################################################################

import sys

from conll import *

# Finds all direct dependencies. Essentially goes through all nodes
# and combines them and their children each into a 2-tuple.
def get_deps(tree):
    deps = []

    for child in tree.children:
        deps.append((tree, child))
        deps += get_deps(child)

    return deps

# Find if there exist any NIL dependencies in the tree that match the
# dependencies provided.
def get_nil(tree, deps):
    pass

if len(sys.argv) < 2:
    raise TypeError('Not enough arguments provided')

filename = sys.argv[1]

with open(filename) as f:
    t = TreeBank(f.read())

