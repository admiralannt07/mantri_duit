# MAGATRA

> Your Personal Financial Reality Checker.
> Aplikasi pencatat keuangan berbasis Chat & OCR dengan fitur "Reality Check" untuk menjaga kesehatan finansial UMKM.

<img width="1406" height="672" alt="banner_magatra" src="https://github.com/user-attachments/assets/002e9bfd-39ac-404d-b354-2b1970608367" />

## About The Project

MAGATRA bukan sekadar aplikasi pencatat keuangan biasa (CRUD). Masalah utama generasi muda dan pelaku UMKM bukan hanya pada cara mencatat, melainkan disiplin dan kesadaran akan arus kas (*cashflow*).

MAGATRA hadir dengan pendekatan "Chat-First" yang interaktif, dilengkapi OCR cerdas untuk kemudahan input nota, dan fitur unggulan "Reality Check" yang memberikan umpan balik finansial—terkadang dengan gaya sarkas dan tegas—berdasarkan kebiasaan belanja pengguna dan kondisi saldo aktual.

---

## Screenshots & Demo

Lihat bagaimana MAGATRA bekerja melalui tangkapan layar fitur utamanya di bawah ini.

### 1. Dashboard & Reality Check
Visualisasi arus kas real-time dengan status kesehatan finansial yang "jujur" dan indikator visual sederhana.

<img width="600" height="auto" alt="dashboard magatra" src="https://github.com/user-attachments/assets/b8fc39f2-145a-4ae5-9ce8-5eabaeed6ea2" />


### 2. Smart OCR Scanning
Proses pindai struk belanja fisik yang otomatis mendeteksi merchant, total, dan kategori menggunakan Google Gemini 2.5 Flash.

<img width="600" height="auto" alt="scan nota magatra" src="https://github.com/user-attachments/assets/1ec3e3cd-5721-48cc-aa33-a165d38cc5b7" />


### 3. Sarcastic Chat Advisor
Interaksi dengan AI "Satpam Keuangan" yang memberikan respon lucu namun menohok saat pengguna ingin melakukan pengeluaran impulsif.

<img width="600" height="auto" alt="chat mantri magatra" src="https://github.com/user-attachments/assets/fdf7f961-f9c5-4d4b-82a8-65553f252fc7" />


### 4. Mobile Navigation & Context Switching
Desain responsif untuk perangkat mobile. Fitur **Context Switching** pada header memungkinkan pengguna mengganti profil/konteks usaha (misal: dari "Warung Kelontong" ke "Startup Tech") secara instan, yang akan mengubah gaya bahasa dan perspektif roasting dari AI.

<img width="600" height="auto" alt="konteks switch magatra" src="https://github.com/user-attachments/assets/44f0ebf8-3363-4a45-b42e-ed0d89ad1bb8" />
<img width="auto" height="340" alt="mobile header responsive" src="https://github.com/user-attachments/assets/db8297fe-a04f-4afd-9276-9c69e178bd11" />


### 5. Transaction History (CRUD)
Manajemen riwayat transaksi yang lengkap dengan fitur pencarian, filter, dan kemampuan edit/hapus data.

<img width="600" height="auto" alt="history magatra" src="https://github.com/user-attachments/assets/e5b86301-2996-4aed-89d2-32ff20490410" />

---

## Key Features

* **Chat-Based Entry**
  Catat pengeluaran semudah mengirim pesan. Didukung oleh HTMX untuk pengalaman yang responsif tanpa reload halaman penuh.

* **Smart OCR with Gemini 2.5 Flash**
  Scan struk belanja fisik atau bukti transfer. Sistem akan otomatis memvalidasi gambar dan mengonversi menjadi data transaksi terstruktur (Nama Merchant, Total, Tanggal, Kategori, Tipe Transaksi IN/OUT).

* **Reality Check & Sarcastic Advisor**
  Analisis AI yang bertindak sebagai "Satpam Keuangan". AI akan memberikan peringatan keras jika rasio pengeluaran terhadap modal usaha mencapai titik kritis (Logic 50/30/10).

* **Financial Dashboard**
  Visualisasi arus kas real-time dengan indikator visual sederhana untuk memantau kesehatan finansial secara instan.

* **Context-Aware Memory**
  Chatbot memiliki memori jangka pendek untuk mengingat konteks percakapan sebelumnya dan profil usaha pengguna, membuat interaksi terasa personal.

---

## Tech Stack

Project ini dibangun dengan arsitektur Monolith yang modular, memanfaatkan teknologi modern untuk performa dan skalabilitas:

* **Backend Framework**: Django 5.0 (Python)
* **Frontend Interactivity**: HTMX & Alpine.js logic
* **Styling**: Tailwind CSS v4 + DaisyUI 5
* **Database**: SQLite (Development) / PostgreSQL (Production)
* **AI & OCR Engine**: Google Gemini 2.5 Flash
* **Deployment**: Railway (Gunicorn + WhiteNoise)

---

## Project Structure

Struktur folder project disusun agar mudah dipahami, modular, dan mengikuti prinsip Clean Architecture pada Django:

```text
mantri_duit/
├── config/                 # Konfigurasi Utama Project (Settings, URL Routing)
├── core/                   # Logika Utama Aplikasi
│   ├── services/           # Service Layer (Business Logic & AI)
│   │   ├── chat_service.py # Logic Chat, Memori, & Persona AI
│   │   ├── ocr_handler.py  # Logic, Validasi & Handling OCR Struk
│   │   ├── prompts.py      # System Instructions & Prompt Engineering
│   │   └── gemini_client.py# Integrasi Client Google Gemini
│   ├── views/              # Modular Controllers (Auth, Transaksi, Chat)
│   ├── models.py           # Schema Database
│   └── forms.py            # Validasi Input Form
├── static/                 # Static Files
│   ├── src/                # Source CSS (Input Tailwind)
│   ├── dist/               # Compiled CSS (Output Tailwind)
│   └── js/                 # Custom JavaScript
├── templates/              # HTML Templates
│   ├── auth/               # Halaman Login & Register
│   ├── dashboard/          # Halaman Utama Aplikasi (Chat, Scan, History)
│   ├── partials/           # Komponen HTMX Reusable
│   └── layout/             # Base Layout & Navbar
├── manage.py               # Entry Point Django
├── Procfile                # Konfigurasi Deployment (Gunicorn)
└── requirements.txt        # Daftar Dependency Python
````

-----

## Getting Started

Ikuti langkah ini untuk menjalankan project di komputer lokal Anda.

### Prerequisites

Pastikan Anda sudah menginstall perangkat lunak berikut:

  * **Python 3.10** atau lebih baru
  * **Git**
  * **Node.js LTS (v24.11.1)** & **NPM** (Wajib untuk kompilasi Tailwind CSS v4)

### 1\. Clone Repository

```bash
git clone https://github.com/admiralannt07/mantri_duit.git
cd mantri_duit
```

### 2\. Setup Virtual Environment

Disarankan menggunakan virtual environment agar dependencies Python tidak bentrok dengan sistem utama.

**Windows:**

```bash
python -m venv env
env\Scripts\activate
```

**Mac / Linux:**

```bash
python3 -m venv env
source env/bin/activate
```

### 3\. Install Python Dependencies

Install library backend yang dibutuhkan (Django, Google Generative AI, dll).

```bash
pip install -r requirements.txt
```

### 4\. Install Node Dependencies & Build CSS

Karena project ini menggunakan Tailwind CSS v4, Anda **wajib** melakukan instalasi paket dan *build* aset statis sebelum menjalankan server agar tampilan tidak rusak (404).

```bash
# Install package (Tailwind & DaisyUI)
npm install

# Build file CSS output ke static/dist/styles.css
npm run build
```

> **Note:** Untuk development (auto-reload CSS), Anda bisa membiarkan terminal lain menjalankan `npm run dev`.

### 5\. Environment Configuration

Duplikasi file contoh `.env.example` (jika ada) atau buat file `.env` baru di root folder project.

Isi variabel berikut:

```env
SECRET_KEY=django-insecure-kunci-rahasia-anda
DEBUG=True
GEMINI_API_KEY=Isi_Dengan_API_Key_Google_AI_Studio_Anda
```

> **Note:** Anda bisa mendapatkan Gemini API Key secara gratis di [Google AI Studio](https://aistudio.google.com/).

### 6\. Database Setup

Jalankan migrasi database untuk membuat tabel-tabel yang diperlukan oleh aplikasi (User, Transaction, ChatHistory, UserProfile).

```bash
python manage.py migrate
```

### 7\. Run the Application

Jalankan server development lokal.

```bash
python manage.py runserver
```

Buka browser dan akses aplikasi di: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

--------

## Testing Strategy

MAGATRA memprioritaskan stabilitas aplikasi. Kami menerapkan **Unit Testing** dan **Integration Testing** yang komprehensif untuk memastikan setiap fitur berjalan sesuai logika bisnis.

### Advanced Mocking Architecture
Salah satu tantangan dalam mengetes aplikasi AI adalah ketergantungan pada API eksternal (Google Gemini).

Untuk mengatasinya, kami menggunakan teknik **Mocking (`unittest.mock`)**. Sistem testing kami memanipulasi respons AI secara lokal sehingga:
1.  **Cepat**: Tidak ada latensi jaringan.
2.  **Stabil**: Tidak terpengaruh koneksi internet.
3.  **Cost-Effective**: Tidak memakan kuota API Key saat testing.

### Running Tests
Pastikan virtual environment aktif, lalu jalankan perintah:

```bash
python manage.py test
````

Untuk melihat laporan cakupan kode (*Code Coverage*):

```bash
coverage run --source='core' manage.py test
coverage report
```


### Demo Video

Lihat demonstrasi lengkap fitur MAGATRA dalam aksi:

<video width="1406" height="672" autoplay 
    loop alt="banner_magatra" src="https://github.com/user-attachments/assets/524c6252-ff34-4229-8d1a-8471d63030c8" />

-----

## Team

Dibuat oleh **AI Enslavement Team**.
