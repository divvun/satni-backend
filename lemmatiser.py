"""Lemmatise incoming words"""
import re
import sys
from collections import namedtuple
from pathlib import Path

import hfst

ATTS = re.compile(r'@[^@]+@')

Classification = namedtuple('Classification', 'regex classification')


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

    def lemmatise(self, word):
        """Lemmatize word using a descriptive analyser."""
        return sorted(
            {analysis.split('+')[0]
             for analysis in self.analyse(word)})


class SmeLemmatiser(Lemmatiser):
    """Given a wordform and a language, spit out possible wordforms."""
    classifications = {
        'verb_abessive':
        Classification(re.compile(r'.*VABess.*'), '+V+VABess'),
        'verb_gerundium':
        Classification(re.compile(r'.*\+Ger.*'), '+V+Ger'),
        'verb_action_form':
        Classification(re.compile(r'.*\+V\+Actio.*'), '+V+Actio+Nom'),
        'verb_genitive':
        Classification(re.compile(r'.*\+V\+VGen.*'), '+V+VGen'),
        'adjective_ordinal_number':
        Classification(re.compile(r'.*\+A\+Ord.*'), '+A+Ord+Sg+Nom'),
        'attributive':
        Classification(re.compile(r'.*\+N\+Attr.*'), '+N+Attr'),
        'propernoun':
        Classification(re.compile(r'.*\+N\+Prop.*'), '+N+Prop+Sg+Nom'),
        'collective_numeral':
        Classification(re.compile(r'.*\+N\+Coll.*'), '+N+Coll+Sg+Nom'),
        'noun_abbreviation':
        Classification(re.compile(r'.*\+N\+ABBR.*'), '+N+ABBR+Sg+Nom'),
        'nomen_agentis':
        Classification(re.compile(r'.*\+N\+NomAg.*'), '+N+NomAg+Sg+Nom'),
        'noun_acronym':
        Classification(re.compile(r'.*\+N\+ACR.*'), '+N+ACR+Sg+Nom'),
        'adverb_abbreviation':
        Classification(re.compile(r'.*\+Adv\+ABBR.*'), '+Adv+ABBR'),
        'numeral':
        Classification(re.compile(r'.*\+Num\+(Sg|Pl|Ess)'), '+Num+Sg+Nom'),
        'adverb':
        Classification(re.compile(r'.*\+Adv$'), '+Adv'),
        'verb':
        Classification(
            re.compile(r'^\+V\+(Inf|Ind|Imprt|Cond|Pot|PrfPrc|PrsPrc)'),
            '+V+Inf'),
        'adjective':
        Classification(re.compile(r'^\+A\+(Sg|Pl|Attr|Ess)'), '+A+Sg+Nom'),
        'noun':
        Classification(re.compile(r'^\+N\+(Sg|Pl|Attr|Ess|G3|G7|NomAg)'),
                       '+N+Sg+Nom')
    }

    removable_regex_tags = {
        'adjective_comp_superl': re.compile(r'\+A\+Der/(Comp|Superl)'),
        'semantic': re.compile(r'\+Sem/[^+]+'),
        'possesive_suffix': re.compile(r'\+Px.+$'),
        'foc': re.compile(r'\+Foc/[\w-]+$'),
        'version': re.compile(r'\+v\d')
    }

    removable_tags = {
        'transitivity': '+TV',
        'intransitivity': '+IV',
        'qst': '+Qst',
        'subqst': '+Subqst',
    }

    def clean_analysis(self, analysis):
        """Clean analysis for use in ending_tags."""
        for tagregex in self.removable_regex_tags.values():
            analysis = tagregex.sub('', analysis)
        for tag in self.removable_tags.values():
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

    def classify(self, ending_tags):
        """Classify PoS according to ending_tags."""
        for tag in self.classifications.values():
            if tag.regex.match(ending_tags):
                return tag.classification

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
            self.removable_regex_tags['adjective_comp_superl'].sub('', suff))
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


def lemmatiser(language):
    """Get a language specific lemmatiser."""
    return Lemmatiser(language) if language != 'sme' else SmeLemmatiser(
        language)


if __name__ == '__main__':
    this_lemmatiser = lemmatiser(sys.argv[1])
    for p in this_lemmatiser.lemmatise(sys.argv[2]):
        print(f'«{p}»')
