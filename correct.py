################################################################################
#
# Compares an input UD TreeBank with an automatically annotated TreeBank from
# the shared CONLL task. Using frequencies of variation nuclei in the shared
# CONLL task output variation nuclei in the input UD TreeBank that do not match
# the patterns already seen.
#
################################################################################

from collections import defaultdict, namedtuple
import itertools
import os
import sys

from lib.conll import *

import numpy

LEFT = 'left'
RIGHT = 'right'
TOTAL = 'total'
MAX_VALUE = 'max_value'
MAX_RELATION = 'max_relation'

# Context is a tuple to represent the important contextual features that two
# lemmas can occur with. This includes the immediate neighboring words outside
# of the pair (external context), words inside the pair (internal context), and
# the dependency relation that the head of the pair has to its respective head.
Context = namedtuple('Context', ['internal_ctx', 'external_ctx', 'head_dep'])

Error = namedtuple('Error', ['lines', 'relationship'])

# Finds the external context around these two words as a 2-tuple. The first item
# of the tuple is the external lemma before the first word in the sentence. The
# second item of the tuple is the external lemma after the second word in the
# sentence. Note that first or second refers to position in the sentence not
# parameter order.
# TODO: Consolidate logic with methods in consistency script.
def _external_context(sentence, word1, word2):
    if sentence.indexes[word1.index] < sentence.indexes[word2.index]:
        prev = word1
        after = word2
    else:
        prev = word2
        after = word1

    ctx_index1 = sentence.indexes[prev.index] - 1
    ctx_index2 = sentence.indexes[after.index] + 1

    if ctx_index1 > -1:
        ctx1 = sentence[ctx_index1].lemma
    else:
        ctx1 = None

    if ctx_index2 < len(sentence):
        ctx2 = sentence[ctx_index2].lemma
    else:
        ctx2 = None

    return (ctx1, ctx2)

# Finds the internal context between the two words as a tuple of lemmas. These
# lemmas are found in order starting from the first word in the sentence out of
# word1 or word2, to the last word before the other word.
def _internal_context(sentence, word1, word2):
    # Get the list of words including the first word then trim it off.
    words = sentence[word1.index : word2.index] or sentence[word2.index : word1.index]
    trimmed = words[1:]

    return tuple(map(lambda word: word.lemma, trimmed))

################################################################################
#
# Main script.
#
# The first argument should be the filename of the UD treebank file we are
# trying to find incorrect annotations on. The second argument is a folder with
# at least one file that is a treebank. The third argument is optional. It is
# how many treebanks to randomnly use from the folder for the correctness check.
# If this argument is omitted then all files in the folder specified in the
# second argument are used.
#
################################################################################

if len(sys.argv) < 3:
    raise TypeError('Not enough arguments provided.')


filenames = os.listdir(sys.argv[2])
if sys.argv < 4:
    s = len(filenames)
else:
    s = int(sys.argv[3])
random_files = numpy.random.choice(filenames, size=(s), replace=False)

for random_file in random_files:
    print random_file

    # Construct the nuclei relations for the automatically generated TreeBank.
    # The organization of this structure is for the first level to be a set of
    # lemmas. The second level is a Context tuple which consists of the internal
    # and external context along with the dependency relation of the head of the
    # governor of the set of lemmas. The third level is the relationship between
    # these two lemmas and the direction of the head. Note that the actual head
    # of the lemmas is not known, only that the two are related. This probably
    # does not make a difference since it actually helps to catch errors if they
    # are related to the direction of the relationship.
    #
    # There are three special fields in this
    # dict. Once the lemma and context are specified, there is also a TOTAL
    # field which is the number of total lemma pairs with such a context, a MAX
    # field which is the number of times the most frequent relationship happened
    # and MAX_RELATION which is the most frequency relationship.
    auto_nuclei = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))

    # Create a generator of the sentences in the TreeBank rather than storing them
    # in memory.
    automatic_t = TreeBank()
    for sentence in automatic_t.genr(sys.argv[2] + '/' + random_file):
        # TODO: Test that this traversal actually works.
        tree = SentenceTree(sentence)
        for tree1 in tree:
            for tree2 in tree1.children:
                head = tree1.node
                child = tree2.node

                lemmas = frozenset((head.lemma, child.lemma))

                internal = _internal_context(sentence, head, child)
                external = _external_context(sentence, head, child)

                context = Context(internal, external, head.dep)
                direction = LEFT if sentence.indexes[head.index] < sentence.indexes[child.index] else RIGHT
                relationship = (direction, child.dep)

                auto_nuclei[lemmas][context][relationship] += 1
                auto_nuclei[lemmas][context][TOTAL] += 1

                # Update the MAX and MAX_RELATION as necessary.
                updated_value = auto_nuclei[lemmas][context][relationship]
                if updated_value > auto_nuclei[lemmas][context][MAX_VALUE]:
                    auto_nuclei[lemmas][context][MAX_VALUE] = updated_value
                    auto_nuclei[lemmas][context][MAX_RELATION] = relationship

errors = defaultdict(lambda: defaultdict(list))


# Create a generator of the sentences in the TreeBank rather than storing them
# in memory.
# NOTE: Is there any way to combine these two loops, seems awfully repetitive.
# No common code can be put into method? Possibly a generator.
t = TreeBank()
for sentence in t.genr(sys.argv[1]):
    tree = SentenceTree(sentence)
    for tree1 in tree:
        for tree2 in tree1.children:
            head = tree1.node
            child = tree2.node

            lemmas = frozenset((head.lemma, child.lemma))

            internal = _internal_context(sentence, head, child)
            external = _external_context(sentence, head, child)

            context = Context(internal, external, head.dep)
            direction = LEFT if sentence.indexes[head.index] < sentence.indexes[child.index] else RIGHT
            relationship = (direction, child.dep)

            if relationship != auto_nuclei[lemmas][context][MAX_RELATION]:
                e = Error((head.line_num, child.line_num), relationship)
                errors[lemmas][context].append(e)

for lemmas, value in errors.items():
    print lemmas

    for context, errors in value.items():
        for e in errors:
            print '\t{}\t{}\t{}'.format(*e)
