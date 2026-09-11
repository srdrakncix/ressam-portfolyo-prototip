# -*- coding: utf-8 -*-
"""Hero gorselini hazirla: duvardaki Ingilizce yaziyi kaldir, kirp, uret.

Kaynak kaynak/hero/salon-genel.png -- musterinin urettigi salon kurgusu,
sekiz eserin tamami tek mekanda.

Iki sorun var:

1. Duvarda goruntuye GOMULU Ingilizce metin: "ART / LIVES / DIFFERENTLY
   / HERE". Site uc dilli (TR/EN/FR) ve birincil dil Turkce; goruntuye
   gomulu metin cevrilemez, yani Fransizca sayfada da Ingilizce durur.
   Olculdu: yazi duz bir duvar panelinin ortasinda (x 1155..1215,
   y 390..462), etrafinda temiz zemin var. Her satir icin bandin
   solundaki ve sagindaki temiz duvar arasinda dogrusal ara deger
   yaziliyor; duvarin kendi egimi 60 px'lik acikligi gozle belli
   etmiyor.

2. Alt %40 bos cilali zemin. Hero'da bu kadar bos zemin kadraji
   zayiflatiyor; kirpma zemini kesip asilma cizgisini kadrajin alt
   ucuna yakin tutuyor.

Cikti kaynak/hero altinda kalir; siteye baglanmasi ayri bir istir.
"""
import io
import os
import sys

from PIL import Image

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

BURA = os.path.dirname(os.path.abspath(__file__))
KAYNAK = os.path.join(BURA, 'kaynak', 'hero', 'salon-genel.png')
CIKTI = os.path.join(BURA, 'kaynak', 'hero')

# Yazinin kutusu, olculdu (bkz. modul aciklamasi). Pay birakiliyor:
# harflerin kenar yumusamasi kutunun 2-3 px disina tasiyor.
YAZI = (1152, 386, 1219, 466)
PAY = 4

# Temiz duvarin alinacagi mesafe: bandin iki yanindan bu kadar uzakta
# hala ayni duvar panelinde olan sutunlar.
ORNEK = 10


def yaziyi_kaldir(im):
    """Yazi bandini ustundeki ve altindaki temiz duvarla doldur.

    EKSEN ONEMLI. Ilk denemede satir boyunca (yatay) ara deger
    verilmisti ve sonuc yapistirilmis belli olan bir dikdortgendi:
    duvarin dokusu DIKEY bantlar halinde, yani degisim x boyunca. Yatay
    ara deger tam o degisimi siliyor ve duz bir yama birakiyor.

    Dogrusu sutun boyunca (dikey) ara deger: her x kendi ustundeki ve
    altindaki temiz duvardan besleniyor, boylece duvarin yatay yapisi
    (panel kenari, bantlar) oldugu gibi kaliyor ve yalnizca yazinin
    bulundugu dikey aciklik kapaniyor.

    Kenarlar ayrica yumusatiliyor: sert sinir, dolgu kusursuz olsa bile
    yamayi belli ediyor.
    """
    import numpy as np

    x0, y0, x1, y1 = YAZI
    x0 -= PAY; y0 -= PAY; x1 += PAY; y1 += PAY

    a = np.asarray(im, dtype=np.float64).copy()
    # Temiz besleyici satirlar: bandin ustunde ve altinda ORNEK kadar
    # uzakta, birkac satirin ortalamasi (tek satir gurultuyu tasir).
    ust = a[y0 - ORNEK - 3:y0 - ORNEK, x0:x1].mean(axis=0)
    alt = a[y1 + ORNEK:y1 + ORNEK + 3, x0:x1].mean(axis=0)

    boy = y1 - y0
    t = np.linspace(0.0, 1.0, boy)[:, None, None]
    dolgu = ust[None, :, :] * (1.0 - t) + alt[None, :, :] * t

    # Tuy: kenarlarda dolgu ile ozgun goruntu karisiyor. Kosinus rampasi
    # -- dogrusal rampa kendi kirilma cizgisini birakiyor.
    TUY = 7

    def rampa(n, uzunluk):
        r = np.ones(n)
        u = min(uzunluk, n // 2)
        if u > 0:
            k = 0.5 - 0.5 * np.cos(np.pi * (np.arange(u) + 0.5) / u)
            r[:u] = k
            r[-u:] = k[::-1]
        return r

    m = rampa(boy, TUY)[:, None] * rampa(x1 - x0, TUY)[None, :]
    m = m[:, :, None]

    a[y0:y1, x0:x1] = dolgu * m + a[y0:y1, x0:x1] * (1.0 - m)
    return Image.fromarray(np.clip(a, 0, 255).astype('uint8'), 'RGB')


def kirp(im, alt_kes=0.13, ust_kes=0.03):
    """Olu zemini kes, GENISLIGE DOKUNMA.

    Ilk deneme 16:9 oranini korumak icin yataydan da kesiyordu ve sonuc
    kotuydu: soldaki buyuk kalabalik sahnesi bir dilime iniyordu. Oysa
    bu kadrajin tek isi sekiz eseri ayni mekanda gostermek; kenardaki
    eseri kesmek kadrajin varlik sebebini yiyor.

    O yuzden tam genislik korunuyor ve yalnizca dikey kirpiliyor: oran
    16:9'dan ~2.1:1'e geniliyor, ki hero bandi icin zaten iyi bir sekil.

    Kirpma az tutuluyor -- son kadraj kararini VARLIGA GOMMEK yanlis
    olur. Sayfa object-fit: cover ve object-position ile istedigi bandi
    seciyor; burada kesilen sey yalnizca hicbir kadrajda ise yaramayan
    bos cilali zemin ve tavanin ust serididir.
    """
    W, H = im.size
    ust = int(round(H * ust_kes))
    alt = int(round(H * alt_kes))
    return im.crop((0, ust, W, H - alt))


def main():
    if not os.path.isfile(KAYNAK):
        raise SystemExit('kaynak yok: ' + KAYNAK)
    im = Image.open(KAYNAK).convert('RGB')
    print('kaynak      %s  %dx%d' % (os.path.basename(KAYNAK), *im.size))

    im = yaziyi_kaldir(im)
    temiz = os.path.join(CIKTI, 'salon-temiz.png')
    im.save(temiz)
    print('yazi kaldirildi -> %s' % os.path.basename(temiz))

    k = kirp(im)
    print('kirpildi    %dx%d  (oran %.3f)' % (*k.size, k.size[0] / float(k.size[1])))

    # Iki olcu: genis ekran ve telefon. Hero tam genislik oldugu icin
    # buyuk olcu 2400 px; telefonda dikey kadraj daha iyi durur ama o
    # ayri bir karar, simdilik ayni kadrajin kucugu.
    for ad, en in (('hero-2400', 2400), ('hero-1200', 1200)):
        boy = int(round(en * k.size[1] / float(k.size[0])))
        r = k.resize((en, boy), Image.LANCZOS)
        yol = os.path.join(CIKTI, ad + '.webp')
        r.save(yol, 'WEBP', quality=82, method=6)
        print('%-12s %4dx%-4d  %6d bayt' % (ad, en, boy, os.path.getsize(yol)))


if __name__ == '__main__':
    main()
