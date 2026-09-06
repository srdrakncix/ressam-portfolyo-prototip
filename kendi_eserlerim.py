# -*- coding: utf-8 -*-
"""Gerçek eserleri siteye almak.

Kullanım:
    python kendi_eserlerim.py <eserler_klasoru>

Klasördeki her görsel bir eser olur. Dosya adı sıralamayı belirler,
bu yüzden 01-aksam-kizili.jpg, 02-ay-dogarken.jpg gibi isimlendir.

Script her görseli:
  - 1500 piksele indirir, WebP q72 olarak kodlar
  - 20 piksellik bulanık bir önizleme (LQIP) üretir
  - baskın rengi hesaplar (paspartu ve zemin rengi bundan türüyor)
  - en-boy oranını ölçer
ve images.json dosyasını yeniden yazar.

Sonra:
    python build.py aski.html    out_aski.html
    python build.py fasikul.html out_fasikul.html
    python build.py kunye.html   out_kunye.html

DİKKAT — eser bilgileri (başlık, yıl, seri, ölçü, not, durum) content.py
dosyasındaki WORKS sözlüğünden geliyor. Anahtarlar buradaki 'id' değerleriyle
eşleşmeli. Bu script id olarak dosya adının uzantısız hâlini kullanır.
"""
import io, os, sys, json, base64
from PIL import Image, ImageFilter

FULL_W, FULL_Q = 1500, 72
LQIP_W, LQIP_Q = 20, 40
EXT = {'.jpg', '.jpeg', '.png', '.tif', '.tiff', '.webp', '.bmp'}


def enc(im, w, q, blur=0):
    im = im.copy()
    im.thumbnail((w, w * 10), Image.LANCZOS)
    if blur:
        im = im.filter(ImageFilter.GaussianBlur(blur))
    buf = io.BytesIO()
    im.save(buf, 'WEBP', quality=q, method=6)
    return base64.b64encode(buf.getvalue()).decode(), len(buf.getvalue())


def avg_hex(im):
    s = im.copy()
    s.thumbnail((1, 1))
    r, g, b = s.convert('RGB').getpixel((0, 0))
    return f'#{r:02x}{g:02x}{b:02x}'


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    folder = sys.argv[1]
    files = sorted(f for f in os.listdir(folder)
                   if os.path.splitext(f)[1].lower() in EXT)
    if not files:
        sys.exit(f'{folder} içinde görsel bulunamadı.')

    out, total = [], 0
    for f in files:
        path = os.path.join(folder, f)
        im = Image.open(path).convert('RGB')
        full, size = enc(im, FULL_W, FULL_Q)
        lq, _ = enc(im, LQIP_W, LQIP_Q, blur=1)
        total += size
        wid = os.path.splitext(f)[0]
        out.append({
            'id': wid,
            'src_title': wid, 'src_artist': '', 'src_date': '',
            'src_medium': '', 'src_dim': '',      # ölçüyü content.py'den ver
            'w': im.width, 'h': im.height,
            'ratio': round(im.width / im.height, 4),
            'tone': avg_hex(im),
            'full': full, 'lqip': lq,
        })
        print(f'{wid:34} {im.width}×{im.height}  oran {out[-1]["ratio"]:.2f}  '
              f'{out[-1]["tone"]}  {round(size/1024)} KB')

    json.dump(out, io.open('images.json', 'w', encoding='utf-8'))
    mb = total * 1.34 / 1024 / 1024
    print(f'\n{len(out)} eser · gömülü toplam ~{mb:.2f} MB · 16 MB sınırı '
          f'{"AŞILDI — FULL_W veya FULL_Q düşür" if mb > 14 else "güvenli"}')
    print('\nSıradaki: content.py içindeki WORKS anahtarlarını yukarıdaki '
          'id değerleriyle eşle, sonra build.py çalıştır.')


if __name__ == '__main__':
    main()
