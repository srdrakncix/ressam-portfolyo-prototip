# -*- coding: utf-8 -*-
"""Eser seçimi: EN-BOY ORANINA göre.

Önceki seçim en açık 18 eseri alıyordu. Sonuç duvarda "pazar reyonu" gibiydi:
40 cm'lik eserin yanında 184 cm'lik eser, dikeyin yanında yatay. Çerçeveler
büyüklü küçüklü olunca duvar dağınık görünüyor.

Artık ölçüt oran: 1.49–1.57 bandındaki eserler alınıyor (±%2.6). Genişlik
hepsinde AYNI (132 cm), yükseklik her eserin kendi gerçek oranından geliyor,
yani hiçbir eser kırpılmıyor ya da bozulmuyor; yükseklik farkı en fazla %6.
Tek formatta çalışan bir ressam — hem gerçekçi hem duvarda derli toplu.

full genişliği 1686'ya çıkarıldı: detay görünümü tam ekran beyaz zeminde
açıldığı için 1500 px yetmiyordu. 1686 kaynağın tavanı.
"""
import json, io, os, base64
from PIL import Image, ImageFilter

SECILEN = [64772, 64736, 68792, 64724, 68784, 64764, 64732, 64748, 65353, 68388, 69844]
EN_CM = 132.0                       # bütün eserlerin genişliği
FULL_W, FULL_Q, LQIP_W, LQIP_Q = 1686, 78, 20, 40

pool = {a['id']: a for a in json.load(io.open('aic_pool.json', encoding='utf-8'))['George Inness']}


def enc(im, w, q, blur=0):
    im = im.copy(); im.thumbnail((w, w * 10), Image.LANCZOS)
    if blur: im = im.filter(ImageFilter.GaussianBlur(blur))
    b = io.BytesIO(); im.save(b, 'WEBP', quality=q, method=6)
    return base64.b64encode(b.getvalue()).decode(), len(b.getvalue())


def avg(im):
    s = im.copy(); s.thumbnail((1, 1)); return s.convert('RGB').getpixel((0, 0))


out, toplam = [], 0
for aid in SECILEN:
    im = Image.open(os.path.join('cache', f'{aid}.jpg')).convert('RGB')
    oran = im.width / im.height
    boy = round(EN_CM / oran)                      # yükseklik gerçek orandan
    r, g, b = avg(im)
    full, sz = enc(im, FULL_W, FULL_Q)
    lq, _ = enc(im, LQIP_W, LQIP_Q, blur=1)
    a = pool[aid]
    toplam += sz
    out.append({'id': aid, 'src_title': a['title'], 'src_artist': a['artist_title'],
                'src_date': a['date_display'], 'src_medium': a['medium_display'],
                'src_dim': f'{boy} × {EN_CM:.0f} cm',
                'w': im.width, 'h': im.height, 'ratio': round(oran, 4),
                'tone': f'#{r:02x}{g:02x}{b:02x}', 'full': full, 'lqip': lq})
    print('%-8s oran %.3f  ->  %g × %g cm   %4d KB   %s'
          % (aid, oran, boy, EN_CM, sz // 1024, a['title'][:32]))

json.dump(out, io.open('images.json', 'w', encoding='utf-8'))
oranlar = [o['ratio'] for o in out]
boylar = [float(o['src_dim'].split('×')[0]) for o in out]
print('\n%d eser · toplam %.2f MB' % (len(out), toplam / 1048576))
print('oran  %.3f – %.3f  (yayılım %%%.1f)' % (min(oranlar), max(oranlar),
      100 * (max(oranlar) / min(oranlar) - 1)))
print('boy   %g – %g cm  (yayılım %%%.1f)' % (min(boylar), max(boylar),
      100 * (max(boylar) / min(boylar) - 1)))
print('genişlik hepsinde %g cm' % EN_CM)
