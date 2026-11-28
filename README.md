# SisaRasa

**Temukan resep Indonesia dari bahan yang sudah kamu punya.**

SisaRasa adalah sistem pencarian resep berbasis bahan. Pengguna menulis bahan yang tersedia di dapur, lalu SisaRasa menampilkan resep berperingkat beserta bahan yang sudah cocok dan bahan inti yang masih perlu disiapkan.

Repo ini berisi dua sisi SisaRasa:

| Branch | Isi |
|---|---|
| `main` (branch ini) | Riset STKI: notebook, data, dan hasil evaluasi |
| [`deployment`](https://github.com/Elnathz/sisarasa/tree/deployment) | Aplikasi web: backend FastAPI dan frontend Next.js |

## Masalah

Pencarian resep pada umumnya dimulai dari nama masakan. Padahal pertanyaan yang sering muncul di dapur justru kebalikannya: "bahan yang ada ini bisa dimasak jadi apa?"

Akibatnya pengguna harus:

1. Menebak nama menu lebih dulu.
2. Membuka resep satu per satu.
3. Mencocokkan daftar bahannya secara manual dengan isi dapur.
4. Mengulang dari awal jika bahan utamanya ternyata tidak ada.

Proses ini melelahkan, dan bahan yang masih layak pakai bisa terlewat karena tidak terpikir cara mengolahnya. Ada juga kendala bahasa. Orang menulis `bamer`, `baput`, atau `cabe rawit`, dan sering salah ketik, sementara resep di internet ditulis dengan takaran, merek, dan catatan persiapan yang tidak seragam.

## Yang diselesaikan SisaRasa

| Kebutuhan | Cara SisaRasa |
|---|---|
| Mulai dari bahan, bukan nama menu | Query berupa daftar bahan; setiap resep diperlakukan sebagai dokumen yang diperingkat |
| Tahu seberapa cocok sebuah resep | Persentase cakupan bahan inti resep yang sudah dimiliki |
| Tahu apa yang kurang | Daftar bahan cocok dan bahan inti yang perlu dibeli, dipisah dari bumbu dapur umum |
| Menulis bahan dengan bahasa sehari-hari | Normalisasi sinonim dan singkatan (`bamer` menjadi bawang merah, `baput` menjadi bawang putih) |
| Salah ketik | Saran ejaan dari kamus bahan (`minyk` menjadi minyak goreng, `thau` menjadi tahu); input tidak diganti tanpa pilihan pengguna |
| Resep internet yang berantakan | Parser membuang takaran, satuan, merek, dan catatan persiapan, lalu membedakan bahan majemuk (`bawang goreng` tidak sama dengan `bawang merah`) |

Contoh: dengan query `ayam, bawang merah, bawang putih, kecap manis, cabai rawit`, SisaRasa menampilkan resep seperti Ayam Kecap beserta persentase kecocokan, bahan yang sudah ada, bahan yang perlu dibeli, komposisi asli, dan langkah memasak.

## Untuk siapa

| Pengguna | Kebutuhan |
|---|---|
| Mahasiswa atau pekerja yang tinggal di kos | Mencari ide masakan dari persediaan bahan yang terbatas |
| Pekerja yang bingung menentukan menu setelah beraktivitas | Titik awal pencarian tanpa harus memikirkan nama menu |
| Pengelola dapur rumah tangga | Membandingkan beberapa resep dan bahan tambahan yang dibutuhkan |
| Orang yang ingin memanfaatkan isi kulkas | Memasukkan bahan yang masih layak pakai ke dalam pilihan menu |

Pengurangan limbah makanan adalah motivasi, bukan hasil yang sudah diukur. Riset ini belum menguji dampak SisaRasa terhadap limbah makanan atau kepuasan pengguna.

## Posisi terhadap solusi lain

Chhipa dkk. memakai TF-IDF dan cosine pada bahan resep [1], sedangkan BEIR membandingkan BM25 dengan model lain pada benchmark temu kembali [2]. Anotasi frasa bahan [3] dan pengujian per jenis typo [4] menjadi acuan audit parser dan pencarian. SisaRasa menerapkan metode tersebut pada kueri bahan bahasa Indonesia.

SisaRasa mengambil jalur yang bisa dijelaskan dan tidak butuh pelatihan:

1. Normalisasi bahan bahasa Indonesia termasuk sebutan sehari-hari, dengan token bahan komposit.
2. Perbandingan empat model retrieval pada korpus, query, dan penilaian relevansi yang sama.
3. Saran ejaan dari kamus bahan yang dibatasi ketersediaan di korpus, tanpa query log.

Klaim ini dibatasi pada literatur yang ditelaah, bukan klaim sebagai yang pertama. Tabel studi terdahulu lengkap ada di notebook.

## Cara kerja

1. **Data:** dua dataset resep Indonesia digabung, disaring, dan dideduplikasi.
2. **Parser bahan:** setiap baris bahan dinormalkan menjadi nama kanonik. Bahan pokok dapur (garam, air, minyak) dipisahkan dari bahan inti.
3. **Retrieval:** empat model diindeks dan dibandingkan.

| Model | Ide |
|---|---|
| Set-Overlap | Kemiripan Jaccard antara himpunan bahan inti query dan resep |
| TF-IDF Cosine | Bobot bahan berdasarkan kelangkaan, ditambah kanal judul |
| BM25 | Model probabilistik klasik pada token bahan [2] |
| SisaRasa Hybrid | Gabungan BM25, TF-IDF, cakupan bahan, pemakaian bahan pengguna, Jaccard, penalti bahan kurang, dan kecocokan protein |

## Riset

Riset berada di [notebooks/sisarasa_v4.ipynb](notebooks/sisarasa_v4.ipynb). Notebook v1 sampai v3 disimpan sebagai riwayat.

| | Pertanyaan | Ukuran utama |
|---|---|---|
| RQ1 | Bagaimana SisaRasa Hybrid dibanding Set-Overlap, TF-IDF Cosine, dan BM25? | nDCG@10, MAP@10, P@5, menang/seri/kalah per query, interval bootstrap 95% |
| RQ2 | Apa pengaruh komponen kecocokan protein dan penalti bahan kurang? | Perubahan metrik saat satu bobot dinolkan (ablation) |
| RQ3 | Seberapa baik saran bahan menangani salah eja? | Kandidat benar ditawarkan, saran keliru pada input valid |

Evaluasi memakai penilaian relevansi otomatis berbasis aturan bahan (pseudo-qrels `proxy_v3`), pemulihan resep sumber, ablation, uji sensitivitas rubric, interval bootstrap, dan diagnostik ejaan. Ambang keberhasilan ditetapkan di `CONFIRMATION_PROTOCOL` sebelum set konfirmasi dibangkitkan, lalu set itu dijalankan satu kali dengan seed dan keluarga query baru.

Hasil protokol `sisarasa_v4_research_2` belum tersedia karena notebook versi ini belum dijalankan pada korpus penuh. Run lama di `artifacts/evaluation_runs/` berasal dari protokol sebelumnya dan korpus sebelum quality gate pasca-parsing, jadi angkanya tidak bisa dibandingkan langsung.

### Batasan

- Relevansi dinilai oleh rubric otomatis berbasis irisan bahan, bukan oleh manusia. Rubric dan Hybrid berbagi sinyal yang sama.
- Query evaluasi dibangkitkan dari korpus dan tidak mewakili semua kosakata pengguna.
- Split dev dan test sudah diperiksa saat analisis, sehingga bersifat eksploratif. Set konfirmasi mengurangi masalah ini, tetapi tetap dinilai dengan pseudo-qrels.
- Kepuasan pengguna, pengurangan limbah makanan, gizi, dan alergi tidak diukur.

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

Jalankan dari kernel baru dengan Restart Kernel and Run All. Set konfirmasi hanya sah jika dijalankan satu kali tanpa mengubah parser, bobot, rubric, ambang, atau seed setelah hasilnya terlihat.

Efek samping: Cell 1 memasang paket yang belum ada, notebook membaca `.env`, dapat mengunduh dataset, dan menulis run baru ke `artifacts/evaluation_runs/`. Run lama tidak ditimpa.

Contoh setelah seluruh sel selesai:

```python
search_sisarasa("ayam, bawang putih, kecap manis", top_k=5, model_name="hybrid")
PARSER.suggest_query("minyk, thu, susi")
```

Setiap run tersimpan di `artifacts/evaluation_runs/<run-id>/` dengan subfolder `proxy/`, `known_item/`, `research/`, `spelling/`, dan `confirmation/`. File `_SUCCESS` menandakan ekspor selesai, dan `metadata.json` mencatat versi normalisasi, rubric, protokol riset, serta hash korpus dan query.

Aplikasi web ada di branch `deployment`. Perubahan riset di `main` tidak otomatis masuk ke sana; branch itu perlu di-merge dari `main` bila aplikasinya ingin mengikuti versi riset terbaru.

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

## Referensi

Rujukan aktif memakai sumber primer terbit 2021?2025. Daftar untuk impor tersedia di [RIS rujukan primer](Paper/Referensi%20primer%20SisaRasa.ris).

1. Chhipa, S., Berwal, V., Hirapure, T., & Banerjee, S. (2022). Recipe Recommendation System Using TF-IDF. *ITM Web of Conferences, 44, 02006*. [Teks sumber](https://pdfs.semanticscholar.org/0147/673758991cd5f458bd379bb9615b056f6f8d.pdf). DOI 10.1051/itmconf/20224402006.
2. Thakur, N., Reimers, N., R?ckl?, A., Srivastava, A., & Gurevych, I. (2021). BEIR: A Heterogeneous Benchmark for Zero-shot Evaluation of Information Retrieval Models. *NeurIPS Datasets and Benchmarks*. [Teks sumber](https://datasets-benchmarks-proceedings.neurips.cc/paper_files/paper/2021/hash/65b9eea6e1cc6bb9f0cd2a47751a186f-Abstract-round2.html).
3. Goel, M., Agarwal, A., Agrawal, S., Kapuriya, J., Konam, A. V., Gupta, R., Rastogi, S., Niharika, & Bagler, G. (2024). Deep Learning Based Named Entity Recognition Models for Recipes. *LREC-COLING 2024, 4542?4554*. [Teks sumber](https://aclanthology.org/2024.lrec-main.406/).
4. Kakkar, V., Sharma, C., Pande, M., & Kumar, S. (2023). Search Query Spell Correction with Weak Supervision in E-commerce. *ACL 2023, Industry Track, 687?694*. [Teks sumber](https://aclanthology.org/2023.acl-industry.66/). DOI 10.18653/v1/2023.acl-industry.66.
5. Craswell, N., Mitra, B., Yilmaz, E., Campos, D., & Lin, J. (2022). Overview of the TREC 2021 Deep Learning Track. *TREC 2021 Proceedings, NIST SP 500-335*. [Teks sumber](https://trec.nist.gov/pubs/trec30/papers/Overview-DL.pdf). DOI 10.6028/NIST.SP.500-335.deep-overview.
6. Ortiz, K. J. P., Bautista, P. N. P., Dimailig, M. V. D., & Llamzon, A. C. D. (2023). Recipe Recommendation System Using IoT-Based Food Inventory Management of Perishables for Household Food Waste Reduction. *Chemical Engineering Transactions, 106, 361?366*. [Teks sumber](https://www.cetjournal.it/cet/23/106/061.pdf). DOI 10.3303/CET23106061.
7. Ashraf, M. M., & Maduranga, M. W. P. (2025). Ingredient-Only Recipe Recommendation via Self-Supervised Contrastive Learning for Sustainable Cooking. *Journal of Future Artificial Intelligence and Technologies, 2(2), 215?226*. [Teks sumber](https://faith.futuretechsci.org/index.php/FAITH/article/view/98). DOI 10.62411/faith.3048-3719-98.

## Pengembang

Farros Rifantiarno Ramadhani (A11.2024.15694), S1 Teknik Informatika, Universitas Dian Nuswantoro. UTS mata kuliah Sistem Temu Kembali Informasi.
