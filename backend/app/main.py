import time
from contextlib import asynccontextmanager
from typing import Optional, List
from fastapi import FastAPI, Query, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.app.config import API_TITLE, API_DESCRIPTION, API_VERSION, CORS_ORIGINS
from backend.app.engine import engine
from backend.app.models import (
    SearchRequest,
    SearchResponse,
    RecipeDetail,
    StatsResponse,
    PopularIngredientsResponse
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Load parquet corpus and serialized hybrid model once
    print("[FASTAPI] Starting up SisaRasa API ...")
    engine.initialize()
    yield
    # Shutdown
    print("[FASTAPI] Shutting down SisaRasa API ...")

app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=API_VERSION,
    lifespan=lifespan
)

# Enable CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", tags=["Health"])
async def root():
    return {
        "app": API_TITLE,
        "version": API_VERSION,
        "status": "online",
        "docs": "/docs"
    }

@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy" if engine.is_ready else "initializing",
        "corpus_loaded": engine.is_ready,
        "total_recipes": len(engine.recipes_dict) if engine.is_ready else 0
    }

@app.get("/api/stats", response_model=StatsResponse, tags=["Metadata"])
async def get_system_stats():
    """Mengembalikan statistik korpus resep dan metrik evaluasi model."""
    if not engine.is_ready:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Mesin pencari sedang menginisialisasi indeks resep."
        )
    return engine.get_stats()

@app.get("/api/popular-ingredients", response_model=PopularIngredientsResponse, tags=["Metadata"])
async def get_popular_ingredients():
    """Mengembalikan daftar bahan sisa populer untuk chip cepat di frontend UI."""
    return engine.get_popular_ingredients()

@app.get("/api/search", response_model=SearchResponse, tags=["Retrieval"])
async def search_recipes_get(
    q: str = Query(..., description="Daftar bahan yang dimiliki (misal: 'ayam, tahu, wortel')"),
    top_k: int = Query(12, ge=1, le=50, description="Jumlah rekomendasi resep yang diinginkan")
):
    """
    Pencarian resep berbasis bahan sisa via GET request.
    Mengembalikan ranking resep, persentase kecocokan, bahan cocok, dan bahan yang kurang.
    """
    if not engine.is_ready:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Mesin pencari sedang menginisialisasi indeks resep."
        )
    return engine.search(query=q, top_k=top_k)

@app.post("/api/search", response_model=SearchResponse, tags=["Retrieval"])
async def search_recipes_post(request: SearchRequest):
    """Pencarian resep berbasis bahan sisa via POST request dengan JSON body."""
    if not engine.is_ready:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Mesin pencari sedang menginisialisasi indeks resep."
        )
    return engine.search(query=request.query, top_k=request.top_k)

@app.get("/api/recipe/{doc_id}", response_model=RecipeDetail, tags=["Recipe Detail"])
async def get_recipe_detail(
    doc_id: str,
    q: Optional[str] = Query(None, description="Query bahan sisa aktif untuk menghitung bahan cocok vs belanja")
):
    """
    Mengambil data lengkap satu resep (bahan mentah, langkah pembuatan, sumber asal).
    Jika parameter 'q' diberikan, akan otomatis menghitung bahan cocok dan bahan yang perlu dibeli.
    """
    if not engine.is_ready:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Mesin pencari sedang menginisialisasi indeks resep."
        )
    recipe = engine.get_recipe(doc_id=doc_id, query=q)
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resep dengan ID '{doc_id}' tidak ditemukan."
        )
    return recipe
