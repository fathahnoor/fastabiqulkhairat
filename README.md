# Fastabiqulkhairat

Watchface Amazfit T-Rex Pro 360 x 360, memakai kaligrafi dan aset visual yang diberikan pengguna.

![Watchface](out/preview.png)

[Binary](out/fastabiqulkhairat.bin) | [Skenario waktu](out/scenarios.png) | [Digit yang diseragamkan](out/digits-normalized.png) | [Laporan verifikasi](out/validation.json)

## Desain dan aset

- `reference/approved-design.png`: desain final pengguna. Kaligrafi, ornamen, garis, ikon metrik, dan label diambil langsung dari gambar ini. Tidak diketik ulang atau digambar ulang.
- `reference/digits-approved.jpg`: lembar digit pengguna. Seluruh digit besar diambil dari lembar ini; angka 4 memakai varian lipatan pada baris kedua.
- Proporsi badan digit memakai tinggi 81 px dan lebar 66 px, kecuali angka 1 yang tetap ramping pada 38 px. Semua aset memiliki margin transparan 1 px di kiri dan kanan: sel 68 x 81 px untuk digit lain dan 40 x 81 px untuk angka 1. Jarak dirapikan dengan memangkas padding, bukan melebarkan bentuk angka 1.
- Titik dua berasal dari desain final. Area angka statis dibersihkan menggunakan tekstur gelap dari gambar yang sama, lalu diisi aset dinamis.
- Digit kecil yang tersedia di desain dipotong langsung; digit kecil lainnya berasal dari lembar digit. MON dan AUG juga dipotong langsung. Nama hari/bulan lain memakai font pendukung Rajdhani, sedangkan kondisi cuaca lain memakai ikon programatis karena aset lengkapnya tidak terdapat dalam lampiran.

Gambar sumber disimpan tanpa perubahan. Build memeriksa hash sumber dan kesamaan piksel area kaligrafi pada latar 360 x 360. File font Noto Kufi Arabic dan Oxanium serta tekstur generasi lama masih tersimpan untuk riwayat, tetapi tidak dipakai untuk kaligrafi atau jam pada build ini.

## Waktu proporsional

Koreksi pengguna mengutamakan bentuk asli dan jarak proporsional. Angka 1 tetap ramping, dengan margin transparan 1 px per sisi seperti digit lain. Jam tanpa nol awal dan menit selalu dua digit.

UIHH v2 memakai jam berperataan `Center`, titik dua sebagai `SuffixImage`, dan menit `Independent: false`. Menit mengikuti lebar aktual gambar digit. Bentuk 1 tidak diperlebar untuk mengisi sel digit lain.

Batas format: perataan jam memakai jangkar awal yang tetap, sehingga grup waktu bergeser 14 px ke kiri jika menit memuat satu angka 1, atau 28 px jika menitnya 11. Pengguna secara eksplisit memilih bentuk dan jarak proporsional daripada rata tengah yang ketat. Build menguji batas ini pada 1.440 kombinasi waktu, bukan mengklaim semuanya tepat berpusat. Lihat `out/spacing-aod-review.png` untuk contoh 5:11, 11:11, dan 21:10.

## Build dan validasi

```powershell
python tools/build.py
```

Memerlukan Python dan Pillow. Tidak diperlukan pembentukan font Arab atau imagegen untuk build. Proses membuat aset, mengemas binary UIHH v2 terkompresi, membongkar kembali binary, membandingkan parameter dan semua piksel, lalu merender preview dari hasil pembongkaran.

AOD mempertahankan seluruh elemen. Intensitas kanal RGB angka jam, menit, dan titik dua adalah 85%. Teks dan angka lainnya, termasuk tanggal, suhu, metrik, satuan, label, dan kaligrafi, memakai 80%. Ikon, ornamen, dan latar tetap 30%. Khusus angka langkah, BPM, baterai, dan tanggal pada AOD, sel diperbesar dari 11 x 13 menjadi 14 x 18 px dengan intensitas 100%. Label, nama hari/bulan, dan simbol persen tidak diperbesar. Posisi angka disesuaikan agar tetap terpisah dari ikon serta label. Data dinamis: hari, bulan, tanggal, suhu, kondisi cuaca, langkah, detak jantung, dan baterai. Kesegaran data bergantung pada firmware.

Target adalah T-Rex Pro generasi awal. Instalasi fisik dan perilaku firmware, termasuk grup waktu dan pembaruan AOD, belum diuji pada jam. Hasil uji perangkat lunak tersedia di `out/validation.json`.

## Lisensi dan sumber teknis

Kode turunan skema [watchface-js](https://github.com/Nadeflore/watchface-js) mengikuti GPL-3.0, lihat `LICENSE` dan `tools/LICENSE.watchface-js`. Packer diadaptasi dari baseline lokal TEL-U T-Rex Pro. Semantik digit mengikuti [editor SashaCX75](https://github.com/SashaCX75/AmazFit_Watchface_Editor_2/blob/master/GTR_Watch_face/PreviewToBitmap.cs).

Font yang tersimpan berlisensi SIL OFL, salinan lisensi ada di `assets/fonts`. Desain dan lembar digit diberikan pengguna; lisensi kode tidak dimaksudkan sebagai klaim kepemilikan karya visual pihak lain.
