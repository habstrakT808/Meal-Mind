# Meal-Mind

## Model ML Serialization

Untuk mengurangi ukuran backend dan meningkatkan performa, model Machine Learning disimpan dalam format terpisah menggunakan joblib.

### Cara Menggunakan

1. Untuk melatih dan menyimpan model:

   ```bash
   cd backend
   python train_models.py
   ```

2. Model yang sudah dilatih akan disimpan di direktori `models/`

3. Saat aplikasi berjalan, model akan dimuat otomatis dari file yang tersimpan.

### Manfaat

- Mengurangi ukuran backend saat deployment
- Mempercepat proses startup aplikasi
- Memisahkan proses pelatihan model dari penggunaan model
- Memungkinkan model diperbarui tanpa mengubah kode aplikasi

### Model yang Diserialisasi

- `tfidf_vectorizer.joblib` - TF-IDF Vectorizer untuk rekomendasi makanan

### Catatan

- Pastikan direktori `models/` ada dan dapat ditulis oleh aplikasi
- Jika file model tidak ditemukan, model akan dibuat ulang secara otomatis
