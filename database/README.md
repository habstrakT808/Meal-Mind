# MealMind Database Setup

Aplikasi MealMind menggunakan SQLite sebagai database default untuk menyimpan data pengguna, rekomendasi makanan, dan aktivitas.

## Penggunaan SQLite

SQLite adalah database ringan berbasis file yang tidak memerlukan instalasi server terpisah. Sangat cocok untuk pengembangan dan aplikasi dengan jumlah pengguna terbatas.

## Setup Database

SQLite tidak memerlukan setup khusus. Database akan secara otomatis dibuat saat aplikasi pertama kali dijalankan.

```bash
# Pastikan Anda berada di direktori backend
cd backend

# Jalankan script inisialisasi database
python init_db.py
```

## Lokasi Database

File database SQLite disimpan di:

```
backend/instance/mealmind_dev.db
```

## Backup dan Restore

### Backup Database

Untuk membuat backup database:

```bash
# Pastikan Anda berada di direktori backend
cd backend

# Buat backup
python scripts/sqlite_tools.py backup
```

Backup akan disimpan di folder `backend/backups/` dengan format nama:
`mealmind_sqlite_YYYYMMDD_HHMMSS.db`

### Restore Database

Untuk mengembalikan database dari backup:

```bash
cd backend
python scripts/sqlite_tools.py restore --backup-file backups/nama_file_backup.db
```

## Melihat dan Mengedit Database

Untuk melihat dan mengedit isi database SQLite, Anda dapat menggunakan:

1. **SQLite Browser** - Aplikasi GUI untuk SQLite (https://sqlitebrowser.org/)
2. **VSCode Extension** - SQLite Viewer extension untuk Visual Studio Code
3. **Command Line** - Menggunakan SQLite CLI:

```bash
sqlite3 instance/mealmind_dev.db
```

## Struktur Database

Database MealMind menggunakan tabel-tabel berikut:

1. `user` - Akun pengguna (email, password)
2. `user_profile` - Informasi profil pengguna (tinggi, berat badan, dll)
3. `food` - Database item makanan
4. `activity` - Database aktivitas fisik
5. `daily_recommendation` - Rekomendasi makanan harian
6. `daily_checkin` - Check-in harian pengguna

## Migrasi ke PostgreSQL (Jika Diperlukan)

Jika aplikasi berkembang dan memerlukan database yang lebih kuat, Anda dapat bermigrasi ke PostgreSQL di masa mendatang dengan mengikuti panduan di file `backend/SQLITE_README.md`.
