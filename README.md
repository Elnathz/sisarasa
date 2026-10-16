# SisaRasa: Sistem Temu Kembali Informasi Resep Masakan Berbasis Bahan Sisa

[![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Tests](https://img.shields.io/badge/Pytest-9%20Passed-success?logo=pytest&logoColor=white)](backend/tests/)
[![Repository](https://img.shields.io/badge/GitHub-Repository-181717?logo=github&logoColor=white)](https://github.com/Elnathz/sisarasa)
[![Course](https://img.shields.io/badge/Mata%20Kuliah-Sistem%20Temu%20Kembali%20Informasi-orange)](https://github.com/Elnathz/sisarasa)

---

## Identitas Pengembang

- **Nama**: Farros Rifantiarno Ramadhani
- **NIM**: A11.2024.15694
- **Program Studi**: S1 Teknik Informatika
- **Mata Kuliah**: Sistem Temu Kembali Informasi (STKI) - Semester 5
- **Tautan Kaggle**: [https://www.kaggle.com/code/elnathh/sisarasa](https://www.kaggle.com/code/elnathh/sisarasa)

---

## 1. Latar Belakang & Problem Formulation

*Food waste* di tingkat rumah tangga sering kali dipicu oleh ketidakmampuan mengolah sisa bahan makanan di dapur atau kulkas sebelum kedaluwarsa. Kebanyakan mesin pencari resep konvensional berorientasi pada pencarian nama hidangan (misal: "Ayam Goreng Mentega"), bukan berdasarkan bahan mentah yang secara faktual dimiliki pengguna.

**SisaRasa** dirancang sebagai sistem Information Retrieval (IR) cerdas berbasis bahan sisa dengan karakteristik:
1. **Query ($Q$)**: Daftar bahan sisa kulkas fleksibel (misal: `"ayam, wortel, kecap manis"` atau format sehari-hari seperti `"bamer, baput, telor"`).
2. **Dokumen ($D$)**: Korpus 68.747 resep masakan Indonesia bersih.
3. **Culinary NLP Parser**: Menghapus angka, satuan takaran (gram, sdm, sdt, siung), teknik persiapan (potong dadu, iris tipis), menormalisasi sinonim bahasa daerah, dan memisahkan bumbu dasar (*pantry staples* seperti air, garam, minyak) dari bahan inti (*core ingredients*).
4. **SisaRasa Hybrid Ranking**: Memadukan probabilitas leksikal BM25, representasi vektor TF-IDF Cosine, *Core Coverage*, utilitas kueri, Jaccard similarity, penalti bahan belanja yang kurang, dan keselarasan protein utama (*Protein Alignment*).

---

## 2. Dataset & Quality Gate

Korpus dibangun dari penggabungan dua dataset resep masakan Indonesia terbesar:
- **Dataset 1**: `canggih/indonesian-food-recipes` (14.711 resep)
- **Dataset 2**: `junwatu/indonesian-recipes` (66.419 resep)
- **Total Mentah**: **81.130 resep**

### Tahapan Preprocessing & Deduplikasi 2-Tahap:
- **Stage 1 (Exact Deduplication)**: Menghapus resep dengan judul dan bahan identik $\rightarrow$ 69.043 resep.
- **Stage 2 (Near-Duplicate Jaccard Filtering)**: Mengeliminasi resep duplikat dekat dengan threshold Jaccard $\ge 0.85$ $\rightarrow$ **68.747 resep bersih**.

---

## 3. Hasil Evaluasi & Benchmark Model STKI

Evaluasi dilakukan mengikuti standar **TREC Evaluation** pada 48 kueri terstandarisasi yang mencakup 4 skenario riil:
- **Skenario A**: Sisa Kulkas Minimalis (2–3 bahan)
- **Skenario B**: Masak Harian Standar (4–6 bahan)
- **Skenario C**: Kombinasi Bahan Lengkap (7–10 bahan)
- **Skenario D**: Noisy / Colloquial Input (ragam bahasa percakapan sehari-hari)

Sebanyak **3.605 pasangan dokumen-kueri** dinilai relevansinya menggunakan *Qrels Pooling Generator* (Graded Relevance: 0 = Tidak Relevan, 1 = Relevan Parsial, 2 = Relevan Kuat, 3 = Sangat Relevan / Rekomendasi Utama).

### Tabel Performa Komparatif (Overall Benchmark)

| Model | P@5 | R@5 | nDCG@5 | P@10 | R@10 | nDCG@10 | MAP@10 | MRR | Latensi Rata-rata |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Set-Overlap (Jaccard)** | 0.8083 | 0.1681 | 0.8356 | 0.7875 | 0.2883 | 0.8433 | 0.8020 | 0.8880 | **13.9 ms** |
| **TF-IDF Cosine** | 0.6417 | 0.1152 | 0.6162 | 0.5917 | 0.1796 | 0.5974 | 0.5320 | 0.8125 | 71.9 ms |
| **BM25 Okapi** | 0.5292 | 0.0931 | 0.4285 | 0.4854 | 0.1437 | 0.4192 | 0.4367 | 0.6957 | 24.7 ms |
| **SisaRasa Hybrid (Proposed)** | **0.8958** | **0.2036** | **0.8699** | **0.8583** | **0.3210** | **0.8704** | **0.9112** | **0.9444** | 106.5 ms |

> **Kesimpulan STKI**: Model **SisaRasa Hybrid** mengungguli seluruh model baseline di seluruh metrik utama, menghasilkan **MAP@10 = 0.9112** dan **MRR = 0.9444** dengan latensi responsif ~100 ms di atas 68.747 dokumen.

---

## 4. Arsitektur Proyek & Struktur Repositori

```text
sisarasa/
├── backend/                              # Layanan REST API Python (FastAPI)
│   ├── app/
│   │   ├── config.py                     # Konfigurasi path & CORS
│   │   ├── parser.py                     # Indonesian Culinary NLP Engine
│   │   ├── retrievers.py                 # Arsitektur 4 Model Retrieval STKI
│   │   ├── models.py                     # Pydantic Schemas Request & Response
│   │   ├── engine.py                     # Core search engine & Parquet lookup
│   │   └── main.py                       # Endpoint REST API & OpenAPI docs
│   ├── tests/                            # Automated Unit Tests (Pytest)
│   │   ├── test_parser.py                # Pengujian parser NLP kuliner
│   │   └── test_api.py                   # Pengujian endpoint FastAPI
│   ├── requirements.txt                  # Dependensi backend
│   └── run.py                            # Script peluncur server backend
│
├── artifacts/                            # Artefak tersimpan hasil eksekusi pipeline
│   ├── index_sisarasa_hybrid.pkl         # Model retriever terkalibrasi (67.4 MB)
│   ├── sisarasa_corpus_clean.parquet     # Korpus resep bersih (49.8 MB)
│   ├── benchmark_results.csv             # Tabel metrik evaluasi
│   ├── benchmark_queries.json            # 48 kueri evaluasi
│   ├── qrels.json                        # 3.605 ground-truth relevance judgements
│   └── *.png                             # Grafik visualisasi EDA & benchmark
│
├── sisarasa_pipeline.ipynb               # Notebook master pipeline (Cell 1 s.d. 12)
├── .env.example                          # Template konfigurasi environment
├── .gitignore                            # Aturan git bersih
└── README.md                             # Dokumentasi proyek
```

---

## 5. Panduan Instalasi & Menjalankan Sistem

### A. Prasyarat Lingkungan
- Python 3.10 atau lebih baru (direkomendasikan via Conda/Virtualenv).
- Lingkungan conda `sisarasa`:
  ```bash
  conda activate sisarasa
  ```

### B. Menjalankan Backend API (FastAPI)
1. Instal dependensi backend:
   ```bash
   pip install -r backend/requirements.txt
   ```
2. Jalankan server:
   ```bash
   python backend/run.py
   ```
3. Akses Swagger UI dokumentasi API di:  
   **[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)**

### C. Menjalankan Pengujian Otomatis (*Unit Tests*)
Jalankan test suite menggunakan `pytest`:
```bash
pytest backend/tests/ -v
```
*(Seluruh 9 unit test mencakup parser NLP, pemisahan bumbu dasar, metrik stats, kalkulasi bahan cocok/kurang, dan endpoint API).*

### D. Menjalankan Notebook Pipeline STKI
Buka dan jalankan seluruh sel notebook secara sekuensial:
```bash
jupyter lab sisarasa_pipeline.ipynb
```

---

## 6. Lisensi & Hak Cipta

Proyek ini dikembangkan untuk pemenuhan tugas mata kuliah **Sistem Temu Kembali Informasi (STKI)**, Program Studi S1 Teknik Informatika, Fakultas Ilmu Komputer, Universitas Dian Nuswantoro (UDINUS).
