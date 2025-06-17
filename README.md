# 🍽️ MealMind - Platform Perencanaan Diet Cerdas

[![Status](https://img.shields.io/badge/status-active-success.svg)]()
[![License](https://img.shields.io/badge/license-MIT-blue.svg)]()

  ![image](https://github.com/user-attachments/assets/f0f91039-4e2a-4303-b995-c5eb2e4d33f8)

## 📋 Deskripsi

**MealMind** adalah platform diet cerdas berbasis machine learning yang memberikan rekomendasi makanan, pelacakan nutrisi, dan saran aktivitas fisik secara personal sesuai kebutuhan dan preferensi pengguna. Aplikasi ini dirancang untuk membantu pengguna mencapai tujuan diet mereka dengan cara yang sehat dan berkelanjutan.

## ✨ Fitur Utama

- **🧠 Rekomendasi Makanan Cerdas** - Dapatkan saran makanan berdasarkan preferensi, alergi, dan tujuan diet Anda
- **📊 Pelacakan Nutrisi Otomatis** - Monitor asupan kalori, protein, karbohidrat, dan lemak harian
- **📈 Analisis Progress Diet** - Lihat perkembangan diet Anda dari waktu ke waktu dengan grafik intuitif
- **📆 Perencanaan Meal Mingguan** - Susun rencana makan mingguan dengan rekomendasi otomatis
- **🏃 Saran Aktivitas Fisik** - Terima rekomendasi olahraga yang sesuai dengan tujuan dan kondisi fisik Anda
- **🔔 Pengingat Check-in** - Dapatkan notifikasi untuk check-in harian dan jadwal makan
- **📱 Antarmuka Responsif** - Akses aplikasi dengan nyaman dari berbagai perangkat

## 🛠️ Teknologi

### Backend

- **Flask** - Python web framework
- **SQLite** - Database ringan
- **Pandas** - Analisis data
- **Scikit-learn** - Machine learning untuk rekomendasi diet

### Frontend

- **React** - Framework JavaScript untuk UI
- **Tailwind CSS** - Framework CSS untuk styling
- **Chart.js** - Visualisasi data dan grafik progress
- **Axios** - HTTP client untuk API requests

## 🚀 Instalasi dan Penggunaan

### Prasyarat

- Python 3.8+
- Node.js 14+
- npm atau yarn

### Langkah-langkah Instalasi

#### Backend

```bash
# Clone repository
git clone https://github.com/yourusername/meal-mind-project.git
cd meal-mind-project/backend

# Buat virtual environment
python -m venv venv

# Aktifkan virtual environment
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Siapkan database
flask db init
flask db migrate
flask db upgrade

# Jalankan server
flask run
```

#### Frontend

```bash
# Pindah ke direktori frontend
cd ../frontend

# Install dependencies
npm install

# Jalankan aplikasi
npm run dev
```

## 📷 Screenshots

![image](https://github.com/user-attachments/assets/fbbdb4cd-e6b0-4592-9411-d6347cbc9c8e) 
![image](https://github.com/user-attachments/assets/8cc8ab57-0243-4767-8987-49a114cf0008)
![image](https://github.com/user-attachments/assets/6f61a460-7e28-4de0-8951-dc97e2bf7ca0)
![image](https://github.com/user-attachments/assets/e999e09f-624b-48ff-ba6a-e5280b8376e1)
![image](https://github.com/user-attachments/assets/e56ac9ab-d82d-4121-9f08-4cf32136e864)


## 🧪 Struktur Proyek

```
meal-mind-project/
├── backend/
│   ├── app/
│   │   ├── models/       # Model database
│   │   ├── routes/       # API endpoints
│   │   └── ml/           # Algoritma machine learning
│   ├── migrations/       # Database migrations
│   └── instance/         # Instance database
├── frontend/
│   ├── public/           # Aset statis
│   └── src/
│       ├── components/   # Komponen React
│       ├── hooks/        # Custom hooks
│       └── pages/        # Halaman aplikasi
└── docs/                 # Dokumentasi
```

## 🤝 Kontribusi

Kontribusi sangat diterima dan diharapkan! Berikut adalah langkah-langkah untuk berkontribusi:

1. Fork repository
2. Buat branch fitur baru (`git checkout -b feature/AmazingFeature`)
3. Commit perubahan Anda (`git commit -m 'Add some AmazingFeature'`)
4. Push ke branch (`git push origin feature/AmazingFeature`)
5. Buka Pull Request

## 📝 Lisensi

Proyek ini dilisensikan di bawah Lisensi MIT - lihat file [LICENSE](LICENSE) untuk detailnya.

## 📞 Kontak

Nama Anda - [@twitter_handle](https://twitter.com/twitter_handle) - email@example.com

Link Proyek: [https://github.com/yourusername/meal-mind-project](https://github.com/yourusername/meal-mind-project)

---

<p align="center">
  Dibuat dengan ❤️ oleh Tim MealMind
</p>
# Meal-Mind
