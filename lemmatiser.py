# Lemmatise incoming words
import re
import sys
from pathlib import Path

import hfst

ATTS = re.compile(r'@[^@]+@')
PX = re.compile(r'\+Px.+$')
FOC = re.compile(r'\+Foc/[\w-]+$')


class Lemmatiser(object):
    def __init__(self):
        """Initialise HFST analysers."""
        self.analysers = {}
        self.generators = {}
        for path in Path('/usr/share/giella/').glob('???'):
            self.analysers[path.name] = hfst.HfstInputStream(
                str(path / 'analyser-gt-desc.hfstol')).read()
            self.generators[path.name] = hfst.HfstInputStream(
                str(path / 'generator-gt-desc.hfstol')).read()

    def generate_der(self, language, part):
        der_pos = part.find('Der/')
        next_pos = part[der_pos:].find('+')

        uff = f'{part[:der_pos + next_pos]}+N+Sg+Nom'
        for p in self.generators[language].lookup(uff):
            clean = ATTS.sub('', p[0])
            yield clean

    def clean_analysis(self, language, analysis):
        """Clean an analysis."""
        cleaned = FOC.sub('', PX.sub('', ATTS.sub('', analysis)))

        pre, suf = cleaned.rsplit('+Cmp#', maxsplit=1)
        print(pre, suf)

        if '+Der/' not in cleaned:
            yield cleaned.split('+')[0]

        elif '+Der/' in cleaned:
            for der in self.generate_der(language, cleaned):
                yield der

        else:
            yield cleaned

    def lemmatise(self, language, word):
        """Lemmatize word using a descriptive analyser."""
        analyses = self.analysers[language].lookup(word)
        return sorted(
            set([
                p.strip() for analysis in analyses
                for p in self.clean_analysis(language, analysis[0])
                if p.strip()
            ]))


if __name__ == '__main__':
    lemmatiser = Lemmatiser()
    for p in lemmatiser.lemmatise(sys.argv[1], sys.argv[2]):
        print(f'«{p}»')
