# Protokol evaluasi SisaRasa v4

**Status.** Draf untuk kalibrasi penilai, 25 November 2026. Kunci protokol setelah kalibrasi, sebelum membuka label atau hasil analisis set uji. Catat perubahan, alasan, tanggal, dan versi. Perubahan setelah melihat hasil uji memerlukan set uji baru untuk klaim konfirmasi.

## Tujuan dan baseline

Pertanyaan utama: apakah Hybrid mengurutkan resep yang lebih relevan daripada Set-Overlap ketika orang mencari dari bahan yang mereka punya?

Bandingkan empat konfigurasi v4: Set-Overlap, TF-IDF Cosine, BM25, dan SisaRasa Hybrid. Pembanding utama yang ditetapkan di awal adalah Set-Overlap. Hasil terhadap TF-IDF dan BM25 membantu menjelaskan perbedaan sistem. Audit parser, saran ejaan, dan kelayakan bahan mendukung interpretasi hasil ranking.

| Item | Baseline yang dibekukan |
|---|---|
| Notebook dan commit | [sisarasa_v4.ipynb](../notebooks/sisarasa_v4.ipynb), `63b3eab` |
| Run historis | `pseudo-eval-20261107T142228Z-7b205ef7`, `sisarasa_v4_research_2` |
| Protokol dan rubric historis | `sisarasa_v4_confirm_1`, `proxy_v3` |
| Parser dan saran ejaan | `sisarasa_v4_normalization_3`, `sisarasa_v4_suggestions_2` |
| Korpus | 68.745 resep. SHA-256 rekaman penuh `7d3c286510cbfc231b23b8a49c960943292adb2d8993ff785b8706cc1e399d86`. |
| Parameter | Ambil konfigurasi lengkap dari `models` di [metadata run](../artifacts/evaluation_runs/pseudo-eval-20261107T142228Z-7b205ef7/metadata.json). |

Run lama adalah pembanding historis yang memakai label otomatis. Pada 48 query konfirmasi, nDCG@10 Set-Overlap 0,9430 dan Hybrid 0,9209. Nilai tersebut mengukur kesesuaian dengan `proxy_v3`. Simpan run lama sebagai arsip. Jalankan evaluasi baru di direktori dengan ID baru. [Hasil konfirmasi](../artifacts/evaluation_runs/pseudo-eval-20261107T142228Z-7b205ef7/confirmation/overall_results.json) · [Kriteria konfirmasi](../artifacts/evaluation_runs/pseudo-eval-20261107T142228Z-7b205ef7/confirmation/criteria.csv)

## Data, split, dan pembutaan penilai

1. **Kalibrasi.** Gunakan enam skenario buatan pada [template anotasi](sisarasa_v4_template_anotasi.md). Dua penilai mengisi 12 pasangan secara independen. Fasilitator membahas konflik, memperjelas rubric, dan mengulang kasus yang masih ambigu. Seluruh kasus yang dibahas tetap di kalibrasi.
2. **Pilot uji.** Target awal 20 kebutuhan pencarian yang ditulis peserta sebelum melihat hasil. Ambil query daftar bahan saja dan query dengan petunjuk menu atau syarat jelas. Catat jenis dan jumlah query. Gunakan kode peserta, tanpa nama atau kontak pada lembar penilaian. Simpan query asli dan rincian niat yang diberikan peserta. Cantumkan apa yang benar-benar menjadi input ranker.
3. **Pemisahan.** Tetapkan `intent_id` sebelum split. Masukkan variasi bersih, typo, alias, dan parafrasa dari satu kebutuhan ke kelompok yang sama. Pisahkan per peserta jika peserta menyumbang beberapa kebutuhan terkait. Gunakan set pengembangan tersendiri jika tuning diperlukan. Query pilot yang hasilnya dipakai mengubah parser, model, atau rubric menjadi data pengembangan. Set uji konfirmasi harus baru.
4. **Pool.** Untuk setiap query, gabungkan top-10 semua konfigurasi yang akan dibandingkan dalam analisis utama. Deduplikasi dengan `recipe_id`, lalu acak urutan dengan seed yang dicatat. Simpan pemetaan model, rank, skor, dan seed pada lembar fasilitator. Beri penilai teks resep, maksud query, dan stok. Gunakan ID kandidat netral dan sembunyikan model, rank, skor, serta hasil parser. Laporkan ukuran pool sebenarnya. Untuk 20 query dan empat model, batas atas awalnya 800 pasangan sebelum deduplikasi.
5. **Penilaian.** Beri kedua penilai pool yang sama. Simpan label mentah secara terpisah. Catat kesepakatan persis untuk relevansi dan kelayakan sebelum diskusi. Fasilitator menyelesaikan konflik dengan alasan tertulis. Label kosong berarti belum dinilai. Jika seluruh top-10 belum mendapat label final, tandai query dan selesaikan penilaian sebelum menghitung perbandingan utama. Laporkan cakupan penilaian dan daftar query tertunda.

Prosedur pooling dan penilaian bertingkat mengadaptasi [Craswell dkk. (2022)](https://trec.nist.gov/pubs/trec30/papers/Overview-DL.pdf). Pengacakan dan pembutaan identitas model mengikuti rancangan SisaRasa.

## Rubric penilai

**Relevansi.** Nilai apakah hidangan memenuhi maksud yang dinyatakan. Nilai kelayakan bahan pada kolom lain. Resep dapat sangat relevan dan tetap kekurangan bahan.

| Grade | Aturan |
|---|---|
| 3 | Memenuhi tujuan utama, menggunakan bahan yang wajib dipakai sesuai perannya, dan memenuhi syarat eksplisit. Pada query terbuka, hidangan langsung menjawab kebutuhan pengguna. |
| 2 | Alternatif yang masuk akal dan memenuhi semua syarat wajib, tetapi kurang pas pada preferensi atau petunjuk yang tidak wajib. |
| 1 | Hanya cocok pada bagian kecil, misalnya memakai satu bahan tetapi tidak menjawab jenis menu yang dituju. Tidak ada pelanggaran syarat wajib yang eksplisit. |
| 0 | Tidak menjawab maksud query atau melanggar syarat wajib yang dinyatakan. |

**Kelayakan bahan.** Nilai kecukupan berdasarkan stok yang dilaporkan dan daftar bahan resep. Gunakan bumbu asumsi hanya jika tercatat untuk query itu. Untuk pilihan `A atau B`, satu opsi yang tersedia cukup. Bahan opsional tidak menjadi kekurangan wajib.

| Status | Aturan |
|---|---|
| `cukup` | Semua bahan wajib tersedia. Jumlah diperiksa hanya saat skenario meminta kecukupan jumlah. |
| `kurang` | Minimal satu bahan wajib atau jumlah wajib diketahui tidak tersedia. Catat kekurangannya. |
| `tidak_pasti` | Informasi penting tidak diketahui, misalnya stok belum ditimbang pada skenario kuantitas. Catat yang perlu dikonfirmasi. |

Jika ada kekurangan yang sudah pasti sekaligus informasi lain yang belum lengkap, gunakan `kurang` dan catat keduanya. Jika query menyebut syarat alat, nilai syarat tersebut pada relevansi. Status kelayakan di tabel tetap mengukur bahan.

## Eksperimen dan analisis

| ID | Desain | Ukuran |
|---|---|---|
| E1. Ranking | Jalankan konfigurasi v4 pada korpus, query, dan qrels manusia yang sama. Analisis terkontrol berikutnya menyamakan bahan inti, universe kandidat, dan aturan seri. Uji kanal judul sebagai perubahan terpisah. Jika analisis terkontrol menghasilkan kandidat di luar pool, perluas penilaian sebelum membandingkannya. | nDCG@10 utama. P@5 pendamping. Selisih berpasangan, menang/seri/kalah, interval, dan contoh kegagalan. |
| E2. Parser | Bandingkan pencocokan langsung dengan normalisasi v4 pada baris bahan dan query Indonesia yang belum dipakai menyusun kamus. Label entitas kanonik, ID alternatif, dan kasus ambigu. Mulai dengan target pilot 100–150 baris, lalu sesuaikan berdasarkan biaya label. | Precision, recall, F1 mikro untuk entitas, kecocokan seluruh baris, dan jumlah penggabungan identitas yang salah. |
| E3. Typo | Untuk setiap maksud, simpan bentuk bersih, typo, dan target yang dapat diterima. Bekukan parser dan indeks. Bandingkan query bersih, typo sebelum pilihan, dan typo sesudah pilihan benar yang memang ditawarkan. Jika target tak ditawarkan, kondisi sesudah pilihan tetap memakai query typo. Gunakan satu qrels per maksud dan gabungkan top-10 ketiga kondisi ke pool yang dinilai. | Candidate recall@3 per bagian input dengan typo dan target tersedia, peringkat kandidat benar, proporsi input valid yang mendapat saran keliru, dan delta nDCG@10 per maksud. Laporkan target di luar indeks terpisah. Tandai pilihan benar yang disimulasikan. |
| E4. Kelayakan | Gunakan label bahan dari pool yang sama. Catat apakah hasil memakai bahan prioritas. Bedakan resep yang butuh bahan tambahan dari resep siap dengan stok deklaratif. | `Success@5` untuk minimal satu resep dengan relevansi ≥2 dan status `cukup`. Laporkan juga proporsi `tidak_pasti` dan jumlah bahan wajib yang kurang. |

**Ablation.** Setelah perbandingan utama, uji Hybrid lengkap, tanpa protein, dan tanpa penalti bahan kurang. Nolkan satu bobot tiap varian. Pertahankan kandidat, parser, qrels, dan bobot lain. Tambahkan hasil varian ke pool bila perlu. Tafsirkan sebagai diagnostik komponen. Pemulihan resep sumber lama tetap disajikan terpisah.

**Penghitungan.** Gunakan DCG dengan gain `2^grade - 1` dan diskon `log2(rank + 1)`. Denominator nDCG memakai urutan ideal dari pool berlabel. Laporkan query dengan IDCG nol dan hitung nilainya nol pada rerata utama. Gunakan grade ≥2 dan denominator tetap 5 untuk P@5. Hitung selisih model pada query yang sama. Jika suatu kebutuhan punya beberapa varian query, rata-ratakan variannya sebelum bootstrap berpasangan atas `intent_id`. Pakai 10.000 pengulangan dengan seed 42 untuk interval 95%. Laporkan cakupan pool bersama metrik. Set uji pilot menghasilkan estimasi deskriptif yang dipakai untuk merencanakan ukuran uji lanjutan.

**Kriteria keputusan usulan.** Bekukan selisih praktis minimum **+0,02 nDCG@10** untuk Hybrid relatif terhadap Set-Overlap sebelum uji konfirmasi manusia. Hybrid memenuhi aturan keputusan jika estimasi selisih mencapai ambang tersebut dan batas bawah interval 95% berada di atas nol. Jika interval mencakup nol atau ukuran pilot terlalu kecil, simpulkan bahwa perbedaan belum pasti. Ambang ini adalah keputusan proyek. Kesetaraan model memerlukan desain yang mengujinya secara khusus.

## Rujukan eksperimen

Gunakan [RIS rujukan primer](../Paper/Referensi%20primer%20SisaRasa.ris) untuk daftar aktif. Dua ekspor pencarian di `Paper/` menyimpan kandidat bacaan terbit 2021 ke atas. Jumlah sampel, ambang, kasus Indonesia, dan aturan lulus ditetapkan dalam rancangan SisaRasa.

- **E1. Ranking.** Gunakan TF-IDF cosine pada representasi bahan sebagaimana pada Chhipa dkk. Pertahankan BM25 sebagai pembanding dan gunakan satu set kueri serta qrels untuk semua konfigurasi, mengikuti desain benchmark seperti BEIR. [Chhipa dkk. (2022)](https://pdfs.semanticscholar.org/0147/673758991cd5f458bd379bb9615b056f6f8d.pdf) ? [Thakur dkk. (2021)](https://datasets-benchmarks-proceedings.neurips.cc/paper_files/paper/2021/hash/65b9eea6e1cc6bb9f0cd2a47751a186f-Abstract-round2.html)
- **E2. Parser.** Adaptasi anotasi nama, jumlah, satuan, dan kondisi bahan. Tambahkan status opsional dan ID kelompok alternatif untuk skenario belanja SisaRasa. Bandingkan parser lama dan baru pada baris berlabel yang sama. [Goel dkk. (2024)](https://aclanthology.org/2024.lrec-main.406/)
- **E3. Typo.** Uji jenis kesalahan terpisah, termasuk huruf tertukar, pemisahan kata, dan kueri benar. SisaRasa memakai indeks tetap dan menilai saran teratas serta hasil retrieval setelah pilihan eksplisit. [Kakkar dkk. (2023)](https://aclanthology.org/2023.acl-industry.66/)
- **E4. Kelayakan.** Pisahkan daftar nama yang cocok dari kecukupan stok berdasarkan jumlah yang diketahui. Laporkan status `tidak_pasti` jika jumlah diperlukan tetapi datanya kurang. Persentase bahan kueri dalam Ashraf dan Maduranga memakai denominator kueri. SisaRasa mendefinisikan cakupan kebutuhan inti resep untuk penjelasan belanja. [Ortiz dkk. (2023)](https://www.cetjournal.it/cet/23/106/061.pdf) ? [Ashraf dan Maduranga (2025)](https://faith.futuretechsci.org/index.php/FAITH/article/view/98)

### Urutan perbaikan setelah audit

1. **Kelayakan demo.** Simpan penanda opsional sebelum pembersihan catatan. Uji `keju opsional` dan `keju` pada resep dengan stok yang sama. Keju opsional tidak masuk daftar belanja atau denominator kebutuhan inti. Uji juga alternatif dan konjungsi. Di demo, beri label persentase sebagai kecocokan nama bahan dan tampilkan bahwa takaran belum diperiksa.
2. **Normalisasi dan saran.** Tambah fixture `mie lidi`, `- bumbu taliwang`, kurung bertingkat, `dagng sapi`, `daun slaam`, dan `minyk`. Ukur ketepatan entitas, posisi target di daftar saran, serta hasil top-5 sebelum dan setelah pilihan. Pisahkan kasus tanpa target di korpus. Bekukan indeks ketika menguji perubahan saran.
3. **Pemeriksaan sebelum presentasi.** Commit input eksperimen sebelum Run All. Catat hash korpus, manifest, dan qrels saat membandingkan hasil. Jika hanya penjelasan demo berubah, cocokkan hasil ranking dengan baseline. Setelah parser atau label berubah, laporkan hasil sebagai eksploratif dan gunakan set uji baru untuk konfirmasi.

## Kunci fasilitator untuk kalibrasi

Berikan kunci setelah dua lembar penilaian awal dikumpulkan. Kunci membantu mendeteksi tafsir yang berbeda. Simpan alasan setiap revisi rubric di catatan kalibrasi.

| Kandidat | Relevansi | Kelayakan | Alasan yang harus muncul dalam diskusi |
|---|---:|---|---|
| K01-A | 3 | `cukup` | Tahu berperan utama dan semua bahan tersedia. |
| K01-B | 3 | `kurang` | Tujuan terpenuhi, tetapi telur wajib tidak tersedia. |
| K02-A | 3 | `cukup` | Sup bening sesuai petunjuk dan stok cukup. |
| K02-B | 1 | `cukup` | Wortel terpakai, tetapi tumis tidak sesuai target menu. |
| K03-A | 3 | `cukup` | Margarin memenuhi alternatif. Keju opsional. |
| K03-B | 3 | `kurang` | Mentega wajib tidak tersedia. |
| K04-A | 3 | `tidak_pasti` | Berat stok belum diketahui, sedangkan resep perlu 200 g. |
| K04-B | 3 | `cukup` | Jumlah satu potong dan bahan wajib lain tersedia. |
| K05-A | 2 | `cukup` | Tempe tetap signifikan. Hidangan lebih berfokus pada buncis. |
| K05-B | 0 | `cukup` | Resep dapat dibuat, tetapi syarat wajib memakai tempe gagal. |
| K06-A | 3 | `cukup` | Bawang goreng terpakai dan tidak perlu bawang merah mentah. |
| K06-B | 0 | `kurang` | Melanggar syarat bahan dan membutuhkan bawang merah mentah. |

Untuk pilot ini, target kalibrasi adalah minimal **10 dari 12 pasangan** dengan kesepakatan persis pada masing-masing dimensi. Tinjau setiap konflik, terutama grade 0 versus grade ≥2 atau `cukup` versus `kurang`. Jika target belum tercapai atau tafsir aturan masih berbeda, perjelas rubric dan lakukan putaran independen dengan pasangan baru. Catat kesepakatan sebelum diskusi pada setiap putaran. Hasil kalibrasi tidak masuk metrik ranking.

## Checklist sebelum run baru

- [ ] Kalibrasi penilai selesai dan versi rubric dicatat.
- [ ] Manifest query, split, model, metrik, dan aturan interpretasi sudah terkunci.
- [ ] Revisi sumber data, hash input, snapshot korpus, commit notebook, versi Python dan dependensi, serta seed tercatat.
- [ ] Korpus, parser, dan urutan `doc_id` konsisten antara model, pool, qrels, dan evaluasi. Tetapkan aturan seri untuk run baru dan simpan run historis.
- [ ] Paket penilai tidak memuat kolom model, skor, rank, atau identitas pribadi.
- [ ] Label awal, keputusan akhir, dan cakupan top-k disimpan terpisah.
- [ ] Hash manifest query, qrels, dan ranking diekspor. Skor dapat dihitung ulang dari berkas tersebut.
- [ ] Ekspor memakai direktori baru. Tambahkan `_SUCCESS` setelah seluruh keluaran lengkap.
