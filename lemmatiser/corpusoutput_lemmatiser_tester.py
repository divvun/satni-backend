# Send text through hfst-tokenise | hfst-lookup -q analyser-gt-desc
# use it as input for this script
# Test if lemmatiser.generate handles the input
import sys

import lemmatiser

lemmat = lemmatiser.Lemmatiser(sys.argv[1])
with open(f'{sys.argv[1]}.txt') as fp:
    for x, line in enumerate(fp):
        if '?' not in line and '+Err/' not in line \
            and '+Cmp/SplitR' not in line and '+PUNCT' not in line \
                and '+CLB' not in line and '+Arab' not in line \
                    and '+Symbol' not in line and '+Num+Rom' not in line:
            parts = line.split()
            if len(parts) == 3:
                try:
                    lemmat.generate(parts[1])
                except ValueError as error:
                    print(error)
