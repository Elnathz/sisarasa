from pathlib import Path
import os
from dotenv import load_dotenv

# Root of repository is two levels up from backend/app
BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")

ARTIFACTS_DIR = BASE_DIR / "artifacts"
INDEX_PATH = ARTIFACTS_DIR / "index_sisarasa_hybrid.pkl"
CORPUS_PATH = ARTIFACTS_DIR / "sisarasa_corpus_clean.parquet"
BENCHMARK_PATH = ARTIFACTS_DIR / "benchmark_results.csv"

# API Settings
API_TITLE = "SisaRasa Recipe Retrieval API"
API_DESCRIPTION = "API Sistem Temu Kembali Informasi Resep Masakan Indonesia Berbasis Bahan Sisa"
API_VERSION = "1.0.0"

CORS_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
    "*"
]
