# Send text through hfst-tokenise | hfst-lookup -q analyser-gt-desc
# use it as input for this script
# The result of this script is used to analyse how to categorise input
# for the lemmatiser

import re
import sys

y = 0
z = 0
u = 0
lasts = set()

PX = re.compile(r'\+Px.+$')
FOC = re.compile(r'\+Foc/[\w-]+$')
VERSION = re.compile(r'\+v\d')
SEM = re.compile(r'\+Sem/[^+]+')


def add_to_last(uff):
    if '+Der/' in uff:
        der_pos = uff.rfind('Der/')
        next_pos = uff[der_pos:].find('+')
        lasts.add(uff[der_pos + next_pos:])
    else:
        tag = uff.find('+')
        lasts.add(uff[tag:])


with open(sys.argv[1]) as fp:
    for x, line in enumerate(fp):
        if '?' not in line and '+Err/' not in line:
            parts = line.split()
            if len(parts) == 3:
                y += 1
                # print(parts[1])
                cleaned = SEM.sub(
                    '', VERSION.sub('', FOC.sub('', PX.sub(
                        '', parts[1])))).replace('+IV', '').replace('+TV', '')
                if '+Cmp#' in cleaned:
                    add_to_last(cleaned.rsplit('+Cmp#', maxsplit=1)[1].strip())
                else:
                    add_to_last(cleaned.strip())
            else:
                z += 1
        else:
            u += 1

    for last in sorted(lasts):
        print(last)

    print('lines', x)
    print('hits', y)
    print('none hits', z)
    print('unknown', u)
    print('lasts', len(lasts))
