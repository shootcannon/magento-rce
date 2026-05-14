# Magento RCE Web Shell Uploader

<p align="center">
  <a href="https://www.youtube.com/watch?v=Wg2YMIyZBd4">
    <img src="https://img.youtube.com/vi/Wg2YMIyZBd4/maxresdefault.jpg" width="700">
  </a>
</p>

Skrip ini dirancang untuk melakukan pengujian penetrasi otomatis pada platform Magento yang rentan terhadap celah keamanan *file upload* melalui REST API dan GraphQL. Skrip ini secara otomatis akan mencoba mengunggah *web shell* yang disisipkan di dalam file PNG valid untuk melewati validasi sisi server.

## Fitur Utama

*   **Automated SKU Retrieval**: Mengambil SKU produk secara otomatis melalui endpoint GraphQL.
*   **Polyglot PNG Payload**: Membuat file PNG valid dengan *payload* PHP di dalam chunk `tEXt`.
*   **Multi-threading**: Mendukung pemindaian banyak domain sekaligus dengan *thread* yang dapat dikonfigurasi.
*   **Path Discovery**: Mencoba berbagai lokasi folder media Magento untuk menemukan shell yang berhasil diunggah.
*   **Interactive Shell**: Mode interaktif untuk menjalankan perintah sistem langsung setelah shell berhasil dideploy.

## Poc (Proof of Concept)
<img width="1128" height="402" alt="image" src="https://github.com/user-attachments/assets/29bd737b-d83e-4e63-a433-9ec2b2d009cd" />


## Persyaratan

Pastikan Anda memiliki Python 3.x dan pustaka `requests` terinstal.

```bash
pip install requests
```

## Cara Penggunaan

Siapkan file teks (misalnya `targets.txt`) yang berisi daftar domain target, satu per baris.

### Pemindaian Standar
```bash
python rce.py -f targets.txt -t 10 -o hasil.txt
```

### Mode Interaktif
Gunakan flag `-i` jika Anda ingin langsung masuk ke mode command shell setelah ada target yang berhasil ditembus:
```bash
python rce.py -f targets.txt -i
```

### Argumen Baris Perintah
*   `-f`, `--file`: Path ke file daftar domain (Wajib).
*   `-t`, `--threads`: Jumlah thread simultan (Default: 5).
*   `-o`, `--output`: Nama file untuk menyimpan URL shell yang aktif (Default: shells.txt).
*   `--timeout`: Batas waktu request dalam detik (Default: 30).
*   `-i`, `--interactive`: Masuk ke mode interaktif shell setelah proses selesai.

## Struktur Output
Setiap shell yang berhasil akan disimpan ke file output dengan format:
```text
[DOMAIN] https://target-magento.com
[SHELL] https://target-magento.com/pub/media/custom_options/quote/x/y/filename.php
```
