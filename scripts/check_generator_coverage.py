import json
import os
from collections import Counter, defaultdict, namedtuple

from lxml import etree

from generator.generator import ParadigmGenerator
from lemmatiser.lemmatiser import Lemmatiser

from .from_dump import dict_paths, parse_xmlfile

Lemma = namedtuple("Lemma", "lemma pos")


def valid_lemmas(langs):
    name_lemmasest = defaultdict(set)

    dictxmls = (parse_xmlfile(xml_file) for xml_file in dict_paths())

    for dictxml in dictxmls:
        pair = dictxml.getroot().get("id")
        lang = pair[:3]
        if lang in langs:
            with open(f"generator/data/{lang}.json") as json_stream:
                poses = json.load(json_stream).keys()
                for lemma_element in dictxml.iter("l"):
                    pos = lemma_element.get("pos").strip()
                    if pos == "Prop":
                        pos = "N"
                    if lemma_element.text and pos in poses:
                        name_lemmasest[lang].add(Lemma(lemma_element.text.strip(), pos))

    return name_lemmasest


def run():
    langs = ["fin", "sma", "sme", "smj", "smn", "sms"]
    lemmatisers = {lang: Lemmatiser(lang) for lang in langs}
    generators = {lang: ParadigmGenerator(lang) for lang in langs}
    lemmas = valid_lemmas(langs)

    for lang in sorted(lemmas):
        counter = Counter()
        current_analyser = lemmatisers.get(lang)
        current_generator = generators.get(lang)
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
                current_generator.generate_wordforms(lemma.lemma, lemma.pos)
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
