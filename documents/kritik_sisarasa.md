# Kritik Teknis Mendetail: Sistem SisaRasa

> [!CAUTION]
> Ini adalah kritik objektif terhadap blindspot riil dalam metodologi, implementasi, dan deployment proyek. Bukan serangan personal.

---

## 1. BLINDSPOT PALING FATAL: Kebocoran Data dalam Evaluasi (Evaluation Leakage)

Ini masalah terbesar proyek ini dan langsung merusak validitas angka MAP@10 = 0.9112 dan nDCG@10 = 0.8704 yang kamu klaim.

### Buktinya:

Pipeline evaluasi di `notebooks/sisarasa_v3.ipynb` Cell 9 bekerja seperti ini:

```
Model dilatih → Model retrieve kandidat → Skor kandidat → Qrels dihitung dari skor itu → Model dievaluasi dengan Qrels yang sama
```

`QrelGenerator.judge()` menghitung relevansi dengan rumus:
```python
intersection = q_core & d_core
core_coverage = inter_len / (len(d_core) + 1e-9)
query_util = inter_len / (len(q_core) + 1e-9)
```

Dan `SisaRasaHybridRetriever.retrieve()` di `retrievers.py` baris 283-319 menggunakan **formula yang identik secara konseptual**: `core_coverage`, `query_util`, dan `jaccard` yang sama persis.

**Artinya: model meranking dokumen dengan fungsi F(x), dan qrels menilai relevansi dengan fungsi yang secara matematis setara dengan F(x). Model dievaluasi terhadap dirinya sendiri.**

Ini bukan evaluasi independen. Ini circular evaluation. Skor 0.9112 tidak mencerminkan kemampuan retrieval yang sesungguhnya karena model dan judge menggunakan logika yang sama persis.

### Cara Memperbaikinya:
1. **Human judgments**: Kamu atau rekan proyek menilai secara manual 5-10 resep per query — apakah resep tersebut memang enak dimasak dari bahan tersebut.
2. **Held-out evaluator**: Gunakan metrik yang berbeda dari scoring function (misal: user study, atau setidaknya ground truth manual dari Cookpad rating).

---

## 2. Qrels Hanya dari Pooled Candidates, Bukan Full Corpus

Di Cell 9, qrels dibangun dengan cara:

```python
POOL_DEPTH = 30
for model in models.values():
    results = model.retrieve(qtxt, top_k=POOL_DEPTH)
    candidate_pool.update(doc_id for doc_id, _ in results)
```

Hanya 30 dokumen teratas dari setiap model yang masuk ke pool penilaian. Artinya:

- Dokumen yang relevan tapi **tidak diambil oleh model manapun** tidak pernah dinilai (grade default = 0).
- Dalam perhitungan metrik, dokumen yang tidak masuk pool dianggap tidak relevan.
- Recall yang dihitung menjadi sangat optimistis karena "total relevant" hanya dihitung dari pool yang sudah disaring model itu sendiri.

Ini adalah **systematic overestimation of recall** yang umum terjadi dalam TREC pooling, tetapi di sini tidak ada mekanisme koreksinyanya.

---

## 3. Qrels Dibangun Setelah Model di-Index — Bukan Test Set Independen

Urutan eksekusi notebook:
1. Cell 8: Model di-index (`model.index(df_all)`)
2. Cell 9: Qrels dibuat menggunakan **df_all yang sama** dan judgments dari model yang sama
3. Cell 10: Model dievaluasi dengan qrels tersebut

Tidak ada **train-test split** sama sekali. Model melihat seluruh korpus, lalu dievaluasi terhadap pertanyaan yang jawabannya diambil dari korpus yang sama. Ini bukan masalah kecil — ini menjadikan seluruh angka evaluasi tidak dapat dipercaya untuk mengklaim performa di data baru (generalization).

---

## 4. Bobot Hybrid Dibuat Manual, Tidak Ada Tuning Empiris

Di `retrievers.py` baris 212-213:

```python
w1: float = 0.10, w2: float = 0.05, w3: float = 0.20,
w4: float = 0.20, w_jaccard: float = 0.35,
w5: float = 0.10, w_prot: float = 0.25
```

Total bobot = 0.10 + 0.05 + 0.20 + 0.20 + 0.35 - 0.10 + 0.25 = 1.05 (bukan 1.0 karena ada penalti).

Angka-angka ini tidak datang dari grid search, Bayesian optimization, atau bahkan brute-force cross-validation. Terlihat dari notebook bahwa tidak ada Cell yang melakukan hyperparameter search. Ini berarti klaim bahwa model hybrid "lebih baik" dari BM25 murni mungkin benar secara anekdotal, tetapi tidak dapat dijustifikasi secara ilmiah karena tidak ada systematic tuning yang dilakukan terhadap bobot-bobot ini.

---

## 5. SYNONYM_MAP Sangat Terbatas — Cakupan Bumbu Indonesia Sangat Sempit

Di `parser.py`, `SYNONYM_MAP` mencakup variasi umum, tetapi ada celah besar:

- **Variasi ejaan regional tidak ada**: `kunci`, `cekur`, `laos` (nama daerah untuk lengkuas/kencur)
- **Singkatan informal Cookpad tidak lengkap**: `bwg` (bawang), `cm` (cabai merah), `cabe ijo` (cabai hijau) banyak yang belum ada
- **Typo common tidak ditangani sama sekali**: `tempek`, `tahuu`, `ayaam`
- **Nama brand dianggap bahan**: Kecap ABC, Saori, Indofood — parser tidak punya pemetaan brand → kategori bahan generik

Konsekuensinya: query user yang tidak menggunakan ejaan baku langsung menghasilkan skor nol. Untuk sistem yang mengklaim menangani "bahasa informal Cookpad", ini adalah kelemahan struktural.

---

## 6. Protein Alignment Penalty Terlalu Agresif

Di `retrievers.py` baris 306-307:

```python
protein_alignment[protein_inter > 0] = 1.0
protein_alignment[(protein_inter == 0) & self.doc_has_protein] = -0.5
```

Jika user memasukkan query yang **tidak mengandung protein** (misalnya: `"wortel, kentang, tomat, bawang"`), semua resep yang mengandung protein apapun mendapat penalti -0.5 × w_prot = -0.5 × 0.25 = **-0.125** pada skornya.

Ini kontra-intuitif. Jika user tidak menyebutkan protein, ini bisa berarti:
- User memang tidak punya protein (sayur-sayuran saja) → penalti pada resep protein masuk akal
- User lupa atau sengaja tidak menyebut protein → penalti salah sasaran

Tidak ada mekanisme ambiguitas query di sini. Sistem binary: punya protein → reward, tidak punya → semua resep ber-protein kena penalti.

---

## 7. `match_percentage` Salah Secara Konseptual

Di `engine.py` baris 181-182:

```python
denom = max(len(doc_core), 1)
pct = min(100, int(round((len(matched) / denom) * 100)))
```

`match_percentage` dihitung dari **bahan resep yang dimiliki user**, bukan dari **bahan yang diminta resep dibagi bahan yang user punya**.

Contoh ekstrem: User punya 3 bahan: `ayam, bawang, kecap`. Resep mengandung 10 bahan. 3 bahan user ada di resep. `match_percentage = 3/10 = 30%`.

Tetapi dari perspektif user, fakta yang relevan adalah: **"Berapa bahan yang perlu saya beli?"** yaitu 7 dari 10 — artinya resep ini butuh banyak bahan tambahan. Seorang user mungkin lebih memilih resep dengan 4 bahan di mana user sudah punya 3 (75% match) dibandingkan resep dengan 10 bahan di mana user punya 3 (30% match).

Persentase ini ditampilkan di frontend dan bisa menyesatkan user.

---

## 8. Deployment: CORS Dibiarkan `"*"` (Wildcard)

Di `config.py` baris 23:

```python
CORS_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
    "*"
]
```

Baris `"*"` membuat seluruh CORS whitelist di atas tidak berguna. Semua domain dari internet dapat memanggil API ini. Dalam konteks kuliah ini tidak fatal, tetapi ini adalah kebiasaan buruk yang berbahaya jika dibawa ke produksi.

---

## 9. `run.py` Tidak Bisa Dijalankan dari Subdirektori

Di `run.py` baris 13:
```python
uvicorn.run("backend.app.main:app", ...)
```

Modul string `"backend.app.main"` mengasumsikan working directory ada di root proyek. Jika dijalankan dari `backend/`, Python tidak bisa menemukan package `backend`. Kamu sudah mengalami ini sendiri tadi.

Ini sudah ada workaround di baris 6-8 (menambah root ke `sys.path`), tetapi naming convention `"backend.app.main"` tetap hanya berfungsi jika CWD = project root, yang tidak intuitif dan tidak terdokumentasi.

---

## 10. Statistik yang Di-hardcode, Bukan Dihitung Dinamis

Di `engine.py` baris 268-269:

```python
best_map10=0.9112,
best_ndcg10=0.8704
```

Angka ini di-hardcode langsung ke source code, bukan dibaca dari `benchmark_results.csv` yang ada di `artifacts/`. Jika seseorang menjalankan ulang notebook dengan dataset berbeda atau modifikasi model, angka di API tetap menampilkan nilai lama yang stale — sebuah kebohongan teknis yang tersembunyi.

---

## Ringkasan Prioritas

| # | Masalah | Dampak | Sulit? |
|---|---------|--------|--------|
| 1 | Evaluation leakage (qrels = model sendiri) | Kritis — validitas paper hancur | Tinggi |
| 2 | Qrels dari pooled candidates saja | Tinggi — recall overestimated | Sedang |
| 3 | Tidak ada train-test split | Tinggi — generalization tidak teruji | Tinggi |
| 4 | Bobot hybrid tidak di-tune empiris | Sedang — klaim unggul tidak terjustifikasi | Sedang |
| 5 | SYNONYM_MAP terbatas | Sedang — UX buruk untuk input informal | Sedang |
| 6 | Protein penalty agresif | Sedang — false negative untuk query sayuran | Rendah |
| 7 | `match_percentage` konsep salah | Rendah-Sedang — misleading UI | Rendah |
| 8 | CORS wildcard | Rendah (konteks kuliah) | Rendah |
| 9 | `run.py` path-dependent | Rendah — sudah terbukti menyulitkan | Rendah |
| 10 | Statistik di-hardcode | Rendah | Rendah |
