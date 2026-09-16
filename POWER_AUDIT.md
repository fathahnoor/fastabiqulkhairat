# Audit teknis AOD, 17 September 2026

Pengguna selalu memakai AOD dan melaporkan baterai boros. Belum ada angka
penurunan baterai per jam atau hash binary yang terpasang. Audit ini menghasilkan
kandidat optimasi penyimpanan yang mempertahankan tampilan, belum membuktikan
bahwa penyebab boros sudah teratasi.

## Batas platform yang diverifikasi

[Dokumentasi resmi Zepp](https://docs.zepp.com/docs/v2/reference/related-resources/device-list/)
menempatkan T-Rex Pro, deviceSource 83/200, pada kelompok Non-Zepp OS.
Binary project ini berisi parameter UIHH v2 dan bitmap BGRA32. Python berjalan
di komputer saat build, tidak dijalankan di jam. Tidak ada aplikasi JavaScript,
SDK Zepp OS, loop polling sensor, atau timer buatan project di dalam paket ini.

Audit parameter AOD menunjukkan:

- Waktu memuat jam dan menit saja. Tidak ada komponen detik atau animasi.
- Kaligrafi, garis, ornamen, ikon metrik dan label sudah digabung ke satu bitmap latar.
- Skala gambar dan transformasi kecerahan sudah dihitung saat build.
- Langkah, BPM, baterai, suhu, cuaca, hari dan tanggal tetap terhubung ke data firmware.
- Skema UIHH yang tersedia di project tidak menyediakan kontrol refresh tervalidasi.
  Tidak ditambahkan field interval rekaan atau flag firmware yang belum diketahui.

Tidak adanya detik bukan bukti bahwa firmware bangun hanya sekali per menit.
Frekuensi bangun, pembacaan sensor, cache gambar dan redraw aktual belum diukur.
Mengganti SDK atau mempercepat generator Python tidak menyelesaikan konsumsi AOD
pada perangkat ini. Tidak ada dasar saat ini untuk mengklaim kebocoran memori
atau polling berlebihan berasal dari watchface.

## Perubahan algoritma pengemasan

`pack(..., deduplicate_images=True)` mengindeks blob gambar berdasarkan isi byte.
Setiap gambar identik disimpan sekali, lalu entri tabel gambar memakai offset
yang sama. Perbandingan memakai keseluruhan byte, termasuk ukuran, warna dan alpha.
ID logis, urutan 29 kondisi cuaca, semua parameter serta rentang gambar tetap sama.
Tidak ada kuantisasi, peredupan baru, penghilangan field, atau perubahan alignment.

| Ukuran yang diukur | Sebelum | Kandidat |
| --- | ---: | ---: |
| File BIN | 665.910 byte | 630.902 byte |
| Body setelah dekompresi | 1.949.499 byte | 1.821.531 byte |
| Blob fisik | 156 | 116 |
| Entri gambar logis | 156 | 156 |
| Blok QuickLZ 4.096 byte | 475 | 444 |

Pengurangan file 5,26%. Body setelah dekompresi berkurang 127.968 byte,
termasuk 63.984 byte salinan aset AOD. Dari 82 gambar yang dirujuk AOD,
62 memiliki isi unik. Pengurangan ini menyentuh penyimpanan/pemuatan paket.
Itu bukan pengukuran RAM runtime, biaya render, atau penghematan baterai.
Firmware mungkin tetap mendekode setiap ID secara terpisah. Karena piksel sama,
tidak ada pengurangan emisi layar yang direncanakan.

Kompresi memakai format QuickLZ dan ukuran blok lama. Format gambar BGRA32 yang
sudah dipakai tetap dipertahankan. Shared offset dapat dibaca oleh kedua decoder
desktop, tetapi penerimaan firmware harus diuji pada jam. Kandidat karena itu
disimpan terpisah dari binary utama, yang tetap byte-identik dengan baseline.

## Artefak dan verifikasi

- [Kandidat optimized](out/fastabiqulkhairat-optimized.bin)
- [Binary pembanding](out/fastabiqulkhairat.bin)
- [Audit terukur](out/power-audit.json)
- [Verifikasi decoder referensi](out/optimization-reference-check.json)

Decoder lokal membandingkan semua parameter raw dan seluruh blob byte demi byte.
Decoder [Nadeflore/watchface-js](https://github.com/Nadeflore/watchface-js), commit
`0817bf8016b6e2cc8d86e85a284f61318b9b715f`, juga membandingkan seluruh 156 gambar
dengan selisih piksel nol. Decoder referensi mengeluarkan peringatan parameter
yang tidak dikenalnya pada kedua file; kesamaan parameter lengkap diperiksa
terpisah oleh decoder lokal. Uji regresi mencakup duplikat tidak bersebelahan,
perbedaan alpha, urutan ID, kompresi/nonkompresi dan aset tanpa duplikat.

```powershell
python tools/build.py
python -m unittest discover -s tools -p test_package_optimization.py
# Opsional jika source watchface-js tersedia, tidak memerlukan npm install:
node --experimental-vm-modules tools/verify_optimized_reference.mjs build/watchface-js-reference
```

## Pengukuran yang masih diperlukan pada jam

Pasang kandidat lalu periksa transisi normal ke AOD, perubahan menit, pergantian
tanggal dan data metrik. Bila gambar tidak tampil benar, gunakan binary pembanding.

Untuk menilai baterai, bandingkan masing-masing varian selama 24 jam dengan AOD
tetap aktif, firmware dan setelan sensor yang sama, serta aktivitas yang sebanding.
Catat persentase baterai awal/akhir, durasi, GPS/workout dan pengisian daya. Hitung
`(persen awal - persen akhir) / jam`. Ulangi urutan pembanding-kandidat agar hasil
satu hari tidak langsung dianggap efek optimasi. Gunakan pula watchface bawaan
dengan AOD sebagai kontrol untuk membedakan pengaruh watchface dari perangkat.

Jangan mengubah brightness atau jadwal sensor bersamaan dengan pengujian paket.
Penghematan daya tetap berstatus belum terukur sampai data perangkat tersedia.
