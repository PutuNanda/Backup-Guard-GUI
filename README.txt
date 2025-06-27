
README.txt
====================
Backup Guard GUI - Panduan Lengkap Penggunaan

🔥 Deskripsi
Backup Guard GUI adalah aplikasi GUI berbasis Python untuk membackup file/folder secara otomatis dengan fleksibilitas tinggi. Dirancang agar mudah digunakan, siap dijalankan secara portabel tanpa perlu instalasi Python global!

---

📋 Cara Menjalankan

🔹 Versi Portable (tanpa install Python)
1. Ekstrak semua file dari folder ZIP.
2. Jalankan file:
   ```
   run_Backup_Guard.vbs
   ```
   ➜ GUI akan langsung muncul tanpa membuka jendela CMD.
3. Semua dependensi (`Python`, `tkinter`, `tcl`) sudah disiapkan di dalam folder.

🔹 Versi Manual (jika ingin pakai Python global)
1. Pastikan Python ≥ 3.6 sudah terinstall dan mendukung `tkinter`.
2. Install dependensi (jika belum):
   ```bash
   pip install -r requirements.txt
   ```
3. Jalankan aplikasi:
   ```bash
   python Backup_Guard\Backup_Guard_Gui.py
   ```

---

🛠️ Fitur dan Pengaturan

🔹 Path Sumber & Output
- Pilih file/folder sumber untuk dibackup.
- Tentukan folder output backup.

🔹 Interval Backup
| Opsi                | Keterangan                                  |
|---------------------|----------------------------------------------|
| detik               | Backup setiap X detik (misal: 30)            |
| menit               | Backup setiap X menit (misal: 5)             |
| jam                 | Backup setiap X jam (misal: 2)               |
| Menit Perangkat     | Backup tiap kali jam sistem berganti menit   |
| Jam Perangkat       | Backup tiap kali jam sistem berganti jam     |

🔹 Mode Backup
- **Folder**: Backup seluruh folder (isi dan subfolder).
- **File**: Backup file individual.

🔹 Tipe Backup
- **ZIP**: Hasil backup dalam bentuk file `.zip`.
- **Tidak Ada**: File/folder disalin apa adanya tanpa kompresi.

🔹 Format Nama Backup
- Gunakan timestamp dengan format tanggal & waktu.
- Tambahkan nama khusus (optional).
- Pilihan menyertakan nama asli file sumber.

🔹 Manajemen File Lama
- Fitur pembatasan jumlah file backup (hapus otomatis file tertua).
- Jumlah file disesuaikan dengan input angka.
- Aktifkan melalui checkbox.

---

🚀 Contoh Skenario

1. **Backup Folder Setiap 1 Jam**
   - Mode: Folder
   - Interval: 1 + jam
   - Output: ZIP
   - Hasil: `Backup_28-06-2025_10-00.zip`

2. **Backup File Tiap Menit Jam Sistem**
   - Mode: File
   - Interval: Menit Perangkat
   - Output: Tidak Ada
   - Hasil: `data_28-06-2025_10-02.txt`

---

⚠️ Troubleshooting

- ❗ *Path tidak valid*: Periksa karakter spesial atau spasi aneh.
- ⛔ *GUI tidak muncul (portable)*: Pastikan tidak ada file hilang seperti `tkinter`, `tcl8.6`, `tk8.6`, atau `_tkinter.pyd`.
- 🔁 *Backup tidak berjalan*: Mungkin proses masih aktif (tombol “Hentikan Proses” muncul).
- ⚠️ *File corrupt*: Jangan buka/edit file sumber saat proses backup berlangsung.

---

📌 Catatan
- File konfigurasi: `backup_guard_config.json`
- Folder sementara otomatis terhapus setelah backup selesai: `backup_guard_temp/`
- Path, pengaturan, dan mode akan tersimpan otomatis untuk sesi berikutnya.

---

📦 Struktur Folder
```
Backup Guard GUI\
├── run_Backup_Guard.vbs
├── Backup_Guard\
│   ├── Backup_Guard_Gui.py
│   ├── run_bgg_portable.bat
│   ├── backup_guard_config.json
│   ├── backup_guard_temp\
│   └── python_embed\
│       ├── python.exe
│       ├── DLLs\
│       ├── Lib\tkinter\
│       └── tcl\
```

---

💻 Versi: 1.0.0
🧠 Developer: PutuNanda & ChatGPT & DeepSeek

📜 License: MIT  
> Bebas digunakan, dimodifikasi, dan dibagikan.  
> Mohon tetap cantumkan kredit jika merilis versi modifikasi.

---

🎉 Terima kasih telah menggunakan Backup Guard GUI!
Saran, perbaikan, dan kontribusi open source sangat dihargai!
