import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "SisaRasa - Sistem Temu Kembali Resep Bahan Sisa Kulkas",
  description: "Cari resep masakan Indonesia lezat berbasis bahan mentah yang tersisa di kulkas Anda. Ditenagai sistem temu kembali informasi (IR) Hybrid BM25, TF-IDF, dan Culinary NLP.",
  keywords: ["resep masakan", "bahan sisa", "resep kulkas", "STKI", "information retrieval", "masakan indonesia"],
  authors: [{ name: "Farros Rifantiarno Ramadhani" }],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="id">
      <body>
        <div className="bg-ambient-glow" />
        {children}
      </body>
    </html>
  );
}
