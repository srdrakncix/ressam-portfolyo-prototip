# -*- coding: utf-8 -*-
"""Sayfa zemini: TEK bir tablodan dikilmiş, kendini tekrar eden örüntü.

Müşteri kararı: "son indirdiğim fotoğraf yeni arka renk temamız olacak.
Dikine bi foto ama sen ayarlarını yaparsın örüntü oluşturacak şekilde
eklemeler yaparsın."

Kaynak (zemin-oruntu.jpg) 298x1304 px'lik DİKEY bir şerit: üst üçte biri
turkuaz, altı mercan-pembe. İki sonucu var:

1. Tek başına zemin olamaz. `background-size: cover` ile 1920 px'lik bir
   ekrana gerdirilseydi 6.4 kat büyütülmesi gerekiyordu; boya da o oranda
   bulanıklaşıp plastikleşiyordu. Eskiden kaynak 2600 px'lik bir tuvaldı,
   bu yüzden sorun görünmüyordu.
2. Şeridin kendi kurgusu var (üstte gök, altta sıcak boya). Bu kurgu
   korunmalı, kırpılıp atılmamalı.

Çözüm: şerit EKRAN YÜKSEKLİĞİNE göre ölçekleniyor (%135, üstten hizalı)
ve YANA doğru tekrar ediyor -- boyalı bir paravan gibi. Böylece ciddi bir
büyütme yok, sayfanın dikey renk geçişi fotoğrafın kendi geçişi oluyor
(üstte turkuaz, altta mercan) ve yatay tekrar da örüntüyü kuruyor.
Ölçeğin neden %100 değil: bkz. kabuk.css .bg -- üç oran karşılaştırıldı.

Yan yana tekrar ederken ek yerinin görünmemesi için şerit AYNALANIYOR:
  karo = S + ters(S)[1:-1]
Uç sütunlar ikilenmiyor; bu yüzden hem karonun içindeki ek hem de iki karo
arasındaki ek gerçek komşu sütunlara denk geliyor, yani matematiksel
olarak sürekli. Ölçüm bunu her derlemede doğruluyor (dikiş raporu).

Kapılar (geçmeyen derleme çıkmıyor):
  - filigran: kaynağın alt kenarında soluk bir kredi yazısı var, kırpılıyor
    ve kırpıldığı doğrulanıyor.
  - dikiş: ek yerindeki sütun farkı, karonun içindeki ortalama komşu
    farkını AŞMAMALI.
  - okunurluk: perdeyle birleşmiş zemin beyaz kâğıda karşı en az 2:1
    (kâğıdın kenarı her yerde görünsün).
  - kimlik: doygunluk medyanı en az 0.25 -- yıkama fotoğrafın rengini
    öldürmemeli, yoksa "renk teması" diye bir şey kalmıyor.

Kullanım:  python zemin.py
Çıktı:     varlik/zemin/oruntu.webp  +  zeminler.json
"""
import colorsys
import io
import json
import os
import re
import statistics

from PIL import Image

KOK = os.path.dirname(os.path.abspath(__file__))
KAYNAK = os.path.join(KOK, 'zemin-oruntu.jpg')
CIKTI = os.path.join(KOK, 'varlik', 'zemin')
KABUK = os.path.join(KOK, 'kabuk.css')

FILIGRAN = 22          # alt kenardaki kredi yazısı bu kadar kırpılıyor
Q = 74                 # webp kalitesi

# Yıkama. Fotoğraf olduğu gibi bırakıldığında doygunluk medyanı 0.36 ile
# neon sınırındaydı ve beyaz kâğıdın kenarı en parlak yerlerde 2.53:1'e
# düşüyordu. Bu iki sayı ölçülerek seçildi: renk hâlâ turkuaz-mercan ama
# içeriğin arkasına çekiliyor.
DOY = 0.86             # doygunluk çarpanı
AYD = 0.72             # 0.46 üstündeki aydınlığın sıkıştırma oranı
AYD_ESIK = 0.46

# CSS'teki perde (.bg::after). Buradaki sayı ile oradaki BİR olmak zorunda:
# okunurluk ölçümü perdeyle birlikte yapılıyor.
PERDE_A, PERDE_C = 0.18, (20, 18, 22)

# Sayfa başına örüntünün yatay fazı. Tek zemin var (tema tek), ama sayfa
# değişince kabuk iki katmanı çapraz geçiriyor; faz farkı o geçişin
# görünür bir karşılığı olsun diye duruyor. Yüzde: tekrar eden zeminde
# karoyu kaydırır, ölçü ekran genişliğinden bağımsız kalır.
SAYFALAR = ['acilis', 'galeri', 'son', 'seri', 'atolye', 'biyografi',
            'sergiler', 'koleksiyon', 'yayinlar', 'basin', 'iletisim']


# ── ölçü yardımcıları ───────────────────────────────────────────────────

def _lin(c):
    c /= 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def parlaklik(r, g, b):
    return 0.2126 * _lin(r) + 0.7152 * _lin(g) + 0.0722 * _lin(b)


def kontrast(a, b):
    return (max(a, b) + 0.05) / (min(a, b) + 0.05)


def perdele(t):
    """CSS'teki .bg::after ne yapıyorsa onu yapar: koyu perde bindirir."""
    return tuple(int(round((1 - PERDE_A) * c + PERDE_A * v))
                 for c, v in zip(t, PERDE_C))


# ── örüntü ──────────────────────────────────────────────────────────────

def yika(im):
    """Doygunluğu kısar, aydınlıkları bastırır. Boyanın dokusuna
    dokunmuyor -- yalnız renk ve değer taşınıyor."""
    o = im.copy()
    p = o.load()
    en, boy = o.size
    for y in range(boy):
        for x in range(en):
            r, g, b = p[x, y]
            h, l, s = colorsys.rgb_to_hls(r / 255.0, g / 255.0, b / 255.0)
            if l > AYD_ESIK:
                l = AYD_ESIK + (l - AYD_ESIK) * AYD
            rr, gg, bb = colorsys.hls_to_rgb(h, l, s * DOY)
            p[x, y] = (int(rr * 255 + 0.5), int(gg * 255 + 0.5),
                       int(bb * 255 + 0.5))
    return o


def karola(S):
    """S + aynası. Uç sütunlar İKİLENMİYOR (bkz. modül başlığı)."""
    en, boy = S.size
    ayna = S.transpose(Image.FLIP_LEFT_RIGHT).crop((1, 0, en - 1, boy))
    K = Image.new('RGB', (en + ayna.width, boy))
    K.paste(S, (0, 0))
    K.paste(ayna, (en, 0))
    return K


def sutun_ort(im, x):
    p = im.load()
    n = im.height
    return [sum(p[x, y][k] for y in range(n)) / float(n) for k in range(3)]


def dikis_raporu(K):
    """Ek yerlerindeki sütun farkı, karo içindeki komşu farkına göre.

    Aynalama sürekliliği matematikten geliyor ama 'geliyor' demek yeterli
    değil: uç sütunu kırpmayı bir kez unutursam ek yerinde iki özdeş sütun
    kalır ve orada düz bir çizgi oluşur. Sayı o hatayı yakalar."""
    en = K.width
    def fark(a, b):
        pa, pb = sutun_ort(K, a), sutun_ort(K, b)
        return max(abs(u - v) for u, v in zip(pa, pb))
    komsu = statistics.median([fark(x, x + 1) for x in range(0, en - 1, 7)])
    ic = fark(en // 2 - 1, en // 2)          # karonun içindeki ek
    sar = fark(en - 1, 0)                    # iki karo arasındaki ek
    print('dikis           komsu medyan %.2f | ic ek %.2f | sarma ek %.2f'
          % (komsu, ic, sar))
    if ic > komsu * 3 + 1 or sar > komsu * 3 + 1:
        raise SystemExit('HATA: ek yeri komsu sutun farkindan cok sapiyor '
                         '-- ornuntu ek verir.')
    return komsu, ic, sar


def okunurluk_raporu(K):
    """Perdeyle birleşmiş zemin, beyaz kâğıda karşı ne kadar ayrışıyor."""
    k = K.resize((80, 344), Image.LANCZOS)
    ys, ss = [], []
    for renk in k.convert('RGB').getdata():
        c = perdele(renk)
        ys.append(parlaklik(*c))
        ss.append(colorsys.rgb_to_hls(*[v / 255.0 for v in c])[2])
    ys.sort()
    n = len(ys)
    p99, med = ys[int(n * 0.99)], ys[n // 2]
    kagit = parlaklik(255, 255, 255)
    doy = statistics.median(ss)
    print('okunurluk       kagit/zemin  en parlak %.2f:1  medyan %.2f:1'
          % (kontrast(kagit, p99), kontrast(kagit, med)))
    print('kimlik          doygunluk medyan %.2f' % doy)
    if kontrast(kagit, p99) < 2.0:
        raise SystemExit('HATA: en parlak zeminde kagidin kenari kayboluyor '
                         '(%.2f:1 < 2.0).' % kontrast(kagit, p99))
    if doy < 0.25:
        raise SystemExit('HATA: yikama rengi oldurdu (doygunluk %.2f) -- '
                         'tema kalmadi.' % doy)


def kati_renk(K):
    """Görsel yüklenene kadar görünen düz renk: örüntünün turkuaz ucu,
    koyultulmuş. Elle yazılsaydı fotoğraf değişince yanlışa düşerdi."""
    ust = K.crop((0, 0, K.width, int(K.height * 0.22))).resize((16, 16),
                                                               Image.LANCZOS)
    n = 0
    rs = gs = bs = 0
    for r, g, b in ust.getdata():
        rs += r; gs += g; bs += b; n += 1
    h, l, s = colorsys.rgb_to_hls(rs / n / 255.0, gs / n / 255.0, bs / n / 255.0)
    r, g, b = colorsys.hls_to_rgb(h, 0.13, min(s, 0.38))
    return '#%02x%02x%02x' % (int(r * 255 + 0.5), int(g * 255 + 0.5),
                              int(b * 255 + 0.5))


def kati_kapisi(hex_renk):
    """kabuk.css'teki --zemin-kati bu sayıyla aynı mı.

    Renk iki yerde yaşıyor: burada ölçülüyor, orada uygulanıyor. Bu
    projede aynı hata üç kez oldu (satır aydınlığı, #lang opaklığı,
    --tasma-oran): ölçüm bir şeyi doğrularken çalışan kod başka bir sayı
    kullanıyordu. Kapı o ayrışmayı derlemede yakalıyor."""
    s = io.open(KABUK, encoding='utf-8').read()
    m = re.search(r'--zemin-kati:\s*(#[0-9a-fA-F]{6})', s)
    if not m:
        raise SystemExit('HATA: kabuk.css icinde --zemin-kati yok. Ekle:\n'
                         '  :root { --zemin-kati: %s; }' % hex_renk)
    if m.group(1).lower() != hex_renk:
        raise SystemExit('HATA: kabuk.css --zemin-kati %s, olculen %s.\n'
                         '  kabuk.css icinde --zemin-kati degerini %s yap.'
                         % (m.group(1), hex_renk, hex_renk))
    print('kati renk       %s  (kabuk.css ile ayni)' % hex_renk)


# Hamburger çubukları zemin görselinden kesiliyor (kabuk.js paintBurger).
# Ölçü kabuk.css'ten: #menubtn 62 px, yatay dolgu 12 px -> çubuk 38 px;
# yükseklik 5 px; görsel `background-size: 420px auto`.
CUBUK_EN, CUBUK_BOY, CUBUK_GORSEL = 38, 5, 420
DISK_A = 0.92          # #menubtn zemini: rgba(255,255,255,.92)


def cubuklar(K):
    """Üç çubuğun görselden nereyi keseceğini ÖLÇEREK seçer.

    Konumlar eskiden elle yazılıydı (12%/22%, 52%/55%, 30%/82%) ve eski
    zeminde iş görüyordu. Yeni örüntünün alt yarısı açık pembe: aynı
    konumlar ölçüldüğünde üçüncü çubuk beyaz diskin üzerinde 2.66:1'e
    düşüyor, yani grafik eşiğinin (3:1) altında -- menü simgesi soluyor.
    Artık her bölgeden (üst/orta/alt) eşiği GEÇEN en açık aday alınıyor:
    kapı sağlanıyor ama boyanın kendi aydınlık çeşitliliği korunuyor."""
    gorsel_boy = round(CUBUK_GORSEL * K.height / float(K.width))
    olcek = K.width / float(CUBUK_GORSEL)

    def pencere(px, py):
        """background-position yüzdesinin gerçekte gösterdiği parça."""
        x0 = px * (CUBUK_GORSEL - CUBUK_EN)
        y0 = py * (gorsel_boy - CUBUK_BOY)
        k = K.crop((int(x0 * olcek), int(y0 * olcek),
                    int((x0 + CUBUK_EN) * olcek) + 1,
                    int((y0 + CUBUK_BOY) * olcek) + 1)).resize((8, 2),
                                                               Image.LANCZOS)
        n = 0
        r = g = b = 0
        for R, G, B in k.getdata():
            r += R; g += G; b += B; n += 1
        return (r // n, g // n, b // n)

    # Diskin gerçek rengi: %92 beyaz + altındaki (perdeli) zemin.
    zem = perdele(pencere(0.10, 0.10))
    disk = tuple(int(round(DISK_A * 255 + (1 - DISK_A) * c)) for c in zem)
    disk_y = parlaklik(*disk)

    secim, kullanilan_x = [], []
    for et, a, b in (('ust', 0.02, 0.32), ('orta', 0.34, 0.62),
                     ('alt', 0.64, 0.97)):
        adaylar = []
        for i in range(13):
            py = a + (b - a) * i / 12.0
            for j in range(12):
                px = 0.04 + 0.92 * j / 11.0
                c = pencere(px, py)
                k = kontrast(disk_y, parlaklik(*c))
                if k >= 3.5 and all(abs(px - u) > 0.12 for u in kullanilan_x):
                    adaylar.append((parlaklik(*c), px, py, c, k))
        if not adaylar:
            raise SystemExit('HATA: %s bolgesinde 3.5:1 gecen cubuk yok.' % et)
        # Eşiği geçenlerin EN AÇIĞI: en az müdahale.
        y, px, py, c, k = max(adaylar, key=lambda t: t[0])
        kullanilan_x.append(px)
        secim.append(('%d%% %d%%' % (round(px * 100), round(py * 100)), c, k))

    print('hamburger       ' + '  |  '.join(
        '%s %.2f:1' % (p, k) for p, _, k in secim))
    for p, c, k in secim:
        if k < 3.0:
            raise SystemExit('HATA: cubuk %s %.2f:1 -- grafik esigi 3:1.'
                             % (p, k))
    return [p for p, _, _ in secim]


def cubuk_kapisi():
    """Ölçüm 420 px'lik görsele göre yapıldı; kabuk.css de öyle demeli."""
    s = io.open(KABUK, encoding='utf-8').read()
    if 'background-size: %dpx auto' % CUBUK_GORSEL not in s:
        raise SystemExit('HATA: kabuk.css #menubtn i background-size %dpx '
                         'degil -- cubuk olcumu yanlis pencereyi olcuyor.'
                         % CUBUK_GORSEL)


def palet(im, n=9):
    """Menü satırları için n açık ton, şeridin YUKARIDAN AŞAĞIYA bantları.

    Önce sıklığa göre baskın renkler alınıyordu; bu kaynakta dokuz rengin
    dokuzu da aynı soluk maviye düştü (#d3e0e7 ... #d1dfe6), çünkü tek
    tablonun içindeki renk dağılımı eski çok renkli tuvalinki gibi geniş
    değil. Bantlarla şeridin gerçek aralığı çıkıyor: turkuazdan mercana.

    Satır rengini kabuk.js buradan alıyor ama tonu sıcak pencereye,
    doygunluğu ve aydınlığı da firca.css'teki sayılara kelepçeliyor --
    yani menünün ölçülmüş kontrastı bu paletten etkilenmiyor."""
    en, boy = im.size
    out = []
    for i in range(n):
        y0, y1 = int(boy * i / n), int(boy * (i + 1) / n)
        bant = im.crop((0, y0, en, y1)).resize((8, 8), Image.LANCZOS)
        say = 0
        rs = gs = bs = 0
        for r, g, b in bant.convert('RGB').getdata():
            rs += r; gs += g; bs += b; say += 1
        h, l, s = colorsys.rgb_to_hls(rs / say / 255.0, gs / say / 255.0,
                                      bs / say / 255.0)
        rr, gg, bb = colorsys.hls_to_rgb(h, 0.80 + l * 0.14, min(s, 0.30))
        out.append('#%02x%02x%02x' % (int(rr * 255), int(gg * 255),
                                      int(bb * 255)))
    return out


# ── panelden seçilen zemin ────────────────────────────────────────────────
# Ressam panelde (Görünüm) zemini kendisi seçiyor: hazır desen, bir tablosu,
# kendi fotoğrafı ya da düz renk. Yukarıdaki kapılar elle seçilmiş TEK bir
# kaynak için yazıldı ve geçmeyince derlemeyi durduruyor; panelden gelen
# herhangi bir seçimde durmak yerine UYARLANIYOR: okunurluk tutmuyorsa zemin
# koyulaşıyor, çubuk bulunamıyorsa çubuklar düz koyu renk oluyor. Ressam
# "yazılar okunmuyor" diye bir siteyle karşılaşmıyor.
#
# Panelin önizlemesi (panel/index.html ZEMIN) aynı sayıları kullanıyor;
# denetim.py ikisinin aynı olduğunu her derlemede doğruluyor.
SERIT_ORAN = 298 / 1282.0      # şeridin en/boy oranı (kaynak şerit, filigransız)
KAGIT_ESIK = 2.0               # perdeli zeminin beyaz kâğıda karşı en az kontrastı
KARART_ADIM = 0.92             # okunurluk tutana kadar aydınlık bu oranla iner


def serit_kes(im, x):
    """Görselden tam boy dikey şerit. x (0..1): şeridin merkezinin yeri."""
    en, boy = im.size
    sw = max(8, min(en, int(round(boy * SERIT_ORAN))))
    x0 = int(round(min(max(x * en - sw / 2.0, 0), en - sw)))
    return im.crop((x0, 0, x0 + sw, boy))


def renk_serit(hex_renk):
    """Düz renk: ölü düz olmasın diye çok hafif dikey geçiş (üst açık, alt koyu)."""
    r, g, b = (int(hex_renk[i:i + 2], 16) for i in (1, 3, 5))
    h, l, s = colorsys.rgb_to_hls(r / 255.0, g / 255.0, b / 255.0)
    S = Image.new('RGB', (64, 276))
    p = S.load()
    for y in range(S.height):
        ll = max(0.0, min(1.0, l + 0.05 - 0.10 * y / (S.height - 1)))
        rr, gg, bb = colorsys.hls_to_rgb(h, ll, s)
        c = (int(rr * 255 + 0.5), int(gg * 255 + 0.5), int(bb * 255 + 0.5))
        for x in range(S.width):
            p[x, y] = c
    return S


def _p99_kontrast(K, m):
    """Aydınlık m ile çarpıldığında perdeli zeminin en parlak yeri (p99)
    beyaz kâğıda karşı kaç:1. okunurluk_raporu ile aynı ölçüm."""
    k = K.resize((80, 344), Image.LANCZOS)
    ys = []
    for renk in k.convert('RGB').getdata():
        if m < 1:
            h, l, s = colorsys.rgb_to_hls(*[v / 255.0 for v in renk])
            renk = tuple(int(v * 255 + 0.5) for v in colorsys.hls_to_rgb(h, l * m, s))
        ys.append(parlaklik(*perdele(renk)))
    ys.sort()
    return kontrast(parlaklik(255, 255, 255), ys[int(len(ys) * 0.99)])


def karart(im, m):
    o = im.copy()
    p = o.load()
    for y in range(o.height):
        for x in range(o.width):
            h, l, s = colorsys.rgb_to_hls(*[v / 255.0 for v in p[x, y]])
            rr, gg, bb = colorsys.hls_to_rgb(h, l * m, s)
            p[x, y] = (int(rr * 255 + 0.5), int(gg * 255 + 0.5), int(bb * 255 + 0.5))
    return o


def uyarla(K):
    """Okunurluk tutana kadar karart. Çarpanı döndürür (1 = dokunulmadı)."""
    m = 1.0
    for _ in range(40):
        if _p99_kontrast(K, m) >= KAGIT_ESIK:
            break
        m *= KARART_ADIM
    return (karart(K, m) if m < 1 else K), m


def cubuk_rengi(K):
    """Çubuk bulunamazsa: zeminin ortalama tonu, beyaz diske karşı 4:1
    olana kadar koyultulmuş düz renk."""
    k = K.resize((1, 1), Image.LANCZOS).getpixel((0, 0))
    h, l, s = colorsys.rgb_to_hls(*[v / 255.0 for v in k])
    disk = parlaklik(255, 255, 255) * DISK_A + 0.0
    while l > 0.02:
        r, g, b = colorsys.hls_to_rgb(h, l, s)
        c = (int(r * 255 + 0.5), int(g * 255 + 0.5), int(b * 255 + 0.5))
        if kontrast(disk, parlaklik(*c)) >= 4.0:
            return '#%02x%02x%02x' % c
        l -= 0.03
    return '#222222'


def panelden(secim, gorsel_dizin, hedef_dizin, eser_gorseli=None):
    """site.json gorunum.zemin -> hedef_dizin'e örüntü + zemin.json.

    secim: {'tur': 'eser'|'foto'|'renk', 'eser', 'gorsel', 'x', 'renk'}
    eser_gorseli: eser adı -> görsel dosya adı (icerik/eserler'den).
    Dönüş: zemin.json yolu; kaynak bulunamazsa None (hazır desen kalır)."""
    tur = secim.get('tur')
    if tur == 'renk':
        S = renk_serit(secim['renk'])
        ne = 'düz renk ' + secim['renk']
    else:
        ad = (secim.get('gorsel') if tur == 'foto'
              else (eser_gorseli or {}).get(secim.get('eser') or ''))
        yol = os.path.join(gorsel_dizin, ad) if ad else ''
        if not ad or not os.path.exists(yol):
            print('UYARI  zemin kaynagi yok (%s) -- hazir desen kaliyor' % (ad or secim.get('eser')))
            return None
        S = serit_kes(Image.open(yol).convert('RGB'), float(secim.get('x', 0.5)))
        ne = '%s %s, x=%.2f' % (tur, ad, float(secim.get('x', 0.5)))
    # Şerit ekranda ~1100 px boyda gösteriliyor; daha büyüğü yalnız bayt.
    if S.height > 1300:
        S = S.resize((max(8, round(S.width * 1300.0 / S.height)), 1300), Image.LANCZOS)
    K, m = uyarla(karola(yika(S)))
    print('zemin           %s -> karo %dx%d%s' % (ne, K.width, K.height,
          '' if m >= 1 else ' (okunurluk icin %%%d koyultuldu)' % round((1 - m) * 100)))
    try:
        cubuk, cubuk_renk = cubuklar(K), None
    except SystemExit:
        cubuk, cubuk_renk = None, cubuk_rengi(K)
        print('hamburger       duz renk %s' % cubuk_renk)
    b = io.BytesIO()
    K.save(b, 'WEBP', quality=Q, method=6)
    import hashlib
    ad = 'oruntu-%s.webp' % hashlib.sha1(b.getvalue()).hexdigest()[:10]
    os.makedirs(hedef_dizin, exist_ok=True)
    open(os.path.join(hedef_dizin, ad), 'wb').write(b.getvalue())
    p = palet(K)
    meta = {k: {'src': 'assets/zemin/' + ad, 'pos': '%d%% top' % (i * 9),
                'cubuk': cubuk, 'cubukRenk': cubuk_renk, 'palette': p}
            for i, k in enumerate(SAYFALAR)}
    meta['_kati'] = kati_renk(K)
    meta['_dosya'] = ad
    j = os.path.join(hedef_dizin, 'zemin.json')
    json.dump(meta, io.open(j, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    return j


def main():
    if not os.path.exists(KAYNAK):
        raise SystemExit('kaynak yok: ' + KAYNAK)
    os.makedirs(CIKTI, exist_ok=True)
    for f in os.listdir(CIKTI):
        if f.endswith('.webp'):
            os.remove(os.path.join(CIKTI, f))

    ham = Image.open(KAYNAK).convert('RGB')
    S = ham.crop((0, 0, ham.width, ham.height - FILIGRAN))
    print('kaynak %dx%d -> serit %dx%d (alt %d px filigran kirpildi)'
          % (ham.width, ham.height, S.width, S.height, FILIGRAN))

    K = karola(yika(S))
    print('karo   %dx%d  (en/boy %.3f -- serit ekran boyuna oturuyor)'
          % (K.width, K.height, K.width / float(K.height)))

    dikis_raporu(K)
    okunurluk_raporu(K)
    kati = kati_renk(K)
    kati_kapisi(kati)
    cubuk_kapisi()
    cubuk = cubuklar(K)

    ad = 'oruntu.webp'
    K.save(os.path.join(CIKTI, ad), 'WEBP', quality=Q, method=6)

    # Tek zemin, tek palet: tema tek. Sayfalar yalnız yatay fazda ayrışıyor.
    p = palet(K)
    meta = {}
    for i, anahtar in enumerate(SAYFALAR):
        meta[anahtar] = {'src': 'assets/zemin/' + ad,
                         'pos': '%d%% top' % (i * 9),
                         'cubuk': cubuk,
                         'palette': p}
    json.dump(meta, io.open(os.path.join(KOK, 'zeminler.json'), 'w',
                            encoding='utf-8'), ensure_ascii=False, indent=1)

    kb = os.path.getsize(os.path.join(CIKTI, ad)) / 1024.0
    print('palet           %s' % ' '.join(p[:5]))
    print('\n1 oruntu · %.0f KB · %d sayfa ayni zemini paylasiyor'
          % (kb, len(meta)))


if __name__ == '__main__':
    main()
