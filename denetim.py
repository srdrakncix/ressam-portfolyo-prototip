# -*- coding: utf-8 -*-
"""Yayından önceki denetimler — derlemenin hemen ardından koşar.

    python yayinla.py && python denetim.py

Cloudflare Pages'in derleme komutu tam olarak bu. Bir denetim düşerse komut
hata verir, yeni sürüm YAYINA ÇIKMAZ; site son başarılı hâliyle kalır.
(Eskiden aynı denetimler GitHub Actions iş akışının içinde satır satır
yazılıydı; tek yerde dursunlar diye buraya taşındı.)

1. Çıktı tam mı: zorunlu dosyalar, her eserin görseli, sayfalar eserleri
   gerçekten taşıyor mu (ya da site kapalıysa kök sayfa "yapım aşamasında"
   sayfası mı).
2. Menü okunurluğu (menu.py).
3. Yayındaki sayfaların JavaScript'i sözdizimi bakımından sağlam mı.
4. Panelin kapıcısı ve şifreli giriş denemeleri.
"""
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

KOK = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.join(KOK, 'site')
hatalar = []


def adim(ad):
    print('\n── ' + ad)


def hata(m):
    hatalar.append(m)
    print('  HATA ' + m)


# ── 1) çıktı ────────────────────────────────────────────────────────────────
adim('çıktı')
yayin = json.load(io.open(os.path.join(SITE, 'yayin.json'), encoding='utf-8'))
hedef = yayin.get('hedef', 'yerel')
yakinda = yayin.get('yakinda', False)
print('  hedef: ' + {'site': 'saglam.fr (site, panelsiz)', 'panel': 'panel (Cloudflare)',
                     'yerel': 'yerel (site + /panel/)'}.get(hedef, hedef))

if hedef == 'panel':
    # Yalnız panel: kök sayfa panel, sitenin adresi biliniyor, dizine kapalı.
    for y in ('index.html', 'secenekler.json', 'robots.txt'):
        if not os.path.exists(os.path.join(SITE, y)):
            hata('eksik dosya: site/' + y)
    se = json.load(io.open(os.path.join(SITE, 'secenekler.json'), encoding='utf-8'))
    if not str(se.get('site', '')).startswith('https://'):
        hata('panelin site adresi yok ya da https değil: %r' % se.get('site'))
    if 'Disallow: /' not in io.open(os.path.join(SITE, 'robots.txt'), encoding='utf-8').read():
        hata('panel arama motorlarına açık')
    if not os.path.exists(os.path.join(KOK, 'functions', 'api', '[[yol]].js')):
        hata('kapıcı yok: functions/api/[[yol]].js')
else:
    gerekli = ['index.html', '404.html', 'favicon.svg', 'robots.txt', 'sitemap.xml',
               'assets/zemin/oruntu.webp', 'yayin.json', 'eserler.json']
    gerekli += ['onizleme/index.html', 'onizleme/galeri/index.html'] if yakinda else ['galeri/index.html']
    if hedef == 'yerel':
        gerekli += ['panel/index.html', 'panel/secenekler.json']
    for y in gerekli:
        if not os.path.exists(os.path.join(SITE, *y.split('/'))):
            hata('eksik dosya: site/' + y)
    # saglam.fr'de panel OLMAMALI (panel kendi adresinde).
    if hedef == 'site' and os.path.exists(os.path.join(SITE, 'panel')):
        hata('saglam.fr yayınında panel var — olmamalı')

if hedef != 'panel':
    # Panelde "Gizle" denmiş eserler sitede yok; denetim onları aramaz.
    kayitlar = []
    for f in sorted(os.listdir(os.path.join(KOK, 'icerik', 'eserler'))):
        if f.endswith('.json'):
            k = json.load(io.open(os.path.join(KOK, 'icerik', 'eserler', f), encoding='utf-8'))
            if not k.get('gizli'):
                kayitlar.append(k)
    if not kayitlar:
        hata('sitede gösterilecek hiç eser yok')
    for k in kayitlar:
        if not os.path.exists(os.path.join(SITE, 'assets', k['slug'] + '.webp')):
            hata('görseli üretilmeyen eser: ' + k['slug'])

    if yakinda:
        if 'Le site est en construction' not in io.open(os.path.join(SITE, 'index.html'), encoding='utf-8').read():
            hata('site kapalı ama kök sayfa "yapım aşamasında" sayfası değil')
        sayfa = os.path.join(SITE, 'onizleme', 'galeri', 'index.html')
    else:
        sayfa = os.path.join(SITE, 'galeri', 'index.html')
    if os.path.exists(sayfa):
        govde = io.open(sayfa, encoding='utf-8').read()
        for k in kayitlar[:3]:
            if k['baslik'] not in govde:
                hata('galeride eser yok: ' + k['baslik'])
    mb = sum(os.path.getsize(os.path.join(r, f)) for r, _, fs in os.walk(SITE) for f in fs) / 1048576
    print('  %d eser, %s, site/ %.2f MB' % (len(kayitlar), 'site kapalı (önizleme var)' if yakinda else 'site açık', mb))

# ── 2) menü okunurluğu ──────────────────────────────────────────────────────
adim('menü okunurluğu')
r = subprocess.run([sys.executable, 'menu.py'], cwd=KOK, capture_output=True, text=True,
                   encoding='utf-8', errors='replace')
print('  ' + (r.stdout.strip().splitlines() or [''])[-1])
if r.returncode:
    hata('menü okunurluk kapısı düştü\n' + r.stdout[-600:] + r.stderr[-600:])

# ── 3) JavaScript sözdizimi + 4) denemeler (node gerekiyor) ─────────────────
node = shutil.which('node')
if not node:
    hata('node bulunamadı — JavaScript denetlenemedi')
else:
    adim('JavaScript sözdizimi')
    for y in ['index.html', 'galeri/index.html', 'onizleme/index.html',
              'onizleme/galeri/index.html', 'panel/index.html']:
        yol = os.path.join(SITE, *y.split('/'))
        if not os.path.exists(yol):
            continue
        js = '\n'.join(re.findall(r'<script(?![^>]*\bsrc=)[^>]*>(.*?)</script>',
                                  io.open(yol, encoding='utf-8').read(), re.S))
        gec = os.path.join(tempfile.gettempdir(), '_denetim.js')
        io.open(gec, 'w', encoding='utf-8').write(js)
        r = subprocess.run([node, '--check', gec], capture_output=True, text=True)
        print('  %-28s %s' % (y, 'tamam' if not r.returncode else 'BOZUK'))
        if r.returncode:
            hata('bozuk JavaScript: ' + y + ' — ' + (r.stderr.strip().splitlines() or [''])[-1][:200])

    for ad, betik in (('panel kapıcısı', 'panel/kapici-deneme.mjs'),
                      ('şifreli giriş', 'panel/kilit-deneme.mjs')):
        adim(ad)
        r = subprocess.run([node, betik], cwd=KOK, capture_output=True, text=True,
                           encoding='utf-8', errors='replace')
        print('  ' + (r.stdout.strip().splitlines() or [''])[-1])
        if r.returncode:
            hata(ad + ' denemesi düştü\n' + r.stdout[-800:] + r.stderr[-400:])

print()
if hatalar:
    print('DENETİM DÜŞTÜ — %d sorun. Bu sürüm yayına çıkmayacak.' % len(hatalar))
    sys.exit(1)
print('Denetim tamam.')
