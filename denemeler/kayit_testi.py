# -*- coding: utf-8 -*-
"""Panelde Kaydet / Kayıtlar: gerçek tarayıcı (Edge) + sahte GitHub.

    python denemeler/kayit_testi.py

Gerçek GitHub'a dokunmaz. Kayıtların siteyi (main) değiştirmediğini, adıyla
saklandığını, başka oturumda listelendiğini, açılınca o hâlin geldiğini ve
yayınlanabildiğini, silinebildiğini ölçer.
"""
import functools, http.server, io, json, os, re, socketserver, subprocess, sys, threading, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
BURASI = os.path.dirname(os.path.abspath(__file__))
KOK = os.path.dirname(BURASI)
sys.path.insert(0, BURASI)
from sahte_github import Depo  # noqa: E402
from playwright.sync_api import sync_playwright, expect  # noqa: E402

SITE = os.path.join(KOK, 'site')
JETON = 'github_pat_TEST_KAYIT'
expect.set_options(timeout=20000)
sonuc = []


def kontrol(ad, kosul, ayrinti=''):
    sonuc.append(bool(kosul))
    print(('GECTI ' if kosul else 'KALDI ') + ad + (('  -> ' + str(ayrinti)[:200]) if ayrinti != '' else ''), flush=True)


r = subprocess.run([sys.executable, 'yayinla.py'], cwd=KOK, capture_output=True, text=True, encoding='utf-8',
                   errors='replace', env=dict(os.environ, YAYIN_HEDEF='yerel', PYTHONIOENCODING='utf-8'))
kontrol('yerel derleme', r.returncode == 0, r.stderr[-300:])
k_ = os.path.join(SITE, 'panel', 'kilit.json')
if os.path.exists(k_):
    os.remove(k_)

ilk = {}
for kok, _, fs in os.walk(os.path.join(KOK, 'icerik')):
    for f in fs:
        p = os.path.join(kok, f)
        b = open(p, 'rb').read()
        if f.endswith('.json'):
            b = b.replace(b'\r\n', b'\n')
        ilk[os.path.relpath(p, KOK).replace(os.sep, '/')] = b
depo = Depo(ilk, JETON)
y = json.load(io.open(os.path.join(SITE, 'yayin.json'), encoding='utf-8'))
y['izler'] = depo.izler()
io.open(os.path.join(SITE, 'yayin.json'), 'w', encoding='utf-8').write(json.dumps(y))
ana_bas = depo.bas


class Sessiz(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


srv = socketserver.ThreadingTCPServer(('127.0.0.1', 0), functools.partial(Sessiz, directory=SITE))
threading.Thread(target=srv.serve_forever, daemon=True).start()
ADRES = 'http://127.0.0.1:%d/panel/' % srv.server_address[1]


def eser(dosyalar, slug):
    return json.loads(dosyalar['icerik/eserler/%s.json' % slug])


with sync_playwright() as pw:
    tr = pw.chromium.launch(channel='msedge')

    def oturum(vp=None):
        ctx = tr.new_context(viewport=vp or {'width': 1360, 'height': 900}, locale='tr-TR')
        ctx.route('https://api.github.com/**', depo.playwright_yolu)
        ctx.add_init_script("localStorage.setItem('saglam-panel-anahtar', '%s')" % JETON)
        pg = ctx.new_page()
        hs = []
        pg.on('pageerror', lambda e: hs.append(str(e)))
        pg.goto(ADRES)
        expect(pg.locator('.eser-kart')).to_have_count(8)
        return ctx, pg, hs

    ctx, pg, hatalar = oturum()
    cubuk = pg.locator('.cubuk')
    kontrol('"Site güncel" iken de Kaydet var', cubuk.get_by_role('button', name='Kaydet').is_visible())

    def baslik_yaz(i, ad):
        pg.locator('.eser-kart').nth(i).click()
        pg.locator('#cekmece .cekmece-ic input[type=text]').first.fill(ad)
        pg.locator('#cekmece').get_by_role('button', name='Bitti').click()

    def kaydet(ad=None):
        pg.locator('.cubuk').get_by_role('button', name='Kaydet').click()
        expect(pg.locator('#kayit-pencere')).to_be_visible()
        varsayilan = pg.input_value('#kayit-ad')
        if ad:
            pg.fill('#kayit-ad', ad)
        pg.click('#kayit-tamam')
        expect(pg.locator('#bildirim')).to_contain_text('kaydedildi')
        return varsayilan

    baslik_yaz(0, 'Birinci Hâl')
    expect(cubuk).to_contain_text('1 değişiklik')
    kontrol('Kaydet, Yayınla’nın yanında', cubuk.get_by_role('button', name='Kaydet').is_visible() and
            cubuk.get_by_role('button', name='Yayınla', exact=True).is_visible())
    v1 = kaydet()
    kontrol('ilk kaydın adı otomatik "Kayıt 1"', v1 == 'Kayıt 1', v1)
    kontrol('kaydetmek siteyi değiştirmedi', depo.bas == ana_bas and depo.patch_sayisi == 0)
    expect(cubuk).to_contain_text('1 değişiklik')
    kontrol('kayıttan sonra taslak yerinde, Yayınla bekliyor', True)

    baslik_yaz(0, 'İkinci Hâl')
    pg.click('#sekmeler >> text=Sanatçı')
    pg.locator('section.kart', has_text='Biyografi').locator('textarea').fill('Sergi öncesi biyografi.')
    pg.keyboard.press('Control+s')
    expect(pg.locator('#kayit-pencere')).to_be_visible()
    kontrol('Ctrl+S kaydetme penceresini açıyor', pg.input_value('#kayit-ad') == 'Kayıt 2', pg.input_value('#kayit-ad'))
    pg.fill('#kayit-ad', 'Sergi öncesi')
    pg.click('#kayit-tamam')
    pg.wait_for_timeout(1500)
    if pg.locator('#onay').is_visible():
        print('   ONAY PENCERESI:', pg.inner_text('#onay'))
    expect(pg.locator('#bildirim')).to_contain_text('“Sergi öncesi” kaydedildi')
    kontrol('iki kayıt dalı', len(depo.dallar) == 2, list(depo.dallar))
    k1 = [h for d, h in depo.dallar.items()]
    icerikler = sorted(eser(depo.dosyalar(h), 'eser-1')['baslik'] for h in k1)
    kontrol('kayıtlar kendi hâlini taşıyor', icerikler == ['Birinci Hâl', 'İkinci Hâl'], icerikler)
    kontrol('site hâlâ değişmedi', depo.bas == ana_bas)
    ctx.close()

    # başka bir cihaz/oturum: kayıtlar depodan gelir
    ctx, pg, h2 = oturum()
    hatalar += h2
    pg.click('#sekmeler >> text=Kayıtlar')
    satirlar = pg.locator('.kayitlar li')
    expect(satirlar).to_have_count(2)
    adlar = [satirlar.nth(i).locator('b').inner_text() for i in range(2)]
    kontrol('başka oturumda kayıtlar listede, yeniden eskiye', adlar == ['Sergi öncesi', 'Kayıt 1'], adlar)
    pg.screenshot(path=os.path.join(BURASI, 'kayitlar.png'))

    # Kayıt 1'i aç → taslak o hâl; yayınla
    satirlar.nth(1).get_by_role('button', name='Aç').click()
    expect(pg.locator('#bildirim')).to_contain_text('açıldı')
    T = pg.evaluate('T')
    kontrol('kayıt açıldı: eser adı', T['eser']['eser-1']['baslik'] == 'Birinci Hâl', T['eser']['eser-1']['baslik'])
    kontrol('kayıt açıldı: biyografi o günkü gibi boş', not T['site']['biyografi']['tr'])
    n = depo.patch_sayisi
    pg.get_by_role('button', name='Yayınla', exact=True).click()
    t0 = time.time()
    while depo.patch_sayisi == n and time.time() - t0 < 30:
        pg.wait_for_timeout(200)
    kontrol('açılan kayıt yayınlandı', eser(depo.dosyalar(), 'eser-1')['baslik'] == 'Birinci Hâl')
    kontrol('kayıtlar yayından sonra da duruyor', len(depo.dallar) == 2)

    # sil
    pg.click('#sekmeler >> text=Kayıtlar')
    expect(satirlar).to_have_count(2)
    satirlar.nth(0).get_by_role('button', name='Sil').click()
    pg.click('#onay-evet')
    expect(satirlar).to_have_count(1)
    kontrol('kayıt silindi', len(depo.dallar) == 1 and satirlar.nth(0).locator('b').inner_text() == 'Kayıt 1')
    v3 = kaydet()
    kontrol('sıradaki ad "Kayıt 2" (en büyük numara + 1)', v3 == 'Kayıt 2', v3)
    ctx.close()

    # telefon: alttaki çubuğa iki düğme sığıyor
    ctx, pg, h3 = oturum({'width': 390, 'height': 844})
    hatalar += h3
    baslik_yaz(1, 'Telefon')
    sw = pg.evaluate('document.documentElement.scrollWidth')
    b1 = pg.locator('.cubuk').get_by_role('button', name='Kaydet').bounding_box()
    b2 = pg.locator('.cubuk').get_by_role('button', name='Yayınla', exact=True).bounding_box()
    kontrol('telefonda taşma yok, iki düğme ekranda', sw <= 390 and b1 and b2 and b2['x'] + b2['width'] <= 390,
            (sw, b1 and round(b1['x']), b2 and round(b2['x'] + b2['width'])))
    pg.screenshot(path=os.path.join(BURASI, 'kayit-mobil.png'))
    ctx.close()
    kontrol('JS hatası yok', not hatalar, hatalar[:3])
    tr.close()
srv.shutdown()
print('\n%d/%d gecti' % (sum(sonuc), len(sonuc)))
sys.exit(0 if all(sonuc) else 1)
