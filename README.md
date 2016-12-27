This is a personal repository of tools for interfacing with treebanks as a part of the Universal Dependencies (UD) project. The most important tools here is the conll.py file which provides wrappers around loading and extracting the information from a conll file, and the other is the consistency scripts: consistency.py and analyze.py.

## Consistency

A problem in the UD treebanks is ensuring they are self consistent. This is looked at in Boyd et al (2013) and is implemented through these two scripts. The first script consistency.py takes the name of a conll file and analyzes its consistency. The output is as follows.

```
lemma1, lemma2
    R, nsubj at fr-ud-dev_0123#23
    L, aux at fr-ud-dev_2345#24

    L, mwe at fr-ud-dev_0345#23
    L, case at fr-ud-dev_1#23

lemma3, lemma4
    L, dobj at fr-ud-dev_76543#2
    R, name at fr-ud-dev_345#5
```

The unintended lines consisting of a lemma pair are the two lemmas that make up a variation nuclei. This variation nuclei is listed because it may be that the given occurences in the treebank are inconsistent. For reference, right headed means that the head of the relation is to the right of the child and left headed means the head of the relation is to the left of the child. For example lemma1 and lemma2 are annotated in several different ways. It is right headed, with a nsubj relation between the lemmas at sentence with id fr-ud-dev_0123 at index 23. Similarly, it is annotated as left headed with an aux relation at sentence with id fr-ud-dev_2345 at index 24. These two occurences appear to be inconsistent and should be checked.

Tentatively, the input treebank must have sentence ids based on the v2 UD guidelines.

Now after checking the occurences, you must mark each occurence as an ambiguity or actual inconsistency. This is done in the following manner.

```
lemma1, lemma2
    R, nsubj at fr-ud-dev_0123#23
    L, aux at fr-ud-dev_2345#24
    y

    L, mwe at fr-ud-dev_0345#23
    L, case at fr-ud-dev_1#23
    n

lemma3, lemma4
    L, dobj at fr-ud-dev_76543#2
    R, name at fr-ud-dev_345#5
    n
```

A `y` means that the occurence was ambigious, and a `n` means that the occurence was not consistent. There is also `?` to signify unsure. After annotating the entire file in this manner you can now run it with analyze.py. Note that are are some formatting restrictions on the file to be analyzed. Each `y`, `n`, or `?`, must be preceeded by a tab character in the file. An expanded tab into spaces will not work. Further, there must be a separation of one newline between occurences of a lemma pair. Lastly, for the last occurence to be counted, the file must end in a newline.

analyze.py will output the accuracy of the consistency.py script based on each lemma pair and based on the entire output as a percentage of lemma pairs where all occurences are inconsistent and as a percentage of total individual lemma occurences that are inconsistent. This is subject to change however.
