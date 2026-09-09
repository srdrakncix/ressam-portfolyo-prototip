# -*- coding: utf-8 -*-
"""Butun eserleri secilen levhanin duvarina asar, iki kirpim uretir.

  <slug>-genis.jpg   eser kadrajin ~%40'i  - detay / mekan karesi
  <slug>-dar.jpg     eser kadrajin ~%62'si - katalog izgarasindaki kart

Kirpimlar ESERE gore ortalaniyor ve eserin gercek genisligine gore
olculuyor; levha degisince elle ayar gerekmiyor.
"""
import io
import json
import os
import sys
import time

import oda

KOK = os.path.dirname(os.path.abspath(__file__))
OLCEK = 2.4
PAY = {'genis': 0.40, 'dar': 0.62}      # eserin kadraj genisligindeki payi


def olcu_al(mekan, gen_cm, yuk_cm):
    """Eserin 2.4x levhadaki merkezi ve piksel genisligi."""
    mek = dict(oda.MEKANLAR[mekan])
    mek['kose'] = [(x * OLCEK, y * OLCEK) for x, y in mek['kose']]
    u = mek.get('u', mek['en'] / 2.0)
    cx, cy = oda.duvar_noktasi(mek, u, 150.0)
    sx, _ = oda.duvar_noktasi(mek, u - gen_cm / 2, 150.0)
    return cx, cy, abs(cx - sx) * 2


def eserler():
    kk = os.path.join(KOK, 'icerik', 'eserler')
    liste = []
    for ad in sorted(os.listdir(kk)):
        if ad.endswith('.json'):
            with io.open(os.path.join(kk, ad), encoding='utf-8') as f:
                e = json.load(f)
            liste.append((e.get('sira') or 999, e['slug']))
    liste.sort()
    return [s for _, s in liste]


def main():
    mekan = 'kup'
    argv = [a for a in sys.argv[1:] if not a.startswith('--')]
    for a in sys.argv[1:]:
        if a.startswith('--mekan='):
            mekan = a.split('=', 1)[1]
    cikti = os.path.join(KOK, 'kaynak', 'oda-cikti', mekan)
    os.makedirs(cikti, exist_ok=True)

    atlanan = []
    for i, slug in enumerate(argv or eserler(), 1):
        t = time.time()
        try:
            tam = oda.uret(slug, mekan=mekan, olcek=OLCEK)
        except ValueError as hata:
            atlanan.append(str(hata))
            print('  %2d  %-16s ATLANDI' % (i, slug))
            continue
        e = oda.eser_oku(slug)
        cx, cy, epx = olcu_al(mekan, float(e['olcu']['genislik_cm']),
                              float(e['olcu']['yukseklik_cm']))
        for ad, pay in PAY.items():
            w = epx / pay
            h = w * 2 / 3
            kutu = (int(cx - w / 2), int(cy - h * 0.46),
                    int(cx + w / 2), int(cy - h * 0.46 + h))
            kutu = (max(0, kutu[0]), max(0, kutu[1]),
                    min(tam.width, kutu[2]), min(tam.height, kutu[3]))
            tam.crop(kutu).save(os.path.join(cikti, '%s-%s.jpg' % (slug, ad)),
                                quality=93, subsampling=0, optimize=True)
        print('  %2d  %-16s %.1f sn' % (i, slug, time.time() - t))

    for h in atlanan:
        print('  ! ' + h)
    print('cikti:', cikti)


if __name__ == '__main__':
    main()
