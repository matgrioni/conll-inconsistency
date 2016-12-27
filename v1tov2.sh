#!/bin/bash

######################################################################
# This is a conversion script to change the French UD Treebank in v1
# to v2. This is not portable to other languages as of yet at least,
# or at least it probably won't be tested. To use simply provide the
# Treebank file that you wish to convert to match certain v2
# guidelines. The features that this script updates are listed below:
#
# To be tested!
# Part of Speech tags:
#   - CONJ -> CCONJ
#
# Morphological Features:
#   - Negative -> Polarity
#   - Aspect=Pro -> Aspect=Prosp
#   - VerbForm=Trans -> VerbForm=Conv
#   - Definite=Red -> Definite=Cons
#
# Syntactic Relations:
#   - dobj -> obj
#   - nsubjpass -> nsubj:pass
#   - csubjpass -> csubj:pass
#   - auxpass -> aux:pass
#
# As always, please diff the output and the input to make the changes
# are accurate.
######################################################################

syntactic_relations=(dobj obj nsubjpass nsubj:pass csubjpass csubj:pass auxpass aux:pass)

filename=$1
sed -i 's/\tCONJ\t/\tCCONJ\t/g' $filename

sed -i 's/Negative/Polarity/g' $filename
sed -i 's/Aspect=Pro/Aspect=Prosp/g' $filename
sed -i 's/VerbForm=Trans/VerbForm=Conv/g' $filename
sed -i 's/Definite=Red/Definite=Cons/g' $filename

for ((i=0; i < ${#syntactic_relations[@]}; i += 2));
do
    sed -i "s/\t${syntactic_relations[i]}\t/\t${syntactic_relations[i+1]}\t/g" $filename
done
