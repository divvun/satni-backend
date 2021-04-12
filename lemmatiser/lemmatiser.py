# Lemmatise incoming words
import re

import hfst


class Lemmatiser(object):
    atts = re.compile(r'@[^@]+@')

    def __init__(self, path):
        """Initialise HFST analysers."""
        self.analyser = hfst.HfstInputStream(str(path)).read()

    def analyse(self, word):
        """Analyse word."""
        return (self.atts.sub('', analysis[0]).split('+')[0]
                for analysis in self.analyser.lookup(word)
                if '?' not in analysis[0] and '+Err' not in analysis[0])

    def lemmatise(self, word):
        """Lemmatize word using a descriptive analyser."""
        return (analysis for analysis in self.analyse(word)
                if '+Cmp#' not in analysis and '+Der/' not in analysis)
