# Git and Development Conventions for SisaRasa

## 1. Mandatory Atomic Commits
- Setiap git commit **WAJIB** berupa *atomic commit*: satu commit hanya mencakup satu perubahan logis terisolasi (single responsibility).
- Dilarang menggabungkan perubahan yang tidak berhubungan ke dalam satu commit (contoh: jangan gabungkan refactor backend dengan update README).
- Selalu gunakan format Conventional Commits:
  - `feat(...)`: Fitur atau endpoint baru
  - `fix(...)`: Perbaikan bug
  - `refactor(...)`: Restrukturisasi atau pembersihan kode tanpa mengubah perilaku eksternal
  - `test(...)`: Menambah atau memperbarui automated test suite
  - `docs(...)`: Dokumentasi (README, docstrings)
  - `chore(...)`: Pemeliharaan, dependensi, atau konfigurasi
  - `build(...)`: Perubahan sistem build, gitignore, atau dependensi paket
  - `perf(...)`: Optimasi performa dan latensi
- Pesan commit harus deskriptif, profesional, dan menjelaskan esensi perubahan.

## 2. Konfirmasi Sebelum Modifikasi
- Sebelum melakukan modifikasi kode yang signifikan atau merestrukturisasi file, konfirmasikan rencana perubahan kepada pengguna terlebih dahulu.
- Jelaskan apa yang akan diubah dan alasannya, lalu tunggu persetujuan sebelum eksekusi.

## 3. Standar Kualitas Kode (PEP 8 & Clean Code)
- Tidak boleh ada komentar sel notebook (seperti `# CELL X:...`) atau duplikasi impor di modul backend produksi.
- Seluruh kelas dan fungsi utama harus memiliki docstring dan type hints yang jelas.
- Pastikan seluruh pengujian unit otomatis selalu lolos (`pytest backend/tests/ -v`).

## 4. Larangan Gaya Penulisan AI Slop dan Emoji
- Dilarang menggunakan em dash (simbol tanda pisah panjang), emoji, atau kalimat berbunga-bunga/klise khas AI (AI slop).
- Tulisan (markdown, komentar kode, dokumen, pesan commit) harus ringkas, langsung pada inti persoalan, teknis, dan natural seperti tulisan manusia.

