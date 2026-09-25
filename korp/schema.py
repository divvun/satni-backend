"""GraphQL query for checking lemma existence in the Korp corpus."""

import graphene

from .client import KORP_INFO, lemma_exists


class Query(graphene.ObjectType):
    """Query class for Korp."""

    korp_lemma_exists = graphene.Boolean(
        language=graphene.String(required=True),
        lemma=graphene.String(required=True),
    )

    def resolve_korp_lemma_exists(self, info, language, lemma):
        """Check, with caching, whether the lemma exists in the Korp corpus."""
        if language not in KORP_INFO:
            return False

        return lemma_exists(language, lemma)
