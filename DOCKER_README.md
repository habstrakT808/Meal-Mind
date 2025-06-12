# Deployment MealMind dengan Docker

Panduan ini menjelaskan cara men-deploy aplikasi MealMind menggunakan Docker.

## Prasyarat

- Docker dan Docker Compose terinstal di sistem Anda
- Git (untuk mengclone repository)

## Langkah-langkah Deployment

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/meal-mind-project.git
cd meal-mind-project
```

### 2. Menjalankan dengan Docker Compose

Pastikan Anda berada di direktori root proyek (yang berisi file `docker-compose.yml`).

```bash
docker-compose up --build
```

Perintah ini akan:
- Membangun image Docker untuk backend dan frontend
- Membuat dan menjalankan container untuk kedua layanan
- Menghubungkan layanan backend dan frontend

### 3. Mengakses Aplikasi

Setelah container berjalan:

- Frontend dapat diakses di: http://localhost:5173
- Backend dapat diakses di: http://localhost:5000

### 4. Menghentikan Aplikasi

Untuk menghentikan aplikasi dan container, gunakan:

```bash
# Jika dijalankan di foreground (terminal yang sama)
Ctrl+C

# Atau dari terminal lain
docker-compose down
```

## Troubleshooting

### Masalah Database

Jika Anda mengalami masalah dengan database, Anda dapat mengakses container backend dan menjalankan perintah inisialisasi database:

```bash
# Masuk ke container backend
docker exec -it meal-mind-main_backend_1 bash

# Di dalam container, jalankan:
python init_db.py
```

### Logs

Untuk melihat log dari layanan:

```bash
# Log semua layanan
docker-compose logs

# Log layanan tertentu
docker-compose logs backend
docker-compose logs frontend

# Log secara real-time
docker-compose logs -f
```

## Konfigurasi Tambahan

### Environment Variables

Anda dapat menambahkan variabel lingkungan di file `.env` di direktori root atau langsung dalam `docker-compose.yml`.

### Volume Persistence

Data akan disimpan di volume Docker. Untuk backup database, Anda dapat mengakses file SQLite di `/app/mealmind_dev.db` dalam container backend. 