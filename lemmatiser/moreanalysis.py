"""Lemmatise incoming words"""
import re
import sys
from collections import namedtuple
from pathlib import Path

import hfst

ATTS = re.compile(r"@[^@]+@")

Classification = namedtuple("Classification", "regex classification")
Analysis = namedtuple("Analysis", "analysis weight")


class Lemmatiser:
    """Given a wordform and a language, spit out possible wordforms."""

    def __init__(self, lang):
        """Initialise HFST analysers."""
        path = Path("/usr/share/giella") / lang
        self.analyser = hfst.HfstInputStream(
            str(path / "analyser-gt-desc.hfstol")
        ).read()
        self.generator = hfst.HfstInputStream(
            str(path / "generator-gt-norm.hfstol")
        ).read()

    def analyse(self, word):
        """Analyse word.

        Args:
            word: a word that should be analysed

        Returns:
            list: a list of hfst analyses
        """
        return (
            Analysis(ATTS.sub("", analysis[0]), analysis[1])
            for analysis in self.analyser.lookup(word)
            if "?" not in analysis[0] and "+Err" not in analysis[0]
        )


if __name__ == "__main__":
    this_lemmatiser = Lemmatiser(sys.argv[1])
    for p in this_lemmatiser.analyse(sys.argv[2]):
        print(f"«{p.analysis}: {p.weight}»")
