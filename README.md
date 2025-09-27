# WAHYUDINFLIX2

Aplikasi streaming scraper yang memungkinkan pengguna menemukan dan menonton film serta serial TV dari berbagai sumber.

## Fitur

- Pencarian film dan serial TV
- Scraping konten dari berbagai situs
- Player embedded untuk menonton konten
- UI yang menyerupai platform streaming populer

## Instalasi Lokal atau VPS

### Prasyarat

- Python 3.8 atau lebih baru
- pip (Python package manager)
- Git

### Langkah-langkah Instalasi

1. **Clone repository**
   ```bash
   git clone https://github.com/tuwiliyt/wahyudinflix2.git
   cd wahyudinflix2
   ```

2. **Buat virtual environment (disarankan)**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Di Linux/Mac
   # atau
   venv\Scripts\activate  # Di Windows
   ```

3. **Instal dependensi**
   ```bash
   pip install -r requirements.txt
   ```

4. **Jalankan aplikasi**
   ```bash
   cd wahyudinfl2x
   python app.py
   ```

   Atau menggunakan gunicorn (lebih stabil untuk produksi):
   ```bash
   gunicorn wahyudinfl2x.app:app
   ```

5. **Akses aplikasi**
   Buka browser dan kunjungi `http://localhost:5000` atau sesuaikan dengan port yang digunakan.

## Konfigurasi di VPS

### Menggunakan systemd (Ubuntu/Debian)

1. **Buat user khusus untuk aplikasi**
   ```bash
   sudo useradd -r -s /bin/false wahyudinfl2x
   ```

2. **Pindahkan kode ke direktori aplikasi**
   ```bash
   sudo cp -r /path/to/wahyudinflix2 /opt/wahyudinfl2x
   sudo chown -R wahyudinfl2x:wahyudinfl2x /opt/wahyudinfl2x
   ```

3. **Buat file service systemd**
   ```bash
   sudo nano /etc/systemd/system/wahyudinfl2x.service
   ```

4. **Tambahkan konfigurasi berikut**
   ```
   [Unit]
   Description=WAHYUDINFLIX2 Application
   After=network.target

   [Service]
   Type=exec
   User=wahyudinfl2x
   WorkingDirectory=/opt/wahyudinfl2x
   Environment=PATH=/opt/wahyudinfl2x/venv/bin
   ExecStart=/opt/wahyudinfl2x/venv/bin/gunicorn --bind 0.0.0.0:5000 --workers 2 wahyudinfl2x.app:app
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

5. **Aktifkan dan jalankan service**
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable wahyudinfl2x
   sudo systemctl start wahyudinfl2x
   ```

### Deploy dengan Nginx (opsional)

Jika Anda ingin menambahkan Nginx sebagai reverse proxy:

1. **Instal Nginx**
   ```bash
   sudo apt update
   sudo apt install nginx
   ```

2. **Konfigurasi Nginx**
   ```bash
   sudo nano /etc/nginx/sites-available/wahyudinfl2x
   ```

3. **Tambahkan konfigurasi berikut**
   ```
   server {
       listen 80;
       server_name nama-domain-anda.com;

       location / {
           proxy_pass http://127.0.0.1:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   ```

4. **Aktifkan situs**
   ```bash
   sudo ln -s /etc/nginx/sites-available/wahyudinfl2x /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   ```

## Konfigurasi Port

Secara default, aplikasi berjalan di port 5000. Anda dapat mengganti port dengan:

```bash
export PORT=8000  # atau port pilihan Anda
python app.py
```

Atau menggunakan gunicorn:
```bash
gunicorn --bind 0.0.0.0:8000 wahyudinfl2x.app:app
```

## Perbedaan dengan Deployment Cloud

Dibandingkan deployment di platform cloud seperti Render, di server lokal/VPS:

- Anda memiliki kontrol penuh atas IP yang digunakan untuk scraping
- Lebih mungkin untuk menghindari pemblokiran dari situs target
- Anda bertanggung jawab penuh atas keamanan dan pemeliharaan server
- Tidak ada batasan deployment yang diberlakukan platform cloud

## Troubleshooting

### Error saat scraping
Jika scraping gagal, kemungkinan besar karena:
- Sistem keamanan situs target mendeteksi permintaan sebagai bot
- IP server Anda diblokir oleh situs target

### Kinerja lambat
- Pastikan server memiliki cukup RAM dan CPU
- Tambahkan lebih banyak worker di gunicorn sesuai kebutuhan

## Catatan Penting

Aplikasi ini menggunakan teknik web scraping untuk mengambil data dari situs eksternal. Pastikan untuk:
- Mematuhi terms of service situs yang di-scrape
- Menghormati rate limits dan kebijakan akses
- Menggunakan aplikasi dengan tanggung jawab

## Lisensi

Proyek ini adalah proyek pribadi untuk tujuan pembelajaran dan eksperimental.