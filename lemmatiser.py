# Lemmatise incoming words
import re
import sys
from pathlib import Path

import hfst

ATTS = re.compile(r'@[^@]+@')
PX = re.compile(r'\+Px.+$')
FOC = re.compile(r'\+Foc/[\w-]+$')
VERSION = re.compile(r'\+v\d')
SEM = re.compile(r'\+Sem/[^+]+')
ADJECTIVE = re.compile(r'^\+A\+(Sg|Pl|Attr|Ess)')
NOUN = re.compile(r'^\+N\+(Sg|Pl|Attr|Ess|G3|G7|Nomag)')
VERB = re.compile(r'^\+V\+(Inf|Ind|Imprt|Cond|Pot|PrfPrc|PrsPrc)')


class Lemmatiser(object):
    def __init__(self, lang):
        """Initialise HFST analysers."""
        self.analysers = {}
        self.generators = {}
        path = Path('/usr/share/giella') / lang
        self.analyser = hfst.HfstInputStream(
            str(path / 'analyser-gt-desc.hfstol')).read()
        self.generator = hfst.HfstInputStream(
            str(path / 'generator-gt-norm.hfstol')).read()

    def analyse(self, word):
        """Analyse word."""
        return (ATTS.sub('', analysis[0])
                for analysis in self.analyser.lookup(word)
                if '?' not in analysis[0] and '+Err' not in analysis[0])

    def clean_analysis(self, analysis):
        """Clean analysis for use in ending_tags."""
        return SEM.sub('', VERSION.sub('', FOC.sub('', PX.sub(
            '', analysis)))).replace('+IV', '').replace('+TV', '')

    def ending_tags(self, cleaned_input):
        """Find the ending tags of cleaned_input."""
        if '+Der/' in cleaned_input:
            der_pos = cleaned_input.rfind('Der/')
            next_pos = cleaned_input[der_pos:].find('+')
            return cleaned_input[der_pos + next_pos:]

        tag = cleaned_input.find('+')
        return cleaned_input[tag:]

    def classify(self, ending_tags):
        """Classify PoS according to ending_tags."""
        if 'VABess' in ending_tags:
            return '+V+VABess'

        if '+Ger' in ending_tags:
            return '+V+Ger'

        if '+V+Actio' in ending_tags:
            return '+V+Actio+Nom'

        if '+V+VGen' in ending_tags:
            return '+V+VGen'

        if '+A+Ord' in ending_tags:
            return '+A+Ord+Sg+Nom'

        if '+N+Attr' in ending_tags:
            return '+N+Attr'

        if VERB.match(ending_tags):
            return '+V+Inf'

        if ADJECTIVE.match(ending_tags):
            return '+A+Sg+Nom'

        if NOUN.match(ending_tags):
            return '+N+Sg+Nom'

        raise SystemExit(f'classify {ending_tags}')

    def remove_last_tags(self, analysis):
        """Remove last tags from analysis."""
        if '+Der/' in analysis:
            der_pos = analysis.rfind('Der/')
            next_pos = analysis[der_pos:].find('+')
            return analysis[:der_pos + next_pos]

        tag = analysis.find('+')
        return analysis[:tag]

    def generate(self, analysis):
        """Generate word forms from the ending_tags."""
        if '+Cmp#' in analysis:
            parts = analysis.rsplit('+Cmp#', maxsplit=1)
            cmp = f'{parts[0]}+Cmp#'
            suff = parts[1]
        else:
            cmp = ''
            suff = analysis

        start = self.remove_last_tags(suff)
        ending_tags = self.classify(self.ending_tags(
            self.clean_analysis(suff)))

        return (ATTS.sub('', generated[0]) for generated in
                self.generator.lookup(f'{cmp}{start}{ending_tags}'))

    def lemmatise(self, word):
        """Lemmatize word using a descriptive analyser."""
        return sorted({
            generated
            for analysis in self.analyse(word)
            for generated in self.generate(analysis)
        })


if __name__ == '__main__':
    lemmatiser = Lemmatiser(sys.argv[1])
    for p in lemmatiser.lemmatise(sys.argv[2]):
        print(f'«{p}»')
