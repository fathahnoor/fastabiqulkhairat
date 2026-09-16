#!/usr/bin/env python3
"""Pack folder proyek watchface menjadi .bin T-Rex Pro.

Susunan folder:
  watchface.json   parameter bernama (lihat tools/trexpro_wf.py SCHEMA)
  0.png ... N.png  gambar sesuai ImageIndex yang dirujuk
  preview.png      preview 220x220 (opsional; jadi gambar terakhir)

Pakai:
  python tools/pack_watchface.py build/telu out/telu_trex_pro.bin
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from trexpro_wf import names_to_ids, encode_image, pack, shift_image_ids, validate_image_references  # noqa: E402


def load_png_rgba(path):
    from PIL import Image
    img = Image.open(path).convert("RGBA")
    return img.size[0], img.size[1], img.tobytes()


def main(argv):
    if len(argv) != 3:
        print("pakai: pack_watchface.py <folder> <out.bin>")
        return 1
    folder = Path(argv[1])
    named = json.loads((folder / "watchface.json").read_text())
    firmware_named = shift_image_ids(named, 1)
    params = names_to_ids(firmware_named)
    images = []
    pngs = sorted(folder.glob("[0-9]*.png"), key=lambda p: int(p.stem))
    assert [int(p.stem) for p in pngs] == list(range(len(pngs))), "PNG indices must be contiguous from zero"
    for p in pngs:
        w, h, px = load_png_rgba(p)
        blob = encode_image(px, w, h)
        images.append(blob)
        print("img %s: %dx%d -> %d byte" % (p.name, w, h, len(blob)))
    preview_file = folder / "preview.png"
    if preview_file.exists():
        w, h, px = load_png_rgba(preview_file)
        assert (w, h) == (220, 220), "preview harus 220x220, dapat %dx%d" % (w, h)
        images.append(encode_image(px, w, h))
        print("preview: 220x220 -> %d byte (index %d)" % (len(images[-1]), len(images) - 1))
    validate_image_references(firmware_named, images)
    (folder / "firmware_params.json").write_text(json.dumps(firmware_named, indent=2))
    out = pack(params, images, compress=True)
    Path(argv[2]).write_bytes(out)
    print("ditulis %s (%d byte, %d gambar, terkompresi)" % (argv[2], len(out), len(images)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
