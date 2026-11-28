"""Exercise ingredient explanations through the notebook search entry point."""

import ast
import io
import json
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

from scripts.run_parser_typo_pilot import load_parser


NOTEBOOK = Path(__file__).resolve().parents[1] / "notebooks" / "sisarasa_v4.ipynb"


class SearchIngredientAlternativesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        notebook = json.loads(NOTEBOOK.read_bytes())
        parser, _ = load_parser(notebook)
        cls.namespace = {"np": np, "pd": pd, "PARSER": parser,
                         "IndonesianIngredientParser": type(parser),
                         "Dict": Dict, "List": List, "Optional": Optional, "Tuple": Tuple}
        definitions = {
            "e22a85dc": {"_identity_token_func", "BaseRetriever", "SetOverlapRetriever"},
            "b60a76c9": {"_retrieve_filtered", "search_sisarasa"},
        }
        for cell in notebook["cells"]:
            if cell["id"] not in definitions:
                continue
            tree = ast.parse("".join(cell["source"]))
            nodes = [node for node in tree.body
                     if isinstance(node, (ast.Import, ast.ImportFrom))
                     or getattr(node, "name", None) in definitions[cell["id"]]]
            exec(compile(ast.Module(nodes, []), cell["id"], "exec"), cls.namespace)
        cls.parser = parser

    def search_frame(self, raw, query, **kwargs):
        fields = self.parser.extract_ingredients_from_recipe(raw)
        corpus = pd.DataFrame([{**fields, "doc_id": "recipe", "title_clean": "Resep uji",
                                "main_category": "other", "ingredients_raw_list": raw,
                                "steps_raw_list": []}])
        self.parser.set_known_ingredients(fields["ingredients_all_set"])
        ranker = self.namespace["SetOverlapRetriever"](self.parser)
        ranker.index(corpus)
        self.namespace["df_all"] = corpus
        for key in ("model_setoverlap", "model_tfidf", "model_bm25", "model_hybrid"):
            self.namespace[key] = ranker
        with redirect_stdout(io.StringIO()) as printed:
            result = self.namespace["search_sisarasa"](query, model_name="setoverlap", **kwargs)
        return result, printed.getvalue()

    def search(self, raw, query, **kwargs):
        result, printed = self.search_frame(raw, query, **kwargs)
        return result.iloc[0], printed

    def test_one_or_both_options_satisfy_one_requirement(self):
        raw = ["2 sdm mentega atau margarin", "pisang"]
        self.assertEqual(self.parser.extract_ingredients_from_recipe(raw)["ingredients_core_set"],
                         {"mentega", "margarin", "pisang"})
        cases = (
            ("mentega, pisang", 100.0, "-", 0.6667),
            ("margarin, pisang", 100.0, "-", 0.6667),
            ("mentega, margarin, pisang", 100.0, "-", 1.0),
            ("pisang", 50.0, "margarin atau mentega", 0.3333),
        )
        for query, match, missing, score in cases:
            with self.subTest(query=query):
                result, printed = self.search(raw, query)
                self.assertEqual(result["Match%"], match)
                self.assertEqual(result["Missing Core"], missing)
                self.assertEqual(result["Score"], score)
                if missing != "-":
                    self.assertIn(f"Perlu Dibeli  : {missing}", printed)

    def test_conjunctions_remain_separate_requirements(self):
        result, _ = self.search(
            ["mentega ATAU margarin dan pisang + telur"], "margarin, pisang",
        )
        self.assertEqual(result["Match%"], 66.7)
        self.assertEqual(result["Missing Core"], "telur")

    def test_pantry_item_can_satisfy_a_stated_alternative(self):
        result, _ = self.search(["minyak wijen atau minyak goreng", "pisang"],
                                "minyak goreng, pisang")
        self.assertEqual(result["Match%"], 100.0)
        self.assertEqual(result["Missing Core"], "-")

    def test_parenthetical_note_does_not_create_an_alternative(self):
        result, _ = self.search(["mentega (atau margarin)", "pisang"], "margarin, pisang")
        self.assertEqual(result["Match%"], 50.0)
        self.assertEqual(result["Missing Core"], "mentega")

    def test_explicit_optional_items_are_not_required(self):
        for line in (
            "keju opsional", "keju (opsional untuk taburan)", "keju boleh diskip",
            "keju opsional untuk taburan", "keju [opsional]",
            "keju opsional (untuk taburan)", "keju opsional, kalau suka",
        ):
            with self.subTest(line=line):
                result, _ = self.search(["pisang", line], "pisang")
                self.assertEqual(result["Match%"], 100.0)
                self.assertEqual(result["Missing Core"], "-")
                self.assertEqual(result["Score"], 0.5)
        required, _ = self.search(["pisang", "keju"], "pisang")
        self.assertEqual(required["Match%"], 50.0)
        self.assertEqual(required["Missing Core"], "keju")
        unspecified_amount, _ = self.search(["pisang", "keju secukupnya"], "pisang")
        self.assertEqual(unspecified_amount["Missing Core"], "keju")
        negated_note, _ = self.search(["pisang", "keju tidak  opsional"], "pisang")
        self.assertEqual(negated_note["Match%"], 50.0)
        self.assertNotEqual(negated_note["Missing Core"], "-")

    def test_optional_notes_keep_other_requirements(self):
        result, _ = self.search(["keju opsional dan telur", "pisang"], "pisang")
        self.assertEqual(result["Match%"], 50.0)
        self.assertEqual(result["Missing Core"], "telur")
        alternative, _ = self.search(
            ["mentega atau margarin", "keju opsional", "pisang"], "margarin, pisang",
        )
        self.assertEqual(alternative["Match%"], 100.0)
        self.assertEqual(alternative["Missing Core"], "-")
        mixed, _ = self.search(["pisang", "mentega opsional atau margarin"], "pisang")
        self.assertEqual(mixed["Match%"], 50.0)
        self.assertEqual(mixed["Missing Core"], "margarin atau mentega")
        note, _ = self.search(["pisang", "tahu (tambahkan keju opsional)"], "pisang")
        self.assertEqual(note["Missing Core"], "tahu")
        note, _ = self.search(["pisang", "tahu (tambahkan keju opsional) (untuk taburan)"], "pisang")
        self.assertEqual(note["Missing Core"], "tahu")

    def test_all_optional_recipe_does_not_display_a_percentage(self):
        result, printed = self.search(["keju optional atau mentega tidak wajib"], "keju")
        self.assertTrue(pd.isna(result["Match%"]))
        self.assertEqual(result["Missing Core"], "-")
        self.assertIn("tidak ada bahan inti wajib", printed)

    def test_coverage_label_explains_that_quantities_were_not_checked(self):
        result, printed = self.search(["200 g pisang"], "10 g pisang")
        self.assertEqual(result["Match%"], 100.0)
        self.assertIn("Kecocokan nama bahan inti", printed)
        self.assertIn("Takaran belum diperiksa", printed)

    def test_typo_choice_matches_the_clean_ingredient_query(self):
        for typo, target in (("dagng sapi", "daging sapi"), ("daun slaam", "daun salam")):
            with self.subTest(typo=typo):
                raw = ["pisang", target]
                unconfirmed, _ = self.search_frame(raw, f"pisang, {typo}")
                offered = {note["original"]: note["candidates"]
                           for note in unconfirmed.attrs["suggestions"]}
                self.assertIn(target, offered.get(typo, [])[:3])
                self.assertEqual(unconfirmed.attrs["resolved_query"], f"pisang, {typo}")
                self.assertEqual(unconfirmed.iloc[0]["Match%"], 50.0)
                corrected, _ = self.search_frame(raw, f"pisang, {typo}",
                                                 ingredient_choices={typo: target})
                clean, _ = self.search_frame(raw, f"pisang, {target}")
                self.assertTrue(corrected.equals(clean))
                self.assertEqual(corrected.iloc[0]["Match%"], 100.0)
                self.assertEqual(corrected.attrs["corrections"][0]["source"], "user_confirmed")
                self.assertEqual(clean.attrs["suggestions"], [])
                absent, _ = self.search_frame(["pisang"], f"pisang, {typo}")
                self.assertNotIn(target, [term for note in absent.attrs["suggestions"]
                                          for term in note["candidates"]])

    def test_oil_alone_asks_for_a_core_ingredient_after_correction(self):
        raw = ["ayam", "minyak goreng"]
        result, printed = self.search_frame(raw, "minyk",
                                            ingredient_choices={"minyk": "minyak goreng"})
        self.assertTrue(result.empty)
        self.assertEqual(result.attrs["resolved_query"], "minyak goreng")
        self.assertEqual(result.attrs["corrections"][0]["source"], "user_confirmed")
        self.assertIn("Tambahkan minimal satu bahan inti", printed)
        clean, clean_printed = self.search_frame(raw, "minyak goreng")
        self.assertTrue(clean.empty)
        self.assertIn("Tambahkan minimal satu bahan inti", clean_printed)

    def test_oil_choice_preserves_name_coverage_for_a_mixed_query(self):
        raw = ["ayam", "minyak goreng"]
        corrected, _ = self.search_frame(raw, "ayam, minyk",
                                         ingredient_choices={"minyk": "minyak goreng"})
        clean, _ = self.search_frame(raw, "ayam, minyak goreng")
        self.assertTrue(corrected.equals(clean))
        self.assertEqual(corrected.iloc[0]["Match%"], 100.0)
        self.assertEqual(corrected.iloc[0]["Pantry"], "minyak goreng")
