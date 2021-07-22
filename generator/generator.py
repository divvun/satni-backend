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

    def __init__(self, lang):
        """Initialise HFST analysers."""
        path = Path("/usr/share/giella") / lang / "generator-gt-norm.hfstol"
        self.generator = hfst.HfstInputStream(str(path)).read()
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

    def generate_wordforms(self, word, pos):
        """Given a word and pos, generate a paradigm."""
        for paradigm_template in self.paradigm_templates[pos]:
            generated_wordforms = list(self.generate(word, paradigm_template))
            if generated_wordforms:
                yield paradigm_template, generated_wordforms

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
