import {
  SearchResponse,
  RecipeDetail,
  StatsResponse,
  PopularIngredientsResponse,
} from "@/types/recipe";

// In browser or SSR with rewrite, '/api' proxies to http://127.0.0.1:8000/api
const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "";

export async function searchRecipes(
  query: string,
  top_k: number = 12
): Promise<SearchResponse> {
  const params = new URLSearchParams({
    q: query,
    top_k: top_k.toString(),
  });

  const res = await fetch(`${BASE_URL}/api/search?${params.toString()}`);
  if (!res.ok) {
    const errorText = await res.text();
    throw new Error(errorText || "Gagal melakukan pencarian resep.");
  }
  return res.json();
}

export async function getRecipeDetail(
  doc_id: string,
  query?: string
): Promise<RecipeDetail> {
  const params = query ? `?q=${encodeURIComponent(query)}` : "";
  const res = await fetch(`${BASE_URL}/api/recipe/${encodeURIComponent(doc_id)}${params}`);
  if (!res.ok) {
    throw new Error(`Resep ${doc_id} tidak ditemukan.`);
  }
  return res.json();
}

export async function getStats(): Promise<StatsResponse> {
  const res = await fetch(`${BASE_URL}/api/stats`);
  if (!res.ok) {
    throw new Error("Gagal mengambil statistik sistem.");
  }
  return res.json();
}

export async function getPopularIngredients(): Promise<PopularIngredientsResponse> {
  const res = await fetch(`${BASE_URL}/api/popular-ingredients`);
  if (!res.ok) {
    throw new Error("Gagal mengambil daftar bahan populer.");
  }
  return res.json();
}
