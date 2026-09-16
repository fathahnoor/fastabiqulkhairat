"""Build the Fastabiqulkhairat T-Rex Pro dial and verify the packed output."""
import copy
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageChops
import source_assets
from trexpro_wf import (unpack, decode_image, ids_to_names, names_to_ids,
                       shift_image_ids, validate_trexpro_container, validate_image_references)

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / 'build'
OUT = ROOT / 'out'
FONT = ROOT / 'assets/fonts'
GOLD = (210, 170, 91)
CREAM = (249, 225, 175)
ARABIC = 'فاستبقوا الخيرات'
SIZE = 360
TIME = {'center_x': 180, 'y': 159, 'digit_width': 68, 'height': 81,
        'colon_width': 22, 'leading_zero': False, 'alignment': 'center'}


def font(name, size, weight=None):
    f = ImageFont.truetype(str(FONT / name), size)
    if weight is not None:
        f.set_variation_by_axes([weight])
    return f


def glyph(text, name, size, color=CREAM, weight=None, rtl=False):
    f = font(name, size * 4, weight)
    args = {'direction': 'rtl', 'language': 'ar'} if rtl else {}
    box = f.getbbox(text, **args)
    im = Image.new('RGBA', (box[2] - box[0] + 8, box[3] - box[1] + 8))
    ImageDraw.Draw(im).text((4-box[0], 4-box[1]), text, font=f, fill=color, **args)
    im = im.crop(im.getbbox())
    return im.resize((max(1, round(im.width/4)), max(1, round(im.height/4))), Image.Resampling.LANCZOS)


def cell(text, width, height, size=21, name='Rajdhani-SemiBold.ttf', color=CREAM, weight=None):
    im = glyph(text, name, size, color, weight)
    if im.width > width-2 or im.height > height:
        scale = min((width-2)/im.width, height/im.height)
        im = im.resize((max(1, int(im.width*scale)), max(1, int(im.height*scale))), Image.Resampling.LANCZOS)
    out = Image.new('RGBA', (width, height))
    out.alpha_composite(im, ((width-im.width)//2, (height-im.height)//2))
    return out


def centered(canvas, im, x, y):
    canvas.alpha_composite(im, (round(x-im.width/2), y))


def star(draw, cx, cy, radius):
    points = []
    for i in range(16):
        a = i*math.pi/8-math.pi/2
        r = radius if i % 2 == 0 else radius*.74
        points.append((cx+math.cos(a)*r, cy+math.sin(a)*r))
    draw.line(points+[points[0]], fill=GOLD, width=1)


def icon(kind, size=24):
    im = Image.new('RGBA', (96, 96))
    d = ImageDraw.Draw(im)
    if kind == 'heart':
        d.ellipse((12, 14, 52, 54), fill=GOLD)
        d.ellipse((44, 14, 84, 54), fill=GOLD)
        d.polygon([(13, 39), (83, 39), (48, 84)], fill=GOLD)
    elif kind == 'battery':
        d.polygon([(56, 3), (20, 54), (45, 54), (32, 94), (79, 38), (52, 38)], fill=GOLD)
    elif kind == 'steps':
        d.ellipse((13, 24, 37, 65), fill=GOLD)
        d.ellipse((46, 6, 73, 52), fill=GOLD)
        d.rounded_rectangle((15, 71, 36, 89), radius=6, fill=GOLD)
        d.rounded_rectangle((48, 58, 71, 77), radius=6, fill=GOLD)
    elif kind in ('fog', 'wind', 'sand'):
        for y, x in ((30, 12), (47, 23), (64, 10)):
            d.line((x, y, 87-x//3, y), fill=GOLD, width=5)
        if kind == 'sand':
            for x,y in ((18,76),(40,80),(71,76)):
                d.ellipse((x,y,x+5,y+5),fill=GOLD)
    elif kind == 'moon':
        d.pieslice((19, 10, 82, 80), 65, 290, fill=CREAM)
    else:
        sun = kind in ('sun', 'partly')
        if sun:
            for i in range(8):
                a = i*math.pi/4
                d.line((36+27*math.cos(a), 34+27*math.sin(a), 36+37*math.cos(a), 34+37*math.sin(a)), fill=GOLD, width=4)
            d.ellipse((17, 15, 55, 53), fill=GOLD)
        if kind != 'sun':
            c = CREAM if kind in ('partly', 'cloud') else (171, 157, 128)
            d.ellipse((16, 42, 50, 76), fill=c)
            d.ellipse((37, 29, 74, 72), fill=c)
            d.ellipse((56, 43, 89, 76), fill=c)
            d.rectangle((31, 57, 75, 76), fill=c)
            if kind == 'rain':
                for x in (28, 50, 72):
                    d.line((x, 80, x-5, 93), fill=GOLD, width=4)
            if kind == 'snow':
                for x in (28, 50, 72):
                    d.ellipse((x, 83, x+4, 87), fill=CREAM)
            if kind == 'storm':
                d.polygon([(53, 65), (36, 83), (48, 83), (40, 96), (67, 75), (55, 75)], fill=GOLD)
    return im.resize((size, size), Image.Resampling.LANCZOS)


def background():
    source_assets.approved_crop((178,309,1053,504)).save(OUT/'calligraphy.png')
    return source_assets.background()


def localized(index, count=1):
    return {'Language': 2, 'ImageRange': {'ImageIndex': index, 'ImagesCount': count}}


def number(x, y, index, count=10, align='Left', zero=0, suffix=None):
    node = {'X': x, 'Y': y, 'ImageRange': localized(index, count)}
    if suffix is not None:
        node['SuffixImage'] = localized(suffix)
    return {'Image': node, 'Alignment': align, 'Spacing': 0, 'ZeroPadding': zero}


def generate():
    images = []
    def add(im):
        images.append(im)
        return len(images)-1
    bg = add(background())
    big = len(images)
    for ch in range(10):
        add(source_assets.time_cell(ch))
    colon = Image.new('RGBA', (22,81))
    raw = source_assets.approved_crop((588,600,663,757),(19,43))
    colon.alpha_composite(raw,(1,15))
    colon_id = add(colon)
    small = len(images)
    for ch in '0123456789':
        add(source_assets.small_digit(int(ch)))
    pct = add(source_assets.approved_crop((950,984,1008,1032),(15,13)))
    degree = add(source_assets.approved_crop((367,190,381,209),(4,5)))
    weekdays = len(images)
    for s in ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN']:
        add(source_assets.approved_crop((846,119,990,167),(41,14)) if s=='MON' else cell(s,41,14,19))
    months = len(images)
    for s in ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']:
        add(source_assets.approved_crop((840,188,948,230),(31,12)) if s=='AUG' else cell(s,31,12,17))
    weather = len(images)
    # UIHH weather order follows the existing T-Rex Pro baseline (29 states).
    kinds = ['sun', 'partly', 'partly', 'cloud', 'rain', 'rain', 'rain', 'storm',
             'snow', 'snow', 'snow', 'snow', 'fog', 'fog', 'sand', 'wind',
             'moon', 'cloud', 'cloud', 'rain', 'rain', 'storm', 'snow', 'fog',
             'cloud', 'rain', 'sun', 'cloud', 'cloud']
    for kind in kinds:
        add(source_assets.approved_crop((287,85,410,184),(35,28)) if kind=='partly' else icon(kind,28))
    # The one logical time field compiles to hour + separator + following minute.
    # Include the complete fixed-width minute pair and colon in the group center.
    # Minutes have two fixed advances, so the entire HH:MM width is included.
    hour_x = TIME['center_x'] - (TIME['colon_width'] + 2*TIME['digit_width'])//2 - (2*TIME['digit_width']+1)//2
    time = {'Digital': {'HoursMinutesSeconds': [
        {'Type': 0, 'Independent': True,
         'Text': number(hour_x, TIME['y'], big, align='Center', suffix=colon_id)},
        {'Type': 1, 'Independent': False, 'Text': number(0, 0, big, zero=1)}]}}
    date = {'YearMonthDay': [
        {'Type': 1, 'Independent': True, 'Text': number(241,55,months,12)},
        {'Type': 2, 'Independent': True, 'Text': number(276,55,small,zero=1)}],
        'Week': {'Independent': True, 'Text': number(244,35,weekdays,7)}}
    data = []
    for typ, cx, maxdigits, suffix in [('Steps',90,5,None),('HeartRate',180,3,None),('Battery',270,3,pct)]:
        x = cx-(maxdigits*11+1)//2-(7 if suffix else 0)
        data.append({'Type': typ, 'NumberSequence': {'Independent': True,
                    'Text': number(x,284,small, align='Center', suffix=suffix)}})
    data += [{'Type': 'Weather', 'NumberSequence': {'Independent': True, 'Text': number(85,55,small, suffix=degree)}},
             {'Type': 'Weather', 'Linear': {'Segments': {'X':83,'Y':25}, 'ImageRange': {'ImageIndex': weather, 'ImagesCount': 29}}}]
    # All fields remain in AOD. Use dimmed bitmaps, with no runtime timer.
    count = len(images)
    for index, im in enumerate(images[:]):
        gain = .85 if big <= index <= colon_id else (.80 if small <= index < weather else .30)
        dark = ImageEnhance.Brightness(im).enhance(gain)
        if index == bg:
            # Static Arabic and metric labels are baked into the source background.
            readable = ImageEnhance.Brightness(im).enhance(.80)
            for box in ((48,89,303,145), (66,299,115,311),
                        (167,299,193,311), (247,299,296,311)):
                dark.paste(readable.crop(box), box)
        images.append(dark)
    idle = shift_image_ids({'Time': copy.deepcopy(time), 'Date': copy.deepcopy(date),
                           'Data': copy.deepcopy(data), 'BackgroundImageIndex': bg}, count)
    params = {'Background': {'ImageIndex': bg, 'Preview': localized(len(images))},
              'Time': time, 'System': {'Date': date, 'Data': data}, 'IdleScreen': idle}
    for i, im in enumerate(images):
        im.save(BUILD/f'{i}.png')
    (BUILD/'watchface.json').write_text(json.dumps(params, indent=2), encoding='utf-8')
    (ROOT/'design.json').write_text(json.dumps({'name': 'fastabiqulkhairat', 'device': 'Amazfit T-Rex Pro',
        'screen': [360,360], 'arabic': ARABIC, 'time_field': TIME,
        'compiler': 'hour centered with attached separator and following zero-padded minutes'}, indent=2, ensure_ascii=False), encoding='utf-8')
    return params, images


def text_start(cfg, width, maxdigits, digit_width):
    x = cfg['Image']['X']
    if cfg.get('Alignment') == 'Center':
        x += (digit_width*maxdigits+1)//2-width//2
    return x


def render(params, images, hour=10, minute=47, steps=8327, hr=72, battery=86,
           day=26, month=8, weekday=0, temp=28, condition=1, idle=False):
    mode = params['IdleScreen'] if idle else params
    im = images[mode['BackgroundImageIndex'] if idle else mode['Background']['ImageIndex']].copy()
    fields = mode['Time']['Digital']['HoursMinutesSeconds']
    def digits(cfg, value, maxdigits, forced_x=None, forced_y=None):
        node = cfg['Image']
        base = node['ImageRange']['ImageRange']['ImageIndex']
        text = str(value).zfill(2) if cfg.get('ZeroPadding') else str(value)
        parts = [images[base+int(c)] for c in text]
        width = sum(p.width for p in parts)
        x = text_start(cfg, width, maxdigits, images[base].width) if forced_x is None else forced_x
        start = x
        y = node['Y'] if forced_y is None else forced_y
        for p in parts:
            im.alpha_composite(p, (x,y))
            x += p.width
        if node.get('SuffixImage'):
            p = images[node['SuffixImage']['ImageRange']['ImageIndex']]
            im.alpha_composite(p, (x,y))
            x += p.width
        return start, x
    start, end = digits(fields[0]['Text'], hour, 2)
    _, end = digits(fields[1]['Text'], minute, 2, end, fields[0]['Text']['Image']['Y'])
    assert abs((start+end)/2-180) <= .5, (hour, minute, start, end)
    system = mode if idle else mode['System']
    date = system['Date']
    for cfg, offset in [(date['Week']['Text'], weekday), (date['YearMonthDay'][0]['Text'], month-1)]:
        node = cfg['Image']
        im.alpha_composite(images[node['ImageRange']['ImageRange']['ImageIndex']+offset], (node['X'],node['Y']))
    digits(date['YearMonthDay'][1]['Text'], day, 2)
    values = {'Steps': (steps,5), 'HeartRate': (hr,3), 'Battery': (battery,3), 'Weather': (temp,2)}
    for entry in system['Data']:
        if 'NumberSequence' in entry:
            value, n = values[entry['Type']]
            digits(entry['NumberSequence']['Text'], value, n)
        else:
            node = entry['Linear']
            im.alpha_composite(images[node['ImageRange']['ImageIndex']+condition], (node['Segments']['X'],node['Segments']['Y']))
    return im


def norm(v):
    if isinstance(v, list):
        return norm(v[0]) if len(v)==1 else [norm(x) for x in v]
    if isinstance(v, dict):
        return {str(k):norm(x) for k,x in v.items()}
    return v


def main():
    BUILD.mkdir(exist_ok=True)
    OUT.mkdir(exist_ok=True)
    p, images = generate()
    approved=Image.open(source_assets.SRC).convert('RGBA').resize((360,360),Image.Resampling.LANCZOS)
    region=(48,89,303,145)
    delta=ImageChops.difference(images[0].crop(region),approved.crop(region))
    assert max(channel[1] for channel in delta.getextrema())==0, 'Calligraphy changed'
    atlas=Image.new('RGB',(440,216),(0,0,0))
    for digit in range(10):
        sprite=source_assets.time_cell(digit)
        assert sprite.size==(68,81)
        atlas.paste(sprite,(digit%5*88+10,digit//5*108),sprite)
        ImageDraw.Draw(atlas).text((digit%5*88+39,digit//5*108+87),str(digit),fill=CREAM)
    atlas.save(OUT/'digits-normalized.png')
    preview = render(p, images)
    preview.resize((220,220), Image.Resampling.LANCZOS).save(BUILD/'preview.png')
    subprocess.run([sys.executable, str(ROOT/'tools/pack_watchface.py'), str(BUILD), str(OUT/'fastabiqulkhairat.bin')], check=True, stdout=subprocess.DEVNULL)
    raw = (OUT/'fastabiqulkhairat.bin').read_bytes()
    checks = validate_trexpro_container(raw)
    decoded_params, blobs, _ = unpack(raw)
    firmware = ids_to_names(decoded_params)
    validate_image_references(firmware, blobs)
    assert norm(decoded_params) == norm(names_to_ids(shift_image_ids(p,1)))
    decoded = []
    maxdelta = 0
    for i, blob in enumerate(blobs):
        w,h,px = decode_image(blob)
        im = Image.frombytes('RGBA',(w,h),px)
        decoded.append(im)
        src = images[i] if i<len(images) else Image.open(BUILD/'preview.png').convert('RGBA')
        assert im.size == src.size
        maxdelta = max(maxdelta,max(abs(a-b) for a,b in zip(im.tobytes(),src.tobytes())))
    assert maxdelta <= 8, maxdelta
    roundtrip = shift_image_ids(firmware,-1)
    # Unpacker collapses singleton lists. This dial uses multiple time/date/data entries.
    scenarios = [dict(hour=10,minute=47),dict(hour=9,minute=7),dict(hour=1,minute=11),
                 dict(hour=23,minute=59,steps=99999,hr=220,battery=100,day=31,month=12,weekday=6),
                 dict(hour=0,minute=0,steps=0,hr=0,battery=0,day=1),dict(hour=10,minute=47,idle=True)]
    sheet = Image.new('RGB',(1080,770),(20,20,20))
    labels = ['10:47','9:07','1:11','23:59 / max','0:00 / zero','AOD']
    for i, args in enumerate(scenarios):
        im = render(roundtrip,decoded,**args)
        im.save(OUT/('preview.png' if i==0 else f'preview_{i}.png'))
        sheet.paste(im,(i%3*360,i//3*385))
        ImageDraw.Draw(sheet).text((i%3*360+12,i//3*385+361),labels[i],fill=CREAM)
    sheet.save(OUT/'scenarios.png')
    # Verify the serialized follower settings and actual decoded asset widths.
    hms=roundtrip['Time']['Digital']['HoursMinutesSeconds']
    assert hms[0]['Independent'] and not hms[1]['Independent']
    assert hms[0]['Text']['Alignment']=='Center'
    assert not hms[0]['Text']['ZeroPadding'] and hms[1]['Text']['ZeroPadding']==1
    hbase=hms[0]['Text']['Image']['ImageRange']['ImageRange']['ImageIndex']
    mbase=hms[1]['Text']['Image']['ImageRange']['ImageRange']['ImageIndex']
    colon=decoded[hms[0]['Text']['Image']['SuffixImage']['ImageRange']['ImageIndex']]
    for hour in range(24):
        for minute in range(60):
            width=sum(decoded[hbase+int(c)].width for c in str(hour))
            tail=colon.width+sum(decoded[mbase+int(c)].width for c in f'{minute:02d}')
            start=text_start(hms[0]['Text'],width,2,decoded[hbase].width)
            assert start+(width+tail)/2==180
            assert 0<=start and start+width+tail<=360
    report = {'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),'images':len(blobs),
              'container':checks,'parameter_roundtrip':True,'max_pixel_delta':maxdelta,
              'centered_time_cases':1440,'digit_cell':[68,81],'calligraphy_pixel_delta':0,
              'source_sha256':{str(path.relative_to(ROOT)):hashlib.sha256(path.read_bytes()).hexdigest() for path in (source_assets.SRC,source_assets.SHEET)},'arabic_text':ARABIC,'arabic_source':'unchanged crop from user-approved artwork',
              'device_test':'Pending physical T-Rex Pro installation'}
    (OUT/'validation.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
    print(json.dumps(report,indent=2))


if __name__ == '__main__':
    main()
