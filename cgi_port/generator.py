import os
import re
from collections import defaultdict
from pathlib import Path

import hfst

ATTS = re.compile(r"@[^@]+@")


class ParadigmGenerator(object):
    """Generate paradigms using hfst."""

    def __init__(self, lang):
        """Initialise HFST analysers."""
        path = Path("/usr/share/giella") / lang / "generator-gt-norm.hfstol"
        self.generator = hfst.HfstInputStream(str(path)).read()
        self.lang = lang
        self.lang_template_dir = (
            Path(os.getenv("GTLANGS")) / f"lang-{self.lang}/test/data"
        )
        self.paradigm_templates = self.generate_taglist()

    def generate_taglist(self):
        """Read the grammar for paradigm tag list.

        Call the recursive function that generates the tag list.
        """

        grammar = self.make_grammar()
        tag_dict = self.read_tags()
        paradigm_templates = defaultdict(list)

        # Read each grammar rule and generate the taglist.
        for gram in grammar:
            pos, *subclasses = gram.split("+")
            taglist = []
            self.generate_tag(pos, tag_dict, subclasses, taglist)

            paradigm_templates[pos].extend(taglist)

        return paradigm_templates

    def generate_tag(self, tag, tag_dict, classes, taglist):
        """Travel recursively the taglists and generate the tagsets for pardigm generation.

        Arguments:
            tag: str
            tags_href: dict
            classes: list
            taglist_aref: list
        The taglist is stored to the array reference $taglist_aref.
        """
        if not classes:
            taglist.append(tag)
        else:
            class_, *new_class = classes
            if "?" in class_:
                self.generate_tag(tag, tag_dict, new_class, taglist)

            class_ = class_.replace("?", "")
            if not tag_dict.get(class_):
                self.generate_tag(f"{tag}+{class_}", tag_dict, new_class, taglist)
            else:
                for t in tag_dict[class_]:
                    self.generate_tag(f"{tag}+{t}", tag_dict, new_class, taglist)

    def make_grammar(self):
        """Make the grammar list."""
        filename = (
            f"paradigm_full.{self.lang}.txt"
            if self.lang != "smj"
            else f"paradigm_standard.{self.lang}.txt"
        )
        gramfile = self.lang_template_dir / filename
        with gramfile.open() as gramfile_stream:
            return [line for line in self.valid_tag_lines(gramfile_stream)]

    def generate(self, word, paradigm):
        """Generate a paradigm."""
        return (
            ATTS.sub("", analysis[0])
            for analysis in self.generator.lookup(f"{word}+{paradigm}")
            if "?" not in analysis[0] and "+Err" not in analysis[0]
        )

    def generate_wordforms(self, word, pos):
        """Given a word and pos, generate a paradigm."""
        print(word, pos)

        for i, paradigm_template in enumerate(self.paradigm_templates[pos]):
            generated_wordforms = list(self.generate(word, paradigm_template))
            if generated_wordforms:
                print(
                    i,
                    generated_wordforms,
                    paradigm_template,
                    len(self.paradigm_templates[pos]),
                )

    def read_tags(self):
        """Read morphological tags from a file."""
        tagfile = self.lang_template_dir / f"korpustags.{self.lang}.txt"
        tags = []
        tag_dict = {}
        with tagfile.open() as tagfile_stream:
            for line in self.valid_tag_lines(tagfile_stream):
                if line.startswith("#"):
                    tag_class = line[1:]
                    tag_dict[tag_class] = tags
                    tags = []
                else:
                    tags.append(line.split()[0])

        return tag_dict

    @staticmethod
    def is_valid_tagline(tagline):
        """Check if tagline is something useful."""
        return not (tagline.strip() == "" or tagline.startswith("%") or "=" in tagline)

    def valid_tag_lines(self, tagfile_stream):
        """Return only useful lines."""
        return (
            tagline.strip()
            for tagline in tagfile_stream
            if self.is_valid_tagline(tagline)
        )


def main():
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
        lemmatiser = ParadigmGenerator(lang)
        for pos, stems in pos_dict.items():
            for stem in stems:
                lemmatiser.generate_wordforms(stem, pos)


if __name__ == "__main__":
    main()
