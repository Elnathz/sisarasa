"""Regression tests for archived ranking comparisons."""

import sys
import unittest
from pathlib import Path
from unittest.mock import patch

with patch.object(sys, "path", [str(Path(__file__).resolve().parents[1] / "scripts"), *sys.path]):
    import run_controlled_ranking as ranking


class ControlledReplayTest(unittest.TestCase):
    def test_rank_or_grade_drift_fails_even_with_unchanged_aggregates(self):
        metrics = {"nDCG@10": 0.7, "P@5": 0.2, "MAP@10": 0.5}
        archived = {"BM25": {"confirm": metrics}}
        summary = {"BM25": metrics.copy()}
        expected_rows = (
            b'model,query_id,retrieved_doc_ids,retrieved_grades\n'
            b'BM25,Q1,"[\'doc1\', \'doc2\']","[3, 1]"\n'
        )
        row = {"model": "BM25", "query_id": "Q1",
               "retrieved_doc_ids": ["doc1", "doc2"], "retrieved_grades": [3, 1]}

        ranking.validate_archived_replay(summary, [row], archived, expected_rows)
        for changed in (
            [],
            [row, row],
            [{**row, "retrieved_doc_ids": ["doc2", "doc1"]}],
            [{**row, "retrieved_grades": [1, 3]}],
        ):
            with self.subTest(changed=changed), self.assertRaisesRegex(ValueError, "replay"):
                ranking.validate_archived_replay(summary, changed, archived, expected_rows)
        with self.assertRaisesRegex(ValueError, "replay"):
            ranking.validate_archived_replay(
                {"BM25": {**metrics, "nDCG@10": 0.6}}, [row], archived, expected_rows,
            )
