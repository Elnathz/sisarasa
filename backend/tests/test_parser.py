import pytest
from backend.app.parser import IndonesianIngredientParser, PARSER

class TestIndonesianIngredientParser:
    @pytest.fixture
    def parser(self):
        return PARSER

    def test_strip_measurement_units(self, parser):
        parsed = parser.parse_ingredient_line("250 gr dada ayam fillet, potong dadu")
        assert parsed == "ayam"

    def test_synonym_normalization(self, parser):
        res = parser.parse_query("bamer, baput, cabe rawit")
        core = res["ingredients_core_set"]
        assert "bawang merah" in core
        assert "bawang putih" in core
        assert "cabai rawit" in core

    def test_filter_pantry_staples(self, parser):
        res = parser.parse_query("ayam, air, garam, gula pasir, minyak goreng")
        core = res["ingredients_core_set"]
        assert "ayam" in core
        assert "air" not in core
        assert "garam" not in core
        assert "minyak goreng" not in core

    def test_fractions_and_colloquial(self, parser):
        parsed = parser.parse_ingredient_line("1/2 sdt merica bubuk")
        assert parsed == "merica"

    def test_noise_and_chatter_filtering(self, parser):
        assert parser.parse_ingredient_line("5 bh tahu kuning, belah 4") == "tahu"
        assert parser.parse_ingredient_line("100 gr Bumbu Kacang untuk Sate") == "bumbu kacang"
        assert parser.parse_ingredient_line("1 siung Bawang putih uk besar") == "bawang putih"
        assert parser.parse_ingredient_line("1 papan tempe (resep asli pakai tahu)") == "tempe"
        assert parser.parse_ingredient_line("tusuk sate secukupnya") == ""
        assert parser.parse_ingredient_line("Bahan Sambal :") == ""

    def test_attached_units_and_reduplication(self, parser):
        assert parser.parse_ingredient_line("santan 65ml") == "santan"
        assert parser.parse_ingredient_line("daun jeruk sobek2") == "daun jeruk"
        assert parser.parse_ingredient_line("tomat potong²") == "tomat"

    def test_emoji_and_stray_punctuation(self, parser):
        assert parser.parse_ingredient_line("tomat \U0001f345") == "tomat"
        assert parser.parse_ingredient_line("cabai rawit (") == "cabai rawit"
        assert parser.parse_ingredient_line("ayam (") == "ayam"

    def test_liquid_dilution_and_commercial_modifiers(self, parser):
        assert parser.parse_ingredient_line("500 gr tepung terigu serbaguna") == "tepung terigu"
        assert parser.parse_ingredient_line("1 sdm tepung terigu dilarutkan dengan air") == "tepung terigu"
        assert parser.parse_ingredient_line("2 buah tomat diblender dengan air") == "tomat"
        assert parser.parse_ingredient_line("100 gr tepung tapioka mix dengan air") == "tepung tapioka"
        assert parser.parse_ingredient_line("1 bungkus tepung sasa serbaguna") == "tepung bumbu"
        assert parser.parse_ingredient_line("1 sdt susu bubuk putih di cairkan dg air") == "susu bubuk putih"
        assert parser.parse_ingredient_line("tepung terigu segitiga biru") == "tepung terigu"
        assert parser.parse_ingredient_line("tepung terigu pro sedang") == "tepung terigu"
        assert parser.parse_ingredient_line("1 keping terasi larutan dengan air") == "terasi"
