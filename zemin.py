# -*- coding: utf-8 -*-
"""Sayfa zeminleri: ressamın kendi tablolarından makro kırpıntılar.

rvonkaufmann.com'un yaptığı şey bu — "Hintergruende" klasöründe kendi
tablolarının 30 yakın çekimi var, CMS her sayfaya birini atıyor.
Biz de aynısını yapıyoruz, elimizdeki yüksek çözünürlüklü orijinallerden.

Kullanım:  python zemin.py
Çıktı:     site/assets/zemin/*.webp  +  zeminler.json (renk paletleriyle)
"""
import io, os, json, colorsys
from PIL import Image, ImageFilter

CACHE = 'cache'
OUT   = os.path.join('site', 'assets', 'zemin')
W, Q  = 1600, 70

# (kaynak eser, kırpma merkezi 0-1, yakınlık) — dokusu güçlü bölgeler seçildi
PLAN = [
    ('acilis',     64715,  (0.50, 0.35), 0.30),
    ('son',        68388,  (0.30, 0.55), 0.26),
    ('seri',       65353,  (0.55, 0.30), 0.28),
    ('atolye',     110561, (0.45, 0.60), 0.24),
    ('biyografi',  27777,  (0.40, 0.35), 0.26),
    ('sergiler',   64736,  (0.55, 0.45), 0.28),
    ('koleksiyon', 47669,  (0.45, 0.50), 0.26),
    ('yayinlar',   94127,  (0.50, 0.40), 0.28),
    ('basin',      64729,  (0.50, 0.45), 0.24),
    ('iletisim',   64772,  (0.45, 0.55), 0.30),
]


def crop(im, center, zoom):
    """Görüntünün merkez etrafından kare-ish bir bölge alır."""
    w, h = im.size
    cw, ch = int(w * zoom), int(h * zoom * 1.4)
    cx, cy = int(w * center[0]), int(h * center[1])
    left = max(0, min(w - cw, cx - cw // 2))
    top = max(0, min(h - ch, cy - ch // 2))
    return im.crop((left, top, left + cw, top + ch))


def palette(im, n=9):
    """Zeminden menü için n adet AÇIK ton çıkarır (koyu panel üstünde okunacak)."""
    small = im.copy().resize((60, 60))
    cols = small.convert('RGB').getcolors(60 * 60) or []
    cols.sort(key=lambda c: -c[0])
    out, seen = [], set()
    for _, (r, g, b) in cols:
        h, l, s = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)
        # menü koyu panelde: parlaklığı yükselt, doygunluğu kıs
        l2 = 0.80 + (l * 0.14)
        s2 = min(s, 0.30)
        rr, gg, bb = colorsys.hls_to_rgb(h, l2, s2)
        hexv = '#%02x%02x%02x' % (int(rr * 255), int(gg * 255), int(bb * 255))
        key = hexv[:5]
        if key in seen:
            continue
        seen.add(key)
        out.append(hexv)
        if len(out) >= n:
            break
    while len(out) < n:
        out.append('#efefec')
    return out


def main():
    os.makedirs(OUT, exist_ok=True)
    meta = {}
    for key, wid, center, zoom in PLAN:
        src = os.path.join(CACHE, '%d.jpg' % wid)
        if not os.path.exists(src):
            print('ATLANDI (kaynak yok):', key, wid)
            continue
        im = Image.open(src).convert('RGB')
        c = crop(im, center, zoom)
        c = c.resize((W, int(W * c.height / c.width)), Image.LANCZOS)
        c = c.filter(ImageFilter.GaussianBlur(0.4))     # jpeg gürültüsünü yumuşat
        name = '%s.webp' % key
        c.save(os.path.join(OUT, name), 'WEBP', quality=Q, method=6)
        kb = os.path.getsize(os.path.join(OUT, name)) / 1024
        meta[key] = {'src': 'assets/zemin/' + name, 'palette': palette(c)}
        print('%-12s %4d KB  %s' % (key, kb, ' '.join(meta[key]['palette'][:5])))

    json.dump(meta, io.open('zeminler.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    total = sum(os.path.getsize(os.path.join(OUT, f)) for f in os.listdir(OUT)) / 1024 / 1024
    print('\n%d zemin · %.2f MB' % (len(meta), total))


if __name__ == '__main__':
    main()
