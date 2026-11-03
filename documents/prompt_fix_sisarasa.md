# Prompt Perbaikan Teknis Proyek SisaRasa

## KONTEKS PROYEK

Kamu adalah coding assistant yang bertugas memperbaiki proyek **SisaRasa** — sebuah sistem Information Retrieval (IR) berbasis bahan sisa makanan untuk tugas UTS mata kuliah Sistem Temu Kembali Informasi (STKI) Semester 5, Program S1 Teknik Informatika, Universitas Dian Nuswantoro.

### Struktur proyek (workspace root: `d:\Kuliah\Semester 5\STKI\sisarasa`):

```
sisarasa/
├── backend/app/
│   ├── config.py          # Konfigurasi path dan CORS
│   ├── parser.py          # NLP parser bahan masakan Indonesia (IndonesianIngredientParser)
│   ├── retrievers.py      # 4 model retrieval: SetOverlap, TF-IDF, BM25, SisaRasaHybrid
│   ├── engine.py          # Core search engine, SisaRasaEngine class
│   ├── models.py          # Pydantic schema request/response
│   └── main.py            # FastAPI endpoints
├── notebooks/
│   └── sisarasa_v3.ipynb  # Notebook pipeline utama (Cell 1-12)
├── artifacts/
│   ├── sisarasa_corpus_clean.parquet  # Korpus 68.747 resep bersih
│   ├── index_sisarasa_hybrid.pkl      # Model hybrid terserialisasi
│   ├── benchmark_queries.json         # 48 query evaluasi
│   ├── qrels.json                     # 3.607 relevance judgments
│   └── benchmark_results.csv          # Tabel hasil evaluasi
├── run.py                 # Script launcher backend (bermasalah, lihat issue #9)
└── .env                   # Environment variables
```

### Stack teknologi:
- **Backend**: Python 3.11, FastAPI, uvicorn, pandas, scikit-learn, rank-bm25, pydantic
- **Frontend**: Next.js 16 (TypeScript), React 19
- **Lingkungan**: Miniconda, environment `sisarasa`

---

## DAFTAR ISSUE YANG HARUS DIPERBAIKI

Perbaiki semua issue berikut. Baca setiap file yang relevan secara penuh sebelum mengedit. Konfirmasi setiap perubahan sebelum dieksekusi. Jangan membuat asumsi tentang konten file tanpa membacanya terlebih dahulu.

---

### ISSUE #1 (KRITIS) — Hardcoded Evaluation Stats di `engine.py`

**File**: `d:\Kuliah\Semester 5\STKI\sisarasa\backend\app\engine.py`

**Masalah**:
Di method `get_stats()` (sekitar baris 262-270), nilai MAP dan nDCG di-hardcode langsung ke source code:
```python
best_map10=0.9112,
best_ndcg10=0.8704
```

Jika model diubah atau notebook dijalankan ulang dengan hasil berbeda, nilai ini akan stale (tidak akurat).

**Yang harus dilakukan**:
1. Baca file `d:\Kuliah\Semester 5\STKI\sisarasa\artifacts\benchmark_results.csv` terlebih dahulu untuk memahami strukturnya.
2. Modifikasi method `get_stats()` di `SisaRasaEngine` agar membaca nilai `best_map10` dan `best_ndcg10` secara dinamis dari file `benchmark_results.csv` (yang sudah ada di `BENCHMARK_PATH`).
3. Parsing CSV tersebut di method `initialize()` dan simpan nilainya ke attribute `self.stats`.
4. Fallback ke nilai hardcoded hanya jika file CSV tidak ditemukan atau parsing gagal (dengan log warning).
5. Jangan mengubah signature method `get_stats()` atau `StatsResponse` model.

---

### ISSUE #2 (TINGGI) — CORS Wildcard yang Membatalkan Whitelist

**File**: `d:\Kuliah\Semester 5\STKI\sisarasa\backend\app\config.py`

**Masalah**:
```python
CORS_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
    "*"   # <-- ini membatalkan semua baris di atas
]
```
Baris `"*"` membuat seluruh whitelist tidak berguna karena semua origin diizinkan.

**Yang harus dilakukan**:
1. Hapus baris `"*"` dari daftar `CORS_ORIGINS`.
2. Tambahkan penjelasan komentar singkat di atas list tersebut.
3. Pastikan `allow_origins` di `main.py` tetap menggunakan `CORS_ORIGINS` dari config (sudah benar, jangan diubah).

---

### ISSUE #3 (TINGGI) — `run.py` Path-Dependent dan Tidak Terdokumentasi

**File**: `d:\Kuliah\Semester 5\STKI\sisarasa\backend\run.py`

**Masalah**:
File ini menggunakan string modul `"backend.app.main:app"` yang hanya bekerja jika CWD adalah root proyek (`d:\Kuliah\Semester 5\STKI\sisarasa`). Jika dijalankan dari folder `backend/`, Python tidak menemukan package `backend`. Kamu sudah mengalami error ini secara langsung.

**Yang harus dilakukan**:
1. Baca `run.py` terlebih dahulu.
2. Ganti string `"backend.app.main:app"` dengan `"app.main:app"` supaya bisa dijalankan dari dalam folder `backend/`.
3. Sesuaikan juga `sys.path` manipulation agar menambahkan `backend/` sebagai root, bukan project root.
4. Update komentar di `run.py` untuk menjelaskan bahwa script harus dijalankan dari **dalam folder `backend/`** atau dari root proyek dengan `python backend/run.py`.
5. Verifikasi bahwa `backend/app/__init__.py` ada dan dapat dideteksi sebagai package Python.

---

### ISSUE #4 (SEDANG) — `match_percentage` Konsep Salah dari Perspektif User

**File**: `d:\Kuliah\Semester 5\STKI\sisarasa\backend\app\engine.py`

**Masalah**:
Di method `search()` (sekitar baris 180-182):
```python
denom = max(len(doc_core), 1)
pct = min(100, int(round((len(matched) / denom) * 100)))
```
Ini mengukur "berapa persen bahan resep yang user punya" — bukan pertanyaan yang relevan bagi user.

User sesungguhnya peduli dengan: **"Berapa banyak bahan tambahan yang perlu dibeli?"**.

**Yang harus dilakukan**:
1. Pertahankan kalkulasi `match_percentage` yang ada (jangan ubah) karena nilai ini dipakai untuk ranking dan sudah kompatibel dengan model yang tersimpan di `.pkl`.
2. Tambahkan field baru ke `RecipeCard` di `models.py` dengan nama `shopping_list_count: int` — berisi jumlah bahan yang harus dibeli (yaitu `len(missing_ingredients)`).
3. Di `engine.py` method `search()`, isi field `shopping_list_count` dengan nilai `len(missing)` untuk setiap `RecipeCard` yang dibuat.
4. Lakukan hal yang sama untuk `RecipeDetail` jika relevan.
5. **Jangan ubah** nama field `match_percentage` yang sudah ada karena frontend mungkin sudah menggunakannya.

---

### ISSUE #5 (SEDANG) — Protein Alignment Penalty Terlalu Agresif untuk Query Sayuran

**File**: `d:\Kuliah\Semester 5\STKI\sisarasa\backend\app\retrievers.py`

**Masalah**:
Di method `retrieve()` class `SisaRasaHybridRetriever` (sekitar baris 300-307):
```python
q_proteins = q_core & self.MAIN_PROTEINS
protein_alignment = np.zeros(n)
if q_proteins:
    q_prot_vec = self.protein_vectorizer.transform([list(q_proteins)])
    protein_inter = np.array(self.doc_protein_matrix.dot(q_prot_vec.T).toarray()).flatten()
    protein_alignment[protein_inter > 0] = 1.0
    protein_alignment[(protein_inter == 0) & self.doc_has_protein] = -0.5   # <-- terlalu agresif
```
Jika query tidak mengandung protein (misal: `"wortel, kentang, tomat"`), SEMUA resep yang mengandung protein kena penalti -0.5 × 0.25 = -0.125. Ini tidak fair untuk query sayuran murni.

**Yang harus dilakukan**:
1. Ubah logika penalti protein menjadi lebih konservatif: ganti nilai penalti dari `-0.5` menjadi `-0.2`.
2. Tambahkan kondisi tambahan: penalti hanya diberikan jika query mengandung **setidaknya 2 bahan inti** (q_core_len >= 2) DAN tidak ada protein. Jika query hanya 1 bahan dan itu bukan protein, jangan berikan penalti.
3. Tambahkan komentar penjelasan di atas blok kode tersebut.
4. **Penting**: Perubahan ini hanya pada logika scoring runtime, BUKAN pada model `.pkl` yang tersimpan. Model pkl sudah berisi bobot terlatih. Perubahan ini akan berlaku saat retriever dijalankan ulang.

**Catatan**: Perubahan ini akan membuat model runtime sedikit berbeda dari model pkl yang tersimpan. Ini acceptable karena perubahan yang dilakukan adalah logika post-scoring, bukan parameter model itu sendiri.

---

### ISSUE #6 (SEDANG) — Tambah Synonym untuk Typo Umum dan Bahasa Informal

**File**: `d:\Kuliah\Semester 5\STKI\sisarasa\backend\app\parser.py`

**Masalah**:
`SYNONYM_MAP` tidak mencakup typo umum dan varian nama daerah. Contoh: `"tempek"` tidak dipetakan ke `"tempe"`, `"kunci"` (nama lokal) tidak dipetakan ke `"kencur"`, `"laos"` tidak dipetakan ke `"lengkuas"`.

**Yang harus dilakukan**:
1. Baca seluruh `SYNONYM_MAP` yang ada di `parser.py` terlebih dahulu untuk memahami pola dan format yang digunakan.
2. Tambahkan entri baru ke `SYNONYM_MAP` untuk kategori berikut (letakkan di bagian yang sesuai secara tematik):

   **Typo protein umum**:
   - `"tempek"` → `"tempe"`
   - `"tahuu"` → `"tahu"`
   - `"ayaam"` → `"ayam"`
   - `"telor"` sudah ada, verifikasi saja
   - `"daging"` → `"daging sapi"` (jika berdiri sendiri tanpa kata lain)

   **Nama daerah rempah**:
   - `"laos"` → `"lengkuas"`
   - `"loas"` → `"lengkuas"`
   - `"kunci"` → `"kencur"` (hati-hati: pastikan tidak menimpa kata 'kunci' dalam konteks lain — gunakan protected mapping)
   - `"cekur"` → `"kencur"`
   - `"serei"` → `"serai"`
   - `"sereh"` → `"serai"`

   **Singkatan / informal tambahan**:
   - `"cabe ijo"` → `"cabai hijau"`
   - `"cabe hijau"` → `"cabai hijau"`
   - `"bwng"` → `"bawang"`
   - `"bwng merah"` → `"bawang merah"`
   - `"bwng putih"` → `"bawang putih"`

3. Jangan mengubah entri yang sudah ada.
4. Pastikan urutan kunci di dict tetap dari yang terpanjang ke terpendek (karena pattern matching menggunakan `sorted(..., key=len, reverse=True)` — tambahkan di posisi yang logis berdasarkan panjang string).

---

### ISSUE #7 (RINGAN) — Tambah Health Check Info ke `/health` Endpoint

**File**: `d:\Kuliah\Semester 5\STKI\sisarasa\backend\app\main.py`

**Masalah**:
Endpoint `/health` saat ini hanya mengembalikan status boolean yang sangat minimal:
```python
{"status": "healthy", "corpus_loaded": True, "total_recipes": 68747}
```
Tidak ada informasi versi, waktu startup, atau detail model.

**Yang harus dilakukan**:
1. Baca `main.py` dan `engine.py` terlebih dahulu.
2. Tambahkan field berikut ke response `/health`:
   - `"model_name"`: nama model yang aktif (ambil dari `engine.retriever.name` jika ada)
   - `"total_indexed_docs"`: jumlah dokumen yang terindeks (ambil dari `len(engine.retriever.doc_ids)` jika engine ready)
3. Gunakan try-except saat mengakses `engine.retriever` karena mungkin `None` saat startup.
4. Tetap backward-compatible — jangan hapus field yang sudah ada.

---

## INSTRUKSI EKSEKUSI UMUM

1. **Baca file lengkap sebelum mengedit**. Jangan berasumsi tentang konten file berdasarkan nama saja.
2. **Konfirmasi perubahan sebelum eksekusi** — tampilkan diff atau ringkasan perubahan yang akan dilakukan, tunggu konfirmasi sebelum menyimpan.
3. **Tangani satu issue per satu** secara berurutan dari #1 sampai #8.
4. **Jangan ubah** hal-hal berikut kecuali memang diminta dalam issue:
   - Logika scoring utama di `SisaRasaHybridRetriever`
   - Struktur `SearchResponse` dan `RecipeCard` (kecuali penambahan field di Issue #4)
   - File model `.pkl` di folder `artifacts/`
   - Frontend (folder `frontend/`)
5. **Setelah semua fix**, jalankan unit test untuk memverifikasi tidak ada yang rusak:
   ```powershell
   cd "d:\Kuliah\Semester 5\STKI\sisarasa\backend"
   conda activate sisarasa
   pytest tests/ -v
   ```
6. Laporkan ringkasan semua perubahan yang dilakukan beserta file mana saja yang diedit.

---

## ISSUE #8 (KRITIS) — Tokenisasi Query Salah di Notebook `sisarasa_v3.ipynb` Cell 5

**File**: `d:\Kuliah\Semester 5\STKI\sisarasa\notebooks\sisarasa_v3.ipynb`

**Latar Belakang — Root Cause Bug "bawang goreng"**:

Di notebook, Cell 5 berisi class `IndonesianIngredientParser` yang identik dengan `backend/app/parser.py`. Fungsi `extract_ingredients_from_recipe()` saat ini **digunakan sekaligus untuk dua keperluan yang berbeda** — indexing dokumen dan parsing query — padahal keduanya memerlukan strategi tokenisasi yang berbeda.

Saat indexing dokumen, bahan `"bawang goreng"` dipecah menjadi token: `["bawang_goreng", "bawang", "goreng"]`. Ini benar untuk dokumen agar terjadi partial match.

Namun saat query `"bawang"` dimasukkan oleh user, fungsi yang sama menghasilkan token `"bawang"`. BM25 dan TF-IDF lalu mencocokkan token `"bawang"` ini dengan SEMUA resep yang mengandung bahan apapun yang mengandung kata "bawang" — termasuk `"bawang goreng"` (yang punya sub-token `bawang`). Karena `"bawang goreng"` adalah garnish yang hadir di ribuan resep Indonesia, resep-resep tersebut mendapat skor tinggi secara tidak wajar.

**Solusi yang sudah diterapkan di `backend/app/parser.py`**:

Telah ditambahkan method `_build_query_ir_tokens()` dan diupdate `parse_query()` di `backend/app/parser.py`. Perubahan yang sama harus diterapkan ke Cell 5 di notebook agar konsisten.

**Yang harus dilakukan**:

1. Baca Cell 5 notebook terlebih dahulu (notebook adalah file JSON — cell source ada di field `"source"` dalam array `"cells"`). Jangan mengedit notebook secara langsung dengan text editor; gunakan tool yang memahami format JSONL notebook atau baca JSON-nya terlebih dahulu.

2. Di dalam Cell 5, setelah method `extract_ingredients_from_recipe()` dan sebelum method `parse_query()`, tambahkan method baru berikut ke class `IndonesianIngredientParser`:

```python
def _build_query_ir_tokens(self, all_ingredients: set) -> str:
    """
    Membangun token IR khusus QUERY — berbeda dari indexing dokumen.

    QUERY tidak mendekomposisi compound word agar menghindari false positive:
      - Dokumen: "bawang goreng" → ["bawang_goreng", "bawang", "goreng"]
      - Query:   "bawang"        → ["bawang"] saja (tidak pernah cocok dengan "goreng")
      - Query:   "bawang merah"  → ["bawang_merah"] saja (tidak dipecah jadi "bawang")

    Dengan cara ini, query "bawang" HANYA cocok dengan resep yang memiliki bahan
    "bawang" secara eksplisit — bukan resep "bawang goreng" atau "bawang merah".
    """
    query_ir_tokens = set()
    for ingr in all_ingredients:
        words = ingr.split()
        if len(words) > 1:
            # Hanya tambahkan bentuk compound (underscore), TIDAK pecah
            query_ir_tokens.add("_".join(words))  # e.g., bawang_merah
        else:
            query_ir_tokens.add(ingr)  # e.g., bawang, tempe, ayam
    return " ".join(sorted(query_ir_tokens))
```

3. Di dalam Cell 5, **ganti** method `parse_query()` yang ada:

```python
# SEBELUM (hapus ini):
def parse_query(self, query_string: str) -> Dict[str, Any]:
    """Parse query masukan pengguna (dipisahkan koma atau baris baru)."""
    parts = re.split(r'[,\n]+', query_string)
    lines = [p.strip() for p in parts if p.strip()]
    return self.extract_ingredients_from_recipe(lines)
```

Ganti dengan:

```python
# SESUDAH (ganti dengan ini):
def parse_query(self, query_string: str) -> Dict[str, Any]:
    """
    Parse query masukan pengguna (dipisahkan koma atau baris baru).

    Output dict mengandung dua representasi IR:
    - 'ingredients_ir_text': representasi dokumen (dengan dekomposisi compound) — untuk
      backward-compatibility dengan model yang sudah di-index.
    - 'ingredients_query_ir_text': representasi query (TANPA dekomposisi compound) — digunakan
      oleh retriever saat query-time untuk menghindari false positive sub-token.
    """
    parts = re.split(r'[,\n]+', query_string)
    lines = [p.strip() for p in parts if p.strip()]
    result = self.extract_ingredients_from_recipe(lines)
    # Tambahkan representasi query yang lebih presisi (tidak mendekomposisi compound)
    result["ingredients_query_ir_text"] = self._build_query_ir_tokens(
        result["ingredients_all_set"]
    )
    return result
```

4. Di dalam Cell 8 (build model), cari semua baris yang mengakses `q_parsed["ingredients_ir_text"]` di dalam method `retrieve()` dan `get_scores_array()` pada class `TfidfCosineRetriever` dan `BM25Retriever`. Ganti semua kemunculannya dengan:
```python
q_ir_text = q_parsed.get("ingredients_query_ir_text") or q_parsed["ingredients_ir_text"]
```

5. Jangan mengubah Cell 1-4, Cell 9-12.

6. Setelah selesai mengedit notebook, **jalankan ulang seluruh notebook dari Cell 1 sampai Cell 12** secara berurutan untuk:
   - Regenerate model pkl (`index_sisarasa_hybrid.pkl`, dll.) dengan parser yang sudah diperbaiki
   - Regenerate `benchmark_results.csv` dengan metrik evaluasi terbaru
   - Regenerate `qrels.json`

   Perintah menjalankan notebook dari command line:
   ```powershell
   conda activate sisarasa
   cd "d:\Kuliah\Semester 5\STKI\sisarasa"
   jupyter nbconvert --to notebook --execute notebooks/sisarasa_v3.ipynb --output notebooks/sisarasa_v3.ipynb --ExecutePreprocessor.timeout=3600
   ```

7. Setelah notebook selesai, restart server backend agar memuat model pkl yang baru:
   ```powershell
   # Hentikan server yang sedang berjalan (Ctrl+C di terminal backend)
   # Lalu jalankan ulang dari folder backend:
   cd "d:\Kuliah\Semester 5\STKI\sisarasa\backend"
   conda activate sisarasa
   python run.py
   ```

**Acceptance criteria**:
- Query `"bawang"` di web tidak lagi menampilkan resep "bawang goreng" sebagai hasil utama
- Query `"bawang merah"` menampilkan resep yang mengandung bawang merah sebagai bahan utama
- Query `"tempe, bawang, kecap manis"` menghasilkan `query_ir_text = "bawang kecap_manis tempe"` (bukan `"bawang kecap kecap_manis manis tempe"`)
