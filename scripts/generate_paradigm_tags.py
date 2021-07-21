"""Make taglist for usage in the generator."""
import json
import os
import re
from collections import defaultdict
from pathlib import Path

ATTS = re.compile(r"@[^@]+@")


class TaglistGenerator:
    """Generate tags dictionaries."""
    def __init__(self, lang):
        """Init the class."""
        self.lang = lang
        self.lang_template_dir = (Path(os.getenv("GTLANGS")) /
                                  f"lang-{self.lang}/test/data")

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

        with open(f'generator/data/{self.lang}.json', 'w') as tag_stream:
            json.dump(paradigm_templates, tag_stream, indent=2)

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
                self.generate_tag(f"{tag}+{class_}", tag_dict, new_class,
                                  taglist)
            else:
                for t in tag_dict[class_]:
                    self.generate_tag(f"{tag}+{t}", tag_dict, new_class,
                                      taglist)

    def make_grammar(self):
        """Make the grammar list."""
        filename = (f"paradigm_full.{self.lang}.txt" if self.lang != "smj" else
                    f"paradigm_standard.{self.lang}.txt")
        gramfile = self.lang_template_dir / filename
        with gramfile.open() as gramfile_stream:
            return [line for line in self.valid_tag_lines(gramfile_stream)]

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
        return not (tagline.strip() == "" or tagline.startswith("%")
                    or "=" in tagline)

    def valid_tag_lines(self, tagfile_stream):
        """Return only useful lines."""
        return (tagline.strip() for tagline in tagfile_stream
                if self.is_valid_tagline(tagline))


def run():
    for language in ['fin', 'sma', 'sme', 'smj', 'smn', 'sms']:
        generator = TaglistGenerator(language)
        generator.generate_taglist()
