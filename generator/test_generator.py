"""Test the generator engine."""

import unittest

from nose2.tools import params

from generator.generator import ParadigmGenerator


class TestParadigmGenerator(unittest.TestCase):
    """Test the ParadigmGenerator class."""

    def setUp(self):
        self.generators = {
            language: ParadigmGenerator(language) for language in ["sme", "sma"]
        }

    @params(
        ("sme", "guolli", "N"),
        ("sme", "vuolgit", "V"),
        ("sme", "vielgat", "A"),
        (
            "sme",
            "sihkarvuođaeiseváldi+v3",
            "N",
        ),  # +v3 form is a result from find_best_analysis
        (
            "sme",
            "gielda+N+Cmp/SgNom+Cmp#viessu",
            "N",
        ),  # the compound is returned from the find_best_analysis
        (
            "sme",
            "olgoriika+N+Cmp/SgNom+Cmp#ášši",
            "N",
        ),  # the compound is returned from the find_best_analysis
        (
            "sme",
            "viellja+N+Der/lasj",
            "A",
        ),  # the derivation is returned from the find_best_analysis
        (
            "sme",
            "njammat+V+TV+Der/PassS+V+IV+Der/d",
            "V",
        ),
        (
            "sme",
            "nubbi nubbi",
            "Pron",
        ),
        ("sma", "Magdiel", "N"),
    )
    def test_generate(self, language, word, part_of_speech):
        """Test that the engine itself works as expected."""
        assert (
            list(self.generators[language].generate_wordforms(word, part_of_speech))
            != []
        )

    @params(
        ("sme", "sihkkarvuođaeiseváldi", "N", "sihkarvuođaeiseváldi+v3"),
        ("sme", "gieldaviessu", "N", "gielda+N+Cmp/SgNom+Cmp#viessu"),
        ("sme", "olgoriikaášši", "N", "olgoriika+N+Cmp/SgNom+Cmp#ášši"),
        ("sme", "vieljalaš", "A", "viellja+N+Der/lasj"),
        ("sme", "njammot", "V", "njammat+V+TV+Der/PassS+V+IV+Der/d"),
        ("sme", "nuppit nuppiid", "Pron", "nubbi nubbi"),
        ("sma", "Magdiel", "N", "Magdiel"),
    )
    def test_find_best_analysis(self, language, lemma, pos, best_analysis):
        """Test that the best analysis is found."""
        assert self.generators[language].find_best_analysis(lemma, pos) == best_analysis
