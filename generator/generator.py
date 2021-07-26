"""Paradigm generator engine."""
import json
import re
from collections import namedtuple
from pathlib import Path

import hfst

ATTS = re.compile(r"@[^@]+@")
Analysis = namedtuple("Analysis", "wordform weight")


class ParadigmGenerator:
    """Generate paradigms using hfst."""

    best_analysis = {"N": "+N+Sg+Nom"}

    def __init__(self, lang):
        """Initialise HFST analysers."""
        analyser_path = Path("/usr/share/giella") / lang / "analyser-gt-desc.hfstol"
        self.analyser = hfst.HfstInputStream(str(analyser_path)).read()

        generator_path = Path("/usr/share/giella") / lang / "generator-gt-norm.hfstol"
        self.generator = hfst.HfstInputStream(str(generator_path)).read()
        self.lang = lang
        self.paradigm_templates = self.read_taglist()

    def read_taglist(self):
        """Read paradigm generation templates."""
        with open(f"generator/data/{self.lang}.json") as json_stream:
            return json.load(json_stream)

    def generate(self, word, paradigm_template):
        """Generate a paradigm."""
        return (
            Analysis(ATTS.sub("", analysis[0]), analysis[1])
            for analysis in self.generator.lookup(f"{word}+{paradigm_template}")
            if "?" not in analysis[0] and "+Err" not in analysis[0]
        )

    def analyse(self, word):
        """Generate a paradigm."""
        return (
            Analysis(ATTS.sub("", analysis[0]), analysis[1])
            for analysis in self.analyser.lookup(word)
            if "?" not in analysis[0] and "+Err" not in analysis[0]
        )

    def make_generatable_word(self, word, pos):
        """Return a generatable word."""
        if list(self.generate(word, self.best_analysis[pos][1:])):
            return word

        return self.find_best_analysis(word, pos)

    def generate_wordforms(self, word, pos):
        """Given a word and pos, generate a paradigm."""
        generatable_word = self.make_generatable_word(word, pos)

        for paradigm_template in self.paradigm_templates[pos]:
            generated_wordforms = list(
                self.generate(generatable_word, paradigm_template)
            )
            if generated_wordforms:
                yield paradigm_template, generated_wordforms

    def find_best_analysis(self, word, pos):
        """Given a word and a part of speech, find the best analysis of it."""

        no_compounds = [
            analysis
            for analysis in self.analyse(word)
            if "+Cmp#" not in analysis.wordform
        ]

        if no_compounds:
            with_best_analysis = [
                no_compound
                for no_compound in no_compounds
                if no_compound.wordform.endswith(self.best_analysis[pos])
            ]
            if len(with_best_analysis) == 1:
                result = with_best_analysis[0].wordform.replace(
                    self.best_analysis[pos], ""
                )
                # print(result)
                return result

        return ""

    def example_generate_wordforms(self, word, pos):
        """Used for demo/test purposes."""
        print(word, pos)

        for i, result in enumerate(self.generate_wordforms(word, pos)):
            paradigm_template, generated_wordforms = result
            if generated_wordforms:
                print(
                    i,
                    [
                        generated_wordform.wordform
                        for generated_wordform in generated_wordforms
                    ],
                    paradigm_template,
                    len(self.paradigm_templates[pos]),
                )


def main():
    """Check if generation works as expected."""
    examples = {
        "sme": {
            "N": [
                "Alaska-sápmelaš",
                "juolgi",
                "eahpebassivuohta",
                "haida",
                "goŋge",
                "eitte",
                "eadni",
            ]
        },
        "smj": {"N": ["A-vitamijnna", "biebbmobárnne", "loahkka", "addnejuogos"]},
        "fin": {"N": ["4H-kerholainen", "aakkosto"]},
        "smn": {"N": ["akselkoskâ", "eeči", "ovdâjuurdâ", "aalmuglâšeepos"]},
        "sms": {"N": ["kåʹšǩǩjueʹljest", "jueʹlǧǧ"], "V": ["ruppõõvvâd"]},
        "sma": {
            "A": ["raejnies", "tjïelke"],
            "N": [
                "kreavve",
                "båatsoe",
                "AUF-noere",
                "aahkove",
                "voengele",
                "minngienomme",
            ],
            "V": ["juhtedh", "båetedh"],
        },
    }
    for lang, pos_dict in examples.items():
        generator = ParadigmGenerator(lang)
        for pos, stems in pos_dict.items():
            for stem in stems:
                generator.example_generate_wordforms(stem, pos)


if __name__ == "__main__":
    main()
