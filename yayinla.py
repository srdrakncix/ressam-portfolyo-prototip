# -*- coding: utf-8 -*-
"""Siteyi bastan sona uretir: uc sayfa + sabit varliklar + yayin dosyalari.

Tek komut: `python yayinla.py`

Bunu GitHub Actions da calistiriyor, ben de yerelde. Ikisinin ayni komutu
calistirmasi onemli: "bende calisiyordu" durumunu bastan siliyor.

site/ klasoru TAMAMEN URETILMIS ciktidir ve depoya girmez (.gitignore).
Depoda duran sey kaynaktir: sablonlar, build.py, icerik ve varlik/.
"""
import io
import re
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

# Kok adres SECILEN tasarimi verir. Eskiden duz.html index.html olarak
# yaziliyordu, yani adresi acan herkes PARKTA duran surumu goruyordu;
# gelistirdigimiz sayfa mekan.html'de duruyordu ve kimse oraya ugramiyordu.
# Adreste sayfa adi gorunmesin: musterinin kafasi karismasin diye
# yayinlanan sayfa iki tane ve ikisi de "temiz" adres.
#   /         ana sayfa
#   /galeri/  sergi duvari
# duz.html (parktaki duz surum) ve salon.html (parktaki 3B salon) yayindan
# cikarildi; ikisine de hicbir yerden baglanti yoktu. Kaynaklari depoda.
# YAKINDA. Açıkken saglam.fr'de YALNIZCA "site yapım aşamasında" sayfası
# (yakinda.html) görünür: kök adres o olur, galeri yayından çıkar.
# Müşteri kararı (1 Ekim 2026): "site tamamen yok, onların göreceği şey
# inşa halinde grafiksel bir şey olsun."
# Anahtar artık icerik/site.json'da (yayin.acik): ressam panelden "Siteyi
# yayına aç" diyebiliyor. Buradaki değer yalnız yerel denemede zorlamak
# için: None = site.json ne diyorsa o; True/False = onu ez.
# Asıl site derlenmeye devam ediyor (derleme hatası gizlenmesin diye) ama
# yayına kopyalanmıyor. Panel (/panel/), görseller (/assets/) ve yayın
# damgası etkilenmiyor: panel çalışmaya devam ediyor.
YAKINDA = None

# NEREYE DERLENİYOR. Aynı depodan iki ayrı yayın çıkıyor:
#   site   saglam.fr (GitHub Pages, GitHub Actions derliyor). Ziyaretçinin
#          gördüğü site. PANEL YOK — saglam.fr/panel/ diye bir adres yok.
#   panel  panelfrsaglam.pages.dev (Cloudflare Pages derliyor). Yalnız
#          yönetim paneli + kapıcısı (functions/api). Görselleri ve yayın
#          damgasını saglam.fr'den okuyor (SITE_ADRESI).
#   yerel  bu bilgisayar: site + /panel/ birlikte (denemeler için).
# Hangisi olduğu ortamdan anlaşılıyor; YAYIN_HEDEF ile zorlanabilir.
HEDEF = (os.environ.get('YAYIN_HEDEF') or
         ('panel' if os.environ.get('CF_PAGES') else
          'site' if os.environ.get('GITHUB_ACTIONS') else 'yerel'))
SITE_ADRESI = os.environ.get('SITE_ADRESI', 'https://saglam.fr').rstrip('/')

SAYFALAR = [
    ('mekan.html', 'index.html'),
    ('sergi.html', os.path.join('galeri', 'index.html')),
]


def calistir(*args):
    r = subprocess.run([sys.executable] + list(args), cwd=KOK,
                       capture_output=True, text=True, encoding='utf-8', errors='replace')
    if r.returncode:
        sys.stderr.write(r.stdout + '\n' + r.stderr + '\n')
        raise SystemExit('HATA: ' + ' '.join(args))
    return (r.stdout or '').strip()


def main():
    import site_veri as V
    S = V.oku()           # bozuksa derleme burada, acik bir mesajla durur
    yakinda = (not S['acik']) if YAKINDA is None else YAKINDA
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

    if HEDEF == 'panel':
        panel_derle()
        return

    # 0) zemin: ressam panelden başka bir arka plan seçtiyse burada
    #    üretiliyor; build.py onu ZEMIN_JSON'dan okuyor. Seçim yoksa (hazır
    #    desen) depodaki varlik/zemin + zeminler.json olduğu gibi kalıyor.
    zemin_dizin, zemin = None, None
    os.environ.pop('ZEMIN_JSON', None)
    if S['zemin']['tur'] != 'hazir':
        import glob
        import json as _j
        import tempfile
        import zemin as _Z
        eg = {}
        for f in glob.glob(os.path.join(KOK, 'icerik', 'eserler', '*.json')):
            eg[os.path.basename(f)[:-5]] = _j.load(io.open(f, encoding='utf-8')).get('gorsel')
        zemin_dizin = tempfile.mkdtemp(prefix='zemin-')
        zj = _Z.panelden(S['zemin'], os.path.join(KOK, 'icerik', 'gorseller'), zemin_dizin, eg)
        if zj:
            os.environ['ZEMIN_JSON'] = zj
            zemin = _j.load(io.open(zj, encoding='utf-8'))

    # 1) sayfalar (build.py assets/ icine eser gorsellerini de yaziyor)
    for sablon, hedef in SAYFALAR:
        cikis = os.path.join('site', hedef)
        os.makedirs(os.path.dirname(os.path.join(KOK, cikis)), exist_ok=True)
        print(calistir('build.py', sablon, cikis, '--standalone'))
        # Alt dizindeki sayfanin goreli yollari bir ust dizine bakmali.
        # Sessiz kalirsa galeri sayfasi butun gorsellerini kaybeder ve bunu
        # yalnizca tarayicida gorursun -- derleme uyarmaz.
        derinlik = hedef.replace(chr(92), '/').count('/')
        if derinlik:
            ust = '../' * derinlik
            yol = os.path.join(KOK, cikis)
            s = io.open(yol, encoding='utf-8').read()
            once = s
            # Onunde gelebilecek BUTUN sinirlar. Once yalniz " ' ( vardi
            # ve srcset kirilmisti: virgulle ayrilmis adaylar bosluk ile
            # geliyor, yani "../assets/x-540.webp 540w, assets/x-810.webp"
            # gibi yarim duzeltilmis bir deger uretiliyordu. Olculdu --
            # ikinci ve ucuncu aday 404 verecekti.
            for ham in ('assets/', 'favicon.svg', 'apple-touch-icon.png'):
                for on in ('"', "'", '(', ', ', ',', ' '):
                    s = s.replace(on + ham, on + ust + ham)
                # Cift duzeltmeyi geri al: yukaridaki dongude bir deger
                # birden fazla sinira uyabiliyor.
                s = s.replace(ust + ust + ham, ust + ham)
            s = s.replace('href="./"', 'href="' + ust + '"')
            s = s.replace("location.href = './#'", "location.href = '" + ust + "#'")
            if s == once:
                raise SystemExit('HATA: %s icinde duzeltilecek goreli yol '
                                 'bulunamadi' % hedef)
            io.open(yol, 'w', encoding='utf-8').write(s)
            # build.py varliklari ciktinin YANINA yaziyor; yollar bir ust
            # dizine cevrildigi icin o kopya artik olu. 1.1 MB'lik ikiz.
            ikiz = os.path.join(os.path.dirname(yol), 'assets')
            if os.path.isdir(ikiz):
                shutil.rmtree(ikiz, ignore_errors=True)

    # 2) sabit varliklar: cerceve, duvar, zemin dokulari ve kagit
    #    Bunlar bir kez uretilip depoya alindi (duvar.py, kagit.py, _cerceve.py).
    #    Her derlemede yeniden uretmek gereksiz ve kaynak fotograflari 47 MB.
    kaynak_varlik = os.path.join(KOK, 'varlik')
    hedef_varlik = os.path.join(CIKTI, 'assets')
    n = 0
    # Iki klasor YAYINA GIRMIYOR. Olculdu: assets/cerceve/*.webp
    # (370 KB) ve assets/duvar/salon.webp (43 KB) iki sayfanin
    # hicbirinden referans almiyor -- cerceveler raflanan Fransiz
    # salonundan, duvar da artik uretilmeyen 3B salon sayfasindan kalma.
    # Kaynakta duruyorlar; yalnizca kopyalanmiyorlar.
    # 'hero' de eklendi: salon kurgusu artik ana sayfada kullanilmiyor
    # (musteri karari), kaynakta duruyor ama yayina kopyalanmiyor.
    # 'firca' de eklendi: menu paneli duz kreme gecti (musteri karari),
    # dokuz darbe + taban 361 KB idi ve artik hicbir sayfa referans
    # vermiyor. Kaynak depoda duruyor, yayinda yok.
    ATLA = {'cerceve', 'duvar', 'hero', 'firca'}
    for kok, dizinler, dosyalar in os.walk(kaynak_varlik):
        dizinler[:] = [d for d in dizinler if d not in ATLA]
        bagil = os.path.relpath(kok, kaynak_varlik)
        hedef_dizin = hedef_varlik if bagil == '.' else os.path.join(hedef_varlik, bagil)
        os.makedirs(hedef_dizin, exist_ok=True)
        for d in dosyalar:
            shutil.copy2(os.path.join(kok, d), os.path.join(hedef_dizin, d))
            n += 1
    print(f'varlik/            {n} dosya kopyalandi')
    if zemin:
        # Panelden seçilen zemin: içerik adlı dosya (önbellek eskiyi
        # göstermesin). Hazır desen de yerinde kalıyor; zarar yok.
        shutil.copy2(os.path.join(zemin_dizin, zemin['_dosya']),
                     os.path.join(hedef_varlik, 'zemin', zemin['_dosya']))
        print('zemin             assets/zemin/' + zemin['_dosya'])

    # 3) panel — yalnız yerelde, sitenin yanında. saglam.fr'de panel yok.
    import json as _json
    from datetime import datetime, timezone
    damga = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')
    if HEDEF == 'yerel':
        panel_yaz(os.path.join(CIKTI, 'panel'), site='')

    # 4) yayin damgasi
    #    Panel "site guncellendi mi" sorusunu buradan cevapliyor: her
    #    derlemede degisen tek dosya. ETag'e bakmak da isliyordu ama onun
    #    degismesi Pages'in dosya zaman damgasina bagli - burada olcut acik.
    io.open(os.path.join(CIKTI, 'yayin.json'), 'w', encoding='utf-8').write(
        _json.dumps({'zaman': datetime.now(timezone.utc).isoformat(timespec='seconds'),
                     'surum': os.environ.get('GITHUB_SHA', 'yerel')[:12],
                     # CI denetimi hangi sayfaları arayacağını buradan okuyor.
                     'yakinda': yakinda,
                     'hedef': HEDEF,
                     # Panel "sitede duran sürüm hangisi" sorusunu buradan
                     # cevaplıyor: icerik/ altındaki her dosyanın GIT BLOB
                     # SHA'sı. Panel aynı değeri depo ağacından alıyor, yani
                     # "yayında / yayınlanıyor" ayrımı tahminsiz.
                     'izler': icerik_izleri()}) + chr(10))
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

    # 5b) YAKINDA: kök adres "yapım aşamasında" sayfası, galeri yayından çıkar.
    #     site_ek.py'den ÖNCE: site haritası yalnızca yayında kalan sayfaları
    #     listeliyor.
    if yakinda:
        # Asil site kapaliyken ressam panelden yaptigi degisikligi
        # gorebilsin: ayni sayfalar /onizleme/ altina da yaziliyor.
        # Hicbir yerden baglanti yok, arama motorlarina kapali (noindex +
        # robots.txt). Kok sayfa yakinda.html'e donmeden ONCE kopyalaniyor.
        onizleme_yaz()
        io.open(os.path.join(CIKTI, 'index.html'), 'w', encoding='utf-8').write(
            yakinda_sayfasi(S, zemin))
        shutil.rmtree(os.path.join(CIKTI, 'galeri'), ignore_errors=True)
        print('YAKINDA           kök = yakinda.html, galeri yayında değil')

    # 6) favicon, robots, sitemap, 404
    print(calistir('site_ek.py'))

    toplam = sum(os.path.getsize(os.path.join(r, f))
                 for r, _, fs in os.walk(CIKTI) for f in fs)
    print(f'\nsite/              {toplam / 1048576:.2f} MB')


def _html(s):
    return (str(s).replace('&', '&amp;').replace('<', '&lt;')
            .replace('>', '&gt;').replace('"', '&quot;'))


def yakinda_sayfasi(S, zemin):
    """yakinda.html + panelden gelenler: ad, üç yazı (üç dilde), zemin."""
    import json as _j
    import ceviri as _T
    import site_veri as V
    UI = V.arayuz(S, _T.UI)
    s = io.open(os.path.join(KOK, 'yakinda.html'), encoding='utf-8').read()
    s = s.replace('__AD__', _html(S['sanatci']['ad']))
    for alan in ('teknik', 'mesaj', 'alt'):
        # HTML'deki ilk hâl Fransızca (alan adı .fr); betik dili değiştiriyor.
        s = s.replace('__YK_%s__' % alan.upper(), _html(UI['fr']['yakinda_' + alan]))
        for d in V.DILLER:
            js = _j.dumps(UI[d]['yakinda_' + alan], ensure_ascii=False).replace('</', '<\\/')
            s = s.replace('__YK_%s_%s__' % (alan, d), js)
    if zemin:
        s = s.replace('assets/zemin/oruntu.webp', 'assets/zemin/' + zemin['_dosya'])
        s = re.sub(r'--zemin-kati:\s*#[0-9a-fA-F]{6}', '--zemin-kati: ' + zemin['_kati'], s)
    kalan = re.findall(r'__[A-Z][A-Za-z_]*__', s)
    if kalan:
        raise SystemExit('HATA: yakinda.html icinde doldurulmamis belirtec: ' + ', '.join(sorted(set(kalan))))
    return s


def panel_yaz(hedef_dizin, site):
    """Yönetim panelini hedef_dizin'e yazar: index.html + secenekler.json.

    site: panelin görselleri, yayın damgasını ve önizlemeyi okuduğu sitenin
    adresi. Boşsa panel sitenin içinde (/panel/) duruyor, göreli okur."""
    import json as _json
    from datetime import datetime, timezone
    import content as _C
    import ceviri as _T
    import site_veri as V
    os.makedirs(hedef_dizin, exist_ok=True)
    damga = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')
    io.open(os.path.join(hedef_dizin, 'index.html'), 'w', encoding='utf-8').write(
        io.open(os.path.join(KOK, 'panel', 'index.html'), encoding='utf-8').read()
        .replace('__YAPIM__', damga))
    io.open(os.path.join(hedef_dizin, 'secenekler.json'), 'w', encoding='utf-8').write(
        _json.dumps({
            'site': site,
            'durumlar': [{'anahtar': k, 'ad': v} for k, v in _C.STATUS_TR.items()],
            # Panelin "Menü ve yazılar" bölümü: hangi alanlar, hangi sırayla,
            # boş bırakılırsa ne yazacağı. Tek kaynak site_veri.YAZILAR.
            'yazilar': list(V.YAZILAR),
            'yazi_varsayilan': {d: {k: _T.UI[d][k] for k in V.YAZILAR}
                                for d in V.DILLER},
        }, ensure_ascii=False, indent=2))
    # Sifreli girisin kilidi (kapicisiz yol). Yalniz yerel denemede var.
    kilit = os.path.join(KOK, 'panel', 'kilit.json')
    if os.path.exists(kilit):
        shutil.copy2(kilit, os.path.join(hedef_dizin, 'kilit.json'))
    print('panel             ' + os.path.relpath(hedef_dizin, KOK) +
          (' (site: ' + site + ')' if site else ''))


def panel_derle():
    """Cloudflare: yalnız panel. Kök adres panelin kendisi; kapıcı
    functions/api'de (Cloudflare onu depodan kendisi alıyor). Arama
    motorlarına tamamen kapalı."""
    import json as _json
    import site_veri as V
    V.oku()               # bozuk içerik panel derlemesini de durdursun
    panel_yaz(CIKTI, site=SITE_ADRESI)
    io.open(os.path.join(CIKTI, 'robots.txt'), 'w', encoding='utf-8').write(
        'User-agent: *\nDisallow: /\n')
    io.open(os.path.join(CIKTI, 'yayin.json'), 'w', encoding='utf-8').write(
        _json.dumps({'hedef': 'panel', 'site': SITE_ADRESI}) + chr(10))


ONIZLEME = 'onizleme'
GORELI = ('assets/', 'favicon.svg', 'apple-touch-icon.png')


def onizleme_yaz():
    """Derlenmis ana sayfa ve galeriyi site/onizleme/ altina kopyalar.

    Sayfalar bir dizin derine iniyor: varlik yollari bir ust dizine daha
    bakmali. Ana sayfanin yollari 'assets/..' (her sinirla: " ' ( , bosluk
    -- srcset dersi), galerininki zaten '../assets/..'. Galeriden ana
    sayfaya donus ('../') onizleme icinde kaliyor, dokunulmuyor."""
    gizle = '<meta name="robots" content="noindex, nofollow">'
    hedef = os.path.join(CIKTI, ONIZLEME)
    os.makedirs(os.path.join(hedef, 'galeri'), exist_ok=True)

    s = io.open(os.path.join(CIKTI, 'index.html'), encoding='utf-8').read()
    for ham in GORELI:
        for on in ('"', "'", '(', ', ', ',', ' '):
            s = s.replace(on + ham, on + '../' + ham)
        s = s.replace('../../' + ham, '../' + ham)
    io.open(os.path.join(hedef, 'index.html'), 'w', encoding='utf-8').write(
        s.replace('<meta charset="utf-8">', '<meta charset="utf-8">\n' + gizle, 1))

    s = io.open(os.path.join(CIKTI, 'galeri', 'index.html'), encoding='utf-8').read()
    for ham in GORELI:
        s = s.replace('../' + ham, '../../' + ham)
    io.open(os.path.join(hedef, 'galeri', 'index.html'), 'w', encoding='utf-8').write(
        s.replace('<meta charset="utf-8">', '<meta charset="utf-8">\n' + gizle, 1))
    print('onizleme/         ana sayfa + galeri (noindex)')


def git_blob_sha(yol):
    """Dosyanın git blob SHA'sı -- depodaki baytlara göre (LF)."""
    import hashlib
    ham = open(yol, 'rb').read()
    # Depo LF sakliyor; Windows'ta yerel dosya CRLF olabilir. Yalniz
    # metin dosyalarinda: gorselin baytlarina dokunulmaz.
    if yol.endswith(('.json', '.txt', '.md')):
        ham = ham.replace(bytes([13, 10]), bytes([10]))
    h = hashlib.sha1()
    h.update(b'blob ' + str(len(ham)).encode() + bytes([0]) + ham)
    return h.hexdigest()


def icerik_izleri():
    izler = {}
    for kok, _, dosyalar in os.walk(os.path.join(KOK, 'icerik')):
        for d in dosyalar:
            yol = os.path.join(kok, d)
            izler[os.path.relpath(yol, KOK).replace(chr(92), '/')] = git_blob_sha(yol)
    return dict(sorted(izler.items()))


if __name__ == '__main__':
    main()
