# Template anotasi SisaRasa v4

## Petunjuk untuk penilai

Isi lembar secara mandiri. Pakai kode seperti `A01` untuk penilai. Baca maksud pengguna, syarat wajib, daftar stok, dan bahan resep. Untuk tiap kandidat, isi satu grade relevansi, satu status kelayakan, dan alasan singkat.

- **3** memenuhi maksud utama. **2** alternatif masuk akal yang memenuhi syarat wajib. **1** hanya cocok pada bagian kecil. **0** tidak relevan atau melanggar syarat wajib.
- **`cukup`** berarti semua bahan wajib tersedia. **`kurang`** berarti ada kebutuhan wajib yang diketahui belum terpenuhi. **`tidak_pasti`** berarti informasi penting belum diketahui.
- Resep yang sangat sesuai dapat kekurangan bahan. Resep yang bisa dibuat dapat gagal memenuhi maksud pengguna. Nilai kedua hal itu secara terpisah.
- Satu opsi tersedia cukup ketika resep menulis `atau`. Bahan yang jelas opsional tidak dihitung sebagai kekurangan. Gunakan bumbu yang diasumsikan hanya jika tercatat.
- Biarkan kosong jika kasus belum dinilai. Pakai `tidak_pasti` hanya setelah membaca kasus dan menemukan informasi yang memang kurang.

## Paket kalibrasi

Enam skenario dan dua belas resep ringkas berikut dibuat khusus untuk latihan rubric. Semua bahan dalam kolom kandidat wajib kecuali dinyatakan opsional atau menjadi bagian dari suatu alternatif. Stok disebutkan lengkap untuk kebutuhan latihan. Kecukupan kuantitas hanya dinilai untuk K04.

| ID | Query dan stok yang diberikan | Maksud dan batasan |
|---|---|---|
| K01 | `tahu, bawang putih, kecap manis`. Garam dan minyak diasumsikan tersedia. | Memakai tahu sebagai bahan utama. Menu bebas. |
| K02 | `wortel, kentang, daun bawang`. Air, garam, dan minyak tersedia. | Ingin sup bening wortel. Jenis menu adalah sasaran pencarian, bukan larangan terhadap tumisan. |
| K03 | `roti tawar, margarin`. Gula tersedia. | Ingin roti panggang manis. |
| K04 | `tahu, kecap manis`. Ada satu potong tahu, berat belum diketahui. Minyak tersedia. | Ingin olahan tahu. Nilai kecukupan jumlah sesuai keterangan stok dan resep. |
| K05 | `tempe, buncis, bawang putih`. Minyak dan garam tersedia. | Harus memakai tempe. Lebih suka tumis sederhana dengan tempe sebagai fokus. |
| K06 | `telur, bawang goreng`. Garam, minyak, dan air tersedia. | Ingin telur dengan bawang goreng. Jangan gunakan bawang merah mentah. |

| Kandidat | Resep dan bahan |
|---|---|
| K01-A | **Tahu kecap.** Tahu, bawang putih, kecap manis, minyak, garam. |
| K01-B | **Tahu isi telur.** Tahu sebagai bahan utama, telur sebagai isian wajib, bawang putih, kecap manis, minyak. |
| K02-A | **Sup bening wortel.** Wortel, kentang, daun bawang, air, garam. |
| K02-B | **Tumis wortel kentang.** Wortel, kentang, daun bawang, minyak, garam. |
| K03-A | **Roti panggang gula.** Roti tawar, mentega atau margarin, gula. Keju opsional. |
| K03-B | **Roti panggang mentega manis.** Roti tawar, mentega, gula. |
| K04-A | **Tahu kecap satu porsi.** Tahu 200 g, kecap manis, minyak. |
| K04-B | **Tahu panggang kecap.** Satu potong tahu, kecap manis, minyak. |
| K05-A | **Oseng buncis dengan potongan tempe.** Buncis sebagai bahan utama, tempe sebagai komponen signifikan, bawang putih, minyak, garam. |
| K05-B | **Tumis buncis bawang putih.** Buncis, bawang putih, minyak, garam. |
| K06-A | **Telur dadar tabur bawang goreng.** Telur, bawang goreng, minyak, garam. |
| K06-B | **Telur kukus bawang merah.** Telur, bawang goreng, bawang merah mentah, air, garam. |

### Lembar penilai

Kode penilai `____` · Tanggal `____` · Versi rubric `____`

| Kandidat | Relevansi 0–3 | Kelayakan | Bahan kurang, alternatif, atau informasi yang belum diketahui | Alasan singkat |
|---|---:|---|---|---|
| K01-A | | | | |
| K01-B | | | | |
| K02-A | | | | |
| K02-B | | | | |
| K03-A | | | | |
| K03-B | | | | |
| K04-A | | | | |
| K04-B | | | | |
| K05-A | | | | |
| K05-B | | | | |
| K06-A | | | | |
| K06-B | | | | |

## Template untuk pilot uji

Gunakan baris kosong ini untuk data peserta. Kirim ke penilai hanya petunjuk, konteks query, kandidat anonim, dan lembar label mereka. Simpan pemetaan kandidat dan lembar konflik pada fasilitator.

| query_id | intent_id | Kode peserta | Query asli | Input ranker | Stok dan bumbu asumsi | Bahan prioritas | Preferensi dan syarat wajib | Jenis query | Split |
|---|---|---|---|---|---|---|---|---|---|
| | | | | | | | | | |

| query_id | candidate_id | Judul | Bahan wajib dan alternatif | Bahan opsional | Detail relevan |
|---|---|---|---|---|---|
| | | | | | |

| query_id | candidate_id | assessor_id | Relevansi 0–3 | Kelayakan | Bahan kurang atau informasi tidak pasti | Alternatif yang memenuhi | Alasan |
|---|---|---|---:|---|---|---|---|
| | | | | | | | |

### Lembar fasilitator

| query_id | candidate_id | recipe_id | Model | Rank | Skor asli | Run ID |
|---|---|---|---|---:|---:|---|
| | | | | | | |

Simpan satu baris pemetaan per kemunculan kandidat dalam hasil model. Lembar calon resep untuk penilai tetap satu baris per pasangan query dan kandidat.

| query_id | candidate_id | Label A | Label B | Relevansi final | Kelayakan final | Alasan penyelesaian | Versi rubric |
|---|---|---|---|---:|---|---|---|
| | | | | | | | |

Catat jumlah pasangan yang dilabeli dua penilai. Untuk masing-masing dimensi, bagi jumlah pasangan dengan label identik dengan jumlah pasangan yang dinilai keduanya. Simpan hasil sebelum diskusi. Ekspor grade akhir E1 dengan kunci `query_id` dan `recipe_id` melalui pemetaan kandidat. Ekspor label kelayakan E4 pada kolom terpisah. Grade 0 adalah penilaian nyata. Kandidat yang belum dinilai tetap tercatat sebagai belum dinilai.

## Template label parser dan typo

Kolom ini disiapkan untuk E2 dan E3. Tulis jawaban yang diharapkan dari teks sumber atau maksud pengguna sebelum melihat keluaran parser. Simpan alternatif yang sama-sama masuk akal.

| item_id | Split | Teks asli | Asal (baris resep/query) | Entitas kanonik yang diterima | Kelompok alternatif atau ambiguitas | Penilai | Catatan |
|---|---|---|---|---|---|---|---|
| | | | | | | | |

| typo_id | intent_id | Split | Jenis kasus | Query bersih | Input aktual | Bagian input yang dinilai | Target yang dapat diterima | Target tersedia di indeks | Kandidat yang ditawarkan berurutan | Pilihan yang diterapkan | Catatan |
|---|---|---|---|---|---|---|---|---|---|---|---|
| | | | | | | | | | | | |

Gunakan `typo`, `valid`, atau `tidak_diketahui` pada jenis kasus. Saat evaluasi typo, catat apakah target tersedia di indeks. Laporkan kasus target di luar indeks secara terpisah. Isi kolom kandidat dan pilihan setelah label target dikunci.

Prosedur lengkap tersedia di [protokol evaluasi](sisarasa_v4_protokol_evaluasi.md).
