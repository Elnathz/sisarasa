"use client";

import React, { useEffect, useState } from "react";
import { RecipeDetail } from "@/types/recipe";
import { getRecipeDetail } from "@/services/api";

interface RecipeModalProps {
  docId: string;
  activeQuery: string;
  onClose: () => void;
}

export const RecipeModal: React.FC<RecipeModalProps> = ({
  docId,
  activeQuery,
  onClose,
}) => {
  const [detail, setDetail] = useState<RecipeDetail | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;
    setIsLoading(true);
    setError(null);

    getRecipeDetail(docId, activeQuery)
      .then((data) => {
        if (isMounted) {
          setDetail(data);
          setIsLoading(false);
        }
      })
      .catch((err) => {
        if (isMounted) {
          setError(err.message || "Gagal memuat detail resep.");
          setIsLoading(false);
        }
      });

    const handleKeyDown = (e: globalThis.KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", handleKeyDown);

    return () => {
      isMounted = false;
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, [docId, activeQuery, onClose]);

  return (
    <div
      id="recipe-detail-modal-backdrop"
      onClick={onClose}
      style={{
        position: "fixed",
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundColor: "rgba(0, 0, 0, 0.75)",
        backdropFilter: "blur(8px)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: "16px",
        zIndex: 100,
        animation: "fadeIn 0.2s ease"
      }}
    >
      <div
        id="recipe-detail-modal-content"
        onClick={(e) => e.stopPropagation()}
        style={{
          backgroundColor: "var(--bg-surface)",
          border: "1px solid var(--border-hover)",
          borderRadius: "var(--radius-lg)",
          maxWidth: "850px",
          width: "100%",
          maxHeight: "90vh",
          display: "flex",
          flexDirection: "column",
          overflow: "hidden",
          boxShadow: "0 20px 50px rgba(0, 0, 0, 0.6)"
        }}
      >
        {/* Header */}
        <div style={{
          padding: "20px 24px",
          borderBottom: "1px solid var(--border-subtle)",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "flex-start",
          gap: "16px",
          backgroundColor: "rgba(24, 28, 38, 0.9)"
        }}>
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "6px" }}>
              {detail?.category && (
                <span style={{
                  fontSize: "12px",
                  fontWeight: "600",
                  textTransform: "uppercase",
                  padding: "2px 8px",
                  borderRadius: "4px",
                  backgroundColor: "var(--bg-surface-elevated)",
                  color: "var(--text-secondary)"
                }}>
                  {detail.category}
                </span>
              )}
              {detail?.primary_protein && (
                <span style={{
                  fontSize: "12px",
                  fontWeight: "600",
                  padding: "2px 8px",
                  borderRadius: "4px",
                  backgroundColor: "rgba(234, 88, 12, 0.15)",
                  color: "#fb923c"
                }}>
                  {detail.primary_protein}
                </span>
              )}
              {detail?.match_percentage !== undefined && (
                <span style={{
                  fontSize: "12px",
                  fontWeight: "700",
                  padding: "2px 8px",
                  borderRadius: "var(--radius-full)",
                  backgroundColor: "var(--match-green-bg)",
                  color: "var(--match-green)"
                }}>
                  {detail.match_percentage}% Cocok
                </span>
              )}
            </div>
            <h2 style={{
              fontSize: "clamp(20px, 3vw, 26px)",
              fontWeight: "800",
              color: "#ffffff",
              lineHeight: "1.3"
            }}>
              {detail ? detail.title : "Memuat Resep..."}
            </h2>
          </div>

          <button
            id="close-recipe-modal-btn"
            type="button"
            onClick={onClose}
            style={{
              background: "none",
              border: "none",
              color: "var(--text-secondary)",
              fontSize: "24px",
              cursor: "pointer",
              padding: "4px",
              lineHeight: 1
            }}
          >
            &times;
          </button>
        </div>

        {/* Body Content */}
        <div style={{
          padding: "24px",
          overflowY: "auto",
          flex: 1,
          display: "flex",
          flexDirection: "column",
          gap: "24px"
        }}>
          {isLoading && (
            <div style={{ textAlign: "center", padding: "40px" }}>
              <span className="spinner" style={{ width: "32px", height: "32px", marginBottom: "12px" }} />
              <p style={{ color: "var(--text-secondary)" }}>Memuat takaran bahan dan langkah memasak...</p>
            </div>
          )}

          {error && (
            <div style={{
              padding: "16px",
              borderRadius: "var(--radius-sm)",
              backgroundColor: "rgba(239, 68, 68, 0.15)",
              color: "#f87171",
              border: "1px solid rgba(239, 68, 68, 0.3)"
            }}>
              {error}
            </div>
          )}

          {detail && !isLoading && (
            <div style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))",
              gap: "28px"
            }}>
              {/* Left Column: Ingredients */}
              <div>
                <h3 style={{
                  fontSize: "16px",
                  fontWeight: "700",
                  color: "var(--primary)",
                  marginBottom: "14px",
                  textTransform: "uppercase",
                  letterSpacing: "0.5px"
                }}>
                  Bahan-Bahan ({detail.raw_ingredients.length})
                </h3>

                <ul style={{ listStyle: "none", display: "flex", flexDirection: "column", gap: "8px" }}>
                  {detail.raw_ingredients.map((ingr, idx) => {
                    const isMatched = detail.matched_ingredients.some((m) =>
                      ingr.toLowerCase().includes(m.toLowerCase())
                    );
                    return (
                      <li
                        key={idx}
                        style={{
                          fontSize: "14px",
                          padding: "10px 14px",
                          borderRadius: "var(--radius-sm)",
                          backgroundColor: isMatched
                            ? "rgba(16, 185, 129, 0.1)"
                            : "var(--bg-surface-elevated)",
                          border: isMatched
                            ? "1px solid var(--match-green-border)"
                            : "1px solid var(--border-subtle)",
                          display: "flex",
                          alignItems: "center",
                          justifyContent: "space-between",
                          gap: "8px"
                        }}
                      >
                        <span style={{ color: "#ffffff" }}>{ingr}</span>
                        {isMatched ? (
                          <span style={{
                            fontSize: "11px",
                            fontWeight: "700",
                            color: "var(--match-green)",
                            backgroundColor: "var(--match-green-bg)",
                            padding: "2px 6px",
                            borderRadius: "4px"
                          }}>
                            Ada
                          </span>
                        ) : (
                          <span style={{
                            fontSize: "11px",
                            fontWeight: "600",
                            color: "var(--missing-orange)",
                            backgroundColor: "var(--missing-orange-bg)",
                            padding: "2px 6px",
                            borderRadius: "4px"
                          }}>
                            Beli
                          </span>
                        )}
                      </li>
                    );
                  })}
                </ul>
              </div>

              {/* Right Column: Cooking Steps */}
              <div>
                <h3 style={{
                  fontSize: "16px",
                  fontWeight: "700",
                  color: "var(--primary)",
                  marginBottom: "14px",
                  textTransform: "uppercase",
                  letterSpacing: "0.5px"
                }}>
                  Langkah Memasak ({detail.steps.length})
                </h3>

                <ol style={{ listStyle: "none", display: "flex", flexDirection: "column", gap: "14px" }}>
                  {detail.steps.map((step, idx) => (
                    <li
                      key={idx}
                      style={{
                        display: "flex",
                        gap: "12px",
                        alignItems: "flex-start",
                        fontSize: "14px",
                        lineHeight: "1.6",
                        color: "var(--text-main)"
                      }}
                    >
                      <span style={{
                        flexShrink: 0,
                        width: "26px",
                        height: "26px",
                        borderRadius: "50%",
                        backgroundColor: "var(--bg-surface-elevated)",
                        border: "1px solid var(--border-hover)",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        fontSize: "12px",
                        fontWeight: "700",
                        color: "var(--primary)"
                      }}>
                        {idx + 1}
                      </span>
                      <span>{step}</span>
                    </li>
                  ))}
                </ol>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div style={{
          padding: "16px 24px",
          borderTop: "1px solid var(--border-subtle)",
          backgroundColor: "rgba(24, 28, 38, 0.9)",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center"
        }}>
          <span style={{ fontSize: "12px", color: "var(--text-muted)" }}>
            Sumber: {detail?.source || "SisaRasa Dataset"}
          </span>

          {detail?.url ? (
            <a
              id="source-recipe-external-link"
              href={detail.url}
              target="_blank"
              rel="noopener noreferrer"
              style={{
                fontSize: "13px",
                color: "var(--primary)",
                textDecoration: "underline",
                fontWeight: "600"
              }}
            >
              Buka Resep Asli ↗
            </a>
          ) : (
            <button
              id="modal-close-bottom-btn"
              type="button"
              onClick={onClose}
              style={{
                padding: "8px 20px",
                borderRadius: "var(--radius-sm)",
                backgroundColor: "var(--bg-surface-elevated)",
                color: "#ffffff",
                fontSize: "13px",
                fontWeight: "600",
                border: "1px solid var(--border-subtle)",
                cursor: "pointer"
              }}
            >
              Tutup
            </button>
          )}
        </div>
      </div>
    </div>
  );
};
