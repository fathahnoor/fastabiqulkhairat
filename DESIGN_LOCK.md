# Desain final Fastabiqulkhairat

Sumber kanonis:
- `reference/approved-design.png`: desain final pengguna, jangan ubah kaligrafi, ornamen, ikon metrik, atau label statis.
- `reference/digits-approved.jpg`: digit lengkap dari pengguna. Pilih angka 4 dengan lipatan pada baris kedua.

Koreksi pengguna berikutnya: "beberapa angka proporsinya masih tidak seragam, kamu rapikan juga ya". Ini mengizinkan normalisasi proporsi digit tanpa mengganti bentuk dasar, tekstur emas, atau font sumber.

Implementasi saat ini:
- Pemotongan aset deterministik ada di `tools/source_assets.py`.
- Digit besar memakai badan 66 x 81 px, kecuali angka 1 yang tetap 38 x 81 px. Margin transparan semua digit 1 px per sisi; sel angka 1 adalah 40 x 81 px dan digit lain 68 x 81 px.
- Instruksi terbaru: seluruh jam, titik dua, dan menit harus diperlakukan sebagai satu field dengan alignment Center. `time_group_layout()` menghitung lebar semua komponen sebelum menentukan posisi kiri. Jangan kembali ke perataan jam saja.
- Kaligrafi berasal langsung dari latar desain final. Build memeriksa kesamaan piksel pada area kaligrafi setelah skala layar.
- `tools/build.py` membangun versi desain final; binary lama sudah digantikan setelah validasi.
- Digit kecil yang tersedia, MON, AUG, dan ikon partly cloudy diekstrak. Karakter tanggal/hari lain serta kondisi cuaca lain memakai aset pendukung karena sumber lengkap tidak tersedia.

Jangan kembali memakai Noto Kufi Arabic untuk kaligrafi atau Oxanium untuk jam. Jangan regenerasi desain. Selalu periksa `out/scenarios.png` dan `out/digits-normalized.png` setelah perubahan visual. Instalasi fisik di T-Rex Pro tetap perlu diverifikasi oleh pengguna.

Revisi berikutnya: rapatkan jarak digit 1 dengan memangkas padding; jangan memperlebar bentuk glyph. Badan 38 px dalam sel 40 px, margin kiri dan kanan masing-masing 1 px. Hanya angka langkah, BPM, baterai, dan tanggal AOD memakai sel 14 x 18 px dan intensitas 100%; label/satuan tetap ukuran sebelumnya. Periksa `out/spacing-aod-review.png` dan `out/preview_aod_max.png`.

Koreksi bukti: angka pergeseran 28 px terdahulu berasal dari renderer, bukan pengujian firmware. Pengembang editor menyatakan preview Follow+Center tidak akurat (https://amazfitwatchfaces.com/forum/viewtopic.php?p=13168). Parameter native Center+Follow tidak berubah; hasil pada perangkat masih perlu dikonfirmasi. Jangan menyebut preview sebagai bukti perilaku firmware.
