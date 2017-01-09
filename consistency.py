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
import itertools
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
NIL_RELATION = (NIL, NIL)

ContextVariation = namedtuple('ContextVariation', ['internal_ctx', 'external_ctx', 'head_dep', 'line_number'])
Error = namedtuple('Error', ['dep', 'line_number'])

# Get the external context of the two words in the given sentence as a
# binary tuple of lemmas. The two words should be in the sentence and
# word1 appears before word2 in the sentence.
def calc_external_context(sentence, word1, word2):
    if word1.index < word2.index:
        prev = word1
        after = word2
    else:
        prev = word2
        after = word1

    # Remember that the Word object index is 1-based not 0-based.
    ctx_index1 = prev.index - 2
    ctx_index2 = after.index

    if ctx_index1 > -1:
        ctx1 = sentence[ctx_index1].lemma
    else:
        ctx1 = None

    if ctx_index2 < len(sentence):
        ctx2 = sentence[ctx_index2].lemma
    else:
        ctx2 = None

    return (ctx1, ctx2)

def calc_internal_context(sentence, word1, word2):
    words = sentence[word1.index : word2.index - 1] or sentence[word2.index : word1.index - 1]
    return map(lambda word: word.lemma, words)

def print_errors(errors, header):
    print '----------------------  {}  ----------------------'.format(header)
    for lemmas, lemma_errors in errors.items():
        if len(lemmas) > 1:
            print ', '.join(lemmas)
        else:
            l, = lemmas
            print '{}, {}'.format(l, l)
        for error in lemma_errors:
            dep = ', '.join(error.dep)
            print '\t{} at {}'.format(dep, error.line_number)

        print

######################################################################
#
# Main script
#
######################################################################

if len(sys.argv) < 2:
    raise TypeError('Not enough arguments provided')

dep_heuristic = reduce(lambda acc, option: acc or option in sys.argv, DEPENDENCY_CONTEXT, False)
internal_ctx_pres = reduce(lambda acc, option: acc or option in sys.argv, INTERNAL_CONTEXT, False)

# Find all relations in the treebank and then consolidate the ones
# with identical types but different labels.
# TODO: Explain why defaultdict
filename = sys.argv[1]
relations = defaultdict(lambda: defaultdict(list))
t = TreeBank()
t.from_filename(filename)
for sentence in t:
    index_pairs = itertools.combinations(range(len(sentence.words)), 2)
    for index_pair in index_pairs:
        word1 = sentence.words[index_pair[0]]
        word2 = sentence.words[index_pair[1]]
        lemmas = frozenset((word1.lemma, word2.lemma))
        
        internal_ctx = calc_internal_context(sentence, word1, word2)
        external_ctx = calc_external_context(sentence, word1, word2)

        if word1.dep_index != word2.index and word2.dep_index != word1.index:
            if internal_ctx:
                context = ContextVariation(internal_ctx, external_ctx, NIL, word1.line_num)
                relations[lemmas][NIL_RELATION].append(context)
        else:
            if (internal_ctx_pres and internal_ctx) or not internal_ctx_pres:
                if word1.dep_index == word2.index:
                    head = word2
                    child = word1
                elif word2.dep_index == word1.index:
                    head = word1
                    child = word2

                direction = LEFT if head.index < child.index else RIGHT
                context = ContextVariation(internal_ctx, external_ctx, head.dep, word1.line_num)
                relations[lemmas][(direction, child.dep)].append(context)

nil_errors = defaultdict(set)
context_errors = defaultdict(set)

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
                        nil_errors[related_lemmas].add(Error(dep, variation.line_number))
                        nil_errors[related_lemmas].add(Error((NIL, NIL), nil_variation.line_number))

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
                        # NOTE: The following if statements is for once sent-ids are more common.
                        # if not((variation1.id > -1 and variation2.id > -1) and (variation1.id == variation2.id)):
                        if variation1.external_ctx == variation2.external_ctx:
                            # Lastly, is the check for head dependencies which is on top of the external context.
                            # TODO: Shorter lines
                            if dep_heuristic:
                                if variation1.head_dep == variation2.head_dep:
                                    context_errors[related_lemmas].add(Error(dep1, variation1.line_number))
                                    context_errors[related_lemmas].add(Error(dep2, variation2.line_number))
                            else:
                                context_errors[related_lemmas].add(Error(dep1, variation1.line_number))
                                context_errors[related_lemmas].add(Error(dep2, variation2.line_number))

# Print out the error results
print_errors(nil_errors, 'NIL Errors')

print

print_errors(context_errors, 'Context Errors')

print

print '# of NIL errors: {}'.format(len(nil_errors))
print '# of context errors: {}'.format(len(context_errors))
