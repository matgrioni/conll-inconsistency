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

import consistency
from lib.conll import *
from lib.options import OptionsProcessor

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

# TODO: how should max_relation be handled
# TODO: words is just temporary hopefully. Find a way to get rid of this silly
# thing.
Error = namedtuple('Error', ['lines', 'relationship', 'max_relation',
                             'rel_count', 'max_rel_count', 'words'])

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

op = OptionsProcessor()
op.add_option(('-h', '--head'), 'head_heuristic')
op.add_option(('-i', '--internal'), 'internal_ctx')
op.add_option(('-p', '--morph'), 'morph')
op.add_option(('-wl', '--with-lemmas'), 'with_lemmas')

op.process(sys.argv)

filenames = os.listdir(sys.argv[2])
if sys.argv < 4:
    s = len(filenames)
else:
    s = int(sys.argv[3])
random_files = numpy.random.choice(filenames, size=(s), replace=False)

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

for random_file in random_files:
    print random_file

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

                if op.morph_present():
                    keys = frozenset((':'.join((head.pos, head.features)),
                                     ':'.join((child.pos, child.features))
                else:
                    keys = frozenset((head.lemma, child.lemma))

                internal = _internal_context(sentence, head, child)
                external = _external_context(sentence, head, child)

                context = Context(internal, external, head.dep)
                direction = LEFT if sentence.indexes[head.index] < sentence.indexes[child.index] else RIGHT
                relationship = (direction, child.dep)

                auto_nuclei[lemmas][context][relationship] += 1
                auto_nuclei[lemmas][context][TOTAL] += 1

                # Update the MAX and MAX_RELATION as necessary.
                updated_value = auto_nuclei[keys][context][relationship]
                if updated_value > auto_nuclei[keys][context][MAX_VALUE]:
                    auto_nuclei[keys][context][MAX_VALUE] = updated_value
                    auto_nuclei[keys][context][MAX_RELATION] = relationship

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

            if op.morph_present():
                keys = frozenset((':'.join((head.pos, head.features)),
                                 ':'.join((child.pos, child.features))
            else:
                keys = frozenset((head.lemma, child.lemma))

            internal = _internal_context(sentence, head, child)
            external = _external_context(sentence, head, child)

            context = Context(internal, external, head.dep)
            direction = LEFT if sentence.indexes[head.index] < sentence.indexes[child.index] else RIGHT
            relationship = (direction, child.dep)

            max_relation = auto_nuclei[keys][context][MAX_RELATION]
            max_count = auto_nuclei[keys][context][MAX_VALUE]
            count = auto_nuclei[keys][context][relationship]

            if auto_nuclei[keys][context][TOTAL] > 5 and \
               relationship != max_relation:
                e = Error((head.line_num, child.line_num), relationship,
                          max_relation, count, max_count, (head, child))
                errors[keys][context].append(e)

boyd_errors = consistency.analyze_tb(sys.argv[1], op.morph_present(),
                                     op.internal_ctx_present(),
                                     True,
                                     False,
                                     op.head_heuristic_present())

for keys, value in errors.items():
    if len(keys) > 1:
        print ', '.join(keys)
    else:
        k, = lemmas
        print '{}, {}'.format(k, k)

    for context, errors in value.items():
        for e in errors:
            in_boyd = len(boyd_errors[keys][consistency.Error(e.words, e.relationship, e.lines)]) > 0
            if in_boyd:
                b = 'x'
            else:
                b = ' '
            print '\t{} {: <25}\t{: <25}\t{: <25}\t{: <10}\t{: <10} {}'.format(b, *e)
