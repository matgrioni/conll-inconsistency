#!/usr/bin/python
# coding: utf-8

######################################################################
#
# Algorithm that implements the consistency validations in dependency
# based treebanks outlined in Boyd et al. Provide the file to check
# for inconsistencies in the command line arguments. Further options
# will support the inclusion of different heuristics as explained in
# the second half of the paper.
#
######################################################################

from collections import defaultdict, namedtuple
import sys

from conll import *

# Define constants that will be used in the script. Among them being
# the direction of the relation and the different command line
# options for heuristics. Another is if the internal context must be
# present for NIL to non-NIL comparisons.
DEPENDENCY_CONTEXT = ('-d', '-dependency')
INTERNAL_CONTEXT = ('-i', '-internal')

LEFT = "L"
RIGHT = "R"
NIL = "NIL"

ContextVariation = namedtuple('ContextVariation', ['internal_ctx', 'external_ctx', 'head_dep', 'sent_id'])
Error = namedtuple('Error', ['lemmas', 'dependency1', 'dependency2', 'sent_id1', 'sent_id2'])

# Find if there exist any NIL dependencies in the tree that match the
# dependencies provided.
# Finds all direct dependencies. Essentially goes through all nodes in
# the tree and combines the root and each child into 2-tuples. The
# tuples are composed of the lemmas of the nodes.
def find_relations(sentence, relations):
    nil_relation = (NIL, NIL)

    for i, word1 in enumerate(sentence):
        for word2 in sentence[i+1:]:
            # The two words are not related
            if word1.dep_index != word2.index and word2.dep_index != word1.index:
                nil_lemmas = frozenset((word1.lemma, word2.lemma))

                internal_ctx = calc_internal_context(sentence, word1, word2)
                external_ctx = calc_external_context(sentence, word1, word2)
                context = ContextVariation(internal_ctx, external_ctx, NIL, sentence.id)

                relations[nil_lemmas][nil_relation].append(context)
            else:
                if word1.dep_index == word2.index:
                    head = word2
                    child = word1
                elif word2.dep_index == word1.index:
                    head = word1
                    child = word2
                related_lemmas = frozenset((head.lemma, child.lemma))

                internal_ctx = calc_internal_context(sentence, head, child)

                direction = LEFT if head.index < child.index else RIGHT
                if direction == LEFT:
                    external_ctx = calc_external_context(sentence, head, child)
                else:
                    external_ctx = calc_external_context(sentence, child, head)
                context = ContextVariation(internal_ctx, external_ctx, head.dep, sentence.id)

                # TODO: Comment this or actually make it readable
                relations[related_lemmas][(direction, child.dep)].append(context)

# Get the external context of the two words in the given sentence as a
# binary tuple of lemmas. The two words should be in the sentence and
# word1 appears before word2 in the sentence.
def calc_external_context(sentence, word1, word2):
    ctx_index1 = word1.index - 2
    ctx_index2 = word2.index

    if ctx_index1 < len(sentence) and ctx_index1 > -1:
        ctx1 = sentence[ctx_index1].lemma
    else:
        ctx1 = None

    if ctx_index2 < len(sentence) and ctx_index2 > -1:
        ctx2 = sentence[ctx_index2].lemma
    else:
        ctx2 = None

    return (ctx1, ctx2)

def calc_internal_context(sentence, word1, word2):
    words = sentence[word1.index : word2.index - 1] or sentence[word2.index : word1.index - 1]
    return map(lambda word: word.lemma, words)

######################################################################
#
# Main script
#
######################################################################

if len(sys.argv) < 2:
    raise TypeError('Not enough arguments provided')

dep_heuristic = reduce(lambda acc, option: acc or option in sys.argv, DEPENDENCY_CONTEXT, False)
internal_ctx_pres = reduce(lambda acc, option: acc or option in sys.argv, INTERNAL_CONTEXT, False)

filename = sys.argv[1]
with open(filename) as f:
    treebank = TreeBank(f.read())

# Find all relations in the treebank and then consolidate the ones
# with identical types but different labels.
# TODO: Explain why defaultdict
relations = defaultdict(lambda: defaultdict(list))
for sentence in treebank:
    find_relations(sentence, relations)

nil_errors = []
context_errors = []

for related_lemmas, lemma_variations in relations.items():
    # First check for NIL errors. This is where for a pair of lemmas
    # they appear as NIL in one situation and as related in another
    # and they have the same internal context in both occurences.
    nil_variations = lemma_variations[(NIL, NIL)]
    for nil_variation in nil_variations:
        for dep, variations in lemma_variations.items():
            if dep != (NIL, NIL):
                for variation in variations:
                    if variation.internal_ctx == nil_variation.internal_ctx:
                        # If the internal context needs to be present
                        # then check if it is before adding a new error.
                        # Otherwise, simply add the NIL error to the list.
                        if internal_ctx_pres:
                            if variation.internal_ctx:
                                nil_errors.append(Error(related_lemmas, (NIL, NIL), dep, nil_variation.sent_id, variation.sent_id))
                        else:
                            nil_errors.append(Error(related_lemmas, (NIL, NIL), dep, nil_variation.sent_id, variation.sent_id))

    # Then check for errors using the non-fringe heuristic. This
    # checks between non-NIL relations. If the external contexts
    # of the words are the same then there is most likely an
    # inconsistency.
    deps = lemma_variations.keys()
    for i, dep1 in enumerate(deps):
        for dep2 in deps[i + 1:]:
            if dep1 != (NIL, NIL) and dep2 != (NIL, NIL):
                for variation1 in lemma_variations[dep1]:
                    for variation2 in lemma_variations[dep2]:
                        if variation1.external_ctx == variation2.external_ctx:
                            # Lastly, is the check for head dependencies which is on top of the external context.
                            if dep_heuristic:
                                if variation1.head_dep == variation2.head_dep:
                                    context_errors.append(Error(related_lemmas, dep1, dep2, variation1.sent_id, variation2.sent_id))
                            else:
                                context_errors.append(Error(related_lemmas, dep1, dep2, variation1.sent_id, variation2.sent_id))

# Print out the error results
print '----------------------  NIL Errors  ----------------------'
for error in nil_errors:
    print ', '.join(error.lemmas)
    dep1, dep2 = ', '.join(error.dependency1), ', '.join(error.dependency2)
    print '\t{} in {}, {}'.format(dep1, error.sent_id1[0], error.sent_id1[1])
    print '\t{} in {}, {}'.format(dep2, error.sent_id2[0], error.sent_id2[1])

print
    
print '----------------------    Context Errors    ----------------------'
for error in context_errors:
    print ', '.join(error.lemmas)
    dep1, dep2 = ', '.join(error.dependency1), ', '.join(error.dependency2)
    print '\t{} in {}, {}'.format(dep1, error.sent_id1[0], error.sent_id1[1])
    print '\t{} in {}, {}'.format(dep2, error.sent_id2[0], error.sent_id2[1])

print

print '# of NIL errors: {}'.format(len(nil_errors))
print '# of context errors: {}'.format(len(context_errors))
