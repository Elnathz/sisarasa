"""Compare v4 retrieval features on the archived proxy_v3 confirmation queries.

Use the local sisarasa Python environment. This runner reads both raw sources,
reconstructs the corpus in memory, and writes a new evaluation directory.
"""

import ast
import hashlib
import json
import math
import re
import sys
import time
from collections import defaultdict
from datetime import datetime, timezone
from importlib.metadata import version
from typing import Any, Dict, List, Optional, Set, Tuple

import numpy as np
import pandas as pd

from run_parser_typo_pilot import NOTEBOOK, PROTOCOL, ROOT, git, load_parser, write_json


RUNNER = "scripts/run_controlled_ranking.py"
PARSER_LOADER = "scripts/run_parser_typo_pilot.py"
ARCHIVE = "artifacts/evaluation_runs/pseudo-eval-20261107T142228Z-7b205ef7"
ARCHIVE_FILES = (
    "metadata.json",
    "proxy/assessment_doc_ids.json",
    "confirmation/query_manifest.json",
    "confirmation/qrels.json",
    "confirmation/overall_results.json",
)
HYBRID = "SisaRasa Hybrid"
SET_OVERLAP = "Set-Overlap"
METRICS = {"nDCG@10": "nDCG@10", "P@5": "P@5", "MAP@10": "AP@10"}


def core_ir_text(ingredients):
    return " ".join(sorted(ingredient.replace(" ", "_") for ingredient in ingredients))


class CoreOnlyParser:
    def __init__(self, parser):
        self.parser = parser

    def parse_query(self, query):
        parsed = self.parser.parse_query(query)
        return {**parsed, "ingredients_ir_text": core_ir_text(parsed["ingredients_core_set"])}


class SharedCandidateRanker:
    """Apply a common positive-score candidate policy before the top-k cutoff."""

    def __init__(self, model, candidates):
        self.model = model
        self.candidates = candidates

    def retrieve(self, query, top_k):
        allowed = self.candidates[query]
        results = self.model.retrieve(query, top_k=len(self.model.doc_ids))
        eligible = [(doc_id, score) for doc_id, score in results if doc_id in allowed and score > 0]
        return sorted(eligible, key=lambda item: (-item[1], item[0]))[:top_k]


def frozen_inputs():
    paths = (NOTEBOOK, RUNNER, PARSER_LOADER, PROTOCOL, *(f"{ARCHIVE}/{name}" for name in ARCHIVE_FILES))
    for path in paths:
        git("cat-file", "-e", f"HEAD:{path}")
    git("diff", "--quiet", "HEAD", "--", *paths)
    commit = git("rev-parse", "HEAD").decode("ascii").strip()
    archive = {name: git("show", f"{commit}:{ARCHIVE}/{name}") for name in ARCHIVE_FILES}
    return commit, json.loads(git("show", f"{commit}:{NOTEBOOK}")), archive


def execute_section(notebook, cell_id, namespace, end=None):
    source = "".join(next(cell["source"] for cell in notebook["cells"] if cell["id"] == cell_id))
    if end:
        source, marker, _ = source.partition(end)
        if not marker:
            raise ValueError(f"Checkpoint notebook berubah di sel {cell_id}.")
    exec(compile(source, f"{NOTEBOOK}:{cell_id}", "exec"), namespace)


def load_local_corpus(notebook, parser):
    raw_root = ROOT / "data" / "raw"
    csv_root = raw_root / "indonesian-food-recipes"
    categories = ("ayam", "ikan", "kambing", "sapi", "tahu", "telur", "tempe", "udang")
    csv_files = [csv_root / f"dataset-{category}.csv" for category in categories]
    parquet = raw_root / "indonesian-recipes" / "indonesian_recipes.parquet"
    paths = [*csv_files, parquet]
    fingerprints = {path.relative_to(ROOT).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
                    for path in paths}

    frames = []
    for path, category in zip(csv_files, categories):
        data = pd.read_csv(path, encoding="utf-8", on_bad_lines="skip")
        data["_file_category"] = category
        data["_source_file"] = path.name
        frames.append(data)

    namespace = {
        "ast": ast, "math": math, "re": re, "time": time, "np": np, "pd": pd,
        "List": List, "Set": Set, "Dict": Dict, "Any": Any, "Tuple": Tuple, "Optional": Optional,
        "PARSER": parser, "IndonesianIngredientParser": type(parser),
        "tqdm": lambda values, **kwargs: values,
        "print": lambda *args, **kwargs: None,
        "df_ds1_raw": pd.concat(frames, ignore_index=True),
        "df_ds2_raw": pd.read_parquet(parquet),
    }
    execute_section(notebook, "6c6facc1", namespace)
    execute_section(notebook, "4bc00aad", namespace, end="# ── Quick EDA")
    execute_section(notebook, "a84531e1", namespace, end="def export_corpus_and_indices")
    execute_section(notebook, "e22a85dc", namespace, end="def _check_v4_retrievers")
    execute_section(notebook, "765f2806", namespace, end="def _check_eligible_aggregation")
    return namespace, fingerprints


def build_models(namespace, corpus, parser, model_metadata, core_only=False):
    def parameters(model_name):
        return model_metadata[model_name]["parameters"].copy()

    tfidf_parameters = {"w_ingr": 1.0, "w_title": 0.0} if core_only else parameters("TF-IDF Cosine")
    tfidf = namespace["TfidfCosineRetriever"](parser, **tfidf_parameters)
    bm25 = namespace["BM25Retriever"](parser, **parameters("BM25"))
    hybrid_parameters = parameters(HYBRID)
    epsilon = hybrid_parameters.pop("epsilon")
    hybrid = namespace["SisaRasaHybridRetriever"](parser, bm25, tfidf, **hybrid_parameters)
    hybrid.epsilon = epsilon
    if sorted(hybrid.MAIN_PROTEINS) != model_metadata[HYBRID]["protein_ingredients"]:
        raise ValueError("Daftar protein Hybrid berbeda dari baseline.")
    models = {
        SET_OVERLAP: namespace["SetOverlapRetriever"](parser),
        "TF-IDF Cosine": tfidf,
        "BM25": bm25,
        HYBRID: hybrid,
    }
    for model in models.values():
        model.index(corpus)
    return models


def common_candidates(corpus, queries, parser):
    postings = defaultdict(set)
    for doc_id, ingredients in zip(corpus["doc_id"], corpus["ingredients_core_set"]):
        for ingredient in ingredients:
            postings[ingredient].add(doc_id)
    return {
        text: set().union(*(postings[ingredient] for ingredient in parser.parse_query(text)["ingredients_core_set"]))
        for text in (query["query_text"] for query in queries)
    }


def evaluate_arm(name, models, evaluator, queries, qrels, doc_ids, candidates=None):
    print(f"[EVAL] {name}", flush=True)
    summary, rows = {}, []
    keys = ("query_id", "scenario", "retrieved_doc_ids", "retrieved_grades", *METRICS.values())
    for model_name, model in models.items():
        ranker = model if candidates is None else SharedCandidateRanker(model, candidates)
        overall, _, details = evaluator.evaluate_model(ranker, queries, qrels, doc_ids, "proxy")
        aggregate = overall["confirm"]
        summary[model_name] = {key: aggregate[key] for key in ("query_count", *METRICS)}
        rows.extend({"arm": name, "model": model_name, **{key: row[key] for key in keys}}
                    for row in details)
    return summary, rows


def paired_statistics(differences):
    differences = np.asarray(differences, dtype=float)
    draws = np.random.default_rng(42).choice(differences, size=(10_000, len(differences)))
    low, high = np.quantile(draws.mean(axis=1), [0.025, 0.975])
    return {
        "queries": len(differences),
        "mean": float(differences.mean()),
        "ci_95": [float(low), float(high)],
        "positive": int((differences > 1e-10).sum()),
        "tied": int((np.abs(differences) <= 1e-10).sum()),
        "negative": int((differences < -1e-10).sum()),
    }


def compare_arms(arms):
    gaps = {}
    for arm, rows in arms.items():
        scores = {(row["model"], row["query_id"]): row["nDCG@10"] for row in rows}
        gaps[arm] = {
            query_id: value - scores[SET_OVERLAP, query_id]
            for (model, query_id), value in scores.items() if model == HYBRID
        }
    reference = gaps["v4_shared_candidates"]
    core = gaps["core_shared_candidates"]
    if reference.keys() != core.keys():
        raise ValueError("Arm tidak memakai query yang sama.")
    return {
        "hybrid_minus_set_overlap": {arm: paired_statistics(list(values.values())) for arm, values in gaps.items()},
        "change_in_hybrid_gap_core_minus_v4": paired_statistics([core[key] - reference[key] for key in reference]),
    }


def run(notebook, archive):
    saved = {name: json.loads(blob) for name, blob in archive.items()}
    baseline = saved["metadata.json"]
    queries = saved["confirmation/query_manifest.json"]
    qrels = saved["confirmation/qrels.json"]
    doc_ids = saved["proxy/assessment_doc_ids.json"]
    canonical_queries = json.dumps(queries, sort_keys=True, ensure_ascii=False).encode("utf-8")
    if hashlib.sha256(canonical_queries).hexdigest() != baseline["confirmation_query_manifest_hash_sha256"]:
        raise ValueError("Manifest konfirmasi berbeda dari baseline.")
    if len(queries) != 48 or len({query["family_id"] for query in queries}) != 48:
        raise ValueError("Diharapkan tepat 48 keluarga query konfirmasi.")

    parser, parser_hash = load_parser(notebook)
    print("[KORPUS] Membaca dua sumber lokal dan merekonstruksi korpus v4.", flush=True)
    namespace, fingerprints = load_local_corpus(notebook, parser)
    corpus = namespace["df_all"]
    corpus_hash = namespace["corpus_fingerprint"](corpus)
    if corpus_hash != baseline["corpus_hash_sha256_full_records"] or corpus["doc_id"].tolist() != doc_ids:
        raise ValueError(f"Korpus tidak identik dengan arsip. SHA hasil rekonstruksi {corpus_hash}.")
    print(f"[KORPUS] {len(corpus)} resep dan hash identik dengan arsip.", flush=True)

    evaluator = namespace["IRMetricsEvaluator"]()
    models = build_models(namespace, corpus, parser, baseline["models"])
    candidates = common_candidates(corpus, queries, parser)
    replay, replay_rows = evaluate_arm("archived_replay", models, evaluator, queries, qrels, doc_ids)
    v4, v4_rows = evaluate_arm("v4_shared_candidates", models, evaluator, queries, qrels, doc_ids, candidates)

    core_corpus = corpus.assign(ingredients_ir_text=corpus["ingredients_core_set"].map(core_ir_text))
    core_models = build_models(namespace, core_corpus, CoreOnlyParser(parser), baseline["models"], core_only=True)
    core, core_rows = evaluate_arm("core_shared_candidates", core_models, evaluator, queries, qrels, doc_ids, candidates)
    summaries = {"archived_replay": replay, "v4_shared_candidates": v4, "core_shared_candidates": core}
    rows = {"archived_replay": replay_rows, "v4_shared_candidates": v4_rows, "core_shared_candidates": core_rows}
    old = saved["confirmation/overall_results.json"]
    replay_matches = all(replay[model][key] == old[model]["confirm"][key] for model in replay for key in METRICS)
    return {
        "corpus_hash_sha256_full_records": corpus_hash,
        "document_count": len(corpus),
        "parser_source_sha256": parser_hash,
        "normalization_version": parser.NORMALIZATION_VERSION,
        "query_processing_version": parser.QUERY_PROCESSING_VERSION,
        "raw_input_sha256": fingerprints,
        "replay_matches_archived_metrics": replay_matches,
        "candidate_counts": {query["query_id"]: len(candidates[query["query_text"]]) for query in queries},
    }, summaries, compare_arms(rows), [row for group in rows.values() for row in group]


def main():
    commit, notebook, archive = frozen_inputs()
    now = datetime.now(timezone.utc)
    run_id = f"controlled-ranking-{now:%Y%m%dT%H%M%S%fZ}-{commit[:8]}"
    destination = ROOT / "artifacts" / "evaluation_runs" / run_id
    destination.mkdir(exist_ok=False)
    print(destination, flush=True)
    try:
        provenance, summaries, comparisons, rows = run(notebook, archive)
        metadata = {
            "run_id": run_id,
            "input_commit": commit,
            "created_utc": now.isoformat(),
            "status": "retrospective_proxy_v3",
            "source_run": ARCHIVE,
            "protocol": PROTOCOL,
            "query_count": 48,
            "archive_input_sha256": {name: hashlib.sha256(blob).hexdigest() for name, blob in archive.items()},
            "candidate_rule": "At least one matching core ingredient in both shared-candidate arms.",
            "output_rule": "Positive scores; ties by ascending doc_id in both shared-candidate arms.",
            "core_features": "Same compound core tokens for documents and queries; TF-IDF title weight zero.",
            "bootstrap": {"unit": "query family", "resamples": 10_000, "seed": 42},
            "python": sys.version.split()[0],
            "packages": {package: version(package) for package in ("numpy", "pandas", "scipy", "scikit-learn", "pyarrow")},
            **provenance,
        }
        write_json(destination / "metadata.json", metadata)
        write_json(destination / "overall_results.json", summaries)
        write_json(destination / "paired_comparisons.json", comparisons)
        write_json(destination / "per_query_results.json", rows)
        (destination / "_SUCCESS").touch(exist_ok=False)
    except Exception as error:
        write_json(destination / "failure.json", {"input_commit": commit, "error_type": type(error).__name__})
        raise
    print(json.dumps({"status": metadata["status"], "models": summaries, "comparisons": comparisons}, indent=2))


if __name__ == "__main__":
    main()
