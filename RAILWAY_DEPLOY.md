# Panduan Deployment MealMind ke Railway

Railway adalah platform deployment yang mudah digunakan dan menawarkan tier gratis untuk proyek kecil. Berikut adalah langkah-langkah untuk men-deploy aplikasi MealMind ke Railway:

## Langkah 1: Persiapan

1. Buat akun di [Railway](https://railway.app/)
2. Instal Railway CLI:
   ```bash
   npm install -g @railway/cli
   ```
3. Login ke Railway CLI:
   ```bash
   railway login
   ```

## Langkah 2: Deploy Backend

1. Dari direktori root proyek, inisialisasi proyek Railway:
   ```bash
   railway init
   ```
2. Pilih "Create a new project" dan berikan nama "mealmind-backend"
3. Deploy backend:
   ```bash
   railway up
   ```

## Langkah 3: Konfigurasi Environment Variables

1. Buka dashboard Railway
2. Pilih proyek yang baru dibuat
3. Klik "Variables"
4. Tambahkan variabel-variabel berikut:
   - `FLASK_APP=run.py`
   - `FLASK_ENV=production`
   - `FLASK_DEBUG=0`
   - `SECRET_KEY=your-secret-key` (ganti dengan nilai acak)
   - `JWT_SECRET_KEY=your-jwt-secret` (ganti dengan nilai acak)

## Langkah 4: Deploy Frontend

1. Buat proyek baru di Railway:
   ```bash
   cd frontend
   railway init
   ```
2. Pilih "Create a new project" dan berikan nama "mealmind-frontend"
3. Deploy frontend:
   ```bash
   railway up
   ```

## Langkah 5: Konfigurasi Frontend

1. Buka dashboard Railway
2. Pilih proyek frontend
3. Klik "Variables"
4. Tambahkan variabel berikut:
   - `VITE_API_URL=https://[url-backend-anda].railway.app`

## Langkah 6: Akses Aplikasi

1. Setelah deployment selesai, Railway akan memberikan URL untuk backend dan frontend
2. Akses frontend URL untuk menggunakan aplikasi MealMind

## Catatan Penting

- Railway menawarkan tier gratis dengan batasan tertentu
- Aplikasi akan sleep setelah tidak aktif selama beberapa waktu pada tier gratis
- Untuk penggunaan produksi, pertimbangkan untuk upgrade ke paket berbayar

## Troubleshooting

Jika mengalami masalah:
1. Periksa logs di dashboard Railway
2. Pastikan semua environment variables sudah dikonfigurasi dengan benar
3. Restart service jika diperlukan melalui dashboard 