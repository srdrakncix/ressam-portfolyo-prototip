# -*- coding: utf-8 -*-
"""Menü panelinin okunurluk kapısı.

Panel eskiden BOYAYDI: dokuz fırça darbesi, aralarında nefes delikleri,
altında yazı için ayrı bir taban. Orada okunurluk ancak ölçülerek
bilinebiliyordu — `firca.py` yirmi yazı kutusunun altındaki opaklığı ve
kontrastı gerçek piksellerden okuyordu, çünkü rengin ne olduğunu CSS
söylemiyordu.

Panel düz krem olunca (müşteri kararı: "fırça darbeli menü de depoya
kalkıyor, aynı renk kalsın fakat normal, usturuplu, sade bir menü")
bilinmeyen kalmadı: zemin iki hex arası bir rampa, mürekkepler de hex.
Yani ölçüm kapalı forma indi. Ama KALKMADI — bu projede aynı hata üç kez
oldu (satır aydınlığı, #lang opaklığı, --tasma-oran): ölçüm bir sayıyı
doğrularken çalışan kod başkasını kullanıyordu. Onun için sayılar tek
yerde (kabuk.css panel paleti) duruyor ve buradan OKUNUYOR, burada
yeniden yazılmıyor.

Ölçütler:
  - metin           4.5:1  (WCAG AA)
  - büyük metin     3.0:1  (>= 24 px ya da 18.66 px kalın)
  - grafik/kenar    3.0:1  (WCAG 2.4.11 / 1.4.11)

Zemin olarak panelin EN KOYU ucu alınıyor (--panel-alt): koyu mürekkep
için en kötü durum o. Satır renkleri çalışma anında zeminden üretildiği
için (kabuk.js paintMenu) tek bir renk değil; kelepçenin bütün köşeleri
deneniyor ve en kötüsü rapor ediliyor.

Kullanım:  python menu.py          (hata varsa çıkış kodu 1)
"""
import colorsys
import io
import os
import re
import sys

KOK = os.path.dirname(os.path.abspath(__file__))
KABUK = os.path.join(KOK, 'kabuk.css')

METIN, IRI, GRAFIK = 4.5, 3.0, 3.0

# (degisken, olcut, ad, esik). Panelin uzerinde duran her murekkep.
MUREKKEPLER = [
    ('--m-grup',        'grup etiketi (11 px)',        METIN),
    ('--m-ozel',        'Galeri satiri (17-22 px)',    IRI),
    ('--m-cikis',       'cikis satiri',                METIN),
    ('--m-dil',         'dil kodlari (11 px)',         METIN),
    ('--m-dil-aktif',   'etkin dil + odak halkasi',    METIN),
    ('--m-oniz-ust',    'onizleme ust satiri (11 px)', METIN),
    ('--m-oniz-ad',     'onizleme adi (19-26 px)',     IRI),
    ('--m-oniz-alt',    'onizleme alt metni (13.5 px)', METIN),
    ('--m-kapat-cizgi', 'kapatma cizgisi (grafik)',    GRAFIK),
]


def _lin(c):
    c /= 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def parlaklik(rgb):
    r, g, b = rgb
    return 0.2126 * _lin(r) + 0.7152 * _lin(g) + 0.0722 * _lin(b)


def kontrast(a, b):
    ya, yb = parlaklik(a), parlaklik(b)
    return (max(ya, yb) + 0.05) / (min(ya, yb) + 0.05)


def hex_coz(h):
    h = h.strip().lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def oku():
    """Paleti kabuk.css'ten okur. Eksik bir degisken sessizce gecmesin:
    CSS'te `var(--m-x, #yedek)` yazili oldugu icin degisken silinse bile
    sayfa calisir, yani gozle farkedilmez. Kapi farkeder."""
    s = io.open(KABUK, encoding='utf-8').read()
    pal = dict(re.findall(r'(--[a-z0-9-]+):\s*(#[0-9a-fA-F]{6})', s))
    sayi = dict(re.findall(r'(--satir-[a-z-]+):\s*([0-9.]+)', s))
    return pal, sayi


def satir_renkleri(sayi):
    """kabuk.js paintMenu'nun uretebilecegi BUTUN satir renkleri.

    Ton [merkez-pay, merkez+pay] araligina, doygunluk tavana, aydinlik
    da parlaklik + ((i*3)%%7)*adim basamaklarina kelepceli. En kotu durum
    en ACIK basamak ve tonun uclari; hepsi deneniyor, tahmin yok."""
    merkez = float(sayi.get('--satir-ton-merkez', 33.0))
    pay = float(sayi.get('--satir-ton-pay', 11.0))
    doy = float(sayi.get('--satir-doygunluk', 0.40))
    tab = float(sayi.get('--satir-parlaklik', 0.20))
    adim = float(sayi.get('--satir-adim', 0.015))
    basamaklar = sorted({((i * 3) % 7) for i in range(13)})
    out = []
    for h in (merkez - pay, merkez, merkez + pay):
        for s in (0.0, doy / 2, doy):
            for k in basamaklar:
                l = tab + k * adim
                r, g, b = colorsys.hls_to_rgb(h / 360.0, l, s)
                out.append((int(r * 255 + 0.5), int(g * 255 + 0.5),
                            int(b * 255 + 0.5), h, s, l))
    return out


def main():
    pal, sayi = oku()
    for gerekli in ('--panel-ust', '--panel-alt'):
        if gerekli not in pal:
            sys.exit('HATA: kabuk.css icinde %s yok.' % gerekli)
    ust, alt = hex_coz(pal['--panel-ust']), hex_coz(pal['--panel-alt'])
    # Koyu murekkep icin en kotu zemin panelin EN KOYU ucu.
    zemin = alt if parlaklik(alt) < parlaklik(ust) else ust
    print('panel  %s -> %s   (kapi %s ucuna karsi olculuyor)'
          % (pal['--panel-ust'], pal['--panel-alt'],
             'alt' if zemin is alt else 'ust'))
    print()

    hata = []
    for ad, aciklama, esik in MUREKKEPLER:
        if ad not in pal:
            hata.append('%s kabuk.css icinde yok' % ad)
            continue
        k = kontrast(hex_coz(pal[ad]), zemin)
        im = 'OK ' if k >= esik else 'DUSUK'
        print('%-5s %-16s %-30s %5.2f:1  (esik %.1f)'
              % (im, pal[ad], aciklama, k, esik))
        if k < esik:
            hata.append('%s %.2f:1 < %.1f (%s)' % (ad, k, esik, aciklama))

    # Satir renkleri: calisma aninda uretiliyor, tek hex degil.
    enKotu = None
    for r, g, b, h, s, l in satir_renkleri(sayi):
        k = kontrast((r, g, b), zemin)
        if enKotu is None or k < enKotu[0]:
            enKotu = (k, (r, g, b), h, s, l)
    k, renk, h, s, l = enKotu
    im = 'OK ' if k >= METIN else 'DUSUK'
    print('%-5s #%02x%02x%02x        %-30s %5.2f:1  (esik %.1f)'
          % (im, renk[0], renk[1], renk[2],
             'menu satirlari en kotu hal', k, METIN))
    print('      kelepce kosesi: ton %.0f  doygunluk %.2f  aydinlik %.3f'
          % (h, s, l))
    if k < METIN:
        hata.append('menu satiri %.2f:1 < %.1f' % (k, METIN))

    print()
    if hata:
        sys.exit('MENU OKUNURLUK KAPISI GECMEDI:\n  ' + '\n  '.join(hata))
    print('menu okunurluk kapisi gecti (%d murekkep + satir kelepcesi)'
          % len(MUREKKEPLER))


if __name__ == '__main__':
    main()
