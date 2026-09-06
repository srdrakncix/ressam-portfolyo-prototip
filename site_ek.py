# -*- coding: utf-8 -*-
"""Yayın için gereken yardımcı dosyalar: favicon, 404, robots, sitemap.

Favicon harf içermiyor. Monogram (CS) koysaydık müşterinin gerçek adı
gelince değişmesi gerekirdi; çerçeveli bir manzara işareti hem ada bağlı
değil hem 16 px'te okunuyor.
"""
import os
from PIL import Image, ImageDraw

KOK = 'https://srdrakncix.github.io/ressam-portfolyo-prototip/'
SITE = 'site'

FAVICON = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">
  <rect width="32" height="32" rx="6" fill="#161c14"/>
  <rect x="5.5" y="7" width="21" height="18" fill="#2b3425"/>
  <rect x="5.5" y="17.5" width="21" height="7.5" fill="#6d6a3c"/>
  <circle cx="16" cy="14" r="3.1" fill="#e8cb8c"/>
  <rect x="5.5" y="7" width="21" height="18" fill="none" stroke="#c9a86a" stroke-width="1.5"/>
</svg>
'''
open(os.path.join(SITE, 'favicon.svg'), 'w', encoding='utf-8').write(FAVICON)

# apple-touch-icon: aynı işaret, 180 px
S = 180
im = Image.new('RGB', (S, S), (22, 28, 20))
d = ImageDraw.Draw(im)
k = S / 32.0
d.rectangle([5.5*k, 7*k, 26.5*k, 25*k], fill=(43, 52, 37))
d.rectangle([5.5*k, 17.5*k, 26.5*k, 25*k], fill=(109, 106, 60))
d.ellipse([(16-3.1)*k, (14-3.1)*k, (16+3.1)*k, (14+3.1)*k], fill=(232, 203, 140))
d.rectangle([5.5*k, 7*k, 26.5*k, 25*k], outline=(201, 168, 106), width=max(1, int(1.5*k)))
im.save(os.path.join(SITE, 'apple-touch-icon.png'))

open(os.path.join(SITE, 'robots.txt'), 'w', encoding='utf-8').write(
    'User-agent: *\nAllow: /\n\nSitemap: %ssitemap.xml\n' % KOK)

SAYFALAR = [('', '1.0'), ('mekan.html', '0.9'), ('sergi.html', '0.8')]
sm = ['<?xml version="1.0" encoding="UTF-8"?>',
      '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
for yol, oncelik in SAYFALAR:
    sm += ['  <url>', '    <loc>%s%s</loc>' % (KOK, yol),
           '    <priority>%s</priority>' % oncelik, '  </url>']
sm.append('</urlset>')
open(os.path.join(SITE, 'sitemap.xml'), 'w', encoding='utf-8').write('\n'.join(sm) + '\n')

# 404 — sitenin sade sayfasının diliyle, üç dilde tek satır
open(os.path.join(SITE, '404.html'), 'w', encoding='utf-8').write('''<!doctype html>
<html lang="tr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Sayfa bulunamadı — Cemal Sağlam</title>
<meta name="robots" content="noindex">
<link rel="icon" href="/ressam-portfolyo-prototip/favicon.svg" type="image/svg+xml">
<style>
  :root { color-scheme: light; }
  body {
    margin: 0; min-height: 100vh; background: #fff; color: #111;
    display: grid; place-items: center; padding: 24px;
    font: 400 15px/1.6 -apple-system, "Segoe UI", Helvetica, Arial, sans-serif;
    -webkit-font-smoothing: antialiased;
  }
  main { max-width: 34em; text-align: center; }
  .kod { font-size: 12px; letter-spacing: .22em; color: #999; text-transform: uppercase; }
  h1 { font-weight: 400; font-size: clamp(22px, 1.3rem + 1vw, 30px); margin: 14px 0 6px; }
  p { margin: 0 0 6px; color: #555; }
  p[lang] { font-size: 14px; color: #777; }
  a {
    display: inline-block; margin-top: 26px; color: #111;
    border-bottom: 1px solid #111; text-decoration: none; padding-bottom: 2px;
  }
  a:hover { opacity: .6; }
</style>
</head>
<body>
<main>
  <div class="kod">404</div>
  <h1>Aradığınız sayfa burada değil.</h1>
  <p lang="en">The page you are looking for is not here.</p>
  <p lang="fr">La page que vous cherchez n’est pas ici.</p>
  <a href="/ressam-portfolyo-prototip/">Cemal Sağlam — Resim</a>
</main>
</body>
</html>
''')

# terk edilmiş Three.js prototipi yayından kalksın
olu = os.path.join(SITE, 'galeri.html')
if os.path.exists(olu):
    os.remove(olu); print('yayindan kaldirildi: galeri.html')

for f in ['favicon.svg', 'apple-touch-icon.png', 'robots.txt', 'sitemap.xml', '404.html']:
    print('%-22s %6d bayt' % (f, os.path.getsize(os.path.join(SITE, f))))
