# Samkhan.trade — pembaruan data otomatis

## Cara pasang
1. Unduh ZIP ini dan ekstrak.
2. Buka repositori GitHub `rafkasamkhan07-svg/rafa`.
3. Unggah/ganti `index.html` di root dengan file dari ZIP.
4. Buat folder `.github/workflows/` di root bila belum ada, lalu unggah `update-stocks.yml` ke dalamnya.
5. Buat folder `scripts/` di root, lalu unggah `update_stocks.py` ke dalamnya.
6. Unggah `stocks-live.json` ke root.
7. Commit semua perubahan ke branch `main`.
8. Di GitHub buka tab **Actions**, pilih **Update IDX stock data**, lalu klik **Run workflow** untuk uji pertama.
9. Pastikan Actions sukses. Setelah itu workflow dijadwalkan setiap jam pada hari kerja selama rentang UTC 02–09.

## Catatan penting
- Ini menggunakan pustaka komunitas `yfinance`/Yahoo Finance, bukan API resmi BEI. Data bisa tertunda, tidak tersedia, atau berubah format.
- Harga harian bukan harga tick real-time. Jangan gunakan data ini sebagai satu-satunya dasar transaksi.
- GitHub Actions membutuhkan izin menulis konten repo. Pada Settings → Actions → General, pastikan workflow memiliki izin read/write contents jika push ditolak.
- Baris yang tidak berhasil diperbarui akan mempertahankan data impor lama dan ditandai di properti `source`; selalu periksa `updatedCount` dan log Actions.
- `index.html` tidak perlu diganti lagi setelah pemasangan; workflow hanya memperbarui `stocks-live.json`.
