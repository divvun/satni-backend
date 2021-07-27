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

    removable_tags = re.compile(r"\+(IV|TV|Sem/[^+]+)")

    def __init__(self, lang):
        """Initialise HFST analysers."""
        analyser_path = Path("/usr/share/giella") / lang / "analyser-gt-desc.hfstol"
        self.analyser = hfst.HfstInputStream(str(analyser_path)).read()

        generator_path = Path("/usr/share/giella") / lang / "generator-gt-norm.hfstol"
        self.generator = hfst.HfstInputStream(str(generator_path)).read()
        self.lang = lang
        self.paradigm_templates = self.read_taglist()
        self.best_analyses = {
            pos: [
                f"+{paradigm_template}"
                for paradigm_template in self.paradigm_templates[pos]
            ]
            for pos in ["N", "A", "V", "Pron"]
        }

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
        """Analyse the given wordform."""
        return (
            Analysis(
                self.removable_tags.sub("", ATTS.sub("", analysis[0])), analysis[1]
            )
            for analysis in self.analyser.lookup(word)
            if "?" not in analysis[0] and "+Err" not in analysis[0]
        )

    def generate_and_check(self, word, pos):
        wordforms = list(self.generate_wordforms(word, pos))

        if wordforms:
            return wordforms

        if pos in self.best_analyses.keys():
            generatable_word = self.find_best_analysis(word, pos)
            return list(self.generate_wordforms(generatable_word, pos))

        return []

    def generate_wordforms(self, word, pos):
        """Given a word and pos, generate a paradigm."""
        for paradigm_template in self.paradigm_templates[pos]:
            generated_wordforms = list(self.generate(word, paradigm_template))
            if generated_wordforms:
                yield paradigm_template, generated_wordforms

    @staticmethod
    def get_no_compounds(analyses):
        """Remove analyses containing compound forms."""
        return [analysis for analysis in analyses if "+Cmp#" not in analysis.wordform]

    def get_with_best_analysis(self, analyses, pos):
        """Remove analyses without the best analysis."""
        return [
            Analysis(analysis.wordform.replace(best_analysis, ""), analysis.weight)
            for analysis in analyses
            for best_analysis in self.best_analyses[pos]
            if analysis.wordform.endswith(best_analysis)
        ]

    @staticmethod
    def get_shortest_compound(analyses):
        """Find the shortest analysis."""
        if len(analyses) == 1:
            return analyses[0]

        shortest_analysis, *further_analysis = analyses

        for analysis in further_analysis:
            if len(analysis.wordform.split("+Cmp#")) < len(
                shortest_analysis.wordform.split("+Cmp#")
            ):
                shortest_analysis = analysis

        return shortest_analysis

    def find_best_analysis(self, word, pos):
        """Given a word and a part of speech, find the best analysis of it."""
        with_best_analysis = self.get_with_best_analysis(self.analyse(word), pos)
        no_compounds = self.get_no_compounds(with_best_analysis)

        if no_compounds:
            return no_compounds[0].wordform

        if with_best_analysis:
            return self.get_shortest_compound(with_best_analysis).wordform

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
