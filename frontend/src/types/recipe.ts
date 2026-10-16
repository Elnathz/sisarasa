export interface RecipeCard {
  doc_id: string;
  title: string;
  source: string;
  category?: string;
  url?: string;
  loves?: number;
  score: number;
  match_percentage: number;
  matched_ingredients: string[];
  missing_ingredients: string[];
  total_ingredients_count: number;
  primary_protein?: string;
  preview_steps?: string;
}

export interface RecipeDetail {
  doc_id: string;
  title: string;
  source: string;
  category?: string;
  url?: string;
  loves?: number;
  score?: number;
  match_percentage?: number;
  matched_ingredients: string[];
  missing_ingredients: string[];
  raw_ingredients: string[];
  clean_ingredients: string[];
  core_ingredients: string[];
  steps: string[];
  primary_protein?: string;
}

export interface SearchResponse {
  query: string;
  parsed_core_ingredients: string[];
  total_results: number;
  latency_ms: number;
  results: RecipeCard[];
}

export interface StatsResponse {
  status: string;
  total_recipes: number;
  total_indexed_docs: number;
  model_name: string;
  best_map10: number;
  best_ndcg10: number;
}

export interface PopularIngredientsResponse {
  categories: Record<string, string[]>;
}
