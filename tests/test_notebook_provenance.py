"""Regression tests for notebook Git provenance."""

import ast
import json
import subprocess
import tempfile
import unittest
from pathlib import Path


NOTEBOOK = Path("notebooks/sisarasa_v4.ipynb")
ROOT = Path(__file__).resolve().parents[1]


class NotebookProvenanceTest(unittest.TestCase):
    def test_checkpoint_accepts_output_changes_and_rejects_source_changes(self):
        notebook = json.loads((ROOT / NOTEBOOK).read_bytes())
        cell = next(cell for cell in notebook["cells"] if cell["id"] == "037662b9")
        tree = ast.parse("".join(cell["source"]))
        definitions = [
            node for node in tree.body
            if isinstance(node, ast.FunctionDef) and node.name == "notebook_input_commit"
        ]
        self.assertEqual(len(definitions), 1, "missing notebook input checkpoint")
        namespace = {"Path": Path, "json": json, "subprocess": subprocess}
        exec(compile(ast.Module(definitions, []), str(NOTEBOOK), "exec"), namespace)
        checkpoint = namespace["notebook_input_commit"]

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / NOTEBOOK
            path.parent.mkdir()
            subprocess.run(["git", "init", "--quiet", str(root)], check=True)
            sample = {"cells": [{"cell_type": "code", "id": "fixture", "source": ["x = 1\n"]}]}
            path.write_text(json.dumps(sample), encoding="utf-8")
            subprocess.run(["git", "add", "--", str(NOTEBOOK)], cwd=root, check=True)
            subprocess.run(
                ["git", "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                 "-c", "commit.gpgsign=false", "commit", "--quiet", "-m", "Fixture"],
                cwd=root, check=True,
            )
            commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
            self.assertEqual(checkpoint(root), commit)
            sample["cells"][0].update({"outputs": [], "execution_count": 3})
            path.write_text(json.dumps(sample), encoding="utf-8")
            self.assertEqual(checkpoint(root), commit)
            sample["cells"][0]["source"] = ["x = 2\n"]
            path.write_text(json.dumps(sample), encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "commit"):
                checkpoint(root)
            subprocess.run(["git", "add", "--", str(NOTEBOOK)], cwd=root, check=True)
            with self.assertRaisesRegex(RuntimeError, "commit"):
                checkpoint(root)
