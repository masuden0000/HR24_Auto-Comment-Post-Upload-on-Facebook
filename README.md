# 🤖 Facebook Auto Comment Bot

Bot otomatis untuk mengirim komentar di postingan Facebook menggunakan Python dan Selenium. Mendukung login otomatis, anti-deteksi, pengulangan komentar, dan penanganan verifikasi Facebook.

## ✨ Fitur Utama

- 🔐 **Login Otomatis** - Login ke Facebook secara otomatis
- 🛡️ **Anti-Deteksi** - Teknologi anti-deteksi untuk menghindari pembatasan
- 🔄 **Pengulangan Komentar** - Kirim semua komentar berulang kali sesuai konfigurasi
- ⏰ **Jeda Kustomisasi** - Atur jeda antar komentar dan ulangan
- 🔒 **Handling Verifikasi** - Deteksi dan tangani CAPTCHA, 2FA, Security Checkpoint
- 📱 **User-Friendly** - Antarmuka terminal yang informatif dan mudah dipahami

## �️ Kebutuhan Sistem

- Windows 10/11
- Python 3.7+
- Google Chrome browser
- Koneksi internet yang stabil

## � Instalasi

### 1. Install Python

Download dan install Python dari [python.org](https://python.org/downloads/)

### 2. Install Dependencies

Buka Command Prompt/Terminal dan jalankan:

```bash
pip install selenium webdriver-manager
pip install selenium
```

### 3. Download Script

Download file `skrip.py` ke komputer Anda.

## ⚙️ Konfigurasi

Buka file `skrip.py` dengan text editor dan ubah bagian pengaturan berikut:

```python
# --- PENGATURAN - GANTI SESUAI KEBUTUHAN LO ---
EMAIL_LO = "email_facebook_anda@gmail.com"
PASSWORD_LO = "password_facebook_anda"
URL_POSTINGAN = "https://www.facebook.com/username/posts/1234567890"
KOMENTAR_LO = [
    "Komentar pertama",
    "Komentar kedua",
    "Komentar ketiga",
    "Dan seterusnya..."
]
JEDA_WAKTU = 5                    # Jeda awal sebelum mulai komentar (detik)
JEDA_ANTAR_KOMENTAR_MIN = 15      # Jeda minimum antar komentar (detik)
JEDA_ANTAR_KOMENTAR_MAX = 25      # Jeda maksimum antar komentar (detik)
ULANG_KOMENTAR = 5                # Berapa kali mengulang semua komentar
JEDA_ANTAR_ULANGAN = 120          # Jeda antar ulangan komentar (detik)
```

### 📝 Penjelasan Konfigurasi

| Parameter                 | Deskripsi                       | Contoh                           |
| ------------------------- | ------------------------------- | -------------------------------- |
| `EMAIL_LO`                | Email/username Facebook         | `"user@gmail.com"`               |
| `PASSWORD_LO`             | Password Facebook               | `"password123"`                  |
| `URL_POSTINGAN`           | Link postingan target           | `"https://www.facebook.com/..."` |
| `KOMENTAR_LO`             | List komentar yang akan dikirim | `["komen1", "komen2"]`           |
| `JEDA_WAKTU`              | Waktu tunggu awal               | `5` (detik)                      |
| `JEDA_ANTAR_KOMENTAR_MIN` | Jeda minimum antar komentar     | `15` (detik)                     |
| `JEDA_ANTAR_KOMENTAR_MAX` | Jeda maksimum antar komentar    | `25` (detik)                     |
| `ULANG_KOMENTAR`          | Jumlah pengulangan              | `5` (kali)                       |
| `JEDA_ANTAR_ULANGAN`      | Jeda antar ulangan              | `120` (detik/2 menit)            |

## 🚀 Cara Menjalankan

1. **Buka Command Prompt/Terminal**
2. **Navigasi ke folder script**:
   ```bash
   cd path/to/folder/script
   ```
3. **Jalankan bot**:
   ```bash
   python skrip.py
   ```

## 🔄 Alur Kerja Bot

1. **🚀 Inisialisasi** - Bot setup Chrome dengan konfigurasi anti-deteksi
2. **🔐 Login** - Login otomatis ke Facebook menggunakan kredensial
3. **🛡️ Deteksi Verifikasi** - Bot mendeteksi CAPTCHA/2FA/Security Checkpoint
4. **👤 Manual Intervention** - Jika ada verifikasi, bot minta user selesaikan manual
5. **🎯 Navigasi** - Bot buka postingan target
6. **💬 Komentar** - Bot kirim semua komentar dengan jeda random
7. **🔄 Pengulangan** - Ulangi proses komentar sesuai konfigurasi
8. **✅ Selesai** - Bot tutup browser dan selesai

## 🔒 Penanganan Verifikasi

Bot dapat mendeteksi dan menangani berbagai jenis verifikasi Facebook:

### ✅ Yang Didukung:

- **CAPTCHA** - Sistem anti-bot Facebook
- **Two-Factor Authentication (2FA)** - Verifikasi dua langkah
- **Security Checkpoint** - Pemeriksaan keamanan Facebook
- **Account Verification** - Verifikasi akun Facebook
- **Authentication Platform** - Platform autentikasi Facebook

### 🤝 Proses Manual:

1. Bot mendeteksi verifikasi
2. Bot tampilkan pilihan: Selesaikan manual (Y) atau Batalkan (N)
3. Jika pilih Y: Bot menunggu user selesaikan di browser
4. User selesaikan verifikasi manual di browser
5. User tekan Enter di terminal setelah selesai
6. Bot melanjutkan proses

## ⚠️ Troubleshooting

### 🔴 Error Umum:

**1. "ChromeDriver not found"**

```
Solusi: Install ulang dengan: pip install --upgrade webdriver-manager
```

**2. "Login gagal"**

```
Solusi:
- Periksa email/password
- Selesaikan CAPTCHA yang muncul
- Pastikan akun tidak di-suspend
```

**3. "Comment box tidak ditemukan"**

```
Solusi:
- Pastikan URL postingan benar
- Coba postingan yang lebih baru
- Pastikan akun memiliki akses ke postingan
```

**4. "Verifikasi timeout"**

```
Solusi:
- Selesaikan verifikasi lebih cepat
- Pilih "Selesaikan manual" jika ditanya
- Pastikan koneksi internet stabil
```

### 💡 Tips Mengatasi Masalah:

1. **Jika CAPTCHA muncul**: Selesaikan manual di browser, bot akan menunggu
2. **Jika diminta 2FA**: Masukkan kode dari HP, bot akan melanjutkan otomatis
3. **Jika Security Checkpoint**: Ikuti instruksi Facebook, lalu tekan Enter di terminal
4. **Jika bot stuck**: Tekan Ctrl+C untuk keluar, lalu coba lagi

## 🛡️ Keamanan & Best Practices

### ✅ Do's (Yang Boleh):

- Gunakan akun sendiri
- Atur jeda yang wajar (minimal 15 detik)
- Gunakan komentar yang relevan
- Test dengan postingan sendiri dulu
- Gunakan akun backup untuk testing

### ❌ Don'ts (Yang Tidak Boleh):

- Jangan gunakan untuk spam
- Jangan set jeda terlalu pendek (< 10 detik)
- Jangan gunakan akun utama untuk testing
- Jangan tinggalkan bot tanpa pengawasan
- Jangan gunakan untuk harassment

### 🔐 Tips Keamanan:

1. **Gunakan VPN** jika diperlukan
2. **Jangan share kredensial** dengan orang lain
3. **Backup script** sebelum modifikasi
4. **Monitor aktivitas** akun Facebook
5. **Stop jika ada warning** dari Facebook

## 📊 Contoh Output Terminal

```
============================================================
🤖 FACEBOOK AUTO COMMENT BOT
============================================================
📋 MODE: Login otomatis

📝 INSTRUKSI:
1. Pastikan email/password sudah benar
2. Script akan membuka Chrome otomatis dan login
3. Jika ada CAPTCHA/Verifikasi, selesaikan manual di browser
...

🚀 Memulai bot...
------------------------------------------------------------
Memulai bot auto comment...
✅ Driver Chrome berhasil di-setup.
Mencoba login otomatis...
Login request dikirim...
✅ Login berhasil!
Membuka postingan: https://www.facebook.com/...
Mencari kolom komentar...
Comment box ditemukan dengan selector: div[aria-label*='Tulis komentar']
Mengirim komentar...

� Ulangan ke-1 dari 5
Komentar ke-1 terkirim: 'ramaikan'
Menunggu 18.3 detik sebelum komentar berikutnya...
Komentar ke-2 terkirim: 'akun murah'
...
```

## 🔧 Customization

### Menambah Anti-Deteksi:

```python
# Tambah di bagian chrome_options
chrome_options.add_argument("--disable-popup-blocking")
chrome_options.add_argument("--disable-background-timer-throttling")
```

### Mengubah User Agent:

```python
# Ganti user agent di bagian setup
chrome_options.add_argument("--user-agent=YourCustomUserAgent")
```

### Menambah Selector Comment Box:

```python
# Tambah di list comment_selectors
comment_selectors = [
    "div[aria-label*='Tulis komentar']",
    "div[aria-label*='Write a comment']",
    "your_custom_selector_here",
    # ... selector lain
]
```

## 📈 Upgrade Ideas

- [ ] Support multiple accounts
- [ ] GUI interface dengan Tkinter
- [ ] Logging sistem ke file
- [ ] Statistik komentar yang dikirim
- [ ] Support untuk React/Like otomatis
- [ ] Database untuk menyimpan konfigurasi
- [ ] Scheduler untuk waktu tertentu

## ⚖️ Disclaimer

Script ini dibuat untuk tujuan edukasi dan automasi personal. Penggunaan harus mematuhi Terms of Service Facebook. Developer tidak bertanggung jawab atas penyalahgunaan atau konsekuensi dari penggunaan script ini.

## 📞 Support

Jika mengalami masalah:

1. Periksa bagian Troubleshooting di atas
2. Pastikan semua dependency terinstall
3. Coba dengan akun/postingan berbeda
4. Update Chrome ke versi terbaru

---
