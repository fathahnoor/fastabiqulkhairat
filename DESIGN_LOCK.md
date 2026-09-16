# Desain final Fastabiqulkhairat

Sumber kanonis:
- `reference/approved-design.png`: desain final pengguna, jangan ubah kaligrafi, ornamen, ikon metrik, atau label statis.
- `reference/digits-approved.jpg`: digit lengkap dari pengguna. Pilih angka 4 dengan lipatan pada baris kedua.

Koreksi pengguna berikutnya: "beberapa angka proporsinya masih tidak seragam, kamu rapikan juga ya". Ini mengizinkan normalisasi proporsi digit tanpa mengganti bentuk dasar, tekstur emas, atau font sumber.

Implementasi saat ini:
- Pemotongan aset deterministik ada di `tools/source_assets.py`.
- Semua digit besar berada pada sel 68 x 81 px, badan 66 x 81 px kecuali angka 1 selebar 38 px.
- Jam, titik dua, dan menit tetap satu grup rata tengah melalui suffix dan follower UIHH.
- Kaligrafi berasal langsung dari latar desain final. Build memeriksa kesamaan piksel pada area kaligrafi setelah skala layar.
- `tools/build.py` membangun versi desain final; binary lama sudah digantikan setelah validasi.
- Digit kecil yang tersedia, MON, AUG, dan ikon partly cloudy diekstrak. Karakter tanggal/hari lain serta kondisi cuaca lain memakai aset pendukung karena sumber lengkap tidak tersedia.

Jangan kembali memakai Noto Kufi Arabic untuk kaligrafi atau Oxanium untuk jam. Jangan regenerasi desain. Selalu periksa `out/scenarios.png` dan `out/digits-normalized.png` setelah perubahan visual. Instalasi fisik di T-Rex Pro tetap perlu diverifikasi oleh pengguna.
