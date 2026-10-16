from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class RecipeCard(BaseModel):
    doc_id: str
    title: str
    source: str
    category: Optional[str] = None
    url: Optional[str] = None
    loves: Optional[int] = 0
    score: float
    match_percentage: int
    matched_ingredients: List[str]
    missing_ingredients: List[str]
    total_ingredients_count: int
    primary_protein: Optional[str] = None
    preview_steps: Optional[str] = None

class RecipeDetail(BaseModel):
    doc_id: str
    title: str
    source: str
    category: Optional[str] = None
    url: Optional[str] = None
    loves: Optional[int] = 0
    score: Optional[float] = None
    match_percentage: Optional[int] = None
    matched_ingredients: List[str] = []
    missing_ingredients: List[str] = []
    raw_ingredients: List[str]
    clean_ingredients: List[str] = []
    core_ingredients: List[str] = []
    steps: List[str]
    primary_protein: Optional[str] = None


class SearchRequest(BaseModel):
    query: str = Field(..., json_schema_extra={"example": "ayam, wortel, kecap manis"})
    top_k: int = Field(default=12, ge=1, le=50)


class SearchResponse(BaseModel):
    query: str
    parsed_core_ingredients: List[str]
    total_results: int
    latency_ms: float
    results: List[RecipeCard]

class StatsResponse(BaseModel):
    status: str
    total_recipes: int
    total_indexed_docs: int
    model_name: str
    best_map10: float
    best_ndcg10: float

class PopularIngredientsResponse(BaseModel):
    categories: Dict[str, List[str]]
