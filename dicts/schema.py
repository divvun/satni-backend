import logging

import graphene
from lemmas.models import Lemma
from mongoengine.queryset.visitor import Q
from stems.has_stem_cache import preload_has_stem

from .models import DictEntry
from .types import DictEntryType

LOGGER = logging.getLogger(__name__)


class Query(graphene.ObjectType):
    dict_entry_list = graphene.List(
        DictEntryType,
        exact=graphene.String(required=True),
        src_langs=graphene.List(graphene.String, required=True),
        target_langs=graphene.List(graphene.String, required=True),
        wanted_dicts=graphene.List(graphene.String, required=True),
    )

    def resolve_dict_entry_list(self, info, wanted_dicts, exact=None, **kwargs):
        src_langs = kwargs["src_langs"]
        target_langs = kwargs["target_langs"]

        matching_lemmas = Lemma.objects(lemma=exact)

        dict_entries = []

        if (
            "fin" in src_langs
            and "sme" in target_langs
            and "sammallahtismefin" in wanted_dicts
        ):
            translation_filter = Q(
                translationGroups__translationLemmas__in=matching_lemmas
            ) & Q(dictName="sammallahtismefin")
            dict_entries.extend(DictEntry.objects(translation_filter))

        lookup_filter = (
            Q(lookupLemmas__in=matching_lemmas)
            & Q(srcLang__in=src_langs)
            & Q(targetLang__in=target_langs)
            & Q(dictName__in=wanted_dicts)
        )
        dict_entries.extend(DictEntry.objects(lookup_filter))

        # Precompute hasStem for every lemma that will appear in the
        # response (lookupLemmas + translationLemmas) in a single indexed
        # Stem query, cached on the request. This lets LemmaType.hasStem
        # answer instantly when the frontend asks for it alongside the
        # dict entries, instead of the frontend issuing a separate hasStem
        # query per stem. Note: this re-accesses references that
        # mongoengine already dereferences (and caches) while building
        # this response, so it doesn't add extra queries beyond the one
        # Stem lookup itself.
        lemma_strings = set()
        for entry in dict_entries:
            lemma_strings.update(lemma.lemma for lemma in entry.lookupLemmas)
            for group in entry.translationGroups:
                lemma_strings.update(lemma.lemma for lemma in group.translationLemmas)
        preload_has_stem(info, lemma_strings, src_langs, target_langs, wanted_dicts)

        if dict_entries:
            LOGGER.info(
                f"{exact} "
                f"src: {', '.join(sorted(src_langs))} "
                f"target: {', '.join(sorted(target_langs))} "
                f"dicts: {', '.join(sorted(wanted_dicts))}"
            )

        return dict_entries
