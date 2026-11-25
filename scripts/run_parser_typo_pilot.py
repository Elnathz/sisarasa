"""Run the frozen SisaRasa parser fixture without executing notebook cells.

Run from the repository with python -B scripts/run_parser_typo_pilot.py.
The runner reads committed inputs and writes one new evaluation directory.
"""

import ast
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK = "notebooks/sisarasa_v4.ipynb"
PARSER_CELL = "f095687e"
FIXTURE = "documents/sisarasa_v4_pilot_parser_typo.json"
PROTOCOL = "documents/sisarasa_v4_protokol_evaluasi.md"
RUNNER = "scripts/run_parser_typo_pilot.py"


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT)


def input_commit():
    paths = (NOTEBOOK, FIXTURE, PROTOCOL, RUNNER)
    for path in paths:
        git("cat-file", "-e", f"HEAD:{path}")
    git("diff", "--quiet", "HEAD", "--", *paths)
    return git("rev-parse", "HEAD").decode("ascii").strip()


def load_parser(notebook):
    cell = next(cell for cell in notebook["cells"] if cell["id"] == PARSER_CELL)
    source = "".join(cell["source"])
    tree = ast.parse(source)
    definitions = [
        node
        for node in tree.body
        if isinstance(node, (ast.Import, ast.ImportFrom))
        or isinstance(node, ast.ClassDef) and node.name == "IndonesianIngredientParser"
    ]
    namespace = {}
    exec(compile(ast.Module(definitions, []), f"{NOTEBOOK}:{PARSER_CELL}", "exec"), namespace)
    return namespace["IndonesianIngredientParser"](), hashlib.sha256(source.encode("utf-8")).hexdigest()


def score_entities(rows, prediction_key):
    exact = true_positive = false_positive = false_negative = 0
    for row in rows:
        expected = set(row["expected"])
        predicted = set(row[prediction_key])
        exact += predicted == expected
        true_positive += len(expected & predicted)
        false_positive += len(predicted - expected)
        false_negative += len(expected - predicted)
    predicted_count = true_positive + false_positive
    expected_count = true_positive + false_negative
    return {
        "cases": len(rows),
        "exact": exact,
        "true_positive": true_positive,
        "false_positive": false_positive,
        "false_negative": false_negative,
        "precision": true_positive / predicted_count if predicted_count else None,
        "recall": true_positive / expected_count if expected_count else None,
        "f1": 2 * true_positive / (predicted_count + expected_count)
        if predicted_count + expected_count else None,
    }


def score_typos(rows):
    typos = [row for row in rows if row["kind"] == "typo"]
    eligible = [row for row in typos if row["target_available"]]
    valid = [row for row in rows if row["kind"] == "valid"]
    unknown = [row for row in rows if row["kind"] == "unknown"]
    hits = sum(row["target_rank"] in (1, 2, 3) for row in eligible)
    return {
        "typo_cases": len(typos),
        "eligible_typos": len(eligible),
        "target_unavailable": len(typos) - len(eligible),
        "hits_at_3": hits,
        "candidate_recall_at_3": hits / len(eligible) if eligible else None,
        "before_exact": sum(row["before_exact"] for row in eligible),
        "oracle_exact": sum(row["oracle_exact"] for row in eligible),
        "valid_controls": len(valid),
        "false_suggestions_on_valid": sum(bool(row["offered"]) for row in valid),
        "unknown_controls": len(unknown),
        "unknown_with_suggestions": sum(bool(row["offered"]) for row in unknown),
    }


def evaluate_fixture(parser, fixture):
    known = set(fixture["known_ingredients"])
    parser.set_known_ingredients(known)
    normalization = []
    for case in fixture["normalization"]:
        literal = " ".join(case["input"].lower().split())
        ingredients = parser.extract_ingredients_from_recipe([case["input"]])
        normalization.append({
            **case,
            "literal": [literal] if literal in known else [],
            "parsed": sorted(ingredients["ingredients_all_set"]),
        })
    typos = []
    for case in fixture["typo"]:
        query, target = case["input"], case["target"]
        before = parser.parse_query(query)
        offered = next(
            (item["candidates"] for item in before["suggestions"] if item["original"] == query),
            [],
        )
        rank = offered.index(target) + 1 if target in offered else None
        choices = {query: target} if rank in (1, 2, 3) else {}
        after = parser.parse_query(query, ingredient_choices=choices)
        typos.append({
            **case,
            "target_available": target in known,
            "offered": offered,
            "target_rank": rank,
            "resolved_before": before["resolved_query"],
            "resolved_after_oracle": after["resolved_query"],
            "parsed_before": sorted(before["ingredients_all_set"]),
            "parsed_after_oracle": sorted(after["ingredients_all_set"]),
            "before_exact": target is not None and before["ingredients_all_set"] == {target},
            "oracle_exact": target is not None and after["ingredients_all_set"] == {target},
        })
    return {"normalization": normalization, "typo": typos}


def write_json(path, value):
    with path.open("x", encoding="utf-8", newline="\n") as output:
        json.dump(value, output, ensure_ascii=False, indent=2)
        output.write("\n")


def main():
    commit = input_commit()
    notebook = json.loads(git("show", f"{commit}:{NOTEBOOK}"))
    fixture_bytes = git("show", f"{commit}:{FIXTURE}")
    fixture = json.loads(fixture_bytes)
    parser, parser_hash = load_parser(notebook)
    cases = evaluate_fixture(parser, fixture)
    summary = {
        "status": fixture["status"],
        "scope": fixture["scope"],
        "normalization": {
            "literal": score_entities(cases["normalization"], "literal"),
            "v4_parser": score_entities(cases["normalization"], "parsed"),
        },
        "typo": score_typos(cases["typo"]),
    }
    now = datetime.now(timezone.utc)
    run_id = f"parser-typo-pilot-{now:%Y%m%dT%H%M%S%fZ}-{commit[:8]}"
    metadata = {
        "run_id": run_id,
        "created_utc": now.isoformat(),
        "input_commit": commit,
        "notebook": NOTEBOOK,
        "parser_cell": PARSER_CELL,
        "parser_source_sha256": parser_hash,
        "normalization_version": parser.NORMALIZATION_VERSION,
        "query_processing_version": parser.QUERY_PROCESSING_VERSION,
        "protocol": PROTOCOL,
        "fixture": FIXTURE,
        "fixture_sha256": hashlib.sha256(fixture_bytes).hexdigest(),
        "fixture_version": fixture["version"],
        "status": fixture["status"],
        "scope": fixture["scope"],
        "python": sys.version.split()[0],
    }
    destination = ROOT / "artifacts" / "evaluation_runs" / run_id
    destination.mkdir(exist_ok=False)
    write_json(destination / "metadata.json", metadata)
    write_json(destination / "cases.json", cases)
    write_json(destination / "summary.json", summary)
    (destination / "_SUCCESS").touch(exist_ok=False)
    print(destination)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
