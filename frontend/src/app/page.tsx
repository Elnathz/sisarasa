"use client";

import React, { useState, useEffect, useMemo } from "react";
import { Navbar } from "@/components/Navbar";
import { MetricBanner } from "@/components/MetricBanner";
import { SmartIngredientInput } from "@/components/SmartIngredientInput";
import { RecipeCard } from "@/components/RecipeCard";
import { RecipeModal } from "@/components/RecipeModal";
import { searchRecipes } from "@/services/api";
import { RecipeCard as RecipeCardType } from "@/types/recipe";

export default function Home() {
  const [ingredients, setIngredients] = useState<string[]>([
    "ayam",
    "wortel",
    "kecap",
  ]);
  const [results, setResults] = useState<RecipeCardType[]>([]);
  const [latencyMs, setLatencyMs] = useState<number | undefined>(undefined);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [selectedRecipeDocId, setSelectedRecipeDocId] = useState<string | null>(null);
  const [activeCategoryFilter, setActiveCategoryFilter] = useState<string>("Semua");
  const [sortBy, setSortBy] = useState<"match" | "score">("match");

  const runSearch = async (queryIngredients: string[]) => {
    if (queryIngredients.length === 0) return;
    setIsLoading(true);
    setErrorMessage(null);

    const queryStr = queryIngredients.join(", ");
    try {
      const data = await searchRecipes(queryStr, 18);
      setResults(data.results || []);
      setLatencyMs(data.latency_ms);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Gagal terhubung ke backend FastAPI.";
      setErrorMessage(
        `${msg} Pastikan server backend FastAPI sedang berjalan (python backend/run.py di port 8000).`
      );
    } finally {
      setIsLoading(false);
    }
  };

  // Initial search on first mount
  useEffect(() => {
    runSearch(ingredients);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Filter & Sort results
  const filteredAndSortedResults = useMemo(() => {
    let list = [...results];

    // Filter by protein/category
    if (activeCategoryFilter !== "Semua") {
      list = list.filter((r) => {
        const cat = (r.category || "").toLowerCase();
        const prot = (r.primary_protein || "").toLowerCase();
        const filter = activeCategoryFilter.toLowerCase();

        if (filter === "ayam") return prot.includes("ayam") || cat.includes("ayam");
        if (filter === "telur") return prot.includes("telur") || cat.includes("telur");
        if (filter === "tahu & tempe") return prot.includes("tahu") || prot.includes("tempe");
        if (filter === "daging sapi") return prot.includes("sapi") || cat.includes("daging");
        if (filter === "seafood") return prot.includes("udang") || prot.includes("ikan") || prot.includes("cumi");
        if (filter === "sup & sayur") return cat.includes("sup") || cat.includes("sayur");
        return true;
      });
    }

    // Sort
    list.sort((a, b) => {
      if (sortBy === "match") {
        return b.match_percentage - a.match_percentage || b.score - a.score;
      }
      return b.score - a.score;
    });

    return list;
  }, [results, activeCategoryFilter, sortBy]);

  const categoryFilters = [
    "Semua",
    "Ayam",
    "Telur",
    "Tahu & Tempe",
    "Daging Sapi",
    "Seafood",
    "Sup & Sayur",
  ];

  return (
    <div style={{ minHeight: "100vh", display: "flex", flexDirection: "column" }}>
      <Navbar />

      <main style={{ flex: 1, paddingBottom: "60px" }}>
        {/* Metric Banner for STKI Proof */}
        <div style={{ marginTop: "24px" }}>
          <MetricBanner latencyMs={latencyMs} />
        </div>

        {/* Smart Ingredient Search Bar */}
        <SmartIngredientInput
          ingredients={ingredients}
          onChangeIngredients={setIngredients}
          onSearch={runSearch}
          isLoading={isLoading}
        />

        {/* Results Section */}
        <section
          id="results-section"
          style={{
            maxWidth: "1200px",
            margin: "0 auto",
            padding: "0 24px"
          }}
        >
          {/* Error Message */}
          {errorMessage && (
            <div style={{
              padding: "16px 20px",
              borderRadius: "var(--radius-md)",
              backgroundColor: "rgba(239, 68, 68, 0.12)",
              border: "1px solid rgba(239, 68, 68, 0.35)",
              color: "#f87171",
              marginBottom: "24px",
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between"
            }}>
              <span>{errorMessage}</span>
              <button
                type="button"
                onClick={() => runSearch(ingredients)}
                style={{
                  background: "var(--primary)",
                  color: "#000",
                  border: "none",
                  padding: "6px 14px",
                  borderRadius: "var(--radius-sm)",
                  fontWeight: "700",
                  cursor: "pointer"
                }}
              >
                Coba Lagi
              </button>
            </div>
          )}

          {/* Controls Bar: Categories & Sorting */}
          <div style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            flexWrap: "wrap",
            gap: "14px",
            marginBottom: "24px",
            paddingBottom: "16px",
            borderBottom: "1px solid var(--border-subtle)"
          }}>
            {/* Category Filter Pills */}
            <div style={{ display: "flex", flexWrap: "wrap", gap: "6px" }}>
              {categoryFilters.map((cat) => (
                <button
                  key={cat}
                  id={`filter-${cat.toLowerCase().replace(/[^a-z0-9]/g, "-")}`}
                  type="button"
                  onClick={() => setActiveCategoryFilter(cat)}
                  style={{
                    padding: "6px 14px",
                    borderRadius: "var(--radius-full)",
                    fontSize: "13px",
                    fontWeight: "600",
                    border: activeCategoryFilter === cat
                      ? "1px solid var(--primary)"
                      : "1px solid var(--border-subtle)",
                    backgroundColor: activeCategoryFilter === cat
                      ? "rgba(245, 158, 11, 0.2)"
                      : "var(--bg-surface)",
                    color: activeCategoryFilter === cat ? "var(--primary-hover)" : "var(--text-secondary)",
                    cursor: "pointer",
                    transition: "all 0.15s ease"
                  }}
                >
                  {cat}
                </button>
              ))}
            </div>

            {/* Sorting Select */}
            <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
              <label htmlFor="sort-select" style={{ fontSize: "13px", color: "var(--text-muted)" }}>
                Urutkan:
              </label>
              <select
                id="sort-select"
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value as "match" | "score")}
                style={{
                  padding: "6px 12px",
                  borderRadius: "var(--radius-sm)",
                  backgroundColor: "var(--bg-surface)",
                  color: "var(--text-main)",
                  border: "1px solid var(--border-subtle)",
                  fontSize: "13px",
                  outline: "none",
                  cursor: "pointer"
                }}
              >
                <option value="match">% Kecocokan Tertinggi</option>
                <option value="score">Skor Relevansi IR</option>
              </select>
            </div>
          </div>

          {/* Results Summary */}
          <div style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            marginBottom: "20px"
          }}>
            <span style={{ fontSize: "14px", color: "var(--text-secondary)" }}>
              Ditemukan <strong>{filteredAndSortedResults.length}</strong> resep rekomendasi
              {ingredients.length > 0 && ` untuk kombinasi: ${ingredients.join(", ")}`}
            </span>
          </div>

          {/* Recipe Grid */}
          {filteredAndSortedResults.length > 0 ? (
            <div
              id="recipe-cards-grid"
              style={{
                display: "grid",
                gridTemplateColumns: "repeat(auto-fill, minmax(320px, 1fr))",
                gap: "24px"
              }}
            >
              {filteredAndSortedResults.map((recipe) => (
                <RecipeCard
                  key={recipe.doc_id}
                  recipe={recipe}
                  onSelect={(r) => setSelectedRecipeDocId(r.doc_id)}
                />
              ))}
            </div>
          ) : (
            !isLoading && (
              <div style={{
                textAlign: "center",
                padding: "60px 20px",
                backgroundColor: "var(--bg-surface)",
                borderRadius: "var(--radius-md)",
                border: "1px dashed var(--border-subtle)"
              }}>
                <h3 style={{ fontSize: "18px", color: "#ffffff", marginBottom: "8px" }}>
                  Tidak ada resep yang cocok dengan filter saat ini
                </h3>
                <p style={{ color: "var(--text-secondary)", fontSize: "14px", marginBottom: "16px" }}>
                  Coba ubah filter kategori atau tambahkan variasi bahan kulkas lain pada pencarian.
                </p>
                <button
                  type="button"
                  onClick={() => setActiveCategoryFilter("Semua")}
                  style={{
                    padding: "8px 18px",
                    borderRadius: "var(--radius-sm)",
                    backgroundColor: "var(--primary)",
                    color: "#000",
                    border: "none",
                    fontWeight: "600",
                    cursor: "pointer"
                  }}
                >
                  Reset Filter Kategori
                </button>
              </div>
            )
          )}
        </section>
      </main>

      {/* Recipe Detail Modal */}
      {selectedRecipeDocId && (
        <RecipeModal
          docId={selectedRecipeDocId}
          activeQuery={ingredients.join(", ")}
          onClose={() => setSelectedRecipeDocId(null)}
        />
      )}

      {/* Footer */}
      <footer style={{
        borderTop: "1px solid var(--border-subtle)",
        padding: "24px",
        textAlign: "center",
        fontSize: "13px",
        color: "var(--text-muted)",
        backgroundColor: "var(--bg-subtle)"
      }}>
        <p>
          <strong>SisaRasa</strong> &bull; Proyek Sistem Temu Kembali Informasi (STKI) Semester 5 &bull; Farros Rifantiarno Ramadhani
        </p>
        <p style={{ marginTop: "4px", fontSize: "12px" }}>
          Didukung model SisaRasa Hybrid Ranking (BM25 + TF-IDF + Culinary NLP Parser) &bull; Korpus 68.747 Resep Nusantara
        </p>
      </footer>
    </div>
  );
}
