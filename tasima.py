# -*- coding: utf-8 -*-
"""ESERLERI Python kaynagindan veriye tasir. BIR KEZ calistirilir.

Neden: yonetim paneli .py duzenleyemez. Eserler content.WORKS + ceviri.WORKS +
images.json uzerine dagilmis durumdaydi; artik her eser TEK bir JSON dosyasi
ve gorseli ayri bir dosya.

Kritik tasarim karari - CEVIRI KURALI YAPIYA GOMULU:
  "baslik" tek bir alan, dil ayrimi YOK. Eser adi bir isimdir, cevrilmez.
  "gloss" yalnizca en/fr icin, baslIGIN ALTINDA gosterilen aciklayici karsilik.
  "not" uc dilde ayri.
Yani panelde eser adini yanlislikla cevirmek MUMKUN DEGIL - koyacak yer yok.
Bu kurali bir CMS ayarina birakmaktan daha saglam.

Biyografi, CV, koleksiyon adlari, yayinlar ve basin SU AN TASINMIYOR: nadiren
degisiyorlar ve panelin ilk surumu eser girmek icin. content.py'de kaliyorlar.
"""
import base64
import io
import json
import os
import re
import unicodedata

from PIL import Image

import build
import ceviri
import content

KOK = os.path.dirname(os.path.abspath(__file__))
ESER_DIZIN = os.path.join(KOK, 'icerik', 'eserler')
GORSEL_DIZIN = os.path.join(KOK, 'icerik', 'gorseller')


def slugla(s):
    s = unicodedata.normalize('NFKD', s)
    tr = {'ı': 'i', 'İ': 'i', 'ş': 's', 'Ş': 's', 'ğ': 'g', 'Ğ': 'g',
          'ü': 'u', 'Ü': 'u', 'ö': 'o', 'Ö': 'o', 'ç': 'c', 'Ç': 'c'}
    s = ''.join(tr.get(c, c) for c in s)
    s = ''.join(c for c in s if not unicodedata.combining(c))
    s = re.sub(r'[^A-Za-z0-9]+', '-', s).strip('-').lower()
    return s


def main():
    os.makedirs(ESER_DIZIN, exist_ok=True)
    os.makedirs(GORSEL_DIZIN, exist_ok=True)

    images = {im['id']: im for im in
              json.load(io.open(os.path.join(KOK, 'images.json'), encoding='utf-8'))}
    veri = build.build_data()          # yil atamasi ve olculer buradan gelsin

    n = 0
    for w in veri['works']:
        wid = int(w['id'])
        im = images[wid]
        slug = slugla(w['title'])

        # gorsel: images.json icindeki base64'u gercek dosyaya cikar
        ham = base64.b64decode(im['full'])
        gorsel_ad = slug + '.webp'
        with open(os.path.join(GORSEL_DIZIN, gorsel_ad), 'wb') as f:
            f.write(ham)

        cev = {d: ceviri.WORKS.get(wid, {}).get(d, ('', '')) for d in ('en', 'fr')}

        kayit = {
            'slug': slug,
            'sira': int(w['no']),
            'baslik': w['title'],                      # CEVRILMEZ - tek alan
            'gloss': {'en': cev['en'][0], 'fr': cev['fr'][0]},
            'seri': w['series'],
            'yil': w['year'],
            'durum': w['status'],                      # satilik|koleksiyonda|ayrildi
            'olcu': {'yukseklik_cm': w['ch'], 'genislik_cm': w['cw']},
            'koleksiyon': {'ad': w['collection'], 'yil': w['collYear'] or None},
            'gorsel': gorsel_ad,
            'ortam_gorseli': '',                       # Smartist ev ortami maketi
            'not': {'tr': w['note'], 'en': cev['en'][1], 'fr': cev['fr'][1]},
            'kaynak_kredisi': w['credit'],             # yer tutucu donemi; gercek eserde bos
        }
        yol = os.path.join(ESER_DIZIN, slug + '.json')
        io.open(yol, 'w', encoding='utf-8').write(
            json.dumps(kayit, ensure_ascii=False, indent=2) + '\n')
        n += 1
        print('  %-18s %-22s %3d × %3d cm  %s' %
              (slug, w['title'], w['ch'], w['cw'], w['status']))

    print('\n%d eser -> icerik/eserler/*.json' % n)
    t = sum(os.path.getsize(os.path.join(GORSEL_DIZIN, f))
            for f in os.listdir(GORSEL_DIZIN))
    print('%d gorsel -> icerik/gorseller/  (%.2f MB)' % (len(os.listdir(GORSEL_DIZIN)), t / 1048576))


if __name__ == '__main__':
    main()
