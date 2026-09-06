# -*- coding: utf-8 -*-
"""Dikişsiz salon duvarı karosu.

Karo duvardan RASTGELE bir x'ten kesilirse karonun sağ kenarı bir sonraki
karonun sol kenarının devamı olmaz: silmeler karşıya geçmez, süs motifleri
ikiye bölünür, parke kırılır. Ton eşitlemek bunu gizlemez — sorun geometri.

İki kural:
  1) Kesim DÜZ DUVARA düşsün (pilastr süslerinin ortasına değil), ki ek yeri
     zaten desensiz bir alana gelsin.
  2) Karonun sağ ucuna, SOL ucun hemen solundaki şerit kopyalansın. O zaman
        karo_N[-1] = kaynak[XA-1]   ve   karo_N+1[0] = kaynak[XA]
     yani kaynakta yan yana iki piksel; ek yeri matematiksel olarak yok.

Tekrar periyodu (L) elle tahmin edilmiyor, iki pilastr arası çapraz
korelasyonla ölçülüyor. Bu karoya kenar parlaklığı rampası UYGULANMAZ:
rampa iki ucu farklı katsayılarla çarpıp tam eşleşmeyi bozar.
"""
import os
import numpy as np
from PIL import Image

KAYNAK = 'kaynak/duvar_genis.png'
CIKTI = 'site/assets/duvar/salon.webp'
XA = 428          # 1. pilastr ile büyük pano arasındaki düz duvar
BINDIRME = 46     # sağ uca kopyalanacak düz duvar şeridinin eni

a = np.asarray(Image.open(KAYNAK).convert('RGB')).astype(np.float32)
H, W, _ = a.shape
gri = a.mean(2)

# ── tekrar periyodu: pilastr komşuluğunu ileride ara ─────────────────────
ref = gri[:, 240:400]
ref = ref - ref.mean()
en_iyi, en_iyi_skor = None, -2.0
for L in range(700, 860):
    kar = gri[:, 240 + L:400 + L]
    if kar.shape[1] != ref.shape[1]:
        continue
    kar = kar - kar.mean()
    s = float((ref * kar).sum() / (np.linalg.norm(ref) * np.linalg.norm(kar)))
    if s > en_iyi_skor:
        en_iyi_skor, en_iyi = s, L
L = en_iyi
print('tekrar periyodu L = %d px   (korelasyon %.4f)' % (L, en_iyi_skor))

# ── karoyu kes ve sağ ucu sol ucun devamı yap ────────────────────────────
karo = a[:, XA:XA + L].copy()
serit = a[:, XA - BINDIRME:XA].copy()

# Sınırdaki ışık farkını düzelt, ama SAĞ UCU BOZMA: katsayı sınırda c,
# karonun son sütununda tam 1.0.
komsu = karo[:, L - BINDIRME - 4:L - BINDIRME].mean()
bas = serit[:, 0:4].mean()
c = komsu / bas if bas > 0 else 1.0
t = np.cos(np.linspace(0, np.pi / 2, BINDIRME)) ** 2
karo[:, L - BINDIRME:] = np.clip(serit * (1 + (c - 1) * t)[None, :, None], 0, 255)

out = Image.fromarray(karo.astype(np.uint8), 'RGB')
out.save(CIKTI, 'WEBP', quality=88, method=6)

# ── doğrulama: üç karoyu yan yana koy, ek yerlerini ölç ──────────────────
k = np.asarray(out).astype(np.float32).mean(2)
serit3 = np.hstack([k, k, k])
d = np.abs(np.diff(serit3, axis=1)).mean(0)
ic = float(np.median(d))
p95 = float(np.percentile(d, 95))
ek1, ek2 = float(d[L - 1]), float(d[2 * L - 1])
yapistirma = float(d[L - BINDIRME - 1])
print('karo %dx%d  ·  %d KB  ·  yapistirma katsayisi c = %.4f'
      % (L, H, os.path.getsize(CIKTI) // 1024, c))
print('sutun farki: ortanca %.2f  ·  %%95 dilim %.2f' % (ic, p95))
print('EK YERLERI : %.2f  %.2f   %s' % (ek1, ek2,
      'GORUNMEZ (siradan duvar dokusunun icinde)' if max(ek1, ek2) <= p95 else 'GORUNUR'))
print('yapistirma sinirı: %.2f' % yapistirma)

# ── yuva ölçüleri ────────────────────────────────────────────────────────
PANO_SOL, PANO_SAG = 450, 962
print('\nBIRIM  en:%d  boy:%d' % (L, H))
print('yuva   cx:%.4f  g:%.4f'
      % (((PANO_SOL + PANO_SAG) / 2 - XA) / L, (PANO_SAG - PANO_SOL) / L))

Image.fromarray(np.hstack([np.asarray(out)] * 3)).save('kaynak/doseme.jpg', quality=88)
