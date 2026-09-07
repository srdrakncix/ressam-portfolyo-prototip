# -*- coding: utf-8 -*-
"""Siteyi bastan sona uretir: uc sayfa + sabit varliklar + yayin dosyalari.

Tek komut: `python yayinla.py`

Bunu GitHub Actions da calistiriyor, ben de yerelde. Ikisinin ayni komutu
calistirmasi onemli: "bende calisiyordu" durumunu bastan siliyor.

site/ klasoru TAMAMEN URETILMIS ciktidir ve depoya girmez (.gitignore).
Depoda duran sey kaynaktir: sablonlar, build.py, icerik ve varlik/.
"""
import io
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
    # Ciktiyi SIFIRDAN uret: eski derlemelerden kalan olu dosyalar birikmesin.
    # (Eser gorsellerinin adi degistiginde eskiler sessizce kaliyordu.)
    # Windows klasorun kendisini kilitleyebiliyor; ICERIGI siliyoruz.
    if os.path.isdir(CIKTI):
        for ad in os.listdir(CIKTI):
            yol = os.path.join(CIKTI, ad)
            if os.path.isdir(yol):
                shutil.rmtree(yol, ignore_errors=True)
            else:
                try:
                    os.remove(yol)
                except OSError:
                    pass
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

    # 3) panel + secenekleri
    #    Seri ve durum listeleri content.py'den turetiliyor: panelde elle
    #    yazilirsa iki yer birbirinden kopar.
    import json as _json
    import content as _C
    panel_hedef = os.path.join(CIKTI, 'panel')
    os.makedirs(panel_hedef, exist_ok=True)
    from datetime import datetime, timezone
    damga = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')
    panel_kod = io.open(os.path.join(KOK, 'panel', 'index.html'),
                        encoding='utf-8').read().replace('__YAPIM__', damga)
    io.open(os.path.join(panel_hedef, 'index.html'), 'w',
            encoding='utf-8').write(panel_kod)
    io.open(os.path.join(panel_hedef, 'secenekler.json'), 'w', encoding='utf-8').write(
        _json.dumps({
            'seriler': [{'anahtar': x['key'], 'ad': x['title']} for x in _C.SERIES],
            'durumlar': [{'anahtar': k, 'ad': v} for k, v in _C.STATUS_TR.items()],
            'teknik': _C.MEDIUM_TR,
            'sunucu': getattr(_C, 'PANEL_SUNUCU', ''),
        }, ensure_ascii=False, indent=2))
    # Sifreli girisin kilidi. Panelden kurulunca depoya yaziliyor;
    # icinde GitHub anahtarinin SIFRELENMIS hali var, duz hali degil.
    kilit_kaynak = os.path.join(KOK, 'panel', 'kilit.json')
    if os.path.exists(kilit_kaynak):
        shutil.copy2(kilit_kaynak, os.path.join(panel_hedef, 'kilit.json'))
        print('panel/            index.html + secenekler.json + kilit.json')
    else:
        print('panel/            index.html + secenekler.json')

    # 4) yayin damgasi
    #    Panel "site guncellendi mi" sorusunu buradan cevapliyor: her
    #    derlemede degisen tek dosya. ETag'e bakmak da isliyordu ama onun
    #    degismesi Pages'in dosya zaman damgasina bagli - burada olcut acik.
    io.open(os.path.join(CIKTI, 'yayin.json'), 'w', encoding='utf-8').write(
        _json.dumps({'zaman': datetime.now(timezone.utc).isoformat(timespec='seconds'),
                     'surum': os.environ.get('GITHUB_SHA', 'yerel')[:12]}) + chr(10))
    print('yayin.json        ' + damga)

    # 5) yayindaki eserlerin parmak izi
    #    Panel "bu eser sitede mi, yoksa daha derlenmedi mi" sorusunu buradan
    #    cevapliyor. Deger, kaynak JSON'un GIT BLOB SHA'si: panel zaten ayni
    #    degeri contents API'sinden aliyor, yani karsilastirma tahminsiz.
    import hashlib
    izler = {}
    for ad in sorted(os.listdir(os.path.join(KOK, 'icerik', 'eserler'))):
        if not ad.endswith('.json'):
            continue
        ham = open(os.path.join(KOK, 'icerik', 'eserler', ad), 'rb').read()
        # Depo LF sakliyor; Windows'ta yerel dosya CRLF olabilir.
        # Depodaki baytlara gore hesapla, yoksa yerel iz tutmaz.
        ham = ham.replace(bytes([13, 10]), bytes([10]))
        h = hashlib.sha1()
        h.update(b'blob ' + str(len(ham)).encode() + bytes([0]) + ham)
        izler[ad[:-5]] = h.hexdigest()
    io.open(os.path.join(CIKTI, 'eserler.json'), 'w', encoding='utf-8').write(
        _json.dumps(izler, ensure_ascii=False, indent=1) + chr(10))
    print('eserler.json       %d eser parmak izi' % len(izler))

    # 6) favicon, robots, sitemap, 404
    print(calistir('site_ek.py'))

    toplam = sum(os.path.getsize(os.path.join(r, f))
                 for r, _, fs in os.walk(CIKTI) for f in fs)
    print(f'\nsite/              {toplam / 1048576:.2f} MB')


if __name__ == '__main__':
    main()
