# -*- coding: utf-8 -*-
"""Gelen galeri karelerini eserlerle esler.

Dosya adlari (galeri_01..11) hangi esere ait oldugunu soylemiyor. Gozle
eslestirmek riskli: kahverengi manzaralarin cogu birbirine benziyor ve tek
bir hata siteye yanlis gorsel koyar.

Yontem: odalar beyaz, tek renkli sey tablo. Doygunlugu esigin ustundeki
piksellerin renk histogramini cikarip eserlerle karsilastiriyoruz. Sonra
1-1 atama yapip her eslesmenin ONE CIKMA PAYINI raporluyoruz - ikinci en
iyi adaya gore ne kadar ondeyse o kadar guveniyoruz.
"""
import io
import json
import os
import sys

import numpy as np
from PIL import Image

KOK = os.path.dirname(os.path.abspath(__file__))
ESER_DIZIN = os.path.join(KOK, 'icerik', 'eserler')
GORSEL_DIZIN = os.path.join(KOK, 'icerik', 'gorseller')
GELEN = os.path.join(KOK, 'kaynak', 'gelen')

KOVA = 6            # renk kanali basina kova sayisi
DOYGUNLUK = 40      # bu esigin altindaki (gri/beyaz) pikseller sayilmiyor


def histogram(im):
    a = np.asarray(im.convert('RGB').resize((220, 150), Image.LANCZOS), dtype=np.int16)
    enb, enk = a.max(axis=2), a.min(axis=2)
    renkli = (enb - enk) > DOYGUNLUK
    if renkli.sum() < 200:                       # neredeyse gri: hepsini al
        renkli = np.ones(a.shape[:2], dtype=bool)
    p = a[renkli] * KOVA // 256
    idx = p[:, 0] * KOVA * KOVA + p[:, 1] * KOVA + p[:, 2]
    h = np.bincount(idx, minlength=KOVA ** 3).astype(float)
    return h / h.sum()


def uzaklik(h1, h2):
    """Chi-kare uzakligi."""
    payda = h1 + h2
    payda[payda == 0] = 1
    return float((((h1 - h2) ** 2) / payda).sum())


def eserler():
    liste = []
    for ad in sorted(os.listdir(ESER_DIZIN)):
        if not ad.endswith('.json'):
            continue
        with io.open(os.path.join(ESER_DIZIN, ad), encoding='utf-8') as f:
            e = json.load(f)
        yol = os.path.join(GORSEL_DIZIN, e['gorsel'])
        if not os.path.exists(yol):
            continue
        gen, yuk = e['olcu']['genislik_cm'], e['olcu']['yukseklik_cm']
        im = Image.open(yol)
        if abs(im.width / im.height - gen / yuk) / (gen / yuk) > 0.03:
            continue                              # oran tutmayan eser disarida
        liste.append((e['slug'], e['baslik'], histogram(im)))
    return liste


def main():
    kareler = sorted(f for f in os.listdir(GELEN) if f.lower().endswith('.png'))
    if not kareler:
        raise SystemExit('kaynak/gelen icinde png yok')
    esr = eserler()
    print('%d kare, %d eser' % (len(kareler), len(esr)))

    hk = {k: histogram(Image.open(os.path.join(GELEN, k))) for k in kareler}
    M = {(k, s): uzaklik(hk[k], h) for k in kareler for s, _, h in esr}

    # Aclikgozlu 1-1 atama: en yakin ciftten baslayip ilerliyoruz.
    kalan_k, kalan_s = set(kareler), {s for s, _, _ in esr}
    ad = {s: b for s, b, _ in esr}
    esleme, satir = {}, []
    while kalan_k and kalan_s:
        k, s = min(((k, s) for k in kalan_k for s in kalan_s), key=lambda p: M[p])
        # ikinci en iyi aday: ayni kare icin bir sonraki eser
        digerleri = sorted(M[(k, x)] for x in kalan_s if x != s)
        pay = (digerleri[0] / M[(k, s)]) if digerleri and M[(k, s)] > 0 else 99
        esleme[k] = s
        satir.append((k, s, ad[s], M[(k, s)], pay))
        kalan_k.discard(k)
        kalan_s.discard(s)

    satir.sort()
    print()
    print('%-16s %-16s %-9s %s' % ('kare', 'eser', 'uzaklik', 'one cikma payi'))
    for k, s, b, u, p in satir:
        isaret = '' if p >= 1.35 else '   << ZAYIF, GOZLE DOGRULA'
        print('%-16s %-16s %8.4f   x%.2f%s' % (k, b, u, p, isaret))

    io.open(os.path.join(GELEN, 'esleme.json'), 'w', encoding='utf-8').write(
        json.dumps(esleme, ensure_ascii=False, indent=1))
    print('\nesleme.json yazildi')


if __name__ == '__main__':
    main()
