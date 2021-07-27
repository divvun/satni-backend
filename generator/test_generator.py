"""Test the generator engine."""

import unittest

from nose2.tools import params

from generator.generator import ParadigmGenerator


class TestParadigmGenerator(unittest.TestCase):
    """Test the ParadigmGenerator class."""

    def setUp(self):
        self.generator = ParadigmGenerator("sme")

    @params(
        ("guolli", "N"),
        ("vuolgit", "V"),
        ("vielgat", "A"),
        (
            "sihkarvuođaeiseváldi+v3",
            "N",
        ),  # +v3 form is a result from find_best_analysis
        (
            "gielda+N+Cmp/SgNom+Cmp#viessu",
            "N",
        ),  # the compound is returned from the find_best_analysis
        (
            "olgoriika+N+Cmp/SgNom+Cmp#ášši",
            "N",
        ),  # the compound is returned from the find_best_analysis
    )
    def test_generate(self, word, partOfSpeech):
        """Test that the engine itself works as expected."""
        assert list(self.generator.generate_wordforms(word, partOfSpeech)) != []

    @params(
        ("sihkkarvuođaeiseváldi", "N", "sihkarvuođaeiseváldi+v3"),
        ("gieldaviessu", "N", "gielda+N+Cmp/SgNom+Cmp#viessu"),
        ("olgoriikaášši", "N", "olgoriika+N+Cmp/SgNom+Cmp#ášši"),
    )
    def test_find_best_analysis(self, lemma, pos, best_analysis):
        """Test that the best analysis is found."""
        assert self.generator.find_best_analysis(lemma, pos) == best_analysis
