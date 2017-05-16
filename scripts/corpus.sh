#!/usr/bin/env bash

################################################################################
#
# Script that downloads all the UD corpi listed out line by line in
# endpoints.txt. Takes one optional argument which is the directory where the
# corpi will be cloned. By default this is ~/.
#
################################################################################

# Store the current working directory to be able to change between the directory
# to clone into and where the endpoints file is.
here=$(pwd)
file="./endpoints.txt"

# Read endpoints line by line (corpus by corpus)
while IFS= read -r line
do
    # Clone the corpus into the desired directory.
    cd $1
    git clone $line
    cd $here
done <"$file"
