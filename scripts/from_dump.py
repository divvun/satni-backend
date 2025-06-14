#!/usr/bin/env python3
import glob
import os
import re
import sys

from lxml import etree
from mongoengine.errors import ValidationError
from termwikitools import dumphandler

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
    "lat": "lat",
    "nb": "nob",
    "nn": "nno",
    "se": "sme",
    "sma": "sma",
    "smj": "smj",
    "smn": "smn",
    "sms": "sms",
    "sv": "swe",
}

DICTS = [
    "fin-nob",
    "fin-sme",
    "fin-smn",
    "nob-sma",
    "nob-sme",
    "sma-mul",
    "sma-sme",
    "sme-fin",
    "sme-nob",
    "sme-sma",
    "sme-smn",
    "smn-fin",
    "smn-sme",
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
    lemma_key = f"{expression.expression}{expression.pos}{LANGS[lang]}"
    if not LEMMAS.get(lemma_key):
        lemma = Lemma(
            lemma=expression.expression,
            presentation_lemma=expression.expression,
            pos=expression.pos,
            language=LANGS[lang],
            dialect=None,
            country=None,
        )
        lemma.save()
        LEMMAS[lemma_key] = lemma

    return LEMMAS[lemma_key]


def make_terms(lang, concept):
    """Make terms in the database."""
    for expression in same_lang_sanctioned_expressions(
        lang, concept.related_expressions
    ):
        term = Term(
            status=expression.status,
            sanctioned=expression.sanctioned,
            note=expression.note,
            source=expression.source,
            expression=make_lemma(lang, expression),
        )
        yield term


def get_definition(lang, termwiki_concept):
    """Find the definition"""
    if termwiki_concept.concept_infos is not None:
        for concept_info in termwiki_concept.concept_infos:
            if lang == concept_info.language:
                return concept_info.definition


def get_explanation(lang, termwiki_concept):
    """Find the explanatiion."""
    if termwiki_concept.concept_infos is not None:
        for concept_info in termwiki_concept.concept_infos:
            if lang == concept_info.language:
                return concept_info.explanation


def same_lang_sanctioned_expressions(lang, expressions):
    return [
        expression
        for expression in expressions
        if expression.language == lang and expression.sanctioned == "True"
    ]


def get_valid_langs(termwiki_concept):
    return {
        related_expression.language
        for related_expression in termwiki_concept.related_expressions
        if related_expression.sanctioned == "True"
    }


def make_concepts(title, termwiki_concept, valid_langs):
    for lang in valid_langs:
        c = Concept(
            name=f"{title}",
            language=lang,
            definition=get_definition(lang, termwiki_concept),
            explanation=get_explanation(lang, termwiki_concept),
            terms=make_terms(lang, termwiki_concept),
            collections=list(termwiki_concept.concept.collection)
            if termwiki_concept.concept is not None
            and termwiki_concept.concept.collection is not None
            else set(),
        )
        c.save()


def make_m():
    print("Importing TermWiki content")
    dumper = dumphandler.DumpHandler()
    for title, termwiki_page in dumper.termwiki_pages:
        if termwiki_page.has_sanctioned_sami():
            valid_langs = get_valid_langs(termwiki_page)
            extract_term_stems(termwiki_page, valid_langs)
            make_concepts(title, termwiki_page, valid_langs)


def get_stem(lemma):
    if STEMS.get(lemma) is None:
        STEMS[lemma] = {key: set() for key in ["fromlangs", "tolangs", "dicts"]}

    return STEMS[lemma]


def extract_term_stems(concept, valid_langs):
    for lang in valid_langs:
        for expression in same_lang_sanctioned_expressions(
            lang, concept.related_expressions
        ):
            lemma = expression.expression
            stem = get_stem(lemma)

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


def make_dict_lemma(element, lang, dictprefix):
    normalised_lemma = normalise_lemma(element.text)
    lemma = (
        sammallahti_replacer(normalised_lemma)
        if dictprefix == "sammallahti"
        else normalised_lemma
    )
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


def make_lemmas(translations, target, dictprefix):
    return [
        make_dict_lemma(translation, target, dictprefix)
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


def make_example(example, target):
    translation_element = example.find("./xt")
    if (
        translation_element.get("{http://www.w3.org/XML/1998/namespace}lang") is None
    ) or (
        translation_element.get("{http://www.w3.org/XML/1998/namespace}lang") == target
    ):
        return ExampleGroup(
            example=example.find("./x").text, translation=translation_element.text
        )

    return []


def make_examples(examples, target):
    return [make_example(example, target) for example in examples if len(example)]


def make_translation_group(translation_group, target, dictprefix):
    return TranslationGroup(
        translationLemmas=make_lemmas(
            translation_group.xpath("./t"), target, dictprefix
        ),
        restriction=make_restriction(translation_group),
        exampleGroups=make_examples(translation_group.xpath("./xg"), target),
    )


def make_translation_groups(translation_groups, target, dictprefix):
    return [
        make_translation_group(translation_group, target, dictprefix)
        for translation_group in translation_groups
        if translation_group.get("{http://www.w3.org/XML/1998/namespace}lang") == target
    ]


def add_to_stems(lemma, dictname, src, target):
    if "(+" not in lemma:
        stem = get_stem(lemma)
        stem["dicts"].add(f"{dictname}{src}{target}")
        stem["fromlangs"].add(src)
        stem["tolangs"].add(target)
    else:
        print(f"Not making {lemma} searchable")


def add_dictentry_to_stems(dict_entry, dictprefix, src, target):
    for lookup_lemma in dict_entry.lookupLemmas:
        add_to_stems(
            sammallahti_replacer(lookup_lemma.lemma)
            if dictprefix == "sammallahti"
            else lookup_lemma.lemma,
            dictprefix,
            src,
            target,
        )

    if dictprefix == "sammallahti":
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
            translation_groups = make_translation_groups(
                entry.xpath(".//tg"), target, dictprefix
            )
            if translation_groups:
                dict_entry = DictEntry(
                    dictName=f"{dictprefix}{src}{target}",
                    srcLang=src,
                    targetLang=target,
                    lookupLemmas=make_lemmas(entry.xpath(".//l"), src, dictprefix),
                    translationGroups=translation_groups,
                )
                try:
                    dict_entry.save()
                    yield dict_entry
                except ValidationError as error:
                    print("Invalid entry")
                    print(etree.tostring(entry, encoding="unicode"))
                    print(str(error))


def make_entries(dictxml, dictprefix):
    pair = dictxml.getroot().get("id")
    src = pair[:3]
    target = "nob" if pair[3:] == "mul" else pair[3:]

    for dict_entry in make_dict_entries(dictxml, dictprefix, src, target):
        add_dictentry_to_stems(dict_entry, dictprefix, src, target)


def import_dictfile(xml_file):
    print(f"\t{os.path.basename(xml_file)}")
    dictxml = parse_xmlfile(xml_file)
    make_entries(dictxml, dictprefix="gt")


def dict_paths():
    return [
        xml_file
        for pair in DICTS
        for xml_file in glob.glob(
            os.path.join(os.getenv("GUTHOME"), "giellalt", f"dict-{pair}", "src")
            + "/*.xml"
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
    print("Pekka Sammallahtis sme-fin dictionary")
    xml_file = os.path.join(
        os.getenv("GUTHOME"),
        "giellalt",
        "dict-sme-fin-x-sammallahti",
        "src",
        "sammallahti.xml",
    )
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


def import_smjmed():
    print("Hábmers medicinal smj-nob-smj dictionaries")
    habmer_home = os.path.join(
        os.getenv("GUTHOME"), "giellalt", "dict-smj-nob-x-habmer"
    )
    for xml_file in glob.glob(f"{habmer_home}/*.xml"):
        print(f"\t{os.path.basename(xml_file)}")
        try:
            make_entries(parse_xmlfile(xml_file), dictprefix="habmer")
        except etree.XMLSyntaxError as error:
            print(
                "Syntax error in {} "
                "with the following error:\n{}\n".format(xml_file, error),
                file=sys.stderr,
            )
        except OSError:
            print(f"Continuing without {xml_file}")


def import_sms():
    print("sms dicts")
    dictprefix = "gt"
    for lang in ["fin", "nob", "rus"]:
        for xml_file in glob.glob(
            os.path.join(os.getenv("GUTHOME"), "giellalt", f"dict-{lang}-sms", "src")
            + "/*.xml"
        ):
            if not xml_file.endswith("meta.xml") and "Der_" not in xml_file:
                print(xml_file)
                for dict_entry in make_dict_entries(
                    parse_xmlfile(xml_file), dictprefix, lang, "sms"
                ):
                    add_dictentry_to_stems(dict_entry, dictprefix, lang, "sms")

    for xml_file in glob.glob(
        os.path.join(os.getenv("GUTHOME"), "giellalt", "dict-sms-mul", "src") + "/*.xml"
    ):
        if not xml_file.endswith("meta.xml") and "Der_" not in xml_file:
            dictxml = parse_xmlfile(xml_file)
            for lang in ["fin", "nob", "rus"]:
                print(xml_file, "sms", lang)
                for dict_entry in make_dict_entries(dictxml, dictprefix, "sms", lang):
                    add_dictentry_to_stems(dict_entry, dictprefix, "sms", lang)


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
    import_sammallahti()
    import_dicts()
    make_m()
    import_smjmed()
    import_sms()
    make_stems()
