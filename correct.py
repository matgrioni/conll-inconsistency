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

from lib.conll import *

LEFT = 'left'
RIGHT = 'right'
TOTAL = 'total'

# Nucleus is a tuple to represent the important contextual features that two
# lemmas can occur with. This includes the immediate neighboring words outside
# of the pair (external context), words inside the pair (internal context), and
# the dependency relation that the head of the pair has to its respective head.
# A Nucleus therefore can be thought of as an occurence of words in the corpus.
Nucleus = namedtuple('Nucleus', ['lemmas', 'internal_ctx', 'external_ctx', 'head_dep'])

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
################################################################################

if len(sys.argv) < 2:
    raise TypeError('Not enough arguments provided.')

# The first argument is the filename for the UD TreeBank. The second argument
# is for the shared CONLL task TreeBank.
t = TreeBank()
t.from_filename(sys.argv[0])
# NOTE: This will most certainly be too big. Can possibly random sample from
# a folder or create inverted table?
automatic_t = TreeBank()
automatic_t.from_filename(sys.argv[1]) 

# Construct the nuclei relations for the automatically generated TreeBank. The
# organization of this structure is for the first level to be a Nucleus tuple
# which consists of a lemma pair, internal and external context and a head
# dependency. The second level is the relationship between the lemmas in the
# nucleus. The separation of these two features allow for nuclei to be compared
# based on the relationship between the lemmas while context is fixed.
auto_nuclei = defaultdict(lambda: defaultdict(int))

for sentence in automatic_t:
    index_pairs = itertools.combinations(range(len(sentence.words)), 2)
    for index_pair in index_pairs:
        word1 = sentence[index_pair[0]]
        word2 = sentence[index_pair[1]]

        if word1.index == word2.dep_index or word2.index == word1.dep_index:
            lemmas = frozenset((word1.lemma, word2.lemma))

            internal = _internal_context(sentence, word1, word2)
            external = _external_context(sentence, word1, word2)


            if word1.index == word2.dep_index:
                head = word1
                child = word2
            else:
                head = word2
                child = word1

            nucleus = Nucleus(lemmas, internal, external, head.dep)
            direction = LEFT if sentence.indexes[head.index] < sentence.indexes[child.index] else RIGHT
            relationship = (direction, child.dep)

            auto_nuclei[nucleus][relationship] += 1
            auto_nuclei[nucleus][TOTAL] += 1
