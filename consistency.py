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

LEFT = "L"
RIGHT = "R"
NIL = "NIL"

# Finds all direct dependencies. Essentially goes through all nodes
# and combines them and their children each into a 2-tuple then creates
# and returns the Relation objects formed from that.
def find_relations(tree):
    relations = []

    for child in tree.children:
        direction = LEFT if tree.node.index < child.node.index else RIGHT
        relations.append((direction, tree.node, child.node))

        relations += find_relations(child)

    return relations

# Find if there exist any NIL dependencies in the tree that match the
# dependencies provided.
def find_nils(tree, relations):
    nils = []

    for relation in relations:
        # Matches is the list of all subtrees in tree that have the
        # root node with value relation[1], which is the head of the
        # relation.
        matches = tree.find_trees_by_node(lambda node: node.lemma, relation[1])

        for match in matches:
            children_nodes = map(lambda child: child.node.lemma, match.children)
            if relation[2] not in children_nodes:
                nils.append(relation)

    return nils

if len(sys.argv) < 2:
    raise TypeError('Not enough arguments provided')

filename = sys.argv[1]
with open(filename) as f:
    treebank = TreeBank(f.read())

# Find all relations in the treebank and then consolidate the ones
# with identical types but different labels.
relations = {}
for sentence in treebank:
    s_relations = find_relations(sentence.tree)
    for relation in s_relations:
        simp_relation = (relation[0], relation[1].lemma, relation[2].lemma)
        try:
            relations[simp_relation].add(relation[2].dep)
        except KeyError:
            relations[simp_relation] = { relation[2].dep }
"""
nils = reduce(lambda acc, sentence: acc + find_nils(sentence.tree, relations.keys()), treebank.sentences, [])
for nil in nils:
    relations[nil].add(NIL)
"""

for key, value in relations.iteritems():
    if len(value) > 1:
        print str(key) + ", " + str(value)
