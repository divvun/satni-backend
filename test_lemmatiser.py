import unittest

from nose2.tools import params

import lemmatiser


class TestRegexes(unittest.TestCase):
    """Check that the regexes matches what they are supposed to."""
    @params('+A+Sg+Nom', '+A+Pl+Nom', '+A+Attr', '+A+Ess')
    def test_adjective(self, adjective_value):
        assert lemmatiser.ADJECTIVE.match(adjective_value) is not None

    @params('+N+Sg+Nom', '+N+Pl+Nom', '+N+Attr', '+N+Ess', '+N+G3', '+N+G7',
            '+N+Ess', '+N+NomAg')
    def test_noun(self, adjective_value):
        assert lemmatiser.NOUN.match(adjective_value) is not None

    @params('+V+Ind', '+V+Imprt', '+V+Cond', '+V+Pot', '+V+PrfPrc', '+V+Inf',
            '+V+PrsPrc')
    def test_verb(self, verb_value):
        assert lemmatiser.VERB.match(verb_value) is not None

    @params(('+A+Der/Comp+A+Sg+Nom', '+A+Sg+Nom'),
            ('+A+Der/Superl+A+Sg+Nom', '+A+Sg+Nom'))
    def test_adj_comp_subj(self, test_value, expected):
        assert lemmatiser.REMOVEABLE_REGEX_TAGS['adjective_comp_superl'][
            0].sub('', test_value) == expected


class TestLemmatiser(unittest.TestCase):
    """Test the lemmatiser."""
    def setUp(self):
        self.lemmatisers = {}
        self.lemmatisers['sme'] = lemmatiser.Lemmatiser('sme')

    @params(('sme', 'vuolgin', ['vuolgi', 'vuolgin']),
            ('sme', 'vuolgimat', ['vuolgit', 'vuolgi', 'vuolgin']),
            ('sme', 'biillat', ['biila']),
            ('sme', 'biiladoaibmandiliide', ['biiladoaibmandilli']),
            ('sme', 'Åsai', ['Åsa']), ('sme', 'Ø:i', ['Ø.', 'ø', 'ø.']),
            ('sme', 'www:s', ['www']),
            ('sme', 'vuovdit', ['vuovdi', 'vuovdit']),
            ('sme', 'vuorrasit', ['vuoras', 'vuorrasit']),
            ('sme', 'jearahalliguoktái',
             ['jearahalliguoktá', 'jearahalliguovttes', 'jearahalliguovttis']),
            ('sme', 'vuostái', ['vuosti', 'vuostá', 'vuostái']),
            ('sme', 'vuoi', ['vuoi', 'vai']), ('sme', 'vai', ['vai']),
            ('sme', 'vaikko', ['vaikke', 'vaikko', 'váikke', 'váikko']),
            ('sme', 'nu', ['nu']), ('sme', 'omd.', ['omd.']),
            ('sme', 'viđaid', ['vihtta']), ('sme', 'iige', ['ii']))
    def test_lemmatiser(self, language, word, exptected_results):
        """Test that the lemmatiser return expected values."""
        assert self.lemmatisers[language].lemmatise(word) == sorted(
            exptected_results)
