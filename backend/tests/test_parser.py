import pytest
from backend.app.parser import IndonesianIngredientParser, PARSER

class TestIndonesianIngredientParser:
    @pytest.fixture
    def parser(self):
        return PARSER

    def test_strip_measurement_units(self, parser):
        # 250 gr dada ayam fillet, potong dadu -> ayam
        parsed = parser.parse_ingredient_line("250 gr dada ayam fillet, potong dadu")
        assert "ayam" in parsed

    def test_synonym_normalization(self, parser):
        # bamer -> bawang merah, baput -> bawang putih
        res = parser.parse_query("bamer, baput, cabe rawit")
        core = res["ingredients_core_set"]
        assert "bawang merah" in core
        assert "bawang putih" in core
        assert "cabai rawit" in core

    def test_filter_pantry_staples(self, parser):
        # air, garam, gula, minyak goreng should be filtered from core
        res = parser.parse_query("ayam, air, garam, gula pasir, minyak goreng")
        core = res["ingredients_core_set"]
        assert "ayam" in core
        assert "air" not in core
        assert "garam" not in core
        assert "minyak goreng" not in core

    def test_fractions_and_colloquial(self, parser):
        parsed = parser.parse_ingredient_line("1/2 sdt merica bubuk")
        assert "merica" in parsed
