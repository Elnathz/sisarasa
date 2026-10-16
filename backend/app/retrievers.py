"""
SisaRasa Information Retrieval Models
Contains:
- BaseRetriever
- SetOverlapRetriever
- TfidfCosineRetriever
- BM25Retriever
- SisaRasaHybridRetriever
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Set, Tuple, Any, Optional

import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from backend.app.parser import IndonesianIngredientParser, PARSER


def _identity_token_func(x):
    """Fungsi identitas tingkat modul agar CountVectorizer dapat diserialisasi via pickle."""
    return x


class BaseRetriever(ABC):

    name: str = "Base"

    @abstractmethod
    def index(self, corpus_df: pd.DataFrame):
        pass

    @abstractmethod
    def retrieve(self, query_str: str, top_k: int = 10) -> List[Tuple[str, float]]:
        """Return list of (doc_id, score) sorted by score desc."""
        pass


# -- Model 1: Set-Overlap / Jaccard Baseline -----------------------------------

class SetOverlapRetriever(BaseRetriever):
    name = "Set-Overlap"

    def __init__(self, parser: IndonesianIngredientParser):
        self.parser = parser
        self.doc_ids: List[str] = []
        self.vectorizer: Optional[CountVectorizer] = None
        self.doc_ingr_matrix = None
        self.doc_lengths = None

    def index(self, corpus_df: pd.DataFrame):
        self.doc_ids = corpus_df["doc_id"].tolist()
        core_lists = [list(s) for s in corpus_df["ingredients_core_set"]]
        self.vectorizer = CountVectorizer(
            binary=True,
            tokenizer=_identity_token_func,
            preprocessor=_identity_token_func,
            lowercase=False,
            token_pattern=None
        )
        self.doc_ingr_matrix = self.vectorizer.fit_transform(core_lists)
        self.doc_lengths = np.array(self.doc_ingr_matrix.sum(axis=1)).flatten()

    def retrieve(self, query_str: str, top_k: int = 10) -> List[Tuple[str, float]]:
        q_parsed = self.parser.parse_query(query_str)
        q_core = q_parsed["ingredients_core_set"]
        if not q_core:
            return []

        q_vec = self.vectorizer.transform([list(q_core)])
        intersections = np.array(self.doc_ingr_matrix.dot(q_vec.T).toarray()).flatten()
        q_len = len(q_core)
        unions = self.doc_lengths + q_len - intersections

        with np.errstate(divide='ignore', invalid='ignore'):
            jaccard = np.where(unions > 0, intersections / unions, 0.0)

        top_indices = np.argsort(jaccard)[::-1][:top_k]
        return [(self.doc_ids[i], float(jaccard[i])) for i in top_indices if jaccard[i] > 0]


# -- Model 2: TF-IDF + Cosine Similarity Baseline -----------------------------

class TfidfCosineRetriever(BaseRetriever):
    name = "TF-IDF Cosine"

    def __init__(self, parser: IndonesianIngredientParser, w_ingr: float = 0.70, w_title: float = 0.30):
        self.parser = parser
        self.w_ingr = w_ingr
        self.w_title = w_title
        self.doc_ids: List[str] = []
        self.vectorizer_ingr = TfidfVectorizer(token_pattern=r"(?u)\b\w+\b", lowercase=False)
        self.vectorizer_title = TfidfVectorizer(token_pattern=r"(?u)\b\w+\b", lowercase=False)
        self.tfidf_ingr = None
        self.tfidf_title = None

    def index(self, corpus_df: pd.DataFrame):
        self.doc_ids = corpus_df["doc_id"].tolist()
        ingr_texts = corpus_df["ingredients_ir_text"].fillna("").tolist()
        title_texts = corpus_df["title_ir_text"].fillna("").tolist()
        self.tfidf_ingr = self.vectorizer_ingr.fit_transform(ingr_texts)
        self.tfidf_title = self.vectorizer_title.fit_transform(title_texts)

    def retrieve(self, query_str: str, top_k: int = 10) -> List[Tuple[str, float]]:
        q_parsed = self.parser.parse_query(query_str)
        q_ir_text = q_parsed["ingredients_ir_text"]
        if not q_ir_text.strip():
            return []

        q_vec_ingr = self.vectorizer_ingr.transform([q_ir_text])
        sim_ingr = cosine_similarity(q_vec_ingr, self.tfidf_ingr).flatten()

        q_vec_title = self.vectorizer_title.transform([q_ir_text])
        sim_title = cosine_similarity(q_vec_title, self.tfidf_title).flatten()

        scores = self.w_ingr * sim_ingr + self.w_title * sim_title
        top_indices = np.argsort(scores)[::-1][:top_k]
        return [(self.doc_ids[i], float(scores[i])) for i in top_indices if scores[i] > 0]

    def get_scores_array(self, query_str: str) -> np.ndarray:
        """Return full score array untuk model hybrid."""
        q_parsed = self.parser.parse_query(query_str)
        q_ir_text = q_parsed["ingredients_ir_text"]
        if not q_ir_text.strip():
            return np.zeros(len(self.doc_ids))
        q_vec_ingr = self.vectorizer_ingr.transform([q_ir_text])
        sim_ingr = cosine_similarity(q_vec_ingr, self.tfidf_ingr).flatten()
        q_vec_title = self.vectorizer_title.transform([q_ir_text])
        sim_title = cosine_similarity(q_vec_title, self.tfidf_title).flatten()
        return self.w_ingr * sim_ingr + self.w_title * sim_title


# -- Model 3: Okapi BM25 (Vectorized Sparse Matrix) ---------------------------

class BM25Retriever(BaseRetriever):
    name = "BM25"

    def __init__(self, parser: IndonesianIngredientParser, k1: float = 1.2, b: float = 0.4):
        self.parser = parser
        self.k1 = k1
        self.b = b
        self.doc_ids: List[str] = []
        self.vectorizer: Optional[CountVectorizer] = None
        self.bm25_matrix: Optional[csr_matrix] = None

    def index(self, corpus_df: pd.DataFrame):
        self.doc_ids = corpus_df["doc_id"].tolist()
        texts = corpus_df["ingredients_ir_text"].fillna("").tolist()

        self.vectorizer = CountVectorizer(
            token_pattern=r"(?u)\b\w+\b",
            lowercase=False
        )
        tf_matrix = self.vectorizer.fit_transform(texts)
        N, V = tf_matrix.shape

        doc_len = np.array(tf_matrix.sum(axis=1)).flatten()
        avgdl = float(doc_len.mean()) if N > 0 else 1.0

        # Document frequency df
        df = np.bincount(tf_matrix.indices, minlength=V)

        # Okapi BM25 IDF dengan smoothing +1.0
        idf = np.log((N - df + 0.5) / (df + 0.5) + 1.0)

        # Precompute bobot BM25 sparse matrix
        row_indices = np.repeat(np.arange(N), np.diff(tf_matrix.indptr))
        tf_vals = tf_matrix.data
        len_norm = 1.0 - self.b + self.b * (doc_len / (avgdl + 1e-9))
        denom = tf_vals + self.k1 * len_norm[row_indices]
        bm25_data = (tf_vals * (self.k1 + 1.0) / denom) * idf[tf_matrix.indices]

        self.bm25_matrix = csr_matrix((bm25_data, tf_matrix.indices, tf_matrix.indptr), shape=tf_matrix.shape)

    def retrieve(self, query_str: str, top_k: int = 10) -> List[Tuple[str, float]]:
        scores = self.get_scores_array(query_str)
        if scores.size == 0 or np.all(scores == 0):
            return []
        top_indices = np.argsort(scores)[::-1][:top_k]
        return [(self.doc_ids[i], float(scores[i])) for i in top_indices if scores[i] > 0]

    def get_scores_array(self, query_str: str) -> np.ndarray:
        """Return full score array untuk model hybrid via perkalian matriks sparse."""
        q_parsed = self.parser.parse_query(query_str)
        q_ir_text = q_parsed["ingredients_ir_text"]
        if not q_ir_text.strip() or self.bm25_matrix is None:
            return np.zeros(len(self.doc_ids))

        q_vec = self.vectorizer.transform([q_ir_text])
        if q_vec.nnz == 0:
            return np.zeros(len(self.doc_ids))

        scores = np.array(self.bm25_matrix.dot(q_vec.T).toarray()).ravel()
        return scores


# -- Model 4: SisaRasa Hybrid Culinary Ranking (Proposed Method) ---------------

class SisaRasaHybridRetriever(BaseRetriever):
    name = "SisaRasa Hybrid"

    MAIN_PROTEINS = frozenset({
        "ayam", "daging sapi", "daging kambing", "ikan", "udang",
        "cumi", "telur", "tahu", "tempe",
    })

    def __init__(self, parser: IndonesianIngredientParser,
                 bm25_retriever: BM25Retriever,
                 tfidf_retriever: TfidfCosineRetriever,
                 w1: float = 0.10, w2: float = 0.05, w3: float = 0.20,
                 w4: float = 0.20, w_jaccard: float = 0.35,
                 w5: float = 0.10, w_prot: float = 0.25):
        self.parser = parser
        self.bm25_retriever = bm25_retriever
        self.tfidf_retriever = tfidf_retriever
        self.w1 = w1
        self.w2 = w2
        self.w3 = w3
        self.w4 = w4
        self.w_jaccard = w_jaccard
        self.w5 = w5
        self.w_prot = w_prot
        self.doc_ids: List[str] = []
        self.vectorizer: Optional[CountVectorizer] = None
        self.doc_ingr_matrix = None
        self.doc_core_len = None
        self.protein_vectorizer: Optional[CountVectorizer] = None
        self.doc_protein_matrix = None
        self.doc_has_protein = None
        self.epsilon = 1e-9

    def index(self, corpus_df: pd.DataFrame):
        self.doc_ids = corpus_df["doc_id"].tolist()
        core_lists = [list(s) for s in corpus_df["ingredients_core_set"]]

        # 1. Matriks biner sparse seluruh bahan inti
        self.vectorizer = CountVectorizer(
            binary=True,
            tokenizer=_identity_token_func,
            preprocessor=_identity_token_func,
            lowercase=False,
            token_pattern=None
        )
        self.doc_ingr_matrix = self.vectorizer.fit_transform(core_lists)
        self.doc_core_len = np.array(self.doc_ingr_matrix.sum(axis=1)).flatten()

        # 2. Matriks biner sparse khusus Protein Utama
        doc_proteins = [[p for p in s if p in self.MAIN_PROTEINS] for s in corpus_df["ingredients_core_set"]]
        self.protein_vectorizer = CountVectorizer(
            binary=True,
            tokenizer=_identity_token_func,
            preprocessor=_identity_token_func,
            lowercase=False,
            token_pattern=None
        )
        self.doc_protein_matrix = self.protein_vectorizer.fit_transform(doc_proteins)
        self.doc_has_protein = (np.array(self.doc_protein_matrix.sum(axis=1)).flatten() > 0)

    def _min_max_normalize(self, arr: np.ndarray) -> np.ndarray:
        mn, mx = arr.min(), arr.max()
        if mx - mn < 1e-12:
            return np.zeros_like(arr)
        return (arr - mn) / (mx - mn)

    def retrieve(self, query_str: str, top_k: int = 10) -> List[Tuple[str, float]]:
        q_parsed = self.parser.parse_query(query_str)
        q_core = q_parsed["ingredients_core_set"]
        if not q_core:
            return []

        n = len(self.doc_ids)

        # 1. Skor probabilistik leksikal BM25 (ternormalisasi)
        bm25_raw = self.bm25_retriever.get_scores_array(query_str)
        bm25_norm = self._min_max_normalize(bm25_raw)

        # 2. Skor kecocokan vektor TF-IDF (ternormalisasi)
        tfidf_raw = self.tfidf_retriever.get_scores_array(query_str)
        tfidf_norm = self._min_max_normalize(tfidf_raw)

        # 3. Vektorisasi Set Operations via Perkalian Matriks Sparse
        q_vec = self.vectorizer.transform([list(q_core)])
        intersection = np.array(self.doc_ingr_matrix.dot(q_vec.T).toarray()).flatten()

        q_core_len = len(q_core)
        # Smoothing pada penyebut core_coverage untuk meredam resep terlalu pendek (doc_core_len < 2)
        denom_len = np.maximum(self.doc_core_len, 2.0 if q_core_len >= 2 else 1.0)
        core_coverage = intersection / (denom_len + self.epsilon)
        query_util = intersection / (q_core_len + self.epsilon)

        unions = self.doc_core_len + q_core_len - intersection
        with np.errstate(divide='ignore', invalid='ignore'):
            jaccard = np.where(unions > 0, intersection / unions, 0.0)

        missing = np.maximum(0, self.doc_core_len - intersection - 2)
        missing_penalty = missing / (self.doc_core_len + 3)

        # 4. Main Protein Alignment
        q_proteins = q_core & self.MAIN_PROTEINS
        protein_alignment = np.zeros(n)
        if q_proteins:
            q_prot_vec = self.protein_vectorizer.transform([list(q_proteins)])
            protein_inter = np.array(self.doc_protein_matrix.dot(q_prot_vec.T).toarray()).flatten()
            protein_alignment[protein_inter > 0] = 1.0
            protein_alignment[(protein_inter == 0) & self.doc_has_protein] = -0.5

        # 5. Masking Penalti jika bahan cocok < 2 saat query memiliki >= 2 bahan inti
        min_match_mask = (intersection >= 2) if q_core_len >= 2 else (intersection >= 1)

        # 6. Formula Skor Hybrid Terkalibrasi
        scores = (self.w1 * bm25_norm
                  + self.w2 * tfidf_norm
                  + self.w3 * core_coverage
                  + self.w4 * query_util
                  + self.w_jaccard * jaccard
                  - self.w5 * missing_penalty
                  + self.w_prot * protein_alignment)
        scores = np.where(min_match_mask, scores, scores * 0.25)

        top_indices = np.argsort(scores)[::-1][:top_k]
        return [(self.doc_ids[i], float(scores[i])) for i in top_indices if scores[i] > 0]


