"""Deterministic sprite slicing of the two user-approved source images."""
from pathlib import Path
from functools import cache
from PIL import Image, ImageDraw
ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'reference/approved-design.png'
SHEET=ROOT/'reference/digits-approved.jpg'

def extract(im, box):
    crop=im.crop(tuple(round(v) for v in box)).convert('RGBA')
    pixels=[]
    for r,g,b,a in crop.getdata():
        alpha=max(0,min(255,(max(r,g,b)-22)*255//35))
        pixels.append((r,g,b,alpha) if alpha else (0,0,0,0))
    crop.putdata(pixels)
    return crop.crop(crop.getbbox())

def approved_crop(box, size=None):
    im=extract(Image.open(SRC),box)
    if size: im=im.resize(size,Image.Resampling.LANCZOS)
    return im

@cache
def digits():
    im=Image.open(SHEET)
    boxes=[(100,190,398,545),(414,190,578,545),(609,190,880,545),(905,190,1184,545),
           (849,697,1164,1075),(148,697,445,1075),(486,697,787,1075),(1165,697,1453,1075),
           (576,1138,850,1500),(891,1138,1168,1500)]
    return [extract(im,tuple(v*im.width/1600 for v in box)) for box in boxes]

def time_cell(digit):
    raw=digits()[digit]
    # User requested consistent proportions. Preserve the slim silhouette of 1.
    raw=raw.resize((38 if digit==1 else 66,81),Image.Resampling.LANCZOS)
    result=Image.new('RGBA',(raw.width+2,81))
    result.alpha_composite(raw,(1,0))
    return result

def small_digit(digit):
    # Preserve supplied small-number artwork where the reference contains it.
    boxes={2:(628,987,665,1030),3:(284,985,318,1033),6:(913,987,950,1030),
           7:(355,985,389,1033),8:(246,987,281,1030)}
    raw=approved_crop(boxes[digit]) if digit in boxes else digits()[digit]
    raw=raw.resize((6 if digit==1 else 10,12),Image.Resampling.LANCZOS)
    im=Image.new('RGBA',(11,13))
    im.alpha_composite(raw,((11-raw.width)//2,0))
    return im


def background():
    im=Image.open(SRC).convert('RGBA')
    # Only the variable regions are cleared; all static artwork stays source-identical.
    regions=[(118,542,1140,848),(287,188,379,237),(839,117,996,171),
             (838,185,1028,233),(238,983,398,1033),(584,983,668,1033),(869,983,1007,1033),
             (285,86,410,183)]
    tile=im.crop((450,25,790,155))
    for x0,y0,x1,y1 in regions:
        for y in range(y0,y1):
            for x in range(x0,x1):
                im.putpixel((x,y),tile.getpixel(((x-x0)%tile.width,(y-y0)%tile.height)))
    out=im.resize((360,360),Image.Resampling.LANCZOS)
    # Physical screen mask only; no redesign of the source background.
    mask=Image.new('L',(360,360))
    ImageDraw.Draw(mask).ellipse((0,0,359,359),fill=255)
    base=Image.new('RGBA',(360,360),(0,0,0,255))
    base.paste(out,(0,0),mask)
    return base
