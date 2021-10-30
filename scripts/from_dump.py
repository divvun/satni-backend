#!/usr/bin/env python3
import glob
import os
import re
import sys

from lxml import etree
from mongoengine.errors import ValidationError
from termwikiimporter import bot

from dicts.models import DictEntry, ExampleGroup, Restriction, TranslationGroup
from lemmas.models import Lemma
from stems.models import Stem
from terms.models import Concept, Term

REMOVER_RE = r'[ꞌ|@ˣ."*]'
"""Remove these characters from Sammallahti's original lemmas."""

LEMMAS = {}
STEMS = {}
LANGS = {
    "en": "eng",
    "fi": "fin",
    "nb": "nob",
    "nn": "nno",
    "sv": "swe",
    "lat": "lat",
    "sma": "sma",
    "se": "sme",
    "smj": "smj",
    "smn": "smn",
    "sms": "sms",
}

DICTS = [
    "smenob",
    "nobsme",
    "nobsma",
    "smanob",
    "smefin",
    "finsme",
    "smesmn",
    "smnsme",
    "finsmn",
    "smnfin",
    "finnob",
    "smesma",
    "smasme"
    # uncomment these to do generation coverage
    # "smesmj",
    # "smjnob",
    # "smjsme",
    # "sms2X",
]


def sammallahti_remover(line):
    """Remove Sammallahti's special characters."""
    return re.sub(REMOVER_RE, "", line).strip()


def sammallahti_replacer(line):
    """Replace special characters found in Sammallahti's dictionary."""
    return sammallahti_remover(line).translate(
        str.maketrans("Èéíïēīĵĺōūḥḷṃṇṿạẹọụÿⓑⓓⓖ·ṛü’ ", "Eeiieijlouhlmrvaeouybdg ru' ")
    )


def make_lemma(lang, expression):
    lemma_key = f"{expression['expression']}{expression['pos']}{LANGS[lang]}"
    if not LEMMAS.get(lemma_key):
        lemma = Lemma(
            lemma=expression["expression"],
            presentation_lemma=expression["expression"],
            pos=expression["pos"],
            language=LANGS[lang],
            dialect=None,
            country=None,
        )
        lemma.save()
        LEMMAS[lemma_key] = lemma

    return LEMMAS[lemma_key]


def make_terms(lang, concept):
    for expression in same_lang_sanctioned_expressions(
        lang, concept.related_expressions
    ):
        term = Term(
            status=expression.get("status"),
            sanctioned=expression.get("sanctioned", False),
            note=expression.get("note"),
            source=expression.get("source"),
            expression=make_lemma(lang, expression),
        )
        yield term


def get_definition(lang, concept):
    for concept_info in concept.data["concept_infos"]:
        if lang == concept_info["language"]:
            return concept_info.get("definition")


def get_explanation(lang, concept):
    for concept_info in concept.data["concept_infos"]:
        if lang == concept_info["language"]:
            return concept_info.get("explanation")


def same_lang_sanctioned_expressions(lang, expressions):
    return [
        expression
        for expression in expressions
        if expression["language"] == lang and expression["sanctioned"] == "True"
    ]


def get_valid_langs(concept):
    return {
        lang
        for lang in concept.languages()
        if same_lang_sanctioned_expressions(lang, concept.related_expressions)
    }


def make_concepts(title, concept, valid_langs):
    for lang in valid_langs:
        c = Concept(
            name=f"{title}",
            definition=get_definition(lang, concept),
            explanation=get_explanation(lang, concept),
            terms=make_terms(lang, concept),
            collections=[collection for collection in concept.collections],
        )
        c.save()


def make_m():
    print("Importing TermWiki content")
    dumphandler = bot.DumpHandler()
    for (title, concept) in dumphandler.concepts:
        if concept.has_sanctioned_sami():
            valid_langs = get_valid_langs(concept)
            extract_term_stems(concept, valid_langs)
            make_concepts(title, concept, valid_langs)


def make_empty_stem(lemma):
    STEMS[lemma] = {key: set() for key in ["fromlangs", "tolangs", "dicts"]}


def extract_term_stems(concept, valid_langs):
    for lang in valid_langs:
        for expression in same_lang_sanctioned_expressions(
            lang, concept.related_expressions
        ):
            lemma = expression["expression"]
            stem = STEMS.get(lemma, make_empty_stem(lemma))

            stem["dicts"].add("termwiki")
            stem["fromlangs"].add(LANGS[lang])
            for lang2 in valid_langs:
                if lang2 != lang:
                    stem["tolangs"].add(LANGS[lang2])


# Dict import below here


def normalise_lemma(lemma: str) -> str:
    for offending, replacement in [("\n", " "), ("  ", " ")]:
        while offending in lemma:
            lemma = lemma.replace(offending, replacement)

    return lemma


def make_dict_lemma(element, lang):
    normalised_lemma = normalise_lemma(element.text)
    lemma = sammallahti_replacer(normalised_lemma)
    presentation_lemma = normalised_lemma

    lemma_key = f"{lemma}{presentation_lemma}" f"{element.get('pos')}{lang}"
    if not LEMMAS.get(lemma_key):
        lemma = Lemma(
            lemma=lemma,
            presentation_lemma=normalised_lemma,
            language=lang,
            pos=element.get("pos"),
            dialect=element.get("dialect"),
            country=element.get("country"),
        )
        lemma.save()
        LEMMAS[lemma_key] = lemma

    return LEMMAS[lemma_key]


def make_lemmas(translations, target):
    return [
        make_dict_lemma(translation, target)
        for translation in translations
        if translation.text is not None
    ]


def make_restriction(translation_group):
    restriction_element = translation_group.find("./re")
    if restriction_element is not None:
        return Restriction(
            restriction=restriction_element.text,
            attributes=str(restriction_element.attrib),
        )

    t_element = translation_group.find("./t[@reg]")
    if t_element is not None and t_element.get("reg").lower() != "x":
        return Restriction(restriction=t_element.get("reg"), attributes="")


def make_example(example):
    return ExampleGroup(
        example=example.find("./x").text, translation=example.find("./xt").text
    )


def make_examples(examples):
    return [make_example(example) for example in examples]


def make_translation_group(translation_group, target):
    return TranslationGroup(
        translationLemmas=make_lemmas(translation_group.xpath("./t"), target),
        restriction=make_restriction(translation_group),
        exampleGroups=make_examples(translation_group.xpath("./xg")),
    )


def make_translation_groups(translation_groups, target):
    return [
        make_translation_group(translation_group, target)
        for translation_group in translation_groups
        if translation_group.get("{http://www.w3.org/XML/1998/namespace}lang") == target
    ]


def add_to_stems(lemma, dictname, src, target):
    if "(+" not in lemma:
        stem = STEMS.get(lemma, make_empty_stem(lemma))
        stem["dicts"].add(f"{dictname}{src}{target}")
        stem["fromlangs"].add(src)
        stem["tolangs"].add(target)
    else:
        print(f"Not making {lemma} searchable")


def add_dictentry_to_stems(dict_entry, dictprefix, src, target):
    for lookup_lemma in dict_entry.lookupLemmas:
        add_to_stems(
            sammallahti_replacer(lookup_lemma.lemma)
            if dictprefix == "ps"
            else lookup_lemma.lemma,
            dictprefix,
            src,
            target,
        )

    if dictprefix == "ps":
        for translation_group in dict_entry.translationGroups:
            for translation_lemma in translation_group.translationLemmas:
                add_to_stems(
                    sammallahti_replacer(translation_lemma.lemma),
                    dictprefix,
                    src,
                    target,
                )


def make_dict_entries(dictxml, dictprefix, src, target):
    for entry in dictxml.iter("e"):
        if (
            f"{src}{target}" not in ["smesma", "smasme"] and entry.get("src") != "gg"
        ) or (
            f"{src}{target}" in ["smesma", "smasme"] and entry.get("note") == "checked"
        ):
            dict_entry = DictEntry(
                dictName=f"{dictprefix}{src}{target}",
                srcLang=src,
                targetLang=target,
                lookupLemmas=make_lemmas(entry.xpath(".//l"), src),
                translationGroups=make_translation_groups(entry.xpath(".//tg"), target),
            )
            dict_entry.save()
            yield dict_entry


def make_entries(dictxml, dictprefix):
    pair = dictxml.getroot().get("id")
    src = pair[:3]
    target = pair[3:]

    for dict_entry in make_dict_entries(dictxml, dictprefix, src, target):
        add_dictentry_to_stems(dict_entry, dictprefix, src, target)


def import_dictfile(xml_file):
    print(f"\t{os.path.basename(xml_file)}")
    dictxml = parse_xmlfile(xml_file)
    make_entries(dictxml, dictprefix="gt")


def validate_dictfile(xml_file):
    try:
        dictxml = parse_xmlfile(xml_file)
        pair = dictxml.getroot().get("id")
        if pair not in xml_file:
            return f"{xml_file}:\n\tinvalid id: {pair}"
    except etree.XMLSyntaxError as error:
        return f"{xml_file}:\n\t{error}"


def invalid_dicts():
    for xml_file in dict_paths():
        invalid = validate_dictfile(xml_file)
        if invalid is not None:
            yield invalid


def dict_paths():
    return [
        xml_file
        for pair in DICTS
        for xml_file in glob.glob(
            os.path.join(os.getenv("GTHOME"), "words/dicts", pair, "src") + "/*.xml"
        )
        if not xml_file.endswith("meta.xml") and "Der_" not in xml_file
    ]


def import_dicts():
    for xml_file in dict_paths():
        import_dictfile(xml_file)


def parse_xmlfile(xml_file):
    parser = etree.XMLParser(remove_comments=True)
    return etree.parse(xml_file, parser=parser)


def import_sammallahti():
    print(f"Pekka Sammallahtis sme-fin dictionary")
    xml_file = os.path.join("../sammallahti/sammallahti.xml")
    try:
        print(f"\t{os.path.basename(xml_file)}")
        make_entries(parse_xmlfile(xml_file), dictprefix="sammallahti")
    except etree.XMLSyntaxError as error:
        print(
            "Syntax error in {} "
            "with the following error:\n{}\n".format(xml_file, error),
            file=sys.stderr,
        )
    except OSError:
        print("Continuing without Sammallahti's dictionary")


def make_stems():
    for stem in STEMS:
        try:
            s = Stem(
                stem=stem,
                search_stem=stem.lower(),
                srclangs=list(STEMS[stem]["fromlangs"]),
                targetlangs=list(STEMS[stem]["tolangs"]),
                dicts=list(STEMS[stem]["dicts"]),
            )
            s.save()
        except ValidationError as error:
            print(error)
            print(stem)


def run():
    invalids = invalid_dicts()
    if list(invalids):
        raise SystemExit(
            "Invalid dicts, stopping import:\n{}".format("\n".join(invalids))
        )
    import_sammallahti()
    import_dicts()
    make_m()
    make_stems()
