# SisaRasa: Riset Temu Kembali Resep Berbasis Bahan

SisaRasa adalah studi Sistem Temu Kembali Informasi (STKI) untuk mencari resep masakan Indonesia dari bahan yang dimiliki pengguna. Satu resep adalah satu dokumen, dan daftar bahan pengguna adalah query. Sistem mengembalikan resep berperingkat beserta bahan yang cocok dan bahan inti yang masih kurang.

Branch `main` berisi riset: notebook, data, dan hasil evaluasi. Aplikasi web (backend FastAPI dan frontend Next.js) ada di branch [`deployment`](https://github.com/Elnathz/sisarasa/tree/deployment). Perubahan riset di `main` tidak otomatis masuk ke `deployment`; branch itu perlu di-merge dari `main` bila aplikasinya ingin mengikuti versi riset terbaru.

## Pertanyaan penelitian

| | Pertanyaan | Ukuran utama |
|---|---|---|
| RQ1 | Bagaimana SisaRasa Hybrid dibanding Set-Overlap, TF-IDF Cosine, dan BM25? | nDCG@10, MAP@10, P@5, menang/seri/kalah per query, interval bootstrap 95% |
| RQ2 | Apa pengaruh komponen kecocokan protein dan penalti bahan kurang? | Perubahan metrik saat satu bobot dinolkan (ablation) |
| RQ3 | Seberapa baik saran bahan menangani salah eja? | Kandidat benar ditawarkan, saran keliru pada input valid |

Ambang keberhasilan RQ1 sampai RQ3 ditetapkan di `CONFIRMATION_PROTOCOL` sebelum set konfirmasi dibangkitkan. Rinciannya ada di sel pembuka notebook.

## Notebook

Notebook utama: [notebooks/sisarasa_v4.ipynb](notebooks/sisarasa_v4.ipynb). Notebook v1 sampai v3 disimpan sebagai riwayat.

Alur v4:

1. Memuat dua dataset resep dari berkas lokal.
2. Menyatukan skema, menyaring resep tidak lengkap, dan menghapus duplikat dua tahap.
3. Menormalkan bahan bahasa Indonesia ke token komposit, lalu membuang resep yang tidak menghasilkan bahan kanonik.
4. Membangun indeks Set-Overlap, TF-IDF Cosine, BM25, dan SisaRasa Hybrid.
5. Mengevaluasi dengan pseudo-qrels `proxy_v3` dan pemulihan resep sumber.
6. Menjalankan ablation, sensitivitas rubric, interval bootstrap, latensi, dan diagnostik ejaan.
7. Menjalankan set konfirmasi dengan seed dan keluarga query baru.
8. Mengekspor seluruh hasil ke direktori run baru.

## Data

| Sumber | Isi | Lisensi menurut metadata sumber |
|---|---|---|
| [canggih/indonesian-food-recipes](https://www.kaggle.com/datasets/canggih/indonesian-food-recipes) (Kaggle) | Resep per kategori bahan utama | CC0: Public Domain; data diambil dari Cookpad pada 23 Februari 2018 |
| [junwatu/indonesian-recipes](https://huggingface.co/datasets/junwatu/indonesian-recipes) (Hugging Face) | Judul, bahan, dan langkah memasak | `other` (research-use-as-is); dataset bersifat gated |

Label CC0 dari pengunggah tidak otomatis menyelesaikan hak cipta resep asli. Pemakaian di repo ini terbatas pada riset dan tugas kuliah.

Data mentah tidak disimpan di Git. Letakkan berkasnya di:

```text
data/raw/indonesian-food-recipes/dataset-*.csv
data/raw/indonesian-recipes/indonesian_recipes.parquet
```

Jika berkas Hugging Face belum ada, loader membutuhkan `HF_TOKEN` dari akun yang sudah menyetujui syarat dataset. Salin `.env.example` menjadi `.env`, lalu isi tokennya. Jangan commit `.env`.

## Menjalankan notebook

Butuh Python 3.10 atau lebih baru.

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1          # Windows PowerShell
# source .venv/bin/activate         # macOS/Linux
python -m pip install pandas numpy matplotlib seaborn tqdm scikit-learn rank_bm25 pyarrow datasets kagglehub python-dotenv ipywidgets jupyterlab
jupyter lab notebooks/sisarasa_v4.ipynb
```

Jalankan dari kernel baru dengan Restart Kernel and Run All. Set konfirmasi hanya sah jika dijalankan satu kali tanpa mengubah parser, bobot, rubric, ambang, atau seed setelah hasilnya terlihat. Commit notebook sebelum menjalankannya agar ambang tercatat lebih dahulu daripada hasil.

Efek samping notebook: Cell 1 memasang paket yang belum ada, notebook membaca `.env`, dapat mengunduh dataset, dan menulis run baru ke `artifacts/evaluation_runs/`. Run lama tidak ditimpa.

Contoh pencarian setelah seluruh sel selesai:

```python
search_sisarasa("ayam, bawang putih, kecap manis", top_k=5, model_name="hybrid")
PARSER.suggest_query("minyk, thu, susi")
```

## Hasil evaluasi

Setiap run tersimpan di `artifacts/evaluation_runs/<run-id>/`. File `_SUCCESS` menandakan ekspor selesai, dan `metadata.json` mencatat versi normalisasi, rubric, protokol riset, serta hash korpus dan query.

| Folder | Isi |
|---|---|
| `proxy/` | Query, split, qrels, dan metrik per query untuk dev dan test |
| `known_item/` | Pemulihan resep sumber (Hit@k, MRR@10) |
| `research/` | Ablation, sensitivitas rubric, bootstrap, latensi, resep yang dibuang quality gate |
| `spelling/` | 36 kasus diagnostik ejaan |
| `confirmation/` | Protokol, query, hasil, dan tabel kriteria set konfirmasi |

Run sebelum protokol `sisarasa_v4_research_2` tidak memiliki folder `confirmation/`, dan angkanya berasal dari korpus sebelum quality gate pasca-parsing. Pakai angka dari run terbaru yang sesuai dengan versi notebook.

## Batasan

- Relevansi dinilai oleh rubric otomatis berbasis irisan bahan, bukan oleh manusia. Rubric dan Hybrid berbagi sinyal yang sama.
- Query evaluasi dibangkitkan dari korpus dan tidak mewakili semua kosakata pengguna.
- Split dev dan test sudah diperiksa saat analisis, sehingga bersifat eksploratif. Set konfirmasi mengurangi masalah ini, tetapi tetap dinilai dengan pseudo-qrels.
- Kepuasan pengguna, pengurangan limbah makanan, gizi, dan alergi tidak diukur.

## Struktur

```text
sisarasa/
├── notebooks/           # sisarasa_v4.ipynb (utama) dan versi sebelumnya
├── artifacts/           # Hasil benchmark lama dan evaluation_runs/
├── data/raw/            # Data mentah lokal, tidak di-commit
├── documents/           # Catatan audit dan perbaikan
├── Paper/               # Ekspor pencarian literatur (Elicit, Consensus)
├── Template_Ide_Produk_dan_Rancangan_Penelitian.pdf
└── .env.example
```

## Pengembang

Farros Rifantiarno Ramadhani (A11.2024.15694), S1 Teknik Informatika, Universitas Dian Nuswantoro. UTS mata kuliah Sistem Temu Kembali Informasi.
