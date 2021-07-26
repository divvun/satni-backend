"""Test the generator engine."""

import unittest

from nose2.tools import params

from generator.generator import ParadigmGenerator


class TestParadigmGenerator(unittest.TestCase):
    """Test the ParadigmGenerator class."""

    def setUp(self):
        self.generator = ParadigmGenerator("sme")

    @params(
        ("guolli", "N+Sg+Nom"),
        ("vuolgit", "V+IV+Inf"),
        ("vielgat", "A+Sg+Nom"),
        (
            "sihkarvuođaeiseváldi+v3",
            "N+Sg+Nom",
        ),  # +v3 form is a result from find_best_analysis
        (
            "gielda+N+Cmp/SgNom+Cmp#viessu",
            "N+Sg+Nom",
        ),  # the compound is returned from the find_best_analysis
    )
    def test_generate(self, word, paradigm_template):
        """Test that the engine itself works as expected."""
        assert list(self.generator.generate(word, paradigm_template)) != []

    @params(
        ("sihkkarvuođaeiseváldi", "N", "sihkarvuođaeiseváldi+v3"),
        ("gieldaviessu", "N", "gielda+N+Cmp/SgNom+Cmp#viessu"),
    )
    def test_find_best_analysis(self, lemma, pos, best_analysis):
        """Test that the best analysis is found."""
        assert self.generator.find_best_analysis(lemma, pos) == best_analysis
