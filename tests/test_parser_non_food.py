"""Regression tests for the notebook's non-food filter."""

import json
import unittest
from pathlib import Path

from scripts.run_parser_typo_pilot import load_parser


class ParserNonFoodTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path = Path(__file__).resolve().parents[1] / "notebooks" / "sisarasa_v4.ipynb"
        cls.parser, _ = load_parser(json.loads(path.read_bytes()))

    def test_food_names_survive_the_tool_filter(self):
        for raw, expected in (
            ("bumbu taliwang", "bumbu taliwang"),
            ("2 sdm bumbu Taliwang", "bumbu taliwang"),
            ("sambal taliwang", "sambal taliwang"),
        ):
            with self.subTest(raw=raw):
                recipe = self.parser.extract_ingredients_from_recipe([raw])
                query = self.parser.parse_query(raw)
                self.assertEqual(recipe["ingredients_core_set"], {expected})
                self.assertEqual(query["ingredients_core_set"], {expected})

    def test_standalone_tools_remain_excluded(self):
        for raw in ("tusuk sate", "2 Tusuk Sate", "1 batang lidi", "tali (untuk mengikat)"):
            with self.subTest(raw=raw):
                self.assertEqual(self.parser.parse_ingredient_line(raw), "")
                self.assertEqual(self.parser.parse_query(raw)["ingredients_core_set"], set())
