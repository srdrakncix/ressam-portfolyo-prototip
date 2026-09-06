# -*- coding: utf-8 -*-
"""Siteyi bastan sona uretir: uc sayfa + sabit varliklar + yayin dosyalari.

Tek komut: `python yayinla.py`

Bunu GitHub Actions da calistiriyor, ben de yerelde. Ikisinin ayni komutu
calistirmasi onemli: "bende calisiyordu" durumunu bastan siliyor.

site/ klasoru TAMAMEN URETILMIS ciktidir ve depoya girmez (.gitignore).
Depoda duran sey kaynaktir: sablonlar, build.py, icerik ve varlik/.
"""
import os
import shutil
import subprocess
import sys

# Windows konsolu cp1254; alt sureclerin ciktisindaki karakterler patlatmasin.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

KOK = os.path.dirname(os.path.abspath(__file__))
CIKTI = os.path.join(KOK, 'site')

SAYFALAR = [
    ('duz.html',   'index.html'),
    ('mekan.html', 'mekan.html'),
    ('sergi.html', 'sergi.html'),
]


def calistir(*args):
    r = subprocess.run([sys.executable] + list(args), cwd=KOK,
                       capture_output=True, text=True, encoding='utf-8', errors='replace')
    if r.returncode:
        sys.stderr.write(r.stdout + '\n' + r.stderr + '\n')
        raise SystemExit('HATA: ' + ' '.join(args))
    return (r.stdout or '').strip()


def main():
    os.makedirs(CIKTI, exist_ok=True)

    # 1) sayfalar (build.py assets/ icine eser gorsellerini de yaziyor)
    for sablon, hedef in SAYFALAR:
        print(calistir('build.py', sablon, os.path.join('site', hedef), '--standalone'))

    # 2) sabit varliklar: cerceve, duvar, zemin dokulari ve kagit
    #    Bunlar bir kez uretilip depoya alindi (duvar.py, kagit.py, _cerceve.py).
    #    Her derlemede yeniden uretmek gereksiz ve kaynak fotograflari 47 MB.
    kaynak_varlik = os.path.join(KOK, 'varlik')
    hedef_varlik = os.path.join(CIKTI, 'assets')
    n = 0
    for kok, _, dosyalar in os.walk(kaynak_varlik):
        bagil = os.path.relpath(kok, kaynak_varlik)
        hedef_dizin = hedef_varlik if bagil == '.' else os.path.join(hedef_varlik, bagil)
        os.makedirs(hedef_dizin, exist_ok=True)
        for d in dosyalar:
            shutil.copy2(os.path.join(kok, d), os.path.join(hedef_dizin, d))
            n += 1
    print(f'varlik/            {n} dosya kopyalandi')

    # 3) favicon, robots, sitemap, 404
    print(calistir('site_ek.py'))

    toplam = sum(os.path.getsize(os.path.join(r, f))
                 for r, _, fs in os.walk(CIKTI) for f in fs)
    print(f'\nsite/              {toplam / 1048576:.2f} MB')


if __name__ == '__main__':
    main()
