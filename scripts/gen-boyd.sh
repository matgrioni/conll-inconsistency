#!/usr/bin/env bash

################################################################################
#
# Script that does all the necessary operations and commands to create the Boyd
# et. al. consistency output in several different directories. This script takes
# three parameters, the location of the UD repositories, the location in which
# to put the results, and the location of the Boyd et. al. script. All these
# locations should be relative. This script will go into all UD repositories
# (those starting with UD) in the provided directory, and run the Boyd et. al.
# method on those combined datasets, placing the result in the appropriate
# folder provided.
#
# Note that currently the paramters given to the Boyd et. al. script are
# - notnil
#
################################################################################

here=$(pwd)

while IFS= read -r dir
do
    cd $dir
    trainfn=$(ls *.conllu | tail -1)
    id="${trainfn%%-ud-train.conllu}"
    cat *.conllu > __tmp.conllu

    python $here/$3/consistency.py __tmp.conllu --notnil > $here/$2/$id.txt

    rm __tmp.conllu
    cd $here
done < <(ls -d $1/UD_* | grep ".")
