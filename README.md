# Hand Tracking - Fanzzx

Program hand tracking berbasis Python yang mendeteksi jumlah jari dan menampilkan teks serta suara Google bahasa Indonesia.

##  Fitur
- Deteksi 1-5 jari secara real-time
- Suara Google Text-to-Speech bahasa Indonesia (wanita)
- Tampilan teks di layar
- Debug panel status tiap jari

##  Pesan per Jari
| Jari | Teks |
|------|------|
|  1 | Halo perkenalkan |
|  2 | Nama saya |
|  3 | Fanzzx saya |
|  4 | Adalah pengembang |
|  5 | Program ini |

##  Kebutuhan
- Python 3.8 - 3.13 (disarankan 3.11)
- Webcam
- Koneksi internet (untuk generate suara pertama kali)

##  Cara Install & Jalankan

### 1. Clone repository
```bash
git clone https://github.com/username/hand-tracking.git
cd hand-tracking
```

### 2. Install semua library
```bash
python -m pip install -r requirements.txt
```

### 3. Jalankan program
```bash
python hand_tracking.py
```

### 4. Keluar program
Tekan **Q** atau **ESC** pada jendela kamera.

##  Struktur File
```
hand-tracking/
├── hand_tracking.py   # Program utama
├── requirements.txt   # Daftar library
├── install.bat        # Install otomatis (Windows)
└── README.md          # Dokumentasi
```

##  Developer
**Fanzzx**
