import pickle
import time
from typing import List, Dict, Set, Tuple, Any, Optional
from pathlib import Path
import pandas as pd
import numpy as np

from backend.app.config import INDEX_PATH, CORPUS_PATH, BENCHMARK_PATH
from backend.app.parser import IndonesianIngredientParser, PARSER
import backend.app.retrievers as retrievers_mod
from backend.app.models import (
    RecipeCard,
    RecipeDetail,
    SearchResponse,
    StatsResponse,
    PopularIngredientsResponse,
)

class SisaRasaUnpickler(pickle.Unpickler):
    """
    Custom unpickler to gracefully load retriever models originally serialized
    from Jupyter Notebook's '__main__' module into the backend application.
    """
    def find_class(self, module, name):
        if module == "__main__":
            if hasattr(retrievers_mod, name):
                return getattr(retrievers_mod, name)
            if name == "IndonesianIngredientParser":
                return IndonesianIngredientParser
            if name == "_identity_token_func":
                return retrievers_mod._identity_token_func
        return super().find_class(module, name)


class SisaRasaEngine:
    """
    Core search & recipe recommendation engine.
    Loads parquet corpus and hybrid retriever once on startup.
    """
    def __init__(self):
        self.parser = PARSER
        self.retriever = None
        self.recipes_df: Optional[pd.DataFrame] = None
        self.recipes_dict: Dict[str, Dict[str, Any]] = {}
        self.is_ready = False
        self.stats = {}

    def initialize(self):
        """Loads corpus and model index into memory."""
        if self.is_ready:
            return

        print(f"[ENGINE] Loading clean corpus from: {CORPUS_PATH} ...")
        t0 = time.time()
        self.recipes_df = pd.read_parquet(CORPUS_PATH)
        self.recipes_df.set_index("doc_id", drop=False, inplace=True)

        # Precompute dict of recipe metadata for rapid O(1) lookup
        for doc_id, row in self.recipes_df.iterrows():
            core_set = row.get("ingredients_core_set")
            if isinstance(core_set, (np.ndarray, list, tuple)):
                core_set = set(core_set)
            elif not isinstance(core_set, set):
                core_set = set()

            raw_ingr = row.get("ingredients_raw_list", [])
            if isinstance(raw_ingr, np.ndarray):
                raw_ingr = raw_ingr.tolist()
            elif not isinstance(raw_ingr, list):
                raw_ingr = []

            steps = row.get("steps_raw_list", [])
            if isinstance(steps, np.ndarray):
                steps = steps.tolist()
            elif not isinstance(steps, list):
                steps = []

            title = row.get("title_raw") or row.get("title_clean") or f"Resep {doc_id}"
            category = row.get("main_category") or "Umum"
            url = row.get("url") or ""
            loves = int(row.get("loves") or 0) if pd.notnull(row.get("loves")) else 0

            self.recipes_dict[doc_id] = {
                "doc_id": doc_id,
                "title": str(title).strip(),
                "source": str(row.get("source", "SisaRasa")),
                "category": str(category).title(),
                "url": str(url),
                "loves": loves,
                "raw_ingredients": raw_ingr,
                "clean_ingredients": list(core_set),
                "core_ingredients": list(core_set),
                "core_set": core_set,
                "steps": steps,
            }


        t_corpus = time.time() - t0
        print(f"[ENGINE] Corpus loaded: {len(self.recipes_dict):,} recipes ({t_corpus:.2f}s)")

        print(f"[ENGINE] Loading SisaRasa Hybrid Retriever from: {INDEX_PATH} ...")
        t1 = time.time()
        with open(INDEX_PATH, "rb") as f:
            self.retriever = SisaRasaUnpickler(f).load()
        t_model = time.time() - t1
        print(f"[ENGINE] Retriever loaded: {len(self.retriever.doc_ids):,} indexed docs ({t_model:.2f}s)")

        self.is_ready = True

    def search(self, query: str, top_k: int = 12) -> SearchResponse:
        """
        Execute hybrid search and calculate real-time match details:
        - matched ingredients (user has)
        - missing ingredients (user needs to buy/procure)
        - match percentage
        """
        if not self.is_ready:
            raise RuntimeError("SisaRasaEngine has not been initialized.")

        t_start = time.perf_counter()
        clean_q = query.strip()
        if not clean_q:
            return SearchResponse(
                query=query,
                parsed_core_ingredients=[],
                total_results=0,
                latency_ms=0.0,
                results=[]
            )

        q_parsed = self.parser.parse_query(clean_q)
        q_core = q_parsed["ingredients_core_set"]
        parsed_core_list = sorted(list(q_core))

        # Retrieve candidates (fetch slightly more candidates to rank/filter)
        candidates = self.retriever.retrieve(clean_q, top_k=top_k)

        results: List[RecipeCard] = []
        for doc_id, score in candidates:
            recipe = self.recipes_dict.get(doc_id)
            if not recipe:
                continue

            doc_core = recipe["core_set"]
            matched = sorted(list(q_core & doc_core))
            missing = sorted(list(doc_core - q_core))

            # Match percentage based on recipe core ingredients
            denom = max(len(doc_core), 1)
            pct = min(100, int(round((len(matched) / denom) * 100)))

            # Detect primary protein
            primary_protein = None
            for p in ["ayam", "daging sapi", "ikan", "udang", "cumi", "telur", "tahu", "tempe"]:
                if p in doc_core:
                    primary_protein = p.title()
                    break

            # Preview steps (first step snippet)
            steps = recipe["steps"]
            preview_steps = steps[0][:120] + "..." if steps else None

            results.append(RecipeCard(
                doc_id=doc_id,
                title=recipe["title"],
                source=recipe["source"],
                category=recipe.get("category"),
                url=recipe.get("url"),
                loves=recipe.get("loves", 0),
                score=round(float(score), 4),
                match_percentage=pct,
                matched_ingredients=matched,
                missing_ingredients=missing,
                total_ingredients_count=len(recipe["raw_ingredients"]),
                primary_protein=primary_protein,
                preview_steps=preview_steps
            ))

        latency_ms = round((time.perf_counter() - t_start) * 1000, 2)

        return SearchResponse(
            query=query,
            parsed_core_ingredients=parsed_core_list,
            total_results=len(results),
            latency_ms=latency_ms,
            results=results
        )

    def get_recipe(self, doc_id: str, query: Optional[str] = None) -> Optional[RecipeDetail]:
        """Fetch full details for a single recipe."""
        recipe = self.recipes_dict.get(doc_id)
        if not recipe:
            return None

        matched = []
        missing = sorted(list(recipe["core_set"]))
        match_percentage = None

        if query:
            q_parsed = self.parser.parse_query(query)
            q_core = q_parsed["ingredients_core_set"]
            matched = sorted(list(q_core & recipe["core_set"]))
            missing = sorted(list(recipe["core_set"] - q_core))
            denom = max(len(recipe["core_set"]), 1)
            match_percentage = min(100, int(round((len(matched) / denom) * 100)))

        primary_protein = None
        for p in ["ayam", "daging sapi", "ikan", "udang", "cumi", "telur", "tahu", "tempe"]:
            if p in recipe["core_set"]:
                primary_protein = p.title()
                break

        return RecipeDetail(
            doc_id=recipe["doc_id"],
            title=recipe["title"],
            source=recipe["source"],
            category=recipe.get("category"),
            url=recipe.get("url"),
            loves=recipe.get("loves", 0),
            match_percentage=match_percentage,
            matched_ingredients=matched,
            missing_ingredients=missing,
            raw_ingredients=recipe["raw_ingredients"],
            clean_ingredients=recipe["clean_ingredients"],
            core_ingredients=recipe["core_ingredients"],
            steps=recipe["steps"],
            primary_protein=primary_protein,
        )


    def get_stats(self) -> StatsResponse:
        return StatsResponse(
            status="ready" if self.is_ready else "initializing",
            total_recipes=len(self.recipes_dict),
            total_indexed_docs=len(self.retriever.doc_ids) if self.retriever else 0,
            model_name="SisaRasa Hybrid Culinary Ranking (BM25 + TF-IDF + Set-Coverage + Protein Alignment)",
            best_map10=0.9112,
            best_ndcg10=0.8704
        )

    def get_popular_ingredients(self) -> PopularIngredientsResponse:
        return PopularIngredientsResponse(
            categories={
                "Protein": ["Ayam", "Telur", "Tahu", "Tempe", "Daging Sapi", "Ikan", "Udang", "Cumi"],
                "Sayuran": ["Wortel", "Kentang", "Buncis", "Kol", "Kangkung", "Bayam", "Sawi", "Tomat"],
                "Bumbu & Pelengkap": ["Cabai Rawit", "Cabai Merah", "Bawang Merah", "Bawang Putih", "Santan", "Kecap Manis", "Daun Bawang", "Seledri"]
            }
        )

# Global engine instance
engine = SisaRasaEngine()
