import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.engine import engine

@pytest.fixture(scope="module")
def client():
    # Initialize engine if not already done
    if not engine.is_ready:
        engine.initialize()
    with TestClient(app) as c:
        yield c

def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["corpus_loaded"] is True
    assert data["total_recipes"] == 68747

def test_stats_endpoint(client):
    response = client.get("/api/stats")
    assert response.status_code == 200
    data = response.json()
    assert data["total_recipes"] == 68747
    assert data["total_indexed_docs"] == 68747
    assert data["best_map10"] > 0.90
    assert data["best_ndcg10"] > 0.85

def test_popular_ingredients_endpoint(client):
    response = client.get("/api/popular-ingredients")
    assert response.status_code == 200
    data = response.json()
    assert "categories" in data
    assert "Protein" in data["categories"]
    assert "Sayuran" in data["categories"]

def test_search_endpoint(client):
    response = client.get("/api/search?q=ayam,wortel,kecap&top_k=5")
    assert response.status_code == 200
    data = response.json()
    assert data["total_results"] > 0
    assert "ayam" in data["parsed_core_ingredients"]
    assert data["latency_ms"] < 1000 # Under 1 second

    # Verify first recipe card schema
    first_recipe = data["results"][0]
    assert "doc_id" in first_recipe
    assert "title" in first_recipe
    assert "match_percentage" in first_recipe
    assert "matched_ingredients" in first_recipe
    assert "missing_ingredients" in first_recipe

def test_recipe_detail_endpoint(client):
    # First search to get a doc_id
    search_res = client.get("/api/search?q=ayam,wortel&top_k=1").json()
    sample_id = search_res["results"][0]["doc_id"]

    detail_res = client.get(f"/api/recipe/{sample_id}?q=ayam,wortel")
    assert detail_res.status_code == 200
    data = detail_res.json()
    assert data["doc_id"] == sample_id
    assert len(data["raw_ingredients"]) > 0
    assert len(data["steps"]) > 0
