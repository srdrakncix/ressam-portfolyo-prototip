# -*- coding: utf-8 -*-
"""Eser gorsellerini disariya, yukleneke hazir bir klasore cikarir.

Gemini / ChatGPT gibi araclara verilecek. Onlar webp'i her zaman sevmiyor,
dosya adindan da bir sey anlamiyorlar; o yuzden:
  - JPG'ye ceviriliyor (kalite 95, alt orneklemesiz)
  - Dosya adi sirali + baslik + GERCEK OLCU iceriyor
  - Yaninda liste ve hazir istem metni birakiliyor

Kunye orani gorselin orani ile tutmayan eser AYRI klasore konuyor:
oyle bir gorsel duvara gerilerek basilir.
"""
import io
import json
import os
import shutil
import unicodedata

from PIL import Image

KOK = os.path.dirname(os.path.abspath(__file__))
ESER_DIZIN = os.path.join(KOK, 'icerik', 'eserler')
GORSEL_DIZIN = os.path.join(KOK, 'icerik', 'gorseller')
# Calisma klasorunun icinde: kaynak/ zaten bunun icin var ve depoya
# girmiyor. Masaustune klasor acmak gereksiz.
HEDEF = os.path.join(KOK, 'kaynak', 'yukle')

ORAN_PAY = 0.03


def sadelestir(s):
    """Turkce karakterleri dosya adi icin ASCII'ye indirger."""
    esle = {'ı': 'i', 'İ': 'I', 'ş': 's', 'Ş': 'S', 'ğ': 'g', 'Ğ': 'G',
            'ü': 'u', 'Ü': 'U', 'ö': 'o', 'Ö': 'O', 'ç': 'c', 'Ç': 'C'}
    s = ''.join(esle.get(k, k) for k in s)
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode()
    return ''.join(k if k.isalnum() else '-' for k in s).strip('-')


def eserler():
    liste = []
    for ad in sorted(os.listdir(ESER_DIZIN)):
        if ad.endswith('.json'):
            with io.open(os.path.join(ESER_DIZIN, ad), encoding='utf-8') as f:
                liste.append(json.load(f))
    liste.sort(key=lambda e: (e.get('sira') or 999, e['slug']))
    return liste


# Istem metni ayri dosyada: uzun ve sik degisiyor, Python dizesi
# icinde tutmak hem okunmaz hem de duzenlemesi zor.
ISTEM = os.path.join(KOK, 'istem.txt')


def main():
    if os.path.isdir(HEDEF):
        shutil.rmtree(HEDEF)
    sorunlu = os.path.join(HEDEF, 'SORUNLU-YUKLEME')
    os.makedirs(HEDEF)

    satirlar = ['ESER LISTESI', '=' * 60, '']
    n = 0
    for e in eserler():
        yol = os.path.join(GORSEL_DIZIN, e['gorsel'])
        if not os.path.exists(yol):
            continue
        im = Image.open(yol).convert('RGB')
        gen = int(e['olcu']['genislik_cm'])
        yuk = int(e['olcu']['yukseklik_cm'])
        olcu = '%d x %d cm' % (yuk, gen)

        bek, ger = gen / yuk, im.width / im.height
        uygun = abs(ger - bek) / bek <= ORAN_PAY

        n += 1
        ad = '%02d-%s-%dx%dcm.jpg' % (n, sadelestir(e['baslik']), yuk, gen)
        if uygun:
            hedef = os.path.join(HEDEF, ad)
        else:
            os.makedirs(sorunlu, exist_ok=True)
            hedef = os.path.join(sorunlu, ad)
        im.save(hedef, quality=95, subsampling=0, optimize=True)

        satirlar.append('%02d  %-18s %-14s %s  (%dx%d px)%s'
                        % (n, e['baslik'], olcu, e.get('yil', ''),
                           im.width, im.height,
                           '' if uygun else '   << ORAN TUTMUYOR'))
        print('  %s%s' % (ad, '' if uygun else '   -> SORUNLU'))

    satirlar += ['', 'Olcu "yukseklik x genislik" olarak yazilidir.', '']
    if os.path.isdir(sorunlu):
        satirlar += [
            'SORUNLU-YUKLEME klasorundeki dosyanin en-boy orani kunyedeki',
            'olcuyle tutmuyor. Duvara asildiginda gerilir. Once panelden',
            'dogru fotografi yukle.', '']

    io.open(os.path.join(HEDEF, '00-LISTE.txt'), 'w',
            encoding='utf-8-sig').write('\n'.join(satirlar))
    shutil.copyfile(ISTEM, os.path.join(HEDEF, '00-ISTEM.txt'))
    print('\n%d eser -> %s' % (n, HEDEF))


if __name__ == '__main__':
    main()
