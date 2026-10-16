"use client";

import React, { useState, KeyboardEvent } from "react";

interface SmartIngredientInputProps {
  ingredients: string[];
  onChangeIngredients: (ingredients: string[]) => void;
  onSearch: (ingredients: string[]) => void;
  isLoading: boolean;
}

export const SmartIngredientInput: React.FC<SmartIngredientInputProps> = ({
  ingredients,
  onChangeIngredients,
  onSearch,
  isLoading,
}) => {
  const [inputValue, setInputValue] = useState("");

  const handleAddIngredient = (item: string) => {
    const trimmed = item.trim().toLowerCase();
    if (!trimmed) return;
    if (!ingredients.includes(trimmed)) {
      const updated = [...ingredients, trimmed];
      onChangeIngredients(updated);
    }
    setInputValue("");
  };

  const handleRemoveIngredient = (item: string) => {
    const updated = ingredients.filter((ing) => ing !== item);
    onChangeIngredients(updated);
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" || e.key === ",") {
      e.preventDefault();
      handleAddIngredient(inputValue);
    } else if (e.key === "Backspace" && !inputValue && ingredients.length > 0) {
      handleRemoveIngredient(ingredients[ingredients.length - 1]);
    }
  };

  const handleQuickAdd = (item: string) => {
    handleAddIngredient(item);
  };

  const handleClearAll = () => {
    onChangeIngredients([]);
    setInputValue("");
  };

  const quickCategories = [
    {
      category: "Protein",
      items: ["Ayam", "Telur", "Tahu", "Tempe", "Daging Sapi", "Udang", "Ikan"],
    },
    {
      category: "Sayuran",
      items: ["Wortel", "Kentang", "Buncis", "Kol", "Bayam", "Tomat", "Kangkung"],
    },
    {
      category: "Bumbu & Pelengkap",
      items: ["Bawang Merah", "Bawang Putih", "Cabai Rawit", "Santan", "Kecap Manis"],
    },
  ];

  return (
    <section id="search-section" style={{
      maxWidth: "1200px",
      margin: "0 auto 36px auto",
      padding: "0 24px"
    }}>
      {/* Hero Title */}
      <div style={{ textAlign: "center", marginBottom: "28px" }}>
        <h1 style={{
          fontSize: "clamp(28px, 4vw, 42px)",
          fontWeight: "800",
          letterSpacing: "-1px",
          marginBottom: "12px",
          background: "linear-gradient(135deg, #ffffff 30%, #f59e0b 100%)",
          WebkitBackgroundClip: "text",
          WebkitTextFillColor: "transparent"
        }}>
          Punya Bahan Sisa Apa di Kulkas?
        </h1>
        <p style={{
          fontSize: "clamp(14px, 1.5vw, 17px)",
          color: "var(--text-secondary)",
          maxWidth: "700px",
          margin: "0 auto",
          lineHeight: "1.6"
        }}>
          Ketik bahan-bahan mentah yang Anda miliki. Sistem temu kembali hybrid kami akan
          mencarikan resep masakan Nusantara dengan bahan belanja tambahan paling minimal.
        </p>
      </div>

      {/* Main Search Box */}
      <div style={{
        backgroundColor: "var(--bg-surface)",
        border: "1px solid var(--border-hover)",
        borderRadius: "var(--radius-lg)",
        padding: "16px",
        boxShadow: "var(--shadow-glow)",
        marginBottom: "20px"
      }}>
        {/* Chips Container + Text Input */}
        <div style={{
          display: "flex",
          flexWrap: "wrap",
          alignItems: "center",
          gap: "8px",
          minHeight: "56px",
          padding: "8px 12px",
          backgroundColor: "var(--bg-main)",
          borderRadius: "var(--radius-md)",
          border: "1px solid var(--border-subtle)"
        }}>
          {ingredients.map((item) => (
            <span
              key={item}
              style={{
                display: "inline-flex",
                alignItems: "center",
                gap: "6px",
                padding: "6px 12px",
                borderRadius: "var(--radius-full)",
                backgroundColor: "rgba(245, 158, 11, 0.15)",
                color: "var(--primary-hover)",
                border: "1px solid rgba(245, 158, 11, 0.35)",
                fontSize: "14px",
                fontWeight: "600",
                textTransform: "capitalize"
              }}
            >
              {item}
              <button
                type="button"
                onClick={() => handleRemoveIngredient(item)}
                style={{
                  background: "none",
                  border: "none",
                  color: "var(--primary-hover)",
                  cursor: "pointer",
                  fontSize: "14px",
                  fontWeight: "bold",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  padding: "0 2px"
                }}
              >
                &times;
              </button>
            </span>
          ))}

          <input
            id="ingredient-search-input"
            type="text"
            placeholder={
              ingredients.length === 0
                ? "Ketik nama bahan (contoh: ayam, wortel, kecap) lalu tekan Enter..."
                : "Tambah bahan lain..."
            }
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={handleKeyDown}
            onBlur={() => {
              if (inputValue.trim()) {
                handleAddIngredient(inputValue);
              }
            }}
            style={{
              flex: "1 1 220px",
              background: "transparent",
              border: "none",
              outline: "none",
              color: "#ffffff",
              fontSize: "15px",
              padding: "6px 4px"
            }}
          />
        </div>

        {/* Buttons Bar */}
        <div style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginTop: "16px",
          flexWrap: "wrap",
          gap: "12px"
        }}>
          <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
            <span style={{ fontSize: "13px", color: "var(--text-muted)" }}>
              {ingredients.length} bahan dimasukkan
            </span>
            {ingredients.length > 0 && (
              <button
                id="clear-all-ingredients-btn"
                type="button"
                onClick={handleClearAll}
                style={{
                  background: "none",
                  border: "none",
                  color: "var(--text-muted)",
                  fontSize: "13px",
                  cursor: "pointer",
                  textDecoration: "underline"
                }}
              >
                Reset Semua
              </button>
            )}
          </div>

          <button
            id="submit-search-btn"
            type="button"
            disabled={isLoading || (ingredients.length === 0 && !inputValue.trim())}
            onClick={() => {
              if (inputValue.trim()) {
                const updated = [...ingredients, inputValue.trim().toLowerCase()];
                onChangeIngredients(updated);
                setInputValue("");
                onSearch(updated);
              } else {
                onSearch(ingredients);
              }
            }}
            style={{
              display: "inline-flex",
              alignItems: "center",
              justifyContent: "center",
              gap: "8px",
              padding: "12px 28px",
              borderRadius: "var(--radius-md)",
              backgroundColor: "var(--primary)",
              color: "#0c0e12",
              fontSize: "15px",
              fontWeight: "700",
              border: "none",
              cursor: isLoading || (ingredients.length === 0 && !inputValue.trim()) ? "not-allowed" : "pointer",
              opacity: isLoading || (ingredients.length === 0 && !inputValue.trim()) ? 0.6 : 1,
              boxShadow: "0 4px 16px rgba(245, 158, 11, 0.35)",
              transition: "all 0.2s ease"
            }}
          >
            {isLoading ? (
              <>
                <span className="spinner" />
                <span>Mencari Resep...</span>
              </>
            ) : (
              <span>Cari Resep Terbaik</span>
            )}
          </button>
        </div>
      </div>

      {/* Quick Add Suggestions */}
      <div style={{
        display: "flex",
        flexDirection: "column",
        gap: "10px",
        backgroundColor: "rgba(24, 28, 38, 0.4)",
        padding: "16px 20px",
        borderRadius: "var(--radius-md)",
        border: "1px solid var(--border-subtle)"
      }}>
        <span style={{ fontSize: "12px", color: "var(--text-muted)", fontWeight: "600", textTransform: "uppercase" }}>
          Pilihan Cepat Bahan Kulkas:
        </span>
        <div style={{ display: "flex", flexWrap: "wrap", gap: "8px" }}>
          {quickCategories.flatMap((cat) => cat.items).map((item) => {
            const isSelected = ingredients.includes(item.toLowerCase());
            return (
              <button
                key={item}
                type="button"
                id={`quick-add-${item.toLowerCase().replace(/\s+/g, "-")}`}
                onClick={() => handleQuickAdd(item)}
                disabled={isSelected}
                style={{
                  padding: "5px 12px",
                  borderRadius: "var(--radius-full)",
                  fontSize: "13px",
                  fontWeight: "500",
                  backgroundColor: isSelected ? "rgba(16, 185, 129, 0.15)" : "var(--bg-surface-elevated)",
                  color: isSelected ? "var(--match-green)" : "var(--text-secondary)",
                  border: isSelected ? "1px solid var(--match-green-border)" : "1px solid var(--border-subtle)",
                  cursor: isSelected ? "default" : "pointer",
                  transition: "all 0.15s ease"
                }}
              >
                {isSelected ? `✓ ${item}` : `+ ${item}`}
              </button>
            );
          })}
        </div>
      </div>
    </section>
  );
};
