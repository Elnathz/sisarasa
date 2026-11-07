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

Rekomendasi resep dari bahan yang tersedia sudah pernah dibangun, termasuk untuk resep Indonesia [3]. Pendekatan yang ada umumnya memakai content-based filtering atau TF-IDF dengan satu model [3], [4], embedding dan deep learning yang perlu pelatihan [5], [6], atau pengenalan bahan dari gambar yang hasilnya dicari lewat API eksternal [11]. Normalisasi bahan diakui sebagai masalah sulit [7], [8], dan koreksi ejaan query yang kuat biasanya membutuhkan query log [9] atau model besar [18].

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

DOI diperiksa ke Crossref, DataCite, atau OpenAlex pada 7 November 2026. Ringkasan studi terdahulu berasal dari abstrak.

**Teori dan metode**

1. Manning, C. D., Raghavan, P., & Schütze, H. (2008). *Introduction to information retrieval*. Cambridge University Press. https://nlp.stanford.edu/IR-book/
2. Robertson, S., & Zaragoza, H. (2009). The probabilistic relevance framework: BM25 and beyond. *Foundations and Trends in Information Retrieval*, 3(4), 333–389. https://doi.org/10.1561/1500000019

**Studi terdahulu utama**

3. Syaifudin, Y. W., Fatmawati, T., Ardyningrum, N. A., Siradjuddin, I., Puspitasari, D., & Astiningrum, M. (2023). An implementation of recipe recommendation system based on ingredients availability using content-based and collaborative filtering. *2023 International Conference on Converging Technology in Electrical and Information Engineering (ICCTEIE)*, 96–101. https://doi.org/10.1109/ICCTEIE60099.2023.10366631
4. Chhipa, S., Berwal, V., Hirapure, T., & Banerjee, S. (2022). Recipe recommendation system using TF-IDF. *ITM Web of Conferences*, 44, 02006. https://doi.org/10.1051/itmconf/20224402006
5. Ashraf, M. M., & Maduranga, M. W. P. (2025). Ingredient-only recipe recommendation via self-supervised contrastive learning for sustainable cooking. *Journal of Future Artificial Intelligence and Technologies*, 2(2), 215–226. https://doi.org/10.62411/faith.3048-3719-98
6. Abhishek H B, Mallya, P. R., Hiremath, P. C., Ganguli, S., Pradeep, S. N., & Kannadaguli, P. (2025). AI-recipe recommendation system. *2025 International Conference on Advances in Next-Gen Computer Science (ICANCS)*, 1–6. https://doi.org/10.1109/ICANCS65819.2025.11376688
7. Twomey, N., Fain, M., Ponikar, A., & Sarraf, N. (2020). Towards multi-language recipe personalisation and recommendation. *Proceedings of the 14th ACM Conference on Recommender Systems*, 708–713. https://doi.org/10.1145/3383313.3418478
8. Harashima, J., Hiramatsu, M., & Sanjo, S. (2020). Calorie estimation in a real-world recipe service. *Proceedings of the AAAI Conference on Artificial Intelligence*, 34(08), 13306–13313. https://doi.org/10.1609/aaai.v34i08.7041
9. Li, M., Zhang, Y., Zhu, M., & Zhou, M. (2006). Exploring distributional similarity based models for query spelling correction. *Proceedings of COLING/ACL 2006*, 1025–1032. https://doi.org/10.3115/1220175.1220304
10. Singh, S. K. (2026). Spelling correction in healthcare query-answer systems: Methods, retrieval impact, and empirical evaluation. *arXiv* (praprint). https://doi.org/10.48550/arxiv.2603.19249
11. Rodrigues, M. S., Fidalgo, F., & Oliveira, Â. (2023). RecipeIS—Recipe recommendation system based on recognition of food ingredients. *Applied Sciences*, 13(13), 7880. https://doi.org/10.3390/app13137880
12. Chow, Y., Haw, S., Naveen, P., Anaam, E., & Mahdin, H. B. (2023). Food recommender system: A review on techniques, datasets and evaluation metrics. *Journal of System and Management Sciences*, 13(5). https://doi.org/10.33168/jsms.2023.0510

**Studi pendukung**

13. Bithel, S., & Malagi, S. S. (2021). Unsupervised identification of relevant prior cases. *arXiv* (praprint). https://doi.org/10.48550/arxiv.2107.08973
14. Ghimire, S. (2026). A hybrid search engine combining classical information retrieval with pluggable semantic search. *Proceedings of the International Conference on Innovation in Computing, Science, Engineering and Technology*, 3(1). https://doi.org/10.65091/icicset.v3i1.100
15. Ispirova, G., Eftimov, T., & Koroušić Seljak, B. (2022). Predefined domain specific embeddings of food concepts and recipes: A case study on heterogeneous recipe datasets. *2022 IEEE International Conference on Big Data*, 4074–4083. https://doi.org/10.1109/bigdata55660.2022.10020698
16. Mueller, M., Harvey, M., Elsweiler, D., & Mika, S. (2012). Ingredient matching to determine the nutritional properties of internet-sourced recipes. *Proceedings of the 6th International Conference on Pervasive Computing Technologies for Healthcare*. https://doi.org/10.4108/icst.pervasivehealth.2012.248681
17. Gupta, J., Qin, Z., Bendersky, M., & Metzler, D. (2019). Personalized online spell correction for personal search. *The World Wide Web Conference (WWW '19)*. https://doi.org/10.1145/3308558.3313706
18. Dutta, A., Polushin, G., Zhang, X., & Stein, D. (2024). Enhancing e-commerce spelling correction with fine-tuned transformer models. *Proceedings of the 30th ACM SIGKDD Conference on Knowledge Discovery and Data Mining*. https://doi.org/10.1145/3637528.3671625
19. Dehghani Ghotbabadi, T. (2026). Flavor-aware AI for pre-decision support in everyday food practices. *Extended Abstracts of the 2026 CHI Conference on Human Factors in Computing Systems*, 1–5. https://doi.org/10.1145/3772363.3798732
20. Lidiawati, L., Saputra, H., & Agung, H. (2018). Food recipe recommendation system with suffix tree algorithm based on the available tools and ingredients. *ITSMART*, 7(1). https://jurnal.uns.ac.id/itsmart/article/download/18756/16776
21. Trattner, C., & Elsweiler, D. (2017). Food recommender systems: Important contributions, challenges and future research directions. *arXiv* (praprint). https://doi.org/10.48550/arxiv.1711.02760

## Pengembang

Farros Rifantiarno Ramadhani (A11.2024.15694), S1 Teknik Informatika, Universitas Dian Nuswantoro. UTS mata kuliah Sistem Temu Kembali Informasi.
