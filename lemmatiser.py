# Lemmatise incoming words
import re
import sys
from pathlib import Path

import hfst

ATTS = re.compile(r'@[^@]+@')
ANALYSERS = {}


def init_analysers():
    """Initialise HFST analysers."""
    for path in Path('/usr/share/giella/').glob('???'):
        ANALYSERS[path.name] = hfst.HfstInputStream(
            str(path / 'analyser-gt-desc.hfstol')).read()


# def save_der(part):
#     parts = part.split('+')
#     ders = [part for part in parts[1:] if 'Der/' in part]
#     ders.insert(0, parts[0])
#     return '|'.join(ders)


def clean_analysis(analysis):
    """Clean an analysis."""
    # parts = analysis.split('+Cmp#')

    # return '|'.join([part for part in parts])
    return analysis


def lemmatise(language, word):
    """Lemmatize word using a descriptive analyser."""
    analyses = ANALYSERS[language].lookup(word)
    for p in sorted(set([
            clean_analysis(ATTS.sub('', analysis[0])) for analysis in analyses])):
        print(p)


if __name__ == '__main__':
    init_analysers()
    lemmatise(sys.argv[1], sys.argv[2])
