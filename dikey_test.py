# -*- coding: utf-8 -*-
"""DİKEY FORMAT TESTİ.

Mevcut on bir eserin on biri de yatay — çünkü çerçeveleri eşitlemek için
seçim en-boy oranına göre daraltıldı (1.49–1.57) ve o bantta dikey eser yok.
Müşterinin gerçek işlerinde kesinlikle dikey tuval olacak; duvarın ve
kartların dikeyle ne yaptığı hiç denenmedi.

Bu betik depo verisine DOKUNMADAN, bellekte bir dikey eser ekleyip test
sayfaları üretiyor. En zorlu hâl seçiliyor: diğerleriyle aynı genişlikte
(132 cm) ama oranı gereği çok daha uzun bir tuval.
"""
import base64
import io
import os

from PIL import Image

import build

CIK = 'site'
KAYNAK_ID = 110561          # oran 0.789 — dikey
ASIRI = True                # 230 cm boyunda uc bir tuval ile sina
EN_CM = 132.0


def kodla(im, w, q):
    k = im.copy()
    k.thumbnail((w, w * 10), Image.LANCZOS)
    b = io.BytesIO()
    k.save(b, 'WEBP', quality=q, method=6)
    return base64.b64encode(b.getvalue()).decode()


data = build.build_data()
im = Image.open('cache/%d.jpg' % KAYNAK_ID).convert('RGB')
oran = im.width / im.height
boy = 230 if ASIRI else round(EN_CM / oran)

ornek = data['works'][0]
w = dict(ornek)
w.update({
    'id': str(KAYNAK_ID), 'no': '12', 'slug': 'dikey-test',
    'title': 'Dikey Test', 'series': 'sabah', 'year': 2024,
    'note': 'Dikey format sınaması.', 'status': 'satilik',
    'size': '%d × %d cm' % (boy, EN_CM),
    'sizeIn': '%s × %s in' % (build.inches(boy), build.inches(EN_CM)),
    'cw': round(boy*oran), 'ch': boy, 'area': EN_CM * boy,
    'ratio': round(oran, 4), 'px': [im.width, im.height], 'portrait': True,
    'collection': '', 'collYear': 0,
    'lqip': 'data:image/webp;base64,' + kodla(im, 20, 40),
    'src': 'data:image/webp;base64,' + kodla(im, 1686, 78),
})
data['works'].insert(0, w)   # basa koy: acilista gorunsun
for dil in data['i18n']:
    data['i18n'][dil]['works'][str(KAYNAK_ID)] = {'gloss': '', 'note': w['note']}

print('eklenen dikey eser: %s cm  oran %.3f' % (w['size'].replace(' ', ' '), oran))
print('diger eserler     : 83–88 × 132 cm  oran 1.50–1.59')

kb = build.write_assets(data, CIK) / 1024
for tpl, ad in [('sergi.html', '_dikey_sergi.html'), ('mekan.html', '_dikey_mekan.html')]:
    out = build.render(tpl, data, True)
    io.open(os.path.join(CIK, ad), 'w', encoding='utf-8').write(out)
    print('%-22s %d eser' % (ad, len(data['works'])))
print('assets %.2f MB' % (kb / 1024))
