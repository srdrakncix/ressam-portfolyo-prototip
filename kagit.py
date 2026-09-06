# -*- coding: utf-8 -*-
"""Döşenebilir kâğıt dokusu.

Düz CSS gradyanı kâğıda benzemiyor; kâğıdı kâğıt yapan şey lif dokusu ve
düzensiz tokluk. Gürültü FREKANS UZAYINDA üretiliyor: ters FFT'nin çıktısı
doğası gereği periyodiktir, yani doku kusursuz döşenir. Kenar yamama yok.
"""
import numpy as np
from PIL import Image

N = 256
rng = np.random.default_rng(11)
fy = np.fft.fftfreq(N)[:, None]
fx = np.fft.fftfreq(N)[None, :]


def alan(sx, sy, tohum):
    """Verilen bant genişliğinde periyodik gürültü alanı."""
    g = np.random.default_rng(tohum).normal(size=(N, N))
    F = np.fft.fft2(g) * np.exp(-(fx ** 2) / (2 * sx ** 2) - (fy ** 2) / (2 * sy ** 2))
    a = np.real(np.fft.ifft2(F))
    return a / (a.std() + 1e-9)


lif = alan(0.22, 0.020, 3)      # uzun yatay lifler
lif2 = alan(0.020, 0.22, 5)     # dikey lifler (daha zayıf)
grain = alan(0.30, 0.30, 7)     # ince tanecik
tokluk = alan(0.012, 0.012, 9)  # geniş dalgalı tokluk farkı

L = 1.0 + 0.016 * lif + 0.009 * lif2 + 0.010 * grain + 0.014 * tokluk
L = np.clip(L, 0.90, 1.08)

taban = np.array([252, 250, 246], dtype=np.float32)     # sıcak kâğıt beyazı
img = np.clip(L[..., None] * taban, 0, 255).astype(np.uint8)
Image.fromarray(img, 'RGB').save('site/assets/kagit.webp', 'WEBP',
                                 quality=94, method=6)

k = img.mean(2)
print('kagit.webp %dx%d  ·  %d KB' % (N, N, __import__('os').path.getsize('site/assets/kagit.webp') // 1024))
print('parlaklik %.1f–%.1f (ort %.1f)' % (k.min(), k.max(), k.mean()))
print('dosenme kontrolu — sag/sol kenar farki : %.3f' % np.abs(k[:, -1] - k[:, 0]).mean())
print('               ust/alt kenar farki     : %.3f' % np.abs(k[-1, :] - k[0, :]).mean())
print('               karo ici ortalama fark  : %.3f' % np.abs(np.diff(k, axis=1)).mean())
