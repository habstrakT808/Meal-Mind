# Penggunaan SQLite untuk MealMind

MealMind telah dikonfigurasi untuk menggunakan SQLite sebagai database development. SQLite adalah database sederhana berbasis file yang tidak memerlukan server database terpisah.

## Keunggulan SQLite

1. **Tidak perlu instalasi** - SQLite berjalan langsung tanpa perlu menginstal perangkat lunak tambahan
2. **Portabilitas** - Database SQLite adalah file tunggal, mudah untuk di-backup atau dipindahkan
3. **Kecepatan setup** - Tidak perlu konfigurasi server atau manajemen koneksi
4. **Ringan** - Ideal untuk pengembangan dan aplikasi dengan jumlah pengguna terbatas

## Struktur Database

Database MealMind tetap memiliki struktur yang sama seperti PostgreSQL:

1. **User**: Menyimpan data pengguna (email, password, dll)
2. **UserProfile**: Menyimpan profil pengguna (berat, tinggi, umur, gender, dll)
3. **Food**: Katalog makanan dengan informasi nutrisi
4. **Activity**: Katalog aktivitas fisik
5. **DailyRecommendation**: Rekomendasi makanan dan aktivitas harian
6. **DailyCheckin**: Catatan kepatuhan pengguna terhadap rekomendasi

## Lokasi Database

Database SQLite disimpan sebagai file di:

```
backend/instance/mealmind_dev.db
```

## Cara Menggunakan

### 1. Inisialisasi Database

SQLite database akan otomatis dibuat saat pertama kali aplikasi berjalan, atau Anda bisa menginisialisasi secara manual:

```bash
cd backend
python init_db.py
```

### 2. Backup Database

Untuk membuat backup database:

```bash
cd backend
python scripts/sqlite_tools.py backup
```

File backup akan disimpan di folder `backend/backups/` dengan format:
`mealmind_sqlite_YYYYMMDD_HHMMSS.db`

### 3. Restore Database

Untuk mengembalikan database dari backup:

```bash
cd backend
python scripts/sqlite_tools.py restore --backup-file backups/nama_file_backup.db
```

### 4. Melihat & Mengedit Isi Database

Untuk melihat isi database SQLite, Anda bisa menggunakan:

1. **SQLite Browser** - Aplikasi GUI untuk SQLite (https://sqlitebrowser.org/)
2. **VSCode Extension** - SQLite Viewer extension untuk Visual Studio Code
3. **Command Line** - Menggunakan SQLite CLI:

```bash
sqlite3 instance/mealmind_dev.db
```

## Migrasi ke PostgreSQL (Jika Diperlukan)

Saat aplikasi sudah siap untuk deployment produksi, Anda bisa migrasi ke PostgreSQL:

1. Mengubah `FLASK_ENV` ke `production` di file `.env` atau variabel lingkungan
2. Pastikan PostgreSQL diinstal dan bisa diakses
3. Sesuaikan `DATABASE_URL` di `.env` atau `config.py`
4. Jalankan migrasi database:
   ```
   flask db upgrade
   ```

## Catatan Penting

SQLite memiliki keterbatasan dibandingkan PostgreSQL:

1. **Konkurensi terbatas** - Tidak ideal untuk aplikasi dengan banyak operasi tulis bersamaan
2. **Fitur database terbatas** - Kurangnya fitur seperti stored procedures dan advanced indexes
3. **Skalabilitas terbatas** - Cocok untuk aplikasi kecil hingga menengah

Untuk aplikasi yang sudah siap produksi dan diakses banyak pengguna, sebaiknya migrasi ke PostgreSQL.
