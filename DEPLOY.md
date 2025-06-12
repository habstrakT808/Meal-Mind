# Panduan Deployment MealMind

Dokumen ini berisi panduan untuk men-deploy aplikasi MealMind ke berbagai platform.

## Deploy ke VPS (DigitalOcean, AWS EC2, Linode, dll)

### 1. Persiapan Server

```bash
# Update package list
sudo apt update
sudo apt upgrade -y

# Install Docker dan Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.26.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install Nginx
sudo apt install nginx -y
```

### 2. Clone Repository

```bash
git clone https://github.com/yourusername/meal-mind.git
cd meal-mind
```

### 3. Konfigurasi Nginx

```bash
# Salin file konfigurasi Nginx
sudo cp nginx.conf /etc/nginx/sites-available/mealmind

# Aktifkan konfigurasi
sudo ln -s /etc/nginx/sites-available/mealmind /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 4. Deploy dengan Docker Compose

```bash
# Build dan jalankan container
docker-compose up -d --build
```

### 5. Konfigurasi SSL/TLS dengan Certbot

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Dapatkan sertifikat SSL
sudo certbot --nginx -d mealmind.yourdomain.com
```

## Deploy ke Railway

1. Instal Railway CLI:
   ```bash
   npm install -g @railway/cli
   ```

2. Login ke Railway:
   ```bash
   railway login
   ```

3. Inisialisasi proyek:
   ```bash
   railway init
   ```

4. Deploy proyek:
   ```bash
   railway up
   ```

## Deploy ke Heroku

1. Instal Heroku CLI:
   ```bash
   npm install -g heroku
   ```

2. Login ke Heroku:
   ```bash
   heroku login
   ```

3. Buat aplikasi Heroku:
   ```bash
   heroku create meal-mind-app
   ```

4. Set stack ke container:
   ```bash
   heroku stack:set container
   ```

5. Deploy aplikasi (pastikan file heroku.yml sudah ada):
   ```bash
   git push heroku main
   ```

## Menggunakan Ngrok untuk Testing

1. Jalankan aplikasi dengan Docker Compose:
   ```bash
   docker-compose up
   ```

2. Di terminal terpisah, jalankan Ngrok untuk frontend:
   ```bash
   ngrok http 5173
   ```

3. Di terminal lain, jalankan Ngrok untuk backend:
   ```bash
   ngrok http 5000
   ```

4. Gunakan URL yang diberikan oleh Ngrok untuk mengakses aplikasi

## Tips untuk Production

1. Gunakan variabel lingkungan untuk menyimpan kredensial
2. Aktifkan HTTPS untuk semua koneksi
3. Siapkan backup reguler untuk database
4. Implementasikan monitoring dan logging
5. Atur auto-scaling jika diperlukan 