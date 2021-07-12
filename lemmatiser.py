"""Lemmatise incoming words"""
import re
import sys
from pathlib import Path

import hfst

ATTS = re.compile(r'@[^@]+@')
ADJECTIVE = re.compile(r'^\+A\+(Sg|Pl|Attr|Ess)')
NOUN = re.compile(r'^\+N\+(Sg|Pl|Attr|Ess|G3|G7|NomAg)')
VERB = re.compile(r'^\+V\+(Inf|Ind|Imprt|Cond|Pot|PrfPrc|PrsPrc)')

REMOVEABLE_REGEX_TAGS = {
    'adjective_comp_superl': re.compile(r'\+A\+Der/(Comp|Superl)'),
    'semantic': re.compile(r'\+Sem/[^+]+'),
    'possesive_suffix': re.compile(r'\+Px.+$'),
    'foc': re.compile(r'\+Foc/[\w-]+$'),
    'version': re.compile(r'\+v\d')
}

REMOVEABLE_TAGS = {
    'transitivity': '+TV',
    'intransitivity': '+IV',
    'qst': '+Qst',
    'subqst': '+Subqst',
}


class Lemmatiser:
    """Given a wordform and a language, spit out possible wordforms."""
    def __init__(self, lang):
        """Initialise HFST analysers."""
        path = Path('/usr/share/giella') / lang
        self.analyser = hfst.HfstInputStream(
            str(path / 'analyser-gt-desc.hfstol')).read()
        self.generator = hfst.HfstInputStream(
            str(path / 'generator-gt-norm.hfstol')).read()

    def analyse(self, word) -> list[str]:
        """Analyse word.

        Args:
            word: a word that should be analysed

        Returns:
            list: a list of hfst analyses
        """
        return (ATTS.sub('', analysis[0])
                for analysis in self.analyser.lookup(word)
                if '?' not in analysis[0] and '+Err' not in analysis[0])

    @staticmethod
    def clean_analysis(analysis):
        """Clean analysis for use in ending_tags."""
        for tagregex in REMOVEABLE_REGEX_TAGS.values():
            analysis = tagregex.sub('', analysis)
        for tag in REMOVEABLE_TAGS.values():
            analysis = analysis.replace(tag, '')

        return analysis

    @staticmethod
    def ending_tags(cleaned_input):
        """Find the ending tags of cleaned_input."""
        if '+Der/' in cleaned_input:
            der_pos = cleaned_input.rfind('Der/')
            next_pos = cleaned_input[der_pos:].find('+')
            return cleaned_input[der_pos + next_pos:]

        tag = cleaned_input.find('+')
        return cleaned_input[tag:]

    @staticmethod
    def classify(ending_tags):
        """Classify PoS according to ending_tags."""
        containing_tags = {
            'VABess': '+V+VABess',
            '+Ger': '+V+Ger',
            '+V+Actio': '+V+Actio+Nom',
            '+V+VGen': '+V+VGen',
            '+A+Ord': '+A+Ord+Sg+Nom',
            '+N+Attr': '+N+Attr',
            '+N+Prop': '+N+Prop+Sg+Nom',
            '+N+Coll': '+N+Coll+Sg+Nom',
            '+N+ABBR': '+N+ABBR+Sg+Nom',
            '+N+NomAg': '+N+NomAg+Sg+Nom',
            '+N+ACR': '+N+ACR+Sg+Nom',
            '+Adv+ABBR': '+Adv+ABBR'
        }

        containing_tags.update(
            {f'+Num+{tag}': '+Num+Sg+Nom'
             for tag in ['Sg', 'Pl', 'Ess']})

        for tags, classification in containing_tags.items():
            if tags in ending_tags:
                return classification

        if ending_tags.endswith('+Adv'):
            return '+Adv'

        if VERB.match(ending_tags):
            return '+V+Inf'

        if ADJECTIVE.match(ending_tags):
            return '+A+Sg+Nom'

        if NOUN.match(ending_tags):
            return '+N+Sg+Nom'

        return None

    @staticmethod
    def remove_last_tags(analysis):
        """Remove last tags from analysis."""
        if '+Der/' in analysis:
            der_pos = analysis.rfind('Der/')
            next_pos = analysis[der_pos:].find('+')
            return analysis[:der_pos + next_pos]

        tag = analysis.find('+')
        return analysis[:tag]

    def generate(self, analysis):
        """Generate word forms from the ending_tags."""
        if analysis.startswith('ii+'):
            return [analysis.split('+')[0]]

        if '+Cmp#' in analysis:
            parts = analysis.rsplit('+Cmp#', maxsplit=1)
            cmp = f'{parts[0]}+Cmp#'
            suff = parts[1]
        else:
            cmp = ''
            suff = analysis

        start = self.remove_last_tags(
            REMOVEABLE_REGEX_TAGS['adjective_comp_superl'].sub('', suff))
        ending_tags = self.ending_tags(self.clean_analysis(suff))

        if any(
                ending_tags.startswith(f'+{tag}')
                for tag in ['Po', 'Pr', 'Interj', 'CS', 'CC', 'Pcle']):
            return [analysis.split('+')[0]]

        classified_tags = self.classify(ending_tags)

        if classified_tags is None:
            raise ValueError(f'Can not handle: {analysis}')

        return (ATTS.sub('', generated[0]) for generated in
                self.generator.lookup(f'{cmp}{start}{classified_tags}'))

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
