# -*- coding: utf-8 -*-
"""Sayfa zeminleri: TEK bir rengarenk tuvalin ayri bolgeleri.

Eskiden her sayfa ayri bir esere aitti. Ama olculdu: on bir eserin on
biri turuncu-kahve (doygunluk %28-%82, hepsi ayni aile). Yani sayfalar
arasi gezerken renk degismiyordu.

Simdi kaynak tek bir renkli tuval ve her sayfa onun BASKA bir bolgesine
denk geliyor. Bolgeler goz kararina degil OLCUYE gore seciliyor: tuval
izgara halinde taraniyor, her pencerenin baskin rengi bulunuyor ve her
sayfa kendine atanan renk tonuna en yakin pencereyi aliyor.

  - galeri ILK secer ve hedefi kirmizi: o sayfanin kirmizi olmasi sart.
  - Secilen pencereler birbirinden uzak durmaya zorlaniyor, yoksa iki
    sayfa tuvalin ayni yerinden kirpilip ayni gorunuyor.

Kullanim:  python zemin.py
Cikti:     varlik/zemin/*.webp  +  zeminler.json (menu paletleriyle)
"""
import colorsys
import io
import json
import math
import os

from PIL import Image, ImageDraw, ImageFilter

KOK = os.path.dirname(os.path.abspath(__file__))
TUVAL = os.path.join(KOK, 'zemin-tuval.jpg')
CIKTI = os.path.join(KOK, 'varlik', 'zemin')

CALISMA_EN = 2600      # tuval bu genislige buyutulup oyle kirpiliyor
W, Q = 1600, 72        # cikti genisligi ve webp kalitesi
PENCERE = 0.34         # kirpma penceresi: tuval genisliginin bu kadari
IZGARA = 11            # tarama izgarasi (IZGARA x IZGARA aday pencere)
UZAKLIK = 0.20         # secilen pencereler arasi en az mesafe (0-1)

# (anahtar, hedef ton derecesi). Galeri en basta: kirmiziyi o kapsin.
PLAN = [
    ('galeri',       0),
    ('acilis',      28),
    ('son',        140),
    ('seri',       212),
    ('atolye',     288),
    ('biyografi',  102),
    ('sergiler',   238),
    ('koleksiyon',  45),
    ('yayinlar',   312),
    ('basin',      178),
    ('iletisim',    68),
]


def dokulu_buyut(im, en):
    """Buyutup uzerine tuval dokusu ve gren ekler.

    Duz LANCZOS buyutmesi boyayi plastiklestiriyor: firca izi kayboluyor,
    geriye bulanik bir JPEG kaliyor. Ince bir dokuma ve gren, zemine
    yeniden 'boya' hissi veriyor.
    """
    im = im.resize((en, round(en * im.height / im.width)), Image.LANCZOS)
    w, h = im.size

    doku = Image.new('L', (w, h), 128)
    d = ImageDraw.Draw(doku)
    for x in range(0, w, 3):
        d.line([(x, 0), (x, h)], fill=136)
    for y in range(0, h, 3):
        d.line([(0, y), (w, y)], fill=120)
    doku = doku.filter(ImageFilter.GaussianBlur(0.6))

    # dokuyu yumusak isik gibi bindir: acik yerleri acar, koyuyu korur
    px, dp = im.load(), doku.load()
    for y in range(h):
        for x in range(w):
            k = (dp[x, y] - 128) / 255.0
            r, g, b = px[x, y]
            px[x, y] = (min(255, max(0, int(r + r * k * 0.55))),
                        min(255, max(0, int(g + g * k * 0.55))),
                        min(255, max(0, int(b + b * k * 0.55))))
    return im


def pencere_rengi(im, cx, cy, pw, ph):
    """Bir pencerenin baskin tonu, doygunlugu, parlakligi."""
    k = im.crop((cx - pw // 2, cy - ph // 2, cx + pw // 2, cy + ph // 2))
    k = k.resize((24, 16), Image.LANCZOS)
    tx = ty = 0.0
    s_top = l_top = 0.0
    n = 0
    for r, g, b in k.getdata():
        h, l, s = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)
        a = h * 2 * math.pi
        tx += math.cos(a) * s          # ton ortalamasi cembersel: agirlik doygunluk
        ty += math.sin(a) * s
        s_top += s
        l_top += l
        n += 1
    ton = (math.degrees(math.atan2(ty, tx)) + 360) % 360
    return ton, s_top / n, l_top / n


def ton_farki(a, b):
    d = abs(a - b) % 360
    return min(d, 360 - d)


def sec(im):
    """Her sayfa icin pencere merkezi secer. Sirayla, PLAN'daki oncelikle."""
    w, h = im.size
    pw, ph = int(w * PENCERE), int(w * PENCERE * 2 / 3)
    adaylar = []
    for gy in range(IZGARA):
        for gx in range(IZGARA):
            cx = int(pw / 2 + (w - pw) * gx / (IZGARA - 1))
            cy = int(ph / 2 + (h - ph) * gy / (IZGARA - 1))
            ton, doy, parlak = pencere_rengi(im, cx, cy, pw, ph)
            adaylar.append({'cx': cx, 'cy': cy, 'ton': ton,
                            'doy': doy, 'parlak': parlak})

    secilen, alinan = {}, []
    for anahtar, hedef in PLAN:
        en_iyi, en_iyi_puan = None, -1e9
        for a in adaylar:
            if any(math.hypot((a['cx'] - b['cx']) / w,
                              (a['cy'] - b['cy']) / h) < UZAKLIK for b in alinan):
                continue
            # Ton yakinligi asil olcut; doygunluk odul, asiri koyuluk ceza.
            # Ayrica ZATEN ALINMIS bir tona yakinsa ceza: tuvalde her renk
            # yok, hedefi karsilanamayan sayfalar hep ayni renge dusuyordu
            # (uc sayfa birden kirmizi cikmisti).
            tekrar = min([ton_farki(a['ton'], b['ton']) for b in alinan] or [180])
            puan = (-ton_farki(a['ton'], hedef) / 180.0 * 100
                    + a['doy'] * 45
                    - max(0.0, 0.30 - a['parlak']) * 120
                    - max(0.0, 40 - tekrar) * 1.6)
            if puan > en_iyi_puan:
                en_iyi, en_iyi_puan = a, puan
        if en_iyi is None:                      # yer kalmadi: mesafeyi gozardi et
            en_iyi = max(adaylar, key=lambda a: -ton_farki(a['ton'], hedef))
        secilen[anahtar] = (en_iyi, pw, ph)
        alinan.append(en_iyi)
    return secilen


def palette(im, n=9):
    """Zeminden menu icin n adet ACIK ton cikarir (koyu panel ustunde okunacak)."""
    small = im.copy().resize((60, 60))
    cols = small.convert('RGB').getcolors(60 * 60) or []
    cols.sort(key=lambda c: -c[0])
    out, seen = [], set()
    for _, (r, g, b) in cols:
        h, l, s = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)
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


TON_ADI = [(0, 'kirmizi'), (30, 'turuncu'), (55, 'sari'), (95, 'yesil'),
           (165, 'turkuaz'), (200, 'mavi'), (260, 'mor'), (320, 'pembe')]


def ton_adi(t):
    return min(TON_ADI, key=lambda p: ton_farki(p[0], t))[1]


def main():
    if not os.path.exists(TUVAL):
        raise SystemExit('kaynak tuval yok: ' + TUVAL)
    os.makedirs(CIKTI, exist_ok=True)
    for f in os.listdir(CIKTI):
        if f.endswith('.webp'):
            os.remove(os.path.join(CIKTI, f))

    ham = Image.open(TUVAL).convert('RGB')
    print('tuval %dx%d -> %d px, doku ekleniyor...' % (ham.width, ham.height, CALISMA_EN))
    im = dokulu_buyut(ham, CALISMA_EN)

    secilen = sec(im)
    meta = {}
    print('\n%-12s %-9s %-6s %s' % ('sayfa', 'ton', 'doyg', 'palet'))
    for anahtar, hedef in PLAN:
        a, pw, ph = secilen[anahtar]
        c = im.crop((a['cx'] - pw // 2, a['cy'] - ph // 2,
                     a['cx'] + pw // 2, a['cy'] + ph // 2))
        c = c.resize((W, round(W * c.height / c.width)), Image.LANCZOS)
        ad = '%s.webp' % anahtar
        c.save(os.path.join(CIKTI, ad), 'WEBP', quality=Q, method=6)
        meta[anahtar] = {'src': 'assets/zemin/' + ad, 'palette': palette(c)}
        print('%-12s %-9s %4d%%  %s' % (anahtar, ton_adi(a['ton']),
                                        int(a['doy'] * 100),
                                        ' '.join(meta[anahtar]['palette'][:4])))

    json.dump(meta, io.open(os.path.join(KOK, 'zeminler.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    mb = sum(os.path.getsize(os.path.join(CIKTI, f))
             for f in os.listdir(CIKTI)) / 1024 / 1024
    print('\n%d zemin · %.2f MB · varlik/zemin/' % (len(meta), mb))


if __name__ == '__main__':
    main()
