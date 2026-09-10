# -*- coding: utf-8 -*-
"""Menu panelini firca darbeleriyle boyar.

Menu artik siyah bir dikdortgen degil: yedi firca darbesiyle boyanmis bir
alan. Bu betik o darbeleri gercek boya fotograflarindan uretiyor, panele
yerlestiriyor, YAZI ALTINI OLCUYOR ve CSS yerlesimini yaziyor.

  girdi   firca-ham/*.jpg        gercek boya fotograflari (yapay zeka uretti)
  cikti   varlik/firca/*.webp    siteye giden darbeler
          firca.css              CSS yerlesimi (derlemede enjekte edilir)

Kullanim:  python firca.py


NEDEN BOYLE -- uc deneme coptu, sebepleri kayitli olsun:

1. BANDIN ICINE DOKU CARPMAK.  Duzgun bir egriyle band cizip uzerine boya
   fotografini yatayda gerdirdim. Saten kumas cikti: gerdirilen kil izi
   uzayip ipek parlamasina donuyor, uclar da 45 derece kesik kose oluyor.

2. YUZLERCE INCE KIL CIZMEK.  Firca darbesini kil demeti olarak modelledim.
   Tel demeti cikti. Yanlis varsayim suydu: yuklu bir darbenin govdesi
   COGUNLUKLA DOLUDUR; kil karakteri govdenin icinde degil, kenarinda,
   birkac seyrek izde ve dagilan kuru ucta yasar.

3. Ikisinin ortak hatasi: kutleyi ben cizmeye calistim.

Simdiki yol hicbir sey cizmiyor. Fotografta ZATEN olan darbeyi aliyor:
kagit beyazini olcup sifira cekiyor, en buyuk bagli boya kutlesini
ayikliyor, ana eksenini ikinci momentlerden bulup yatiriyor.


VE ASIL KARAR -- SAYDAMLIK ile DOKUYU ayirmak:

Panelde 13 satir + onizleme sutunu var, yani yazi panelin neredeyse
tamamini kapliyor. "Delikli boya" bu yaziyi tasiyamaz; olctum, 20 yazi
kutusunun 19'u dusuyordu. Delikleri kapatinca da panel duz bir kirmizi
dikdortgene dondu ve butun firca karakteri gitti.

  ALFA -> darbenin DOLDURULMUS silueti. Ici opak, kenari tirtikli.
  RENK -> darbenin HAM yogunlugu. Kil izi, kuruyan uc, basinc farki;
          hepsi burada, DEGER farki olarak.

Gercek yagliboya da boyledir: ortu verici bir katta firca izini gordugun
sey saydamlik degil, kalinlik farkindan gelen degerdir. Boya inceldiginde
saydamlasmiyor, aciliyor.
"""
import io
import json
import math
import os
import sys

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageOps

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

KOK = os.path.dirname(os.path.abspath(__file__))
HAM = os.path.join(KOK, 'firca-ham')
VARLIK = os.path.join(KOK, 'varlik', 'firca')
CSS_YOL = os.path.join(KOK, 'firca.css')
OLCUM = os.path.join(KOK, 'kaynak', 'firca')

# Panelin gercek olcusu -- tarayicidan okundu, goz karari degil.
EN, BOY = 600, 857
TABAN = 0.92        # yazi altinda en dusuk opaklik
ISIK_TAVAN = 0.30   # yazi altinda en yuksek bagil parlaklik (acik yazi okunsun)

SURE = 300          # bir darbenin supurme suresi (ms)
ARALIK = 66         # darbeler arasi gecikme (ms)

# Menudeki her yazi kutusu (panel yereli). Bunlarin altinda boya opak olmali.
SATIR_Y = [113, 155, 227, 269, 312, 354, 396, 485, 527, 570, 612, 654, 697, 739]
YAZI_KUTULARI = (
    [('satir%02d' % i, 30, y, 195, 41) for i, y in enumerate(SATIR_Y)]
    + [('dil', 30, 802, 195, 29),
       ('kapat', 30, 30, 58, 58),
       ('oniz-gorsel', 293, 226, 270, 152),
       ('oniz-ust', 293, 520, 270, 17),
       ('oniz-ad', 293, 544, 270, 30),
       ('oniz-alt', 293, 579, 270, 44)]
)

# Ham fotograf -> darbe adi. Govde olanlarin cekirdegi masif, karakter
# olanlar tirtikli ve dagilan.
SECIM = [('govde-1', 'badana-11.jpg'), ('govde-2', 'bicak-11.jpg'),
         ('govde-3', 'kuru-27.jpg'),   ('karakter-1', 'kuru-11.jpg'),
         ('karakter-2', 'yagli-27.jpg'), ('karakter-3', 'bicak-27.jpg')]

# Sira ressamin sirasi: genis bir ust darbe, sol kenari muhurleyen dikey
# pas, sonra govdeyi kuran yataylar, sonda karakter ve duzeltme.
#   (darbe, sol%, ust%, genislik%, donme, yatay_ayna)
YERLESIM = [
    ('govde-1',    -14,  -9, 134,  -4, False),
    ('govde-3',     -4,  -4, 164,  90, False),
    ('karakter-2',  -6,  -5, 116,   5, False),
    ('govde-2',    -14,  26, 132,  -2, True),
    ('karakter-3', -14,  43, 140,   3, True),
    ('karakter-1', -12,  68, 138,  -3, True),
    ('karakter-1',   4,  29,  74,  -7, False),
]

# Fransiz kirmizisi. Ton panel boyunca capraz iniyor: ust darbe ile alt
# darbe ayni renkte olmasin, tuvalde de olmaz.
FR = [(0.00, (163, 30, 44)), (0.28, (134, 21, 35)), (0.60, (103, 17, 28)),
      (0.85, (78, 18, 26)), (1.00, (63, 22, 29))]

EGRI_LO, EGRI_HI = 14, 168   # ham yogunluk egrisi: pus sifira, cekirdek opak


# ══ 1. FOTOGRAFTAN DARBEYI AYIKLA ═══════════════════════════════════════

def yogunluk(yol):
    """Boya yogunlugu: kagit beyazi sifir, en koyu boya 255.

    Once kenardan pay kesiliyor. Fotografin kendi kenari koyu (vinyet); o
    ince rim darbeye baglanip en buyuk bagli kutlenin parcasi oluyor ve
    kutle karenin tamamina yayiliyor. Uc darbe boyle bozulmustu; kutleyi
    reddetmek ise yaramadi, cunku kutle hem rim hem darbeydi.
    """
    im = Image.open(yol).convert('L')
    pay = max(4, int(min(im.size) * 0.025))
    im = im.crop((pay, pay, im.width - pay, im.height - pay))
    px = sorted(im.getdata())
    n = len(px)
    kagit, koyu = px[int(n * 0.86)], px[int(n * 0.004)]
    if kagit - koyu < 25:
        return None
    d = Image.new('L', im.size)
    kaynak, hedef = im.load(), d.load()
    olcek = 255.0 / (kagit - koyu)
    for y in range(im.height):
        for x in range(im.width):
            v = (kagit - kaynak[x, y]) * olcek
            hedef[x, y] = 0 if v <= 0 else (255 if v >= 255 else int(v))
    return d


def en_buyuk_kutle(d, esik=70):
    """En buyuk bagli boya kutlesi (birlestir-bul, tek gecis)."""
    w, h = d.size
    px = d.load()
    etiket = [0] * (w * h)
    ebeveyn = [0]

    def bul(a):
        while ebeveyn[a] != a:
            ebeveyn[a] = ebeveyn[ebeveyn[a]]
            a = ebeveyn[a]
        return a

    def birlestir(a, b):
        ra, rb = bul(a), bul(b)
        if ra != rb:
            ebeveyn[max(ra, rb)] = min(ra, rb)

    for y in range(h):
        satir = y * w
        for x in range(w):
            if px[x, y] < esik:
                continue
            sol = etiket[satir + x - 1] if x else 0
            ust = etiket[satir - w + x] if y else 0
            if sol and ust:
                etiket[satir + x] = sol
                birlestir(sol, ust)
            elif sol or ust:
                etiket[satir + x] = sol or ust
            else:
                ebeveyn.append(len(ebeveyn))
                etiket[satir + x] = len(ebeveyn) - 1

    sayim = {}
    for i, e in enumerate(etiket):
        if e:
            k = bul(e)
            etiket[i] = k
            sayim[k] = sayim.get(k, 0) + 1
    if not sayim:
        return None
    kazanan = max(sayim, key=sayim.get)

    m = Image.new('L', (w, h), 0)
    mp = m.load()
    for y in range(h):
        satir = y * w
        for x in range(w):
            if etiket[satir + x] == kazanan:
                mp[x, y] = 255
    return m


def ana_eksen(m):
    """Kutlenin ana ekseninin yatayla acisi. Yapay zeka 'yatay' demeyi
    dinlemedi, sekiz adayin sekizi de caprazdi; darbeyi buradan yatiriyoruz."""
    w, h = m.size
    mp = m.load()
    n = sx = sy = 0
    for y in range(0, h, 2):
        for x in range(0, w, 2):
            if mp[x, y]:
                sx += x
                sy += y
                n += 1
    if n < 50:
        return 0.0
    ox, oy = sx / n, sy / n
    xx = yy = xy = 0.0
    for y in range(0, h, 2):
        for x in range(0, w, 2):
            if mp[x, y]:
                dx, dy = x - ox, y - oy
                xx += dx * dx
                yy += dy * dy
                xy += dx * dy
    return math.degrees(0.5 * math.atan2(2 * xy, xx - yy))


def darbeyi_al(dosya):
    """Bir fotograftan tek darbenin alfa maskesi."""
    d = yogunluk(os.path.join(HAM, dosya))
    if d is None:
        return None
    m = en_buyuk_kutle(d)
    if m is None:
        return None
    dp, mp = d.load(), m.load()
    for y in range(d.height):
        for x in range(d.width):
            if not mp[x, y]:
                dp[x, y] = 0

    aci = ana_eksen(m)
    d = d.rotate(aci, resample=Image.BICUBIC, expand=True, fillcolor=0)
    kutu = d.getbbox()
    if kutu:
        d = d.crop(kutu)
    d = d.point(lambda v: 0 if v <= EGRI_LO else
                (255 if v >= EGRI_HI else
                 int((v - EGRI_LO) * 255.0 / (EGRI_HI - EGRI_LO))))
    kutu = d.getbbox()
    if kutu:
        d = d.crop(kutu)
    if d.width > 900:
        d = d.resize((900, max(1, round(900 * d.height / d.width))), Image.LANCZOS)
    return d


# ══ 2. SILUET: IC DELIKLERI KAPAT, DIS TIRTIGI KORU ═════════════════════

def _genislet(im, r):
    """Yuvarlak genisletme. Pillow'un MaxFilter'i KARE cekirdekli ve
    siluetin sinirina dik acili basamaklar birakiyor -- panelde dijital
    gorunen delikler cikti. Gauss izotropiktir; bulanik + esik ayni isi
    yuvarlak cekirdekle yapar."""
    return im.filter(ImageFilter.GaussianBlur(r * 0.62)).point(
        lambda v: 255 if v > 46 else 0)


def _daralt(im, r):
    return im.filter(ImageFilter.GaussianBlur(r * 0.62)).point(
        lambda v: 255 if v > 209 else 0)


def doldur(a, esik=76, yaricap=10):
    """Kapama + disariya bagli olmayan bosluklari doldurma.

    Dis silueti bozmuyor: tirtik cok daha buyuk olcekte. Ama darbenin
    govdesindeki igne delikleri kapaniyor -- yazi onlarin ustunde duracak.
    """
    ikili = a.point(lambda v: 255 if v >= esik else 0)
    ikili = _daralt(_genislet(ikili, yaricap), yaricap)
    w, h = ikili.size
    ped = Image.new('L', (w + 2, h + 2), 0)
    ped.paste(ikili, (1, 1))
    ters = ped.point(lambda v: 0 if v else 255)
    ImageDraw.floodfill(ters, (0, 0), 128)
    delik = ters.point(lambda v: 255 if v == 255 else 0).crop((1, 1, w + 1, h + 1))
    dolu = ikili.copy()
    dolu.paste(255, (0, 0), delik)
    return ImageChops.lighter(a, dolu)


# ══ 3. PANELE YERLESTIR VE BOYA ═════════════════════════════════════════

def fr(t):
    t = max(0.0, min(1.0, t))
    for i in range(len(FR) - 1):
        a, ca = FR[i]
        b, cb = FR[i + 1]
        if a <= t <= b:
            u = (t - a) / (b - a)
            return tuple(int(ca[k] + (cb[k] - ca[k]) * u) for k in range(3))
    return FR[-1][1]


def donustur(ham, wy, donme, ayna):
    if ayna:
        ham = ham.transpose(Image.FLIP_LEFT_RIGHT)
    w = max(1, int(EN * wy / 100.0))
    h = max(1, round(w * ham.height / ham.width))
    ham = ham.resize((w, h), Image.LANCZOS)
    siluet = doldur(ham)
    if donme:
        ham = ham.rotate(donme, resample=Image.BICUBIC, expand=True, fillcolor=0)
        siluet = siluet.rotate(donme, resample=Image.BICUBIC, expand=True, fillcolor=0)
    return ham, siluet


def boya_darbe(ham, siluet, ox, oy):
    """Doku RENKTE, alfa siluet. Ince boya acilir ama solmaz -- doygunlugu
    korumazsak panel plastik ortu gibi duruyor (denendi)."""
    w, h = siluet.size
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    px, hp, sp = im.load(), ham.load(), siluet.load()
    for y in range(h):
        ty = (oy + y) / float(BOY)
        for x in range(w):
            a = sp[x, y]
            if not a:
                continue
            r, g, b = fr(0.30 * ((ox + x) / float(EN)) + 0.70 * ty)
            kal = hp[x, y] / 255.0
            ac = 1.0 + (1.0 - kal) * 0.20
            gri = (r + g + b) / 3.0
            kar = (1.0 - kal) * 0.14
            px[x, y] = (min(255, int((r * (1 - kar) + gri * kar) * ac)),
                        min(255, int((g * (1 - kar) + gri * kar) * ac)),
                        min(255, int((b * (1 - kar) + gri * kar) * ac)), a)
    return im


def kur(darbeler):
    panel = Image.new('RGBA', (EN, BOY), (0, 0, 0, 0))
    parcalar = []
    for ad, xy, yy, wy, donme, ayna in YERLESIM:
        ham, siluet = donustur(darbeler[ad], wy, donme, ayna)
        ox, oy = int(EN * xy / 100.0), int(BOY * yy / 100.0)
        d = boya_darbe(ham, siluet, ox, oy)
        gec = Image.new('RGBA', (EN, BOY), (0, 0, 0, 0))
        gec.paste(d, (ox, oy))
        panel = Image.alpha_composite(panel, gec)
        parcalar.append({'gorsel': d, 'ox': ox, 'oy': oy})
    return panel, parcalar


# ══ 4. OLC ══════════════════════════════════════════════════════════════

def isik(r, g, b):
    return (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255.0


def ic_kontrol(panel, pay=45):
    """Panelin ICINDE delik olmamali.

    Yazi kutulari tek tek gecse bile aralarinda kalan bir bosluk panelin
    ARKASINDAKI SAYFAYI gosteriyor -- menu bir tablonun degil, beyaz
    katalog kagidinin ustunde duruyor. Tarayicida goruldu: y610-640
    bandindaki bosluktan katalog sizdi ve boya araligi gibi degil, hata
    gibi durdu.

    Kural: dis sinir tirtikli olabilir, olmali da; ama kenardan `pay`
    kadar iceride her yer opak.
    """
    ap = panel.getchannel('A').load()
    kotu = []
    for y in range(pay, BOY - pay, 3):
        for x in range(pay, EN - pay, 3):
            if ap[x, y] < TABAN * 255:
                kotu.append((x, y))
    toplam = len(range(pay, BOY - pay, 3)) * len(range(pay, EN - pay, 3))
    if not kotu:
        return 0.0, None
    xs = [k[0] for k in kotu]
    ys = [k[1] for k in kotu]
    return len(kotu) / float(toplam), (min(xs), min(ys), max(xs), max(ys))


def olc(panel):
    px = panel.load()
    rapor = []
    for ad, x, y, w, h in YAZI_KUTULARI:
        dusuk, altta, n, en_isik = 255, 0, 0, 0.0
        for yy in range(y + 2, y + h - 2, 2):
            for xx in range(x + 2, x + w - 2, 2):
                if not (0 <= xx < EN and 0 <= yy < BOY):
                    continue
                r, g, b, a = px[xx, yy]
                dusuk = min(dusuk, a)
                if a < TABAN * 255:
                    altta += 1
                en_isik = max(en_isik, isik(r, g, b))
                n += 1
        rapor.append({'ad': ad, 'dusuk': dusuk / 255.0,
                      'delik': altta / max(1, n), 'isik': en_isik})
    return rapor


# ══ 5. DISARI: VARLIKLAR + CSS ══════════════════════════════════════════

def yogun_uc(im, dikey):
    """Boyanin yuklu oldugu uc. Supurme oradan baslamali: ters yonden
    supuren bir darbe hemen sahte gorunur, cunku firca boyayi biraktigi
    yerden tasimaya baslamaz."""
    a = im.getchannel('A')
    n = 12
    if dikey:
        dilim = [sum(a.crop((0, int(a.height * k / n), a.width,
                             int(a.height * (k + 1) / n))).tobytes()) for k in range(n)]
        return 'ust' if sum(dilim[:n // 2]) >= sum(dilim[n // 2:]) else 'alt'
    dilim = [sum(a.crop((int(a.width * k / n), 0,
                         int(a.width * (k + 1) / n), a.height)).tobytes()) for k in range(n)]
    return 'sol' if sum(dilim[:n // 2]) >= sum(dilim[n // 2:]) else 'sag'


def disari(parcalar):
    os.makedirs(VARLIK, exist_ok=True)
    for f in os.listdir(VARLIK):
        if f.endswith('.webp'):
            os.remove(os.path.join(VARLIK, f))

    satirlar = []
    for i, p in enumerate(parcalar, 1):
        g = p['gorsel']
        kutu = g.getchannel('A').getbbox()
        if not kutu:
            continue
        kirpik = g.crop(kutu)
        ad = 'panel-%d.webp' % i
        kirpik.save(os.path.join(VARLIK, ad), 'WEBP', quality=88, method=6, exact=True)
        dikey = kirpik.height > kirpik.width * 1.25
        satirlar.append({
            'dosya': 'assets/firca/' + ad,
            'sol': round((p['ox'] + kutu[0]) / EN * 100, 2),
            'ust': round((p['oy'] + kutu[1]) / BOY * 100, 2),
            'en': round(kirpik.width / EN * 100, 2),
            'boy': round(kirpik.height / BOY * 100, 2),
            'yon': yogun_uc(kirpik, dikey),
            'bayt': os.path.getsize(os.path.join(VARLIK, ad)),
        })
    return satirlar


def css_yaz(satirlar):
    p = ['/* URETILDI - python firca.py. Elle duzenleme: yerlesim olculerek',
         '   bulunuyor, elle degistirilirse yazi altindaki opaklik garantisi',
         '   bozulur. Kaynak: firca.py YERLESIM. */']
    p.append('#boya { --darbe: %d; }   /* kabuk.js kac <i> uretecegini buradan okuyor */'
             % len(satirlar))
    # Konum ve gorsel her zaman gecerli; ANIMASYON yalnizca menu acikken
    # tanimli. Yoksa animasyon sayfa yuklenirken kosuyor ve menu acildiginda
    # coktan bitmis oluyor -- olculdu: acilistan 80 ms sonra darbe %99
    # tamamlanmisti. Secici acik duruma baglaninca animasyon o anda
    # olusuyor, yani supurme acilisla birlikte basliyor.
    for i, r in enumerate(satirlar, 1):
        p.append('#boya i:nth-child(%d) {' % i)
        p.append('  left: %.2f%%; top: %.2f%%; width: %.2f%%; height: %.2f%%;'
                 % (r['sol'], r['ust'], r['en'], r['boy']))
        p.append('  background-image: url(%s);' % r['dosya'])
        p.append('}')
        p.append('#menu:popover-open #boya i:nth-child(%d),' % i)
        p.append('#menu.open #boya i:nth-child(%d) {' % i)
        p.append('  animation-name: sup-%s; animation-delay: %dms;'
                 % (r['yon'], (i - 1) * ARALIK))
        p.append('}')
    io.open(CSS_YOL, 'w', encoding='utf-8', newline='\n').write('\n'.join(p) + '\n')


def main():
    if not os.path.isdir(HAM):
        raise SystemExit('ham fotograf klasoru yok: ' + HAM)
    os.makedirs(OLCUM, exist_ok=True)

    print('darbeler ayikliniyor...')
    darbeler = {}
    for ad, dosya in SECIM:
        a = darbeyi_al(dosya)
        if a is None:
            raise SystemExit('darbe cikarilamadi: ' + dosya)
        darbeler[ad] = a
        print('  %-12s %-14s %4dx%d' % (ad, dosya.replace('.jpg', ''), a.width, a.height))

    panel, parcalar = kur(darbeler)
    rapor = olc(panel)

    print('\n%-14s %9s %8s %8s' % ('yazi kutusu', 'en dusuk', 'delik', 'en isik'))
    kalan = 0
    for r in rapor:
        tamam = r['dusuk'] >= TABAN and r['isik'] <= ISIK_TAVAN
        kalan += 0 if tamam else 1
        print('%-14s %8.0f%% %7.2f%% %8.2f   %s'
              % (r['ad'], r['dusuk'] * 100, r['delik'] * 100, r['isik'],
                 'tamam' if tamam else 'KALDI'))

    ic_oran, ic_kutu = ic_kontrol(panel)
    if ic_kutu:
        print('IC DELIK  %.2f%%  kutu x%d..%d  y%d..%d'
              % (ic_oran * 100, ic_kutu[0], ic_kutu[2], ic_kutu[1], ic_kutu[3]))
    else:
        print('ic delik  yok')

    kapla = sum(1 for v in panel.getchannel('A').tobytes() if v > 20) / float(EN * BOY)
    print('\npanel kaplama %.0f%%   kalan kutu %d/%d' % (kapla * 100, kalan, len(rapor)))

    satirlar = disari(parcalar)
    css_yaz(satirlar)

    print('\n%-16s %8s %8s %8s %8s %7s %8s'
          % ('darbe', 'sol', 'ust', 'en', 'boy', 'yon', 'bayt'))
    for i, r in enumerate(satirlar, 1):
        print('%-16s %7.1f%% %7.1f%% %7.1f%% %7.1f%% %7s %8d'
              % (os.path.basename(r['dosya']), r['sol'], r['ust'], r['en'],
                 r['boy'], r['yon'], r['bayt']))
    print('\ntoplam %d KB   ->  %s  +  firca.css'
          % (sum(r['bayt'] for r in satirlar) // 1024, VARLIK))

    # gorsel dogrulama ciktilari (kaynak/ depoya girmiyor)
    zem = os.path.join(KOK, 'varlik', 'zemin', 'galeri.webp')
    tab = (Image.open(zem).convert('RGB').resize((EN + 340, BOY), Image.LANCZOS)
           if os.path.exists(zem) else Image.new('RGB', (EN + 340, BOY), (28, 26, 30)))
    tab.paste(panel, (0, 0), panel)
    tab.save(os.path.join(OLCUM, 'panel.png'))

    if kalan or ic_oran > 0.001:
        raise SystemExit('\nHATA: %d yazi kutusu yetersiz, ic delik %%%.2f'
                         % (kalan, ic_oran * 100))


if __name__ == '__main__':
    main()
