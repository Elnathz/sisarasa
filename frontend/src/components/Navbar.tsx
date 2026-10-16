"use client";

import React from "react";

interface NavbarProps {
  totalRecipes?: number;
}

export const Navbar: React.FC<NavbarProps> = ({ totalRecipes = 68747 }) => {
  return (
    <header id="app-header" style={{
      position: "sticky",
      top: 0,
      zIndex: 40,
      backdropFilter: "blur(12px)",
      backgroundColor: "rgba(12, 14, 18, 0.8)",
      borderBottom: "1px solid var(--border-subtle)",
      padding: "16px 24px"
    }}>
      <div style={{
        maxWidth: "1200px",
        margin: "0 auto",
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        flexWrap: "wrap",
        gap: "12px"
      }}>
        {/* Brand */}
        <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
          <div style={{
            width: "40px",
            height: "40px",
            borderRadius: "12px",
            background: "linear-gradient(135deg, #f59e0b 0%, #ea580c 100%)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            boxShadow: "0 4px 12px rgba(245, 158, 11, 0.35)",
            fontSize: "20px",
            fontWeight: "bold",
            color: "#ffffff"
          }}>
            SR
          </div>
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
              <span style={{ fontSize: "20px", fontWeight: "800", letterSpacing: "-0.5px" }}>SisaRasa</span>
              <span style={{
                fontSize: "11px",
                fontWeight: "600",
                textTransform: "uppercase",
                padding: "2px 8px",
                borderRadius: "var(--radius-full)",
                backgroundColor: "rgba(245, 158, 11, 0.15)",
                color: "var(--primary)",
                border: "1px solid rgba(245, 158, 11, 0.3)"
              }}>
                STKI Hybrid IR
              </span>
            </div>
            <p style={{ fontSize: "12px", color: "var(--text-muted)" }}>
              Sistem Temu Kembali Resep Berbasis Bahan Sisa
            </p>
          </div>
        </div>

        {/* Action Links & Stats */}
        <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
          <div style={{
            fontSize: "12px",
            color: "var(--text-secondary)",
            padding: "6px 14px",
            borderRadius: "var(--radius-full)",
            backgroundColor: "var(--bg-surface)",
            border: "1px solid var(--border-subtle)",
            display: "flex",
            alignItems: "center",
            gap: "6px"
          }}>
            <span style={{
              width: "8px",
              height: "8px",
              borderRadius: "50%",
              backgroundColor: "var(--match-green)",
              boxShadow: "0 0 8px var(--match-green)"
            }} />
            <span>Korpus: <strong>{totalRecipes.toLocaleString("id-ID")}</strong> Resep</span>
          </div>

          <a
            id="docs-link-btn"
            href="http://127.0.0.1:8000/docs"
            target="_blank"
            rel="noopener noreferrer"
            style={{
              fontSize: "13px",
              fontWeight: "600",
              color: "var(--text-main)",
              padding: "6px 14px",
              borderRadius: "var(--radius-sm)",
              backgroundColor: "var(--bg-surface-elevated)",
              border: "1px solid var(--border-subtle)",
              cursor: "pointer",
              transition: "all 0.2s ease"
            }}
          >
            API Swagger
          </a>

          <a
            id="github-repo-link"
            href="https://github.com/Elnathz/sisarasa"
            target="_blank"
            rel="noopener noreferrer"
            style={{
              fontSize: "13px",
              fontWeight: "600",
              color: "#ffffff",
              padding: "6px 14px",
              borderRadius: "var(--radius-sm)",
              background: "linear-gradient(135deg, #f59e0b 0%, #d97706 100%)",
              boxShadow: "0 2px 8px rgba(245, 158, 11, 0.25)",
              cursor: "pointer"
            }}
          >
            GitHub
          </a>
        </div>
      </div>
    </header>
  );
};
