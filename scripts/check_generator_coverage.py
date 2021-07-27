import json
import os
from collections import Counter, defaultdict, namedtuple

from lxml import etree

from generator.generator import ParadigmGenerator
from lemmatiser.lemmatiser import Lemmatiser

from .from_dump import dict_paths, parse_xmlfile

Lemma = namedtuple("Lemma", "lemma pos")


def valid_dictxmls():
    """Only wanted dict files."""
    langs = ["fin", "sma", "sme", "smj", "smn", "sms"]
    dictxmls = (parse_xmlfile(xml_file) for xml_file in dict_paths())
    for dictxml in dictxmls:
        lang = dictxml.getroot().get("id")[:3]
        if lang in langs:
            with open(f"generator/data/{lang}.json") as json_stream:
                yield lang, json.load(json_stream).keys(), dictxml


def valid_lemmas():
    """Only lemmas that are generatable according the lang.json files."""
    name_lemmasest = defaultdict(set)

    for lang, poses, dictxml in valid_dictxmls():
        for lemma, pos in [
            (lemma_element.text, lemma_element.get("pos").strip())
            for lemma_element in dictxml.iter("l")
        ]:
            pos = "N" if pos == "Prop" else pos
            if lemma and pos in poses:
                name_lemmasest[lang].add(Lemma(lemma.strip(), pos))

    return name_lemmasest


def run():
    """Check if lemmas from dicts are generateble."""
    lemmas = valid_lemmas()

    counter = Counter()
    for lang in sorted(lemmas):
        current_analyser = Lemmatiser(lang)
        current_generator = ParadigmGenerator(lang)
        for lemma in lemmas[lang]:
            counter[lang] += 1
            # if not counter[lang] % 1000:
            #     print(
            #         lang,
            #         counter[lang],
            #         counter[f"{lang}_not_generated"]
            #         if counter.get(f"{lang}_not_generated")
            #         else 0,
            #         counter[f"{lang}_not_analysed"]
            #         if counter.get(f"{lang}_not_analysed")
            #         else 0,
            #     )
            generated = list(
                current_generator.generate_and_check(lemma.lemma, lemma.pos)
            )
            if not generated:
                counter[f"{lang}_not_generated"] += 1

                analyses = list(current_analyser.analyse(lemma.lemma))
                if not analyses:
                    counter[f"{lang}_not_analysed"] += 1
                # print(lang)
                # print(f"\t{lemma.lemma} {lemma.pos}")
                # print(
                #     "\n".join(
                #         [
                #             f"\t\t{a_lemma}"
                #             for a_lemma in current_analyser.lemmatise(lemma.lemma)
                #         ]
                #     )
                # )
                # print(
                #     "\n".join(
                #         f"\t\t\t{analysis.analysis}"
                #         for analysis in current_analyser.analyse(lemma.lemma)
                #     )
                # )

        print(" ".join((f"{key}: {count}" for key, count in counter.items())))
