# -*- coding: utf-8 -*-
"""Eseri gercek bir galeri fotografinin duvarina asar.

Blender yok, 3B yok. Is su: fotograftaki duvarin dort kosesi BIR KEZ
olculuyor; o dortgen ile duvarin gercek olculeri arasindaki homografi
bulunuyor. Sonra herhangi bir eser, kunyesindeki santimetreye gore
duvarda istenen noktaya perspektifiyle oturuyor.

Yapistirmayi inandirici kilan sey uc olcum:
  1) Gercek olcek   - 132 cm'lik eser duvarda 132 cm yer kapliyor.
  2) Odanin isigi   - eserin durdugu noktadaki duvar parlakligi, PANONUN
                      genel seviyesine oranlanip uzerine carpiliyor.
  3) Golge          - levhadaki isik yonune gore; kayma bulaniktan buyuk,
                      yoksa golge isik tarafina dolanip hale birakiyor.

Kullanim:
    python oda.py firtina            # tek eser
    python oda.py firtina --tani     # olculen dortgenleri cizer
"""
import io
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFilter

KOK = os.path.dirname(os.path.abspath(__file__))
ESER_DIZIN = os.path.join(KOK, 'icerik', 'eserler')
GORSEL_DIZIN = os.path.join(KOK, 'icerik', 'gorseller')

SS = 2                 # maske asiri-orneklemesi: kenar merdiveni gitsin
ORAN_PAY = 0.03        # kunye orani ile gorsel orani arasinda kabul edilen fark


# ── OLCULMUS MEKANLAR ─────────────────────────────────────────────────────
# kose: duvar yuzunun dort kosesi (sol-ust, sag-ust, sag-alt, sol-alt)
# en/yuk: o duvarin gercekte kac santimetre oldugu. Ikisinin orani
#         fotograftaki dortgenin oraniyla tutarli olmali, yoksa eser
#         yatayda ve dikeyde farkli olceklerde basiliyor.
# isik: GOLGENIN dustugu yon. Levhadaki gercek isiga bakilarak olculuyor.
MEKANLAR = {
    # Yapay zeka ile uretildi (anahtarsiz, pollinations/flux). Kadrajin
    # TAMAMI duvar: model "gallery hall" deyince kamerayi holun dibine
    # koyup duvari kucultuyordu, duvarin kendisini tarif edince duzeldi.
    'kup': {
        'dosya': 'kup.jpg',
        'kose': [(0, 72), (1086, 72), (1086, 520), (0, 524)],
        'yuk': 300.0,
        'en': 727.0,        # 448 px = 300 cm -> 1086 px = 727 cm
        'isik': (0, 1),
        'kaynak': 'AI (pollinations/flux)',
    },
    'fuar': {
        'dosya': 'fuar.jpg',
        # Panonun kenarlari piksel taramasiyla yeniden olculdu; onceki
        # degerler solda 8, sagda 11 piksel iceriden geciyordu ve alt
        # kenara sahte bir egim veriyordu - eser 0,6 derece egik asili
        # gorunuyordu.
        'kose': [(613, 121), (887, 121), (887, 529), (613, 532)],
        'yuk': 250.0,
        # 274x409 piksellik pano 250 cm yuksekse 168 cm genistir. 160
        # yazildiginda eser yataydan %5 kucuk basiliyordu.
        'en': 168.0,
        # Levhada spotlarin en parlak noktasi x=753, panonun merkezi x=750:
        # isik cepheden vuruyor. Panonun kendi zemin golgesi de yanal kayma
        # yapmadan duz asagi dusuyor.
        'isik': (0, 1),
        'kaynak': 'Gemini ile uretildi',
    },
}


def homografi(hedef, kaynak):
    """PIL'in PERSPECTIVE katsayilari: hedef pikselinden kaynaga esleme."""
    A, B = [], []
    for (hx, hy), (kx, ky) in zip(hedef, kaynak):
        A.append([hx, hy, 1, 0, 0, 0, -kx * hx, -kx * hy])
        A.append([0, 0, 0, hx, hy, 1, -ky * hx, -ky * hy])
        B.append(kx)
        B.append(ky)
    return coz(A, B)


def coz(A, B):
    """8x8 dogrusal sistemi Gauss ile cozer (numpy'siz, bagimlilik artmasin)."""
    n = len(B)
    M = [A[i][:] + [B[i]] for i in range(n)]
    for i in range(n):
        p = max(range(i, n), key=lambda r: abs(M[r][i]))
        if abs(M[p][i]) < 1e-12:
            raise ValueError('tekil matris: koseler bozuk')
        M[i], M[p] = M[p], M[i]
        d = M[i][i]
        M[i] = [v / d for v in M[i]]
        for r in range(n):
            if r == i:
                continue
            f = M[r][i]
            if f:
                M[r] = [a - f * b for a, b in zip(M[r], M[i])]
    return [M[i][n] for i in range(n)]


_ONBELLEK = {}


def _duvar_h(mek):
    """Birim kare (s,t) -> fotograf pikseli esleyen homografi.

    Onbellek anahtari kose listesi. id() ile anahtarlanirken, gecici
    sozluk cop toplanip ayni adres yeniden kullanilinca eski (yanlis
    olcekli) homografi donuyordu.
    """
    ad = tuple(mek['kose'])
    if ad in _ONBELLEK:
        return _ONBELLEK[ad]
    a, b, c, d, e, f, g, h = homografi([(0, 0), (1, 0), (1, 1), (0, 1)], mek['kose'])

    def esle(s, t):
        payda = g * s + h * t + 1.0
        return ((a * s + b * t + c) / payda, (d * s + e * t + f) / payda)

    _ONBELLEK[ad] = esle
    return esle


def duvar_noktasi(mek, u, v):
    """Duvar koordinati (u: soldan cm, v: TABANDAN cm) -> fotograf pikseli."""
    return _duvar_h(mek)(u / mek['en'], 1.0 - v / mek['yuk'])


def eser_oku(slug):
    with io.open(os.path.join(ESER_DIZIN, slug + '.json'), encoding='utf-8') as f:
        return json.load(f)


def oran_uygun(e, im):
    """Kunye orani gorselin orani ile tutuyor mu?"""
    bek = float(e['olcu']['genislik_cm']) / float(e['olcu']['yukseklik_cm'])
    ger = im.width / im.height
    return abs(ger - bek) / bek <= ORAN_PAY, bek, ger


def yerlestir(mek, eser_im, gen_cm, yuk_cm, u_cm, v_cm, oda_boyut):
    """Eseri duvarda (u,v) merkezine gercek olcusuyle koyar."""
    W, H = oda_boyut
    yu, yv = gen_cm / 2.0, yuk_cm / 2.0
    kose = [
        duvar_noktasi(mek, u_cm - yu, v_cm + yv),
        duvar_noktasi(mek, u_cm + yu, v_cm + yv),
        duvar_noktasi(mek, u_cm + yu, v_cm - yv),
        duvar_noktasi(mek, u_cm - yu, v_cm - yv),
    ]
    hedef_en = max(abs(kose[1][0] - kose[0][0]), abs(kose[2][0] - kose[3][0]))

    # Kucultmeyi once LANCZOS ile yap: PERSPECTIVE'in BICUBIC'i 3 kattan
    # fazla kucultmede filtreleyemiyor, gokyuzunde tuz-biber beneklenmesi
    # birakiyordu.
    im = eser_im.convert('RGB')
    hedef_px = max(8, int(hedef_en * 2))
    if im.width > hedef_px * 1.3:
        im = im.resize((hedef_px, max(1, round(im.height * hedef_px / im.width))),
                       Image.LANCZOS)

    gw, gh = im.size
    src = [(0, 0), (gw, 0), (gw, gh), (0, gh)]
    warp = im.convert('RGBA').transform(
        (W, H), Image.PERSPECTIVE, homografi(kose, src), Image.BICUBIC)

    # Maske SS katinda uretilip kucultuluyor: tek katta PERSPECTIVE ikili
    # (0/255) bir maske birakiyor, kenarda 1 piksellik basamaklar cikiyordu.
    kat_ss = homografi([(x * SS, y * SS) for x, y in kose], src)
    mask = Image.new('L', (gw, gh), 255).transform(
        (W * SS, H * SS), Image.PERSPECTIVE, kat_ss, Image.BILINEAR).reduce(SS)
    warp.putalpha(mask)
    return warp, kose


def isik_uygula(oda, katman, mask, mek, olcek=1.0):
    """Eserin durdugu noktadaki duvar parlakligini uzerine carpar.

    Referans, eserin KENDI alani degil PANONUN genel seviyesi. Kendi
    alanina gore normalize edilince ortalama carpan 1.0'a kilitleniyordu:
    duvarda gozle gorulur bir spot havuzu varken eser onu hic yemiyordu.
    """
    yumusak = oda.convert('L').filter(ImageFilter.GaussianBlur(26 * olcek))
    px = yumusak.load()
    W, H = oda.size

    toplam, adet = 0, 0
    for sv in (40, 90, 140, 190, 230):
        for su in range(8, int(mek['en']) - 8, 10):
            x, y = duvar_noktasi(mek, su, sv)
            x, y = int(x), int(y)
            if 0 <= x < W and 0 <= y < H:
                toplam += px[x, y]
                adet += 1
    if not adet:
        return katman
    ort = toplam / adet

    kutu = mask.getbbox()
    if not kutu:
        return katman
    kp = katman.load()
    for y in range(kutu[1], kutu[3]):
        for x in range(kutu[0], kutu[2]):
            a = kp[x, y][3]
            if not a:
                continue
            # Yagliboya beyaz duvar kadar geri yansitmaz: taban 0.92.
            k = 0.92 * px[x, y] / ort
            k = max(0.70, min(1.10, k))
            r, g, b, _ = kp[x, y]
            kp[x, y] = (min(255, int(r * k)), min(255, int(g * k)),
                        min(255, int(b * k)), a)
    return katman


def golge(mask, mek, olcek=1.0):
    """Dusen golge + tuvalin dibindeki temas golgesi.

    Kayma bulaniktan BUYUK olmali. Tersi olunca penumbra dort yana birden
    tasip tabloyu ceviren bir hale birakiyor; olcumde isik tarafinda bile
    %9 koyulma cikmisti.
    """
    dx, dy = mek['isik']
    kat = Image.new('RGBA', mask.size, (0, 0, 0, 0))
    koyu = Image.new('RGBA', mask.size, (22, 23, 24, 255))
    for kayma, bulanik, guc in ((15, 6, 0.26), (4, 2, 0.32)):
        kayma, bulanik = kayma * olcek, bulanik * olcek
        kat.paste(koyu, (int(dx * kayma), int(dy * kayma)),
                  mask.filter(ImageFilter.GaussianBlur(bulanik))
                      .point(lambda v: int(v * guc)))
    return kat


def uret(slug, mekan='fuar', u_cm=None, v_cm=150.0, tani=False, olcek=1.0):
    """olcek: levhayi bu katsayiyla buyutup oyle bindiriyoruz.

    Mekan duz bir yuzey; buyutmede kaybedecek ayrintisi yok. Eser ise
    buyutulmus levhaya daha yuksek cozunurlukte oturuyor.
    """
    mek = dict(MEKANLAR[mekan])
    oda = Image.open(os.path.join(KOK, 'kaynak', 'mekan', mek['dosya'])).convert('RGB')
    if olcek != 1.0:
        oda = oda.resize((int(oda.width * olcek), int(oda.height * olcek)), Image.LANCZOS)
        mek['kose'] = [(x * olcek, y * olcek) for x, y in mek['kose']]
    W, H = oda.size

    e = eser_oku(slug)
    im = Image.open(os.path.join(GORSEL_DIZIN, e['gorsel'])).convert('RGB')
    tamam, bek, ger = oran_uygun(e, im)
    if not tamam:
        raise ValueError(
            'ORAN UYUSMUYOR (%s): kunye %.2f, gorsel %.2f. Boyle basilirsa '
            'eser duvarda gerilir. Panelden dogru fotografi yukle.'
            % (slug, bek, ger))

    if u_cm is None:
        u_cm = mek.get('u', mek['en'] / 2.0)

    katman, kose = yerlestir(mek, im, float(e['olcu']['genislik_cm']),
                             float(e['olcu']['yukseklik_cm']), u_cm, v_cm, (W, H))
    mask = katman.getchannel('A')

    if tani:
        d = ImageDraw.Draw(oda)
        d.line([tuple(map(int, k)) for k in mek['kose']] +
               [tuple(map(int, mek['kose'][0]))], fill=(255, 0, 0), width=3)
        d.line([tuple(map(int, k)) for k in kose] +
               [tuple(map(int, kose[0]))], fill=(0, 200, 255), width=3)
        return oda

    katman = isik_uygula(oda, katman, mask, mek, olcek)
    sonuc = Image.alpha_composite(oda.convert('RGBA'), golge(mask, mek, olcek))
    return Image.alpha_composite(sonuc, katman).convert('RGB')


if __name__ == '__main__':
    slug = sys.argv[1] if len(sys.argv) > 1 else 'firtina'
    tani = '--tani' in sys.argv
    out = uret(slug, tani=tani, olcek=1.0 if tani else 2.4)
    yol = os.path.join(KOK, slug + ('_tani.png' if tani else '_oda.png'))
    out.save(yol)
    print(yol, out.size)
