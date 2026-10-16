"use client";

import React from "react";
import { RecipeCard as RecipeCardType } from "@/types/recipe";

interface RecipeCardProps {
  recipe: RecipeCardType;
  onSelect: (recipe: RecipeCardType) => void;
}

export const RecipeCard: React.FC<RecipeCardProps> = ({ recipe, onSelect }) => {
  const isHighMatch = recipe.match_percentage >= 75;
  const isMidMatch = recipe.match_percentage >= 45 && recipe.match_percentage < 75;

  const matchBadgeBg = isHighMatch
    ? "rgba(16, 185, 129, 0.18)"
    : isMidMatch
    ? "rgba(245, 158, 11, 0.18)"
    : "rgba(249, 115, 22, 0.18)";

  const matchBadgeColor = isHighMatch
    ? "#34d399"
    : isMidMatch
    ? "#fbbf24"
    : "#fb923c";

  const matchBadgeBorder = isHighMatch
    ? "rgba(16, 185, 129, 0.4)"
    : isMidMatch
    ? "rgba(245, 158, 11, 0.4)"
    : "rgba(249, 115, 22, 0.4)";

  return (
    <article
      id={`recipe-card-${recipe.doc_id}`}
      style={{
        backgroundColor: "var(--bg-surface)",
        borderRadius: "var(--radius-md)",
        border: "1px solid var(--border-subtle)",
        padding: "20px",
        display: "flex",
        flexDirection: "column",
        justifyContent: "space-between",
        gap: "16px",
        transition: "transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease",
        position: "relative",
        boxShadow: "var(--shadow-sm)"
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.transform = "translateY(-4px)";
        e.currentTarget.style.borderColor = "var(--border-hover)";
        e.currentTarget.style.boxShadow = "var(--shadow-md)";
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.transform = "translateY(0)";
        e.currentTarget.style.borderColor = "var(--border-subtle)";
        e.currentTarget.style.boxShadow = "var(--shadow-sm)";
      }}
    >
      {/* Top Header: Category, Protein & Match Badge */}
      <div>
        <div style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "flex-start",
          gap: "8px",
          marginBottom: "10px"
        }}>
          <div style={{ display: "flex", flexWrap: "wrap", gap: "6px" }}>
            {recipe.category && (!recipe.primary_protein || recipe.category.toLowerCase() !== recipe.primary_protein.toLowerCase()) && (
              <span style={{
                fontSize: "11px",
                fontWeight: "600",
                textTransform: "uppercase",
                padding: "3px 8px",
                borderRadius: "4px",
                backgroundColor: "var(--bg-surface-elevated)",
                color: "var(--text-secondary)",
                border: "1px solid var(--border-subtle)"
              }}>
                {recipe.category}
              </span>
            )}
            {recipe.primary_protein && (
              <span style={{
                fontSize: "11px",
                fontWeight: "600",
                padding: "3px 8px",
                borderRadius: "4px",
                backgroundColor: "rgba(234, 88, 12, 0.15)",
                color: "#fb923c",
                border: "1px solid rgba(234, 88, 12, 0.3)"
              }}>
                {recipe.primary_protein}
              </span>
            )}
          </div>

          {/* Match Score Badge */}
          <div style={{
            fontSize: "13px",
            fontWeight: "700",
            padding: "4px 10px",
            borderRadius: "var(--radius-full)",
            backgroundColor: matchBadgeBg,
            color: matchBadgeColor,
            border: `1px solid ${matchBadgeBorder}`,
            whiteSpace: "nowrap"
          }}>
            {recipe.match_percentage}% Cocok
          </div>
        </div>

        {/* Recipe Title */}
        <h3 style={{
          fontSize: "18px",
          fontWeight: "700",
          color: "#ffffff",
          lineHeight: "1.35",
          marginBottom: "12px",
          display: "-webkit-box",
          WebkitLineClamp: 2,
          WebkitBoxOrient: "vertical",
          overflow: "hidden"
        }}>
          {recipe.title}
        </h3>

        {/* Ingredient Breakdown */}
        <div style={{ display: "flex", flexDirection: "column", gap: "8px", fontSize: "13px" }}>
          {/* Matched */}
          <div>
            <span style={{ color: "var(--text-muted)", fontSize: "11px", textTransform: "uppercase", fontWeight: "600", display: "block", marginBottom: "4px" }}>
              Bahan Dimiliki ({recipe.matched_ingredients.length}):
            </span>
            <div style={{ display: "flex", flexWrap: "wrap", gap: "4px" }}>
              {recipe.matched_ingredients.length > 0 ? (
                recipe.matched_ingredients.map((ing) => (
                  <span
                    key={ing}
                    style={{
                      fontSize: "12px",
                      padding: "2px 8px",
                      borderRadius: "4px",
                      backgroundColor: "var(--match-green-bg)",
                      color: "#34d399",
                      border: "1px solid var(--match-green-border)",
                      fontWeight: "500"
                    }}
                  >
                    ✓ {ing}
                  </span>
                ))
              ) : (
                <span style={{ color: "var(--text-muted)", fontStyle: "italic", fontSize: "12px" }}>-</span>
              )}
            </div>
          </div>

          {/* Missing / Need to buy */}
          <div>
            <span style={{ color: "var(--text-muted)", fontSize: "11px", textTransform: "uppercase", fontWeight: "600", display: "block", marginBottom: "4px" }}>
              Perlu Tambahan ({recipe.missing_ingredients.length}):
            </span>
            <div style={{ display: "flex", flexWrap: "wrap", gap: "4px" }}>
              {recipe.missing_ingredients.length > 0 ? (
                recipe.missing_ingredients.slice(0, 4).map((ing) => (
                  <span
                    key={ing}
                    style={{
                      fontSize: "12px",
                      padding: "2px 8px",
                      borderRadius: "4px",
                      backgroundColor: "var(--missing-orange-bg)",
                      color: "#fb923c",
                      border: "1px solid var(--missing-orange-border)",
                      fontWeight: "500"
                    }}
                  >
                    + {ing}
                  </span>
                ))
              ) : (
                <span style={{ color: "var(--match-green)", fontWeight: "600", fontSize: "12px" }}>
                  Lengkap di kulkas!
                </span>
              )}
              {recipe.missing_ingredients.length > 4 && (
                <span style={{ fontSize: "11px", color: "var(--text-muted)", alignSelf: "center" }}>
                  +{recipe.missing_ingredients.length - 4} lainnya
                </span>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Bottom CTA */}
      <div style={{
        borderTop: "1px solid var(--border-subtle)",
        paddingTop: "14px",
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center"
      }}>
        <span style={{ fontSize: "12px", color: "var(--text-muted)" }}>
          Skor IR: <strong>{recipe.score.toFixed(3)}</strong>
        </span>

        <button
          id={`view-recipe-btn-${recipe.doc_id}`}
          type="button"
          onClick={() => onSelect(recipe)}
          style={{
            padding: "8px 16px",
            borderRadius: "var(--radius-sm)",
            backgroundColor: "var(--bg-surface-elevated)",
            color: "#ffffff",
            fontSize: "13px",
            fontWeight: "600",
            border: "1px solid var(--border-subtle)",
            cursor: "pointer",
            transition: "all 0.2s ease"
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.backgroundColor = "var(--primary)";
            e.currentTarget.style.color = "#000000";
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.backgroundColor = "var(--bg-surface-elevated)";
            e.currentTarget.style.color = "#ffffff";
          }}
        >
          Lihat Resep
        </button>
      </div>
    </article>
  );
};
