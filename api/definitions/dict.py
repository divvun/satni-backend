from typing import List, Optional

import strawberry

from .lemma import Lemma


@strawberry.type
class Algu:
    lexeme_id: Optional[str]
    word_id: str


@strawberry.type
class LemmaGroup:
    lemmas: List[Lemma]
    algu: Algu


@strawberry.type
class Translation:
    text: str


@strawberry.type
class Restriction:
    text: str


@strawberry.type
class EGExample:
    text: str


@strawberry.type
class EGTranslation:
    text: str


@strawberry.type
class ExampleGroup:
    example: EGExample
    translation: EGTranslation


@strawberry.type
class TranslationGroup:
    restriction: Optional[Restriction]
    translations: List[Translation]
    example_groups: Optional[List[ExampleGroup]]


@strawberry.type
class MeaningGroup:
    translation_groups: List[TranslationGroup]


@strawberry.type
class Dict:
    lemma_group: LemmaGroup
    meaning_groups: List[MeaningGroup]


def make_lemmas(content):
    return [Lemma(**lemma) for lemma in content]


def make_algu(content):
    if content:
        return Algu(**content)


def make_lemma_group(content):
    return LemmaGroup(
        lemmas=make_lemmas(content.get("lemmas")), algu=make_algu(content.get("algu"))
    )


def make_example_group(content):
    return ExampleGroup(
        example=EGExample(**content.get("example")),
        translation=EGTranslation(**content.get("translation")),
    )


def make_translation_groups(translation_groups):
    return [
        TranslationGroup(
            restriction=Restriction(*translation_group.get("restriction"))
            if translation_group.get("restriction") is not None
            else translation_group.get("restriction"),
            translations=[
                Translation(**translation)
                for translation in translation_group.get("translations")
            ],
            example_groups=[
                make_example_group(example_group)
                for example_group in translation_group.get("example_groups")
            ]
            if translation_group.get("example_groups") is not None
            else translation_group.get("example_groups"),
        )
        for translation_group in translation_groups
    ]


def make_meaning_groups(meaning_groups):
    return [
        MeaningGroup(
            translation_groups=make_translation_groups(
                meaning_group.get("translation_groups")
            )
        )
        for meaning_group in meaning_groups
    ]


def make_dict(content):
    return Dict(
        lemma_group=make_lemma_group(content.get("lemma_group")),
        meaning_groups=make_meaning_groups(content.get("meaning_groups")),
    )
