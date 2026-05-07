# ✏️ Cara Ubah Pesan & Suara Google

## 📝 Cara Ubah Teks Pesan

Buka file `hand_tracking.py`, cari bagian ini di paling atas:

```python
MESSAGES = {
    1: "Halo perkenalkan",
    2: "Nama saya",
    3: "Fanzzx saya",
    4: "Adalah pengembang",
    5: "Program ini",
}
```

Ganti teks di dalam tanda kutip sesuai keinginan kamu.

### Contoh — Ganti nama:
```python
MESSAGES = {
    1: "Halo perkenalkan",
    2: "Nama saya",
    3: "Budi saya",
    4: "Adalah pengembang",
    5: "Program ini",
}
```

### Contoh — Ganti semua pesan:
```python
MESSAGES = {
    1: "Selamat datang",
    2: "Di program saya",
    3: "Nama saya Budi",
    4: "Saya dari Bandung",
    5: "Terima kasih",
}
```

Setelah diubah, **simpan file** lalu jalankan ulang program.

---

## 🔊 Cara Ubah Suara Google

Suara Google diatur di fungsi `pregenerate_audio()`.
Cari baris ini:

```python
tts = gTTS(text=teks, lang="id", slow=False)
```

### Ubah kecepatan bicara:
```python
# Normal
tts = gTTS(text=teks, lang="id", slow=False)

# Lebih lambat
tts = gTTS(text=teks, lang="id", slow=True)
```

### Ubah bahasa suara:
```python
# Bahasa Indonesia
tts = gTTS(text=teks, lang="id", slow=False)

# Bahasa Inggris
tts = gTTS(text=teks, lang="en", slow=False)

# Bahasa Jawa
tts = gTTS(text=teks, lang="jw", slow=False)

# Bahasa Sunda
tts = gTTS(text=teks, lang="su", slow=False)
```

---

## ⚠️ Penting
- Perubahan pesan & suara butuh **koneksi internet** saat pertama kali run
  karena suara di-generate ulang oleh Google
- Setelah diubah, jalankan ulang program agar perubahan aktif

---

## 👨‍💻 Developer
**Fanzzx**
