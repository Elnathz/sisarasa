"use client";

import React from "react";

interface MetricBannerProps {
  latencyMs?: number;
}

export const MetricBanner: React.FC<MetricBannerProps> = ({ latencyMs }) => {
  return (
    <section id="metric-banner" style={{
      maxWidth: "1200px",
      margin: "0 auto 32px auto",
      padding: "0 24px"
    }}>
      <div style={{
        display: "grid",
        gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
        gap: "16px",
        backgroundColor: "var(--bg-surface)",
        borderRadius: "var(--radius-md)",
        padding: "20px 24px",
        border: "1px solid var(--border-subtle)",
        boxShadow: "var(--shadow-sm)"
      }}>
        {/* Metric 1 */}
        <div style={{ display: "flex", flexDirection: "column", gap: "4px" }}>
          <span style={{ fontSize: "12px", color: "var(--text-muted)", textTransform: "uppercase", fontWeight: "600" }}>
            Basis Data Korpus
          </span>
          <span style={{ fontSize: "24px", fontWeight: "800", color: "#ffffff" }}>
            68.747
          </span>
          <span style={{ fontSize: "12px", color: "var(--text-secondary)" }}>
            Resep Bersih Nusantara
          </span>
        </div>

        {/* Metric 2 */}
        <div style={{ display: "flex", flexDirection: "column", gap: "4px" }}>
          <span style={{ fontSize: "12px", color: "var(--text-muted)", textTransform: "uppercase", fontWeight: "600" }}>
            Metrik Evaluasi STKI
          </span>
          <div style={{ display: "flex", alignItems: "baseline", gap: "8px" }}>
            <span style={{ fontSize: "24px", fontWeight: "800", color: "var(--primary)" }}>
              0.9112
            </span>
            <span style={{ fontSize: "12px", color: "var(--text-muted)" }}>MAP@10</span>
          </div>
          <span style={{ fontSize: "12px", color: "var(--text-secondary)" }}>
            nDCG@10: <strong>0.8704</strong> | MRR: <strong>0.9444</strong>
          </span>
        </div>

        {/* Metric 3 */}
        <div style={{ display: "flex", flexDirection: "column", gap: "4px" }}>
          <span style={{ fontSize: "12px", color: "var(--text-muted)", textTransform: "uppercase", fontWeight: "600" }}>
            Model Temu Kembali
          </span>
          <span style={{ fontSize: "18px", fontWeight: "700", color: "#ffffff" }}>
            SisaRasa Hybrid
          </span>
          <span style={{ fontSize: "12px", color: "var(--text-secondary)" }}>
            BM25 + TF-IDF + Protein Alignment
          </span>
        </div>

        {/* Metric 4 */}
        <div style={{ display: "flex", flexDirection: "column", gap: "4px" }}>
          <span style={{ fontSize: "12px", color: "var(--text-muted)", textTransform: "uppercase", fontWeight: "600" }}>
            Latensi Inferensi
          </span>
          <div style={{ display: "flex", alignItems: "baseline", gap: "6px" }}>
            <span style={{ fontSize: "24px", fontWeight: "800", color: "var(--match-green)" }}>
              {latencyMs !== undefined ? `${latencyMs} ms` : "~100 ms"}
            </span>
          </div>
          <span style={{ fontSize: "12px", color: "var(--text-secondary)" }}>
            Waktu respon *real-time* pencarian
          </span>
        </div>
      </div>
    </section>
  );
};
