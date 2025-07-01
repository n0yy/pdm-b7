# 📊 **Dashboard Predictive Maintenance (PdM)**

Dashboard monitoring mesin Ilapak 3 secara real-time menggunakan pendekatan _Machine Learning_ untuk mendeteksi anomali dan kebocoran produk secara prediktif.

---

## 🏭 **Overview**

Dashboard ini menampilkan metrik-metrik penting untuk memantau kinerja mesin pengemasan **Ilapak 3**:

![Tab Overview](assets/overview.png)
_Tab Overview: Menampilkan metrik OEE, Ketersediaan, Kinerja, dan Kualitas secara real-time_

![Tab Temperatur](assets/temperature.png)
_Tab Temperatur: Memantau suhu dari 4 titik penyegelan_

![Tab Produksi](assets/production.png)
_Tab Produksi: Memantau kecepatan produksi (RPM), jumlah output, dan tingkat reject_

![Tab Prediksi Kebocoran](assets/leakage_prediction.png)
_Tab Prediksi Kebocoran: Menampilkan prediksi kebocoran berbasis ML, skor kepercayaan, dan distribusi status_

---

## 🧠 Perbandingan Model

| Model         | ROC AUC Score | F1-Score | Accuracy | Precision | Recall   |
| ------------- | ------------- | -------- | -------- | --------- | -------- |
| Random Forest | 0.991143      | 0.882334 | 0.974037 | 0.923292  | 0.853553 |
| LightGBM      | 0.992471      | 0.897406 | 0.976678 | 0.930151  | 0.872522 |
| XGBoost       | 0.991472      | 0.884185 | 0.973707 | 0.915510  | 0.860485 |
| LSTM          | 0.974201      | 0.778972 | 0.960704 | 0.874425  | 0.746912 |

## 📑 **Nomenklatur Datalog ILAPAK 3**

Tabel berikut menjelaskan nomenklatur yang digunakan dalam datalog mesin ILAPAK 3:

### **Tabel Nomenklatur**

| **Nama Kolom (Inggris)**                     | **Nama Kolom (Indonesia)**         | **Deskripsi**                                    |
| -------------------------------------------- | ---------------------------------- | ------------------------------------------------ |
| `times`                                      | Waktu                              | Waktu pencatatan data                            |
| `Shift`                                      | Shift                              | Shift kerja (Pagi/Siang/Malam)                   |
| `Status`                                     | Status Mesin                       | Kondisi mesin (Running, Stopped, Alarm, dll.)    |
| `Suhu Sealing Vertikal Bawah (°C)`           | Suhu Seal Vertikal Bawah           | Suhu elemen penyegel bawah                       |
| `Suhu Sealing Vertikal Atas (°C)`            | Suhu Seal Vertikal Atas            | Suhu elemen penyegel atas                        |
| `Suhu Sealing Horizontal Depan/Kanan (°C)`   | Suhu Seal Horizontal Depan/Kanan   | Suhu penyegel horizontal kanan/depan             |
| `Suhu Sealing Horizontal Belakang/Kiri (°C)` | Suhu Seal Horizontal Belakang/Kiri | Suhu penyegel horizontal kiri/belakang           |
| `Counter Output (pack)`                      | Output Kemasan                     | Jumlah kemasan berhasil                          |
| `Counter Reject (pack)`                      | Reject Kemasan                     | Jumlah kemasan gagal                             |
| `Speed (rpm)`                                | Kecepatan (rpm)                    | Kecepatan mesin                                  |
| `Availability (%)`                           | Ketersediaan                       | Waktu siap operasi dibandingkan total waktu      |
| `Performance (%)`                            | Kinerja                            | Efisiensi kecepatan produksi                     |
| `Quality (%)`                                | Kualitas                           | Produk baik dibandingkan total produksi          |
| `OEE (%)`                                    | Efektivitas Total Mesin            | Kombinasi Availability, Performance, dan Quality |
| `Jaws Position`                              | Posisi Rahang                      | Posisi rahang penyegel                           |
| `Knife Position`                             | Posisi Pisau                       | Posisi pisau pemotong                            |
| `Pump Position Stop`                         | Posisi Stop Pompa                  | Status posisi pompa                              |
| `Doser Drive Enable`                         | Aktivasi Dosing                    | Status sistem dosing                             |
| `Sealing Enable`                             | Aktivasi Penyegelan                | Status sistem penyegelan                         |
| `Machine Alarm`                              | Alarm Mesin                        | Kode alarm bila terjadi gangguan                 |
| `Downtime (hh:mm:ss)`                        | Waktu Henti                        | Total waktu mesin berhenti                       |
| `Output Time (hh:mm:ss)`                     | Waktu Produksi                     | Total waktu produksi aktif                       |
| `Total Time (hh:mm:ss)`                      | Total Waktu                        | Jumlah waktu produksi dan downtime               |

---

### **Catatan Tambahan**

- **Sealing**: Proses penyegelan kemasan (vertikal/horizontal)
- **Jaws**: Rahang penyegel (jenis rotary atau long dwell)
- **OEE**: Metrik untuk mengukur efektivitas total mesin

---

## 🚀 **Fitur Utama**

### Pemantauan Real-time

- 🔁 Auto-refresh data (30s–5 menit)
- 📊 Visualisasi interaktif (Plotly)
- 🧭 Navigasi multi-tab
- 🔴 Indikator status mesin & koneksi

### Analitik Prediktif

- 🤖 Prediksi kebocoran berbasis ML
- 🧠 Confidence Score
- 🏷️ Deteksi anomali (Normal, Warning, Leak)
- 🕰️ Tren historis

### Fitur Teknis

- ⚡ Strategi caching berlapis
- 🛢️ Integrasi database MySQL
- 📱 Desain responsif
- 🚨 Penanganan error dan logging

---

## 📋 **Kebutuhan Sistem**

- Python 3.11+
- Database MySQL
- RAM ≥ 4 GB
- Browser modern (Chrome/Firefox)

### 📦 **Dependensi Utama**

- `streamlit` — Framework dasbor web
- `plotly` — Visualisasi interaktif
- `scikit-learn` — Pipeline ML
- `lightgbm` — Model boosting
- `sqlalchemy` — ORM database
- `pandas` dan `numpy` — Pemrosesan data

---

## 🛠️ **Instalasi**

### 1. Kloning Repository

```bash
git clone <repository-url>
cd lstm-ae-anomaly-detection
```

### 2. Persiapkan Lingkungan Virtual

```bash
python -m venv venv
source venv/bin/activate      # Linux/Mac
venv\Scripts\activate         # Windows

pip install -e .
```

### 3. Konfigurasi Database

Buat file `.env`:

```env
DB_USER=nama_user
DB_PASSWORD=password
DB_HOST=localhost
DB_NAME=nama_database
```

### 4. Setup Model

Pastikan file model tersedia di:

```
src/models/v1/ilapak3/lgbm-model-ilapak3-v1.0.0.pkl
```

---

## 🚦 **Penggunaan**

### Menjalankan Aplikasi

```bash
python main.py
```

Buka browser: [http://localhost:8501](http://localhost:8501)

### Kontrol Dasbor

- 🔄 **Auto-refresh**
- 🕒 **Rentang waktu histori**
- 🔃 **Refresh manual**
- 🧭 **Navigasi antar tab**

---

## 🧭 **Navigasi Tab Dasbor**

### 1. Tab Overview

- 📈 Tren Efisiensi: OEE, Availability, Performance, Quality
- 🧮 Data Terbaru: Tabel data terkini
- 📊 Analisis Historis

### 2. Tab Temperatur

- 🌡️ Pembacaan suhu real-time
- 📉 Statistik suhu (min, max, rata-rata)
- 🚨 Indikator warna per suhu

### 3. Tab Produksi

- ⚙️ Monitor kecepatan (RPM)
- 📦 Output & reject count
- 📊 Korelasi produksi vs reject

### 4. Tab Prediksi Kebocoran

- 🧠 Hasil prediksi kebocoran (Normal/Warning/Leak)
- 📊 Distribusi status
- 🔍 Confidence Score
- ⏳ Tren kebocoran historis

---

## 🔧 **Konfigurasi Sistem**

File: `src/dashboard/config/settings.py`

```python
REFRESH_INTERVALS = [30, 60, 120, 300]
DEFAULT_REFRESH_INTERVAL = 60

TEMP_WARNING_THRESHOLD = 150
TEMP_DANGER_THRESHOLD = 250

PERFORMANCE_WARNING_THRESHOLD = 70
QUALITY_WARNING_THRESHOLD = 95
OEE_WARNING_THRESHOLD = 70
```

---

## 📁 **Struktur Proyek**

```
lstm-ae-anomaly-detection/
├── main.py
├── pyproject.toml
├── src/
│   ├── dashboard/
│   │   ├── app.py
│   │   ├── components/
│   │   ├── tabs/
│   │   ├── utils/
│   │   └── config/
│   └── models/
└── README.md
```

---

## 🔒 **Keamanan**

- 🔐 Variabel lingkungan di `.env`
- 🛡️ Perlindungan SQL Injection (SQLAlchemy)
- 🔒 Koneksi database dengan TLS
- 🧼 Validasi dan sanitasi input

---

## ⚙️ **Optimasi Performa**

### Caching & Memory

- 🕒 Caching data (10–60 detik TTL)
- 💾 Caching hasil prediksi (15–30 detik TTL)
- 🧠 Pemrosesan batch
- 🧹 Pembersihan cache otomatis

---

## 🐛 **Pemecahan Masalah**

| Masalah                  | Solusi                                          |
| ------------------------ | ----------------------------------------------- |
| ❌ Gagal koneksi DB      | Periksa file `.env`, pastikan server jalan      |
| ❌ Model gagal dimuat    | Periksa path model & izin file                  |
| ❌ Lambat/performa buruk | Kurangi refresh & rentang waktu histori         |
| 🔄 Data tidak update     | Pastikan auto-refresh aktif atau refresh manual |

---

## 🧪 **Pengembangan Lokal**

```bash
pip install -e .
streamlit run src/dashboard/app.py --server.enableWebsocketCompression=false
```

### Standar Kode

- ✅ Tipe data (type hint)
- 🧱 Logging & error handling
- 📚 Dokumentasi internal

---

## 👥 Kontributor

Built by **@nangdosan** – BTS Batch 3
