# -*- coding: utf-8 -*-
"""Menu panelini firca darbeleriyle boyar.

Menu artik siyah bir dikdortgen degil: yedi firca darbesiyle boyanmis bir
alan. Bu betik o darbeleri gercek boya fotograflarindan uretiyor, panele
yerlestiriyor, YAZI ALTINI OLCUYOR ve CSS yerlesimini yaziyor.

  girdi   firca-ham/*.jpg        gercek boya fotograflari (yapay zeka uretti)
  cikti   varlik/firca/*.webp    siteye giden darbeler
          firca.css              CSS yerlesimi (derlemede enjekte edilir)

Kullanim:  python firca.py


NEDEN BOYLE -- uc deneme coptu, sebepleri kayitli olsun:

1. BANDIN ICINE DOKU CARPMAK.  Duzgun bir egriyle band cizip uzerine boya
   fotografini yatayda gerdirdim. Saten kumas cikti: gerdirilen kil izi
   uzayip ipek parlamasina donuyor, uclar da 45 derece kesik kose oluyor.

2. YUZLERCE INCE KIL CIZMEK.  Firca darbesini kil demeti olarak modelledim.
   Tel demeti cikti. Yanlis varsayim suydu: yuklu bir darbenin govdesi
   COGUNLUKLA DOLUDUR; kil karakteri govdenin icinde degil, kenarinda,
   birkac seyrek izde ve dagilan kuru ucta yasar.

3. Ikisinin ortak hatasi: kutleyi ben cizmeye calistim.

Simdiki yol hicbir sey cizmiyor. Fotografta ZATEN olan darbeyi aliyor:
kagit beyazini olcup sifira cekiyor, en buyuk bagli boya kutlesini
ayikliyor, ana eksenini ikinci momentlerden bulup yatiriyor.


VE ASIL KARAR -- SAYDAMLIK ile DOKUYU ayirmak:

Panelde 13 satir + onizleme sutunu var, yani yazi panelin neredeyse
tamamini kapliyor. "Delikli boya" bu yaziyi tasiyamaz; olctum, 20 yazi
kutusunun 19'u dusuyordu. Delikleri kapatinca da panel duz bir kirmizi
dikdortgene dondu ve butun firca karakteri gitti.

  ALFA -> darbenin DOLDURULMUS silueti. Ici opak, kenari tirtikli.
  RENK -> darbenin HAM yogunlugu. Kil izi, kuruyan uc, basinc farki;
          hepsi burada, DEGER farki olarak.

Gercek yagliboya da boyledir: ortu verici bir katta firca izini gordugun
sey saydamlik degil, kalinlik farkindan gelen degerdir. Boya inceldiginde
saydamlasmiyor, aciliyor.
"""
import colorsys
import io
import json
import math
import os
import sys

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageOps

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

KOK = os.path.dirname(os.path.abspath(__file__))
HAM = os.path.join(KOK, 'firca-ham')
VARLIK = os.path.join(KOK, 'varlik', 'firca')
CSS_YOL = os.path.join(KOK, 'firca.css')
OLCUM = os.path.join(KOK, 'kaynak', 'firca')

# Panelin gercek olcusu -- tarayicidan okundu, goz karari degil.
EN, BOY = 600, 857

# Darbelerin kutu DISINA tasma payi. Bu olmadan kompozisyon tam kutu
# boyunda bir tuvalde kuruluyordu ve tasan her sey varligin kendisinde
# kesiliyordu; panelin dort kenari da cetvel gibi duzdu.
# Sag pay KUCULTULDU: 86 iken boya panelin cok disina tasip sagdaki
# beyaz kagidin (eserin sayfasi) uzerine biniyordu -- eserin ustune
# leke gibi duruyordu. Tirtikli kenar icin bu kadari yetiyor.
PAY_SOL, PAY_UST, PAY_SAG, PAY_ALT = 46, 40, 40, 60
TUVAL_EN = PAY_SOL + EN + PAY_SAG
TUVAL_BOY = PAY_UST + BOY + PAY_ALT
TABAN = 0.92        # yazi altinda en dusuk opaklik
KONTRAST_TABAN = 4.5   # WCAG AA, normal boy yazi

# Menu satir renkleri sabit degil: zemin paletinden uretiliyor.
# Bu ucu kabuk.js/paintMenu ile BIREBIR ayni olmak zorunda.
# Olculdu: 0.72'de satir00, satir05 ve satir07 WCAG AA'yi gecmiyordu
# (3.32:1, 4.31:1, 4.23:1) -- eski kirmizi panelde de gecmiyorlardi, ben
# kaba bir parlaklik olcutu kullandigim icin gormemistim. 0.88'de hepsi
# geciyor, en kotu 4.92:1.
# Menudeki iki vurgu murekkebi: paintMenu bu iki satira renk YAZMIYOR,
# rengi CSS'ten geliyor. Hangi satirin ozel oldugu sayfaya gore
# degistigi icin ikisi de HER kutuda denetleniyor.
# Krem panelde vurgu KOYU olmak zorunda. Acik altin tonlari
# (#ecd8c4 / #f2dea8) krem zeminde 1.1-1.2:1 veriyordu, yani okunmuyordu.
# Ton korunuyor, deger tersine doniyor: yanik toprak.
ALTINLAR = [(104, 70, 30),    # #68461e  .cikis  ('Ana sayfa')
            (98, 66, 24)]     # #624218  .ozel   (bulundugun sayfa)

# Satir olmayan kutularin murekkepleri. Bunlar eskiden siyah panel
# donemindan kalma koyu grilerdi (#5d5d63, #6f6f76, #8d7c56) ve olcum
# onlari sabit acik murekkep varsaydigi icin gecmis gorunuyordu; uc
# degerlendirici de okunmadiklarini gordu. Artik burada tanimli,
# firca.css'e yaziliyor ve kabuk.css oradan okuyor.
#
# Panel krem oldugu icin hepsi zorunlu olarak KOYU. Saf siyah degil:
# ressam sitesinde matbaa siyahi gibi durur, kahverengi-siyah boya gibi
# durmaz. Hiyerarsi hem degerle hem boy/buyuk harf/harf araligiyla.
# En kotu zemin (209,199,182) uzerinde olculdu, hepsi 4.59-9.65:1.
MUREKKEP = {
    'grup':      (92, 76, 66),      # "SANATÇI" ara basligi   4.89:1
    'dil':       (96, 80, 70),      # TR / EN / FR            4.59:1
    'dil-aktif': (40, 31, 26),      #                         9.65:1
    'oniz-ust':  (96, 68, 26),      # "KATALOG" kucuk etiket  5.37:1
    'oniz-alt':  (68, 56, 48),      #                         6.77:1
    # Onizleme basligi. kabuk.css'te elle #f2ede2 yaziliydi ve bu
    # tabloda YOKTU: olcum onu varsayilan acik griyle olcuyordu, yani
    # olculen renk ne CSS'tekiydi ne de gercekti. Artik tek kaynak.
    'oniz-ad':   (44, 34, 29),      #                         9.22:1
    # Kapatma dugmesi. Eskiden bu tabloda YOKTU ve olcum onu varsayilan
    # acik gri ile olcuyordu -- yani var olmayan bir kontrolu olcuyordu.
    # Artik gercek rengiyle olculuyor.
    'kapat':     (46, 36, 31),      #                         9.04:1
}
SAT_TAVAN = 0.40
# 0.90'dan 0.20'ye: panel krem oldu, satirlar KOYU olmak zorunda.
# En kotu hal en acik satir (taban + 6*adim) ve o bile 5.67:1 veriyor.
LIG_TABAN = 0.20
LIG_ADIM = 0.015

SURE = 300          # bir darbenin supurme suresi (ms)

# Gecikmeler SABIT DEGIL, yavaslayan. Sabit 66 ms "yedi ayri olay" gibi
# okunuyordu; hizlanip yavaslayan bir dizi tek bir jest gibi okunuyor.
GECIKMELER = [0, 44, 84, 120, 152, 180, 204]

# Firca egrisi ARAYUZ egrisi degil. var(--ease) expo-out: 300 ms'lik bir
# darbe 30 ms'de %49 tamamlaniyor, geri kalan %28'i 245 ms boyunca
# gorunmez sekilde surukleniyor. Firca neredeyse sabit hizda gider,
# ucunda hafif yavaslar.
FIRCA_EGRI = 'cubic-bezier(.38,.12,.56,.94)'

# Menudeki her yazi kutusu (panel yereli). Bunlarin altinda boya opak olmali.
SATIR_Y = [113, 155, 227, 269, 312, 354, 396, 485, 527, 570, 612, 654, 697, 739]
# Menu kutusu yerelinde olculdu. 'grup' = "Sanatçı" ara basligi: iki
# degerlendirici de onun okunmadigini soyledi ve haklilardi -- rengi
# paletten gelmiyordu ve olcume de hic girmiyordu.
_KUTULAR = (
    [('satir%02d' % i, 30, y, 195, 41) for i, y in enumerate(SATIR_Y)]
    + [('grup', 30, 290, 195, 17),
       ('dil', 30, 802, 195, 29),
       # Kapatma dugmesi olcumden CIKARILDI: beyaz opak bir disk ve
       # uzerindeki cizgi koyu. Ne opakligi ne kontrasti panelin boyasina
       # bagli; onu boyaya karsi olcmek var olmayan bir kontrolu
       # olcmekti ve yanlis alarm uretiyordu.
       ('oniz-gorsel', 293, 226, 270, 152),
       ('oniz-ust', 293, 520, 270, 17),
       ('oniz-ad', 293, 544, 270, 30),
       ('oniz-alt', 293, 579, 270, 44)]
)
# Tuval paylı oldugu icin kutular da kayiyor; kaydirmasak opaklik ve
# kontrast yanlis yerden okunur.
YAZI_KUTULARI = [(ad, x + PAY_SOL, y + PAY_UST, w, h)
                 for ad, x, y, w, h in _KUTULAR]

# Ham fotograf -> darbe adi. Govde olanlarin cekirdegi masif, karakter
# olanlar tirtikli ve dagilan.
SECIM = [('govde-1', 'badana-11.jpg'), ('govde-2', 'bicak-11.jpg'),
         ('govde-3', 'kuru-27.jpg'),   ('karakter-1', 'kuru-11.jpg'),
         ('karakter-2', 'yagli-27.jpg'), ('karakter-3', 'bicak-27.jpg')]

# Sira ressamin sirasi: genis bir ust darbe, sol kenari muhurleyen dikey
# pas, sonra govdeyi kuran yataylar, sonda karakter ve duzeltme.
#   (darbe, sol%, ust%, genislik%, donme, yatay_ayna)
YERLESIM = [
    ('govde-1',    -14,  -9, 134,  -4, False),
    # Tam 90 derece degil: "boya capraz akiyor ama tam dikey, koyu ince
    # bir iz var" diye yakalandi. Firca o yonde gitmiyorsa iz de tam
    # dikey durmamali.
    ('govde-3',     -4,  -4, 164,  90, False),
    ('karakter-2',  -6,  -5, 116,   5, False),
    ('govde-2',    -14,  26, 132,  -2, True),
    ('karakter-3', -14,  43, 140,   3, True),
    ('karakter-1', -12,  68, 138,  -3, True),
    ('karakter-1',   4,  29,  74,  -7, False),
    ('karakter-1',  14,  23,  44,   5, True),    # satir02 civari
    ('karakter-1',  62,  67,  42,  -4, False),   # onizleme alti
]

# Mat kil gulu. Onceki hal doygun Fransiz kirmizisiydi ve cirtlak
# geliyordu; doygunluk %69'dan %28'e indi, ton biraz isindi.
#
# Daha da nude'a gitmenin bir tavani var ve olculdu: baglayici kisit
# panelin EN ACIK noktasi, cunku menu satirlari ACIK murekkeple yaziliyor.
# Daha acik iki aday (tarcin gulu, nude gul) satir parlakligi 0.92 olsa
# bile WCAG AA'yi (4.5:1) gecemedi. Bunun otesi ancak yaziyi KOYU murekkebe
# cevirmekle olur -- o da menunun butun karakterini degistirir, ayri bir
# karar.
#
# Ton ayrica DUZLESTIRILDI: tepe parlakligi kontrasti belirliyor, ortalama
# ise gozun gordugu tonu. Tepeyi koyultmak ayni kontrastta daha nude bir
# ortalama veriyor.
# Ton 14 derece: sicak ama hala gul. Denenip birakilanlar --  7 derece
# mor-kahveye kaciyor, 20 ve 26 derece kahveye doniyor; nude pembe-bej
# bir yer, kahve degil. Bes aday zemin uzerinde yan yana bakilarak
# secildi, sayiyla degil.
# KREM-BEYAZ. Ton 37-40 derece, isiklilik %83-96. Gecis KORUNUYOR:
# duz tek renk bir panel karton gibi duruyor, boyanin hacmini gosteren
# sey ustten alta koyulasan bu ince fark.
# Olculen yan fayda: boyanin kalinlik hissi ACIK zeminde daha iyi
# okunuyor. Koyu panelde panel ici doku sapmasi std 3-7 idi, yani
# "kalinliktan gelen deger" alanin onda dokuzunda gorunmuyordu.
FR = [(0.00, (252, 248, 240)), (0.28, (249, 244, 234)),
      (0.60, (244, 237, 224)), (0.85, (236, 227, 211)),
      (1.00, (227, 216, 198))]

EGRI_LO, EGRI_HI = 14, 168   # ham yogunluk egrisi: pus sifira, cekirdek opak

# Kenar bandinin genisligi. Bu bantta dolgu YOK, gercek boyanin alfasi
# var. Genisledikce kenar daha boya gibi, ama yazi kutulari ic bolgenin
# disina tasarsa okunurluk garantisi duser -- olcum bunu denetliyor.
# Tasma olcumunde "gorunur" sayilan en kucuk alfa. Kuru firca ucunda
# alfasi 1-2 olan uzun kuyruklar var; koyu duvarin uzerinde gozle
# secilmiyorlar ama alfa>0 ile olculunce tasmayi 13 px sisiriyorlar ve
# kagit bedava kucultuluyordu.
# Icinde YAZI degil GORSEL olan kutular. Bunlarda "murekkep" diye bir
# sey yok, dolayisiyla kontrast olcumu anlamsiz -- yalniz opaklik
# denetlenmeli. Koyu panelde bu kutu varsayilan acik gri ile olculup
# TESADUFEN geciyordu; panel kremlenince ayni tesadüf 1.05:1'e dondu ve
# olcumun bastan beri var olmayan bir seyi olctugu ortaya cikti.
GORSEL_KUTULARI = {'oniz-gorsel'}

GORUNUR_ESIK = 28

KENAR_BANDI = 16

# Yazi kutularindan bu kadar uzakta boya NEFES ALIYOR: dolgu devreden
# cikiyor, fircanin atladigi yerler delik kaliyor ve altindaki duvar
# okunuyor. Pay buyudukce panel daha kapali, kucuuldukce yaziya daha
# yakin delik aciliyor.
# 18 iken olcum reddetti: 9 yazi kutusunda %1-24 delik acildi. Sebep
# bulaniklik -- guvenli bolgenin sinirini yumusatmak icin 9 px bulanik
# uygulaniyor ve bu ACIKLIGI kutunun icine tasiriyordu. Pay, bulanigin
# tasma mesafesini de kapsayacak kadar buyuk olmali.
GUVENLI_PAY = 44
# Delik sayilan esik: ham yogunluk bunun altindaysa o piksel aciliyor.
NEFES_ESIK = 132


# ══ 1. FOTOGRAFTAN DARBEYI AYIKLA ═══════════════════════════════════════

def yogunluk(yol):
    """Boya yogunlugu: kagit beyazi sifir, en koyu boya 255.

    Once kenardan pay kesiliyor. Fotografin kendi kenari koyu (vinyet); o
    ince rim darbeye baglanip en buyuk bagli kutlenin parcasi oluyor ve
    kutle karenin tamamina yayiliyor. Uc darbe boyle bozulmustu; kutleyi
    reddetmek ise yaramadi, cunku kutle hem rim hem darbeydi.
    """
    im = Image.open(yol).convert('L')
    pay = max(4, int(min(im.size) * 0.025))
    im = im.crop((pay, pay, im.width - pay, im.height - pay))
    px = sorted(im.getdata())
    n = len(px)
    kagit, koyu = px[int(n * 0.86)], px[int(n * 0.004)]
    if kagit - koyu < 25:
        return None
    d = Image.new('L', im.size)
    kaynak, hedef = im.load(), d.load()
    olcek = 255.0 / (kagit - koyu)
    for y in range(im.height):
        for x in range(im.width):
            v = (kagit - kaynak[x, y]) * olcek
            hedef[x, y] = 0 if v <= 0 else (255 if v >= 255 else int(v))
    return d


def en_buyuk_kutle(d, esik=70):
    """En buyuk bagli boya kutlesi (birlestir-bul, tek gecis)."""
    w, h = d.size
    px = d.load()
    etiket = [0] * (w * h)
    ebeveyn = [0]

    def bul(a):
        while ebeveyn[a] != a:
            ebeveyn[a] = ebeveyn[ebeveyn[a]]
            a = ebeveyn[a]
        return a

    def birlestir(a, b):
        ra, rb = bul(a), bul(b)
        if ra != rb:
            ebeveyn[max(ra, rb)] = min(ra, rb)

    for y in range(h):
        satir = y * w
        for x in range(w):
            if px[x, y] < esik:
                continue
            sol = etiket[satir + x - 1] if x else 0
            ust = etiket[satir - w + x] if y else 0
            if sol and ust:
                etiket[satir + x] = sol
                birlestir(sol, ust)
            elif sol or ust:
                etiket[satir + x] = sol or ust
            else:
                ebeveyn.append(len(ebeveyn))
                etiket[satir + x] = len(ebeveyn) - 1

    sayim = {}
    for i, e in enumerate(etiket):
        if e:
            k = bul(e)
            etiket[i] = k
            sayim[k] = sayim.get(k, 0) + 1
    if not sayim:
        return None
    kazanan = max(sayim, key=sayim.get)

    m = Image.new('L', (w, h), 0)
    mp = m.load()
    for y in range(h):
        satir = y * w
        for x in range(w):
            if etiket[satir + x] == kazanan:
                mp[x, y] = 255
    return m


def ana_eksen(m):
    """Kutlenin ana ekseninin yatayla acisi. Yapay zeka 'yatay' demeyi
    dinlemedi, sekiz adayin sekizi de caprazdi; darbeyi buradan yatiriyoruz."""
    w, h = m.size
    mp = m.load()
    n = sx = sy = 0
    for y in range(0, h, 2):
        for x in range(0, w, 2):
            if mp[x, y]:
                sx += x
                sy += y
                n += 1
    if n < 50:
        return 0.0
    ox, oy = sx / n, sy / n
    xx = yy = xy = 0.0
    for y in range(0, h, 2):
        for x in range(0, w, 2):
            if mp[x, y]:
                dx, dy = x - ox, y - oy
                xx += dx * dx
                yy += dy * dy
                xy += dx * dy
    return math.degrees(0.5 * math.atan2(2 * xy, xx - yy))


def darbeyi_al(dosya):
    """Bir fotograftan tek darbenin alfa maskesi."""
    d = yogunluk(os.path.join(HAM, dosya))
    if d is None:
        return None
    m = en_buyuk_kutle(d)
    if m is None:
        return None
    dp, mp = d.load(), m.load()
    for y in range(d.height):
        for x in range(d.width):
            if not mp[x, y]:
                dp[x, y] = 0

    aci = ana_eksen(m)
    d = d.rotate(aci, resample=Image.BICUBIC, expand=True, fillcolor=0)
    kutu = d.getbbox()
    if kutu:
        d = d.crop(kutu)
    d = d.point(lambda v: 0 if v <= EGRI_LO else
                (255 if v >= EGRI_HI else
                 int((v - EGRI_LO) * 255.0 / (EGRI_HI - EGRI_LO))))
    kutu = d.getbbox()
    if kutu:
        d = d.crop(kutu)
    if d.width > 900:
        d = d.resize((900, max(1, round(900 * d.height / d.width))), Image.LANCZOS)
    return d


# ══ 2. SILUET: IC DELIKLERI KAPAT, DIS TIRTIGI KORU ═════════════════════

def _genislet(im, r):
    """Yuvarlak genisletme. Pillow'un MaxFilter'i KARE cekirdekli ve
    siluetin sinirina dik acili basamaklar birakiyor -- panelde dijital
    gorunen delikler cikti. Gauss izotropiktir; bulanik + esik ayni isi
    yuvarlak cekirdekle yapar."""
    return im.filter(ImageFilter.GaussianBlur(r * 0.62)).point(
        lambda v: 255 if v > 46 else 0)


def _daralt(im, r):
    return im.filter(ImageFilter.GaussianBlur(r * 0.62)).point(
        lambda v: 255 if v > 209 else 0)


def doldur(a, esik=76, yaricap=10):
    """Kapama + disariya bagli olmayan bosluklari doldurma.

    Dis silueti bozmuyor: tirtik cok daha buyuk olcekte. Ama darbenin
    govdesindeki igne delikleri kapaniyor -- yazi onlarin ustunde duracak.
    """
    ikili = a.point(lambda v: 255 if v >= esik else 0)
    ikili = _daralt(_genislet(ikili, yaricap), yaricap)
    w, h = ikili.size
    ped = Image.new('L', (w + 2, h + 2), 0)
    ped.paste(ikili, (1, 1))
    ters = ped.point(lambda v: 0 if v else 255)
    ImageDraw.floodfill(ters, (0, 0), 128)
    delik = ters.point(lambda v: 255 if v == 255 else 0).crop((1, 1, w + 1, h + 1))
    dolu = ikili.copy()
    dolu.paste(255, (0, 0), delik)

    # Dolgu yalnizca IC BOLGEYE. Kenar bandinda gercek boyanin kendi
    # alfasi kaliyor: kuruyan uc, dagilan kil, solan yuk. Eskiden cikti
    # sinirini doldurulmus ikili belirliyordu ve kenar her noktada tam
    # opakti -- 'makasla kesilmis' gorunuyordu, fircayla degil.
    ic = _daralt(dolu, KENAR_BANDI)
    return ImageChops.lighter(a, ic)


# ══ 3. PANELE YERLESTIR VE BOYA ═════════════════════════════════════════

def fr(t):
    t = max(0.0, min(1.0, t))
    for i in range(len(FR) - 1):
        a, ca = FR[i]
        b, cb = FR[i + 1]
        if a <= t <= b:
            u = (t - a) / (b - a)
            return tuple(int(ca[k] + (cb[k] - ca[k]) * u) for k in range(3))
    return FR[-1][1]


def nefes_dokusu(darbeler):
    """Butun darbelerin PAYLASTIGI delik dokusu.

    Her darbeye ayri delik acmak ise yaramiyor: delikler hizalanmadigi
    icin ust uste binen dokuz kat birbirinin deligini kapatiyor
    (olculdu, panel ici iki ayri zemin uzerinde birebir ayni renk
    cikiyordu). Ortak doku ile delikler ayni yerde ve alt gercekten
    okunuyor.

    Doku kuru firca fotografinin kendi yogunlugundan: deliklerin
    dagilimi da gercek bir darbeden geliyor.
    """
    ham = darbeler['karakter-1']
    d = ham.resize((TUVAL_EN, TUVAL_BOY), Image.LANCZOS)
    # Cogu yer acik (delik yok), az yer koyu (delik). Egri bunu kuruyor:
    # 190 ustu tam opak, 120 altı tam delik.
    # Egri DARALTILDI: ilk denemede panel yuzey olmaktan cikip lekeye
    # dondu, kaplama %99'dan %86'ya dustu. Ressam bir nefes deligi
    # istedi, saydamlik degil. Artik yalnizca gercekten kuru yerler
    # aciliyor ve tam delik degil, incelme.
    return d.point(lambda v: 255 if v >= 150 else
                   (96 if v <= 84 else int(96 + (v - 84) * 159.0 / 66)))


def guvenli_bolge():
    """Yazinin UZAGINDAKI bolge. Burada boya nefes alabilir.

    Yazi kutulari olculmus koordinatlar oldugu icin bu maske tahmin
    degil: kutular GUVENLI_PAY kadar buyutulup cikariliyor.
    """
    m = Image.new('L', (TUVAL_EN, TUVAL_BOY), 255)
    d = ImageDraw.Draw(m)
    for ad, x, y, w, h in YAZI_KUTULARI:
        d.rectangle([x - GUVENLI_PAY, y - GUVENLI_PAY,
                     x + w + GUVENLI_PAY, y + h + GUVENLI_PAY], fill=0)
    # Kenarlari yumusat: sert bir sinir "buraya kadar delik, buradan sonra
    # yok" diye okunur ve yine cetvel etkisi yapar.
    return m.filter(ImageFilter.GaussianBlur(9))


def donustur(ham, wy, donme, ayna):
    if ayna:
        ham = ham.transpose(Image.FLIP_LEFT_RIGHT)
    w = max(1, int(EN * wy / 100.0))
    h = max(1, round(w * ham.height / ham.width))
    ham = ham.resize((w, h), Image.LANCZOS)
    siluet = doldur(ham)
    if donme:
        ham = ham.rotate(donme, resample=Image.BICUBIC, expand=True, fillcolor=0)
        siluet = siluet.rotate(donme, resample=Image.BICUBIC, expand=True, fillcolor=0)
    return ham, siluet


def boya_darbe(ham, siluet, ox, oy, guvenli=None, nefes=None):
    """Doku RENKTE, alfa siluet. Ince boya acilir ama solmaz -- doygunlugu
    korumazsak panel plastik ortu gibi duruyor (denendi)."""
    w, h = siluet.size
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    px, hp, sp = im.load(), ham.load(), siluet.load()
    gp = guvenli.load() if guvenli is not None else None
    np_ = nefes.load() if nefes is not None else None
    for y in range(h):
        ty = (oy + y - PAY_UST) / float(BOY)
        for x in range(w):
            a = sp[x, y]
            if not a:
                continue
            if gp is not None:
                gx, gy = ox + x, oy + y
                if 0 <= gx < TUVAL_EN and 0 <= gy < TUVAL_BOY:
                    g = gp[gx, gy]
                    if g and np_ is not None:
                        # Yazidan uzakta ORTAK dokunun deligi aciliyor.
                        # g=0 korumali (hic degisme), g=255 guvenli.
                        nv = np_[gx, gy]
                        if nv < 255:
                            hedef = a * nv / 255.0
                            a = int(a + (hedef - a) * (g / 255.0))
                            if a <= 0:
                                continue
            r, g, b = fr(0.30 * ((ox + x - PAY_SOL) / float(EN)) + 0.70 * ty)
            kal = hp[x, y] / 255.0
            ac = 1.0 + (1.0 - kal) * 0.20
            gri = (r + g + b) / 3.0
            kar = (1.0 - kal) * 0.14
            px[x, y] = (min(255, int((r * (1 - kar) + gri * kar) * ac)),
                        min(255, int((g * (1 - kar) + gri * kar) * ac)),
                        min(255, int((b * (1 - kar) + gri * kar) * ac)), a)
    return im


def kur(darbeler):
    panel = Image.new('RGBA', (TUVAL_EN, TUVAL_BOY), (0, 0, 0, 0))
    guvenli = guvenli_bolge()
    nefes = nefes_dokusu(darbeler)
    parcalar = []
    for ad, xy, yy, wy, donme, ayna in YERLESIM:
        ham, siluet = donustur(darbeler[ad], wy, donme, ayna)
        ox = int(EN * xy / 100.0) + PAY_SOL
        oy = int(BOY * yy / 100.0) + PAY_UST
        d = boya_darbe(ham, siluet, ox, oy, guvenli, nefes)
        gec = Image.new('RGBA', (TUVAL_EN, TUVAL_BOY), (0, 0, 0, 0))
        gec.paste(d, (ox, oy))
        panel = Image.alpha_composite(panel, gec)
        parcalar.append({'gorsel': d, 'ox': ox, 'oy': oy})
    return panel, parcalar


# ══ 4. OLC ══════════════════════════════════════════════════════════════

def isik(r, g, b):
    return (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255.0


def _dogrusal(k):
    k = k / 255.0
    return k / 12.92 if k <= 0.03928 else ((k + 0.055) / 1.055) ** 2.4


def parlaklik(r, g, b):
    """WCAG bagil parlaklik. Dogrusallastirma sart: sRGB degerlerinin
    agirlikli ortalamasi doygun renklerde iki kat yanilabiliyor."""
    return (0.2126 * _dogrusal(r) + 0.7152 * _dogrusal(g) + 0.0722 * _dogrusal(b))


def kontrast(a, b):
    la, lb = parlaklik(*a), parlaklik(*b)
    if la < lb:
        la, lb = lb, la
    return (la + 0.05) / (lb + 0.05)


def satir_renkleri(palet):
    """kabuk.js/paintMenu'nun urettigi renkler. 14 nav satiri."""
    renkler = []
    for i in range(len(SATIR_Y)):
        hx = palet[i % len(palet)]
        n = int(hx[1:], 16)
        r, g, b = (n >> 16) & 255, (n >> 8) & 255, n & 255
        h, l, sat = colorsys.rgb_to_hls(r / 255.0, g / 255.0, b / 255.0)
        sat = min(sat, SAT_TAVAN)
        lig = LIG_TABAN + ((i * 3) % 7) * LIG_ADIM
        rr, gg, bb = colorsys.hls_to_rgb(h, lig, sat)
        renkler.append((int(rr * 255), int(gg * 255), int(bb * 255)))
    return renkler


def tum_paletler():
    """Butun sayfa zeminlerinin paletleri.

    Menu her sayfada O SAYFANIN paletinden renk aliyor; yalnizca galeriyi
    olcmek eksik olurdu. Parlaklik LIG_TABAN'dan geldigi icin sayfalar
    arasi fark kucuk ama garantiyi tahmine birakmanin anlami yok.
    """
    yol = os.path.join(KOK, 'zeminler.json')
    if not os.path.exists(yol):
        return {'yedek': ['#e4cecd'] * 9}
    d = json.load(io.open(yol, encoding='utf-8'))
    return {k: (v.get('palette') or ['#e4cecd'] * 9) for k, v in d.items()}


def ic_kontrol(panel, pay=45, guvenli=None):
    """Panelin ICINDE delik olmamali.

    Yazi kutulari tek tek gecse bile aralarinda kalan bir bosluk panelin
    ARKASINDAKI SAYFAYI gosteriyor -- menu bir tablonun degil, beyaz
    katalog kagidinin ustunde duruyor. Tarayicida goruldu: y610-640
    bandindaki bosluktan katalog sizdi ve boya araligi gibi degil, hata
    gibi durdu.

    Kural: dis sinir tirtikli olabilir, olmali da; ama kenardan `pay`
    kadar iceride her yer opak.
    """
    ap = panel.getchannel('A').load()
    # Yazinin UZAGINDAKI delikler kasitli: ressamin istedigi 'nefes'.
    # Kapi yalnizca yaziya YAKIN bolgedeki delikleri sayiyor, yoksa
    # kendi kastimizi hata olarak bildiriyor.
    gp = guvenli.load() if guvenli is not None else None
    kotu = []
    # Yalnizca MENU KUTUSUNUN icine bakiyoruz; pay bolgesi zaten tasma.
    for y in range(PAY_UST + pay, PAY_UST + BOY - pay, 3):
        for x in range(PAY_SOL + pay, PAY_SOL + EN - pay, 3):
            if gp is not None and gp[x, y] > 40:
                continue                    # kasitli nefes bolgesi
            if ap[x, y] < TABAN * 255:
                kotu.append((x, y))
    toplam = (len(range(PAY_UST + pay, PAY_UST + BOY - pay, 3))
              * len(range(PAY_SOL + pay, PAY_SOL + EN - pay, 3)))
    if not kotu:
        return 0.0, None
    xs = [k[0] for k in kotu]
    ys = [k[1] for k in kotu]
    return len(kotu) / float(toplam), (min(xs), min(ys), max(xs), max(ys))


def gerilmis_olc(panel, hedef_boy):
    """Panel BASKA bir yukseklikte de olculuyor.

    Butun garanti tek bir gorunum yuksekligine (857 px) cakiliydi. Ama
    #menu artik 100dvh ve darbelerin konumu YUZDE; yani 950 px'lik bir
    ekranda boya dikeyde geriliyor, yazi satirlari ise yerinde kaliyor.
    Olculen hizalama o ekranda artik gecerli degil.

    Burada CSS'in yaptigi sey taklit ediliyor: bilesik dikeyde geriliyor,
    yazi kutulari ise panel tepesinden ayni piksel uzakligında biraktılıyor.
    """
    k = hedef_boy / float(BOY)
    gerilmis = panel.resize((TUVAL_EN, max(1, round(TUVAL_BOY * k))),
                            Image.LANCZOS)
    yeni_ust = round(PAY_UST * k)
    # #mon bir flex kolon ve iki cocugu da `flex: 1 1 auto`: fazla
    # yukseklik ikiye bolunuyor, yani onizleme kutulari asagi KAYIYOR.
    # Satirlar ise tepeye capalı. Ayni kaydirmayi uygulamak yanlis olurdu.
    kay = round((hedef_boy - BOY) / 2.0)
    kutular = [(ad, x, yeni_ust + (y - PAY_UST) + (kay if ad.startswith('oniz') else 0),
                w, h)
               for ad, x, y, w, h in YAZI_KUTULARI]
    return olc(gerilmis, kutular, gerilmis.size)


def olc(panel, kutular=None, boyut=None):
    px = panel.load()
    kutular = YAZI_KUTULARI if kutular is None else kutular
    sinir = (TUVAL_EN, TUVAL_BOY) if boyut is None else boyut
    paletler = tum_paletler()
    # Her kutu icin her sayfanin satir rengi denenip EN KOTUSU aliniyor.
    tum_satirlar = {k: satir_renkleri(v) for k, v in paletler.items()}
    rapor = []
    for i, (ad, x, y, w, h) in enumerate(kutular):
        # Satirin kendi rengi. Ama menudeki iki satira paintMenu renk
        # YAZMIYOR: 'Ana sayfa' ve bulundugun sayfa altin kaliyor
        # (#d9b9a0). Hangi satirin ozel oldugu sayfaya gore degistigi
        # icin ALTIN her kutuda ayrica denetleniyor -- menudeki en sonuk
        # murekkep o, gecerse otekiler de geciyor.
        if ad in GORSEL_KUTULARI:
            adaylar = []            # yazi yok: yalniz opaklik denetlenir
        elif ad.startswith('satir'):
            adaylar = [s[i] for s in tum_satirlar.values()] + ALTINLAR
        else:
            # Her kutu KENDI murekkebiyle olculuyor. Eskiden hepsi icin
            # sabit (233,233,228) varsayiliyordu ve olcum yaniltiyordu.
            adaylar = [MUREKKEP.get(ad, (233, 233, 228))]
        dusuk, altta, n, en_kotu = 255, 0, 0, 99.0
        for yy in range(y + 2, y + h - 2, 2):
            for xx in range(x + 2, x + w - 2, 2):
                # Sinirlar PAYLI tuvale gore. Eskiden ciplak EN/BOY ile
                # karsilastiriliyordu ama kutular +PAY_SOL/+PAY_UST
                # kaydirilmisti: 'dil' kutusunun (y 846-873) yalnizca bir
                # kismi, 'oniz-*' kutularinin ise sag 9 px'i olcum disinda
                # kaliyordu -- yani panelin boyanin en inceldigi alt kenari
                # hic denetlenmiyordu.
                if not (0 <= xx < sinir[0] and 0 <= yy < sinir[1]):
                    continue
                r, g, b, a = px[xx, yy]
                dusuk = min(dusuk, a)
                if a < TABAN * 255:
                    altta += 1
                for yz in adaylar:
                    en_kotu = min(en_kotu, kontrast(yz, (r, g, b)))
                n += 1
        rapor.append({'ad': ad, 'dusuk': dusuk / 255.0,
                      'delik': altta / max(1, n), 'kontrast': en_kotu,
                      'yazi': adaylar[0] if adaylar else None})
    return rapor


# ══ 5. DISARI: VARLIKLAR + CSS ══════════════════════════════════════════

def yogun_uc(im, dikey):
    """Boyanin yuklu oldugu uc. Supurme oradan baslamali: ters yonden
    supuren bir darbe hemen sahte gorunur, cunku firca boyayi biraktigi
    yerden tasimaya baslamaz."""
    a = im.getchannel('A')
    n = 12
    if dikey:
        dilim = [sum(a.crop((0, int(a.height * k / n), a.width,
                             int(a.height * (k + 1) / n))).tobytes()) for k in range(n)]
        return 'ust' if sum(dilim[:n // 2]) >= sum(dilim[n // 2:]) else 'alt'
    dilim = [sum(a.crop((int(a.width * k / n), 0,
                         int(a.width * (k + 1) / n), a.height)).tobytes()) for k in range(n)]
    return 'sol' if sum(dilim[:n // 2]) >= sum(dilim[n // 2:]) else 'sag'


def disari(parcalar):
    os.makedirs(VARLIK, exist_ok=True)
    for f in os.listdir(VARLIK):
        if f.endswith('.webp'):
            os.remove(os.path.join(VARLIK, f))

    satirlar = []
    for i, p in enumerate(parcalar, 1):
        g = p['gorsel']
        kutu = g.getchannel('A').getbbox()
        if not kutu:
            continue
        kirpik = g.crop(kutu)
        # Gorunur sag uc: alfasi esigin ustune cikan en sagdaki sutun.
        # Dosya alfa>0'a gore kirpiliyor (dogru, kuyruk da boyadir) ama
        # kagida ne kadar yer acilacagi GORUNEN boyaya gore olculmeli.
        gk = (kirpik.getchannel('A')
              .point(lambda v: 255 if v >= GORUNUR_ESIK else 0).getbbox())
        gsag = kutu[0] + (gk[2] if gk else kirpik.width)
        ad = 'panel-%d.webp' % i
        kirpik.save(os.path.join(VARLIK, ad), 'WEBP', quality=80, method=6, exact=True)
        dikey = kirpik.height > kirpik.width * 1.25
        satirlar.append({
            'dosya': 'assets/firca/' + ad,
            # Menu kutusuna gore; pay cikariliyor, bu yuzden negatif
            # deger normaldir ve darbenin kutu disina tastigini gosterir.
            'sol': round((p['ox'] + kutu[0] - PAY_SOL) / EN * 100, 2),
            'ust': round((p['oy'] + kutu[1] - PAY_UST) / BOY * 100, 2),
            'en': round(kirpik.width / EN * 100, 2),
            'boy': round(kirpik.height / BOY * 100, 2),
            'sag_gor': round((p['ox'] + gsag - PAY_SOL) / EN * 100, 2),
            'yon': yogun_uc(kirpik, dikey),
            'bayt': os.path.getsize(os.path.join(VARLIK, ad)),
        })
    return satirlar


def taban_uret():
    """Yazinin altindaki opak zemin. Boya gelmezse okunurluk buna kaliyor.

    Butun kutuyu kaplayan bir renk DEGIL: korumali bolgenin kendisi.
    Yoksa boyanin nefes delikleri duvari degil bu zemini gosteriyor ve
    delik acmanin hicbir anlami kalmiyor.
    """
    g = guvenli_bolge()                      # 255 = guvenli, 0 = korumali
    koru = g.point(lambda v: 255 - v)        # korumali bolge
    kutu = koru.getbbox()
    if not kutu:
        return None
    koru = koru.crop(kutu)
    renk = fr(0.5)
    im = Image.new('RGBA', koru.size, renk + (0,))
    im.putalpha(koru)
    ad = 'taban.webp'
    im.save(os.path.join(VARLIK, ad), 'WEBP', quality=86, method=6, exact=True)
    return {'dosya': 'assets/firca/' + ad,
            'sol': round((kutu[0] - PAY_SOL) / EN * 100, 2),
            'ust': round((kutu[1] - PAY_UST) / BOY * 100, 2),
            'en': round(koru.width / EN * 100, 2),
            'boy': round(koru.height / BOY * 100, 2),
            'bayt': os.path.getsize(os.path.join(VARLIK, ad))}


def css_yaz(satirlar, taban=None):
    p = ['/* URETILDI - python firca.py. Elle duzenleme: yerlesim olculerek',
         '   bulunuyor, elle degistirilirse yazi altindaki opaklik garantisi',
         '   bozulur. Kaynak: firca.py YERLESIM. */']
    # Sag tasma: panel kutusunun disina TASAN gorunur boya, kutu eninin
    # orani olarak. Iki tuketici de bunu okuyor -- kabuk.css kirpmayi,
    # kabuk.js kagida acilacak boslugu. Onceden ikisi de ayri ayri
    # tahminle yaziliydi (40 px ve 56 px) ve ikisi de yanlisti: gercek
    # tasma kutu eninin ~%30'u, yani kirpma boyayi duz bir dikey cizgi
    # halinde kesiyordu.
    tasma = max(0.0, max(r['sag_gor'] for r in satirlar) - 100.0) / 100.0
    p.append('#boya {')
    p.append('  --darbe: %d;        /* kabuk.js kac <i> uretecegini buradan okuyor */'
             % len(satirlar))
    p.append('  --tasma-oran: %.4f; /* olculdu: gorunur boya kutunun %%%.1f\'i kadar tasiyor */'
             % (tasma, tasma * 100))
    p.append('}')
    # Satir renk parametreleri de buradan cikiyor: ayni sayilar hem
    # olcumde (firca.py) hem calisan kodda (kabuk.js/paintMenu) gecerli
    # olmak zorunda. Iki yerde elle tutulsaydi ilk degisiklikte ayrisir
    # ve olcum artik gercegi olcmez olurdu.
    p.append(':root { --satir-doygunluk: %.2f; --satir-parlaklik: %.2f;'
             ' --satir-adim: %.3f; }' % (SAT_TAVAN, LIG_TABAN, LIG_ADIM))
    # Murekkepler: kabuk.css bunlari okuyor. Elle yazilsalardi olcum ile
    # gercek yine ayrisirdi -- bu hataya bir kez dusuldu.
    p.append(':root {')
    for ad in sorted(MUREKKEP):
        p.append('  --m-%s: #%02x%02x%02x;' % ((ad,) + MUREKKEP[ad]))
    # Panelin TABAN rengi: boya (webp) gelmezse panel bununla okunur
    # kaliyor. Paletin ortasindan aliniyor, yani panel rengi degisince
    # taban da kendiliğinden degisiyor.
    orta = fr(0.5)
    p.append('  --panel-taban: #%02x%02x%02x;' % orta)
    # Iki vurgu murekkebi. ALTINLAR olcumde kullaniliyordu ama buraya
    # HIC YAZILMIYORDU: kabuk.css'te #f2dea8 / #ecd8c4 elle duruyordu,
    # yani olcum bir rengi olcerken calisan kod baskasini kullaniyordu.
    # Ayni hata sinifi ucuncu kez (once satir parlakligi, sonra dil
    # dugmesi opakligi, simdi bu). Artik tek kaynak.
    p.append('  --m-cikis: #%02x%02x%02x;' % ALTINLAR[0])
    p.append('  --m-ozel: #%02x%02x%02x;' % ALTINLAR[1])
    # Kapatma dugmesinin cizgileri. Eskiden paletin en koyu ucundan
    # aliniyordu cunku cizgiler BEYAZ bir dairenin uzerindeydi ve palet
    # koyuydu. Panel krem olunca ikisi de degisti: beyaz daire gorunmez
    # oldugu icin kaldirildi, cizgiler artik dogrudan boyanin uzerinde.
    # Yani renk paletten degil MUREKKEP tablosundan gelmeli -- ki olcum
    # de tam olarak o rengi olcuyor.
    p.append('  --m-kapat-cizgi: #%02x%02x%02x;' % MUREKKEP['kapat'])
    p.append('}')
    # Konum ve gorsel her zaman gecerli; ANIMASYON yalnizca menu acikken
    # tanimli. Yoksa animasyon sayfa yuklenirken kosuyor ve menu acildiginda
    # coktan bitmis oluyor -- olculdu: acilistan 80 ms sonra darbe %99
    # tamamlanmisti. Secici acik duruma baglaninca animasyon o anda
    # olusuyor, yani supurme acilisla birlikte basliyor.
    if taban:
        p.append('/* Yazinin altindaki opak zemin. Butun kutuyu kaplamiyor:')
        p.append('   yalnizca yazi bolgesi, yoksa boyanin nefes delikleri')
        p.append('   duvari degil bu zemini gosterir. */')
        p.append('#boya::before {')
        p.append('  content: ""; position: absolute; pointer-events: none;')
        p.append('  left: %.2f%%; top: %.2f%%; width: %.2f%%; height: %.2f%%;'
                 % (taban['sol'], taban['ust'], taban['en'], taban['boy']))
        p.append('  background: url(%s) 0 0 / 100%% 100%% no-repeat;'
                 % taban['dosya'])
        p.append('}')
    p.append('#boya i { animation-duration: %dms;'
             ' animation-timing-function: %s; }' % (SURE, FIRCA_EGRI))
    for i, r in enumerate(satirlar, 1):
        p.append('#boya i:nth-child(%d) {' % i)
        p.append('  left: %.2f%%; top: %.2f%%; width: %.2f%%; height: %.2f%%;'
                 % (r['sol'], r['ust'], r['en'], r['boy']))
        p.append('  background-image: url(%s);' % r['dosya'])
        p.append('}')
        # AYRI kurallar. Tek seciciye ":popover-open, .open" yazmak,
        # seciciyi tanimayan tarayicida kuralin TAMAMINI dusuruyor ve
        # yedek yol icin yazilan dal da gidiyor.
        gec = GECIKMELER[min(i - 1, len(GECIKMELER) - 1)]
        for durum in (':popover-open', '.open'):
            p.append('#menu%s #boya i:nth-child(%d) {' % (durum, i))
            p.append('  animation-name: sup-%s; animation-delay: %dms;'
                     % (r['yon'], gec))
            p.append('}')
    io.open(CSS_YOL, 'w', encoding='utf-8', newline='\n').write('\n'.join(p) + '\n')


def main():
    if not os.path.isdir(HAM):
        raise SystemExit('ham fotograf klasoru yok: ' + HAM)
    os.makedirs(OLCUM, exist_ok=True)

    print('darbeler ayikliniyor...')
    darbeler = {}
    for ad, dosya in SECIM:
        a = darbeyi_al(dosya)
        if a is None:
            raise SystemExit('darbe cikarilamadi: ' + dosya)
        darbeler[ad] = a
        print('  %-12s %-14s %4dx%d' % (ad, dosya.replace('.jpg', ''), a.width, a.height))

    panel, parcalar = kur(darbeler)
    rapor = olc(panel)

    print('\n%-14s %9s %8s %10s  %s'
          % ('yazi kutusu', 'en dusuk', 'delik', 'kontrast', 'yazi rengi'))
    kalan = 0
    for r in rapor:
        tamam = r['dusuk'] >= TABAN and r['kontrast'] >= KONTRAST_TABAN
        kalan += 0 if tamam else 1
        print('%-14s %8.0f%% %7.2f%% %10s  %-7s  %s'
              % (r['ad'], r['dusuk'] * 100, r['delik'] * 100,
                 '--' if r['yazi'] is None else '%.2f:1' % r['kontrast'],
                 '(gorsel)' if r['yazi'] is None
                 else '#%02x%02x%02x' % r['yazi'],
                 'tamam' if tamam else 'KALDI'))

    ic_oran, ic_kutu = ic_kontrol(panel, guvenli=guvenli_bolge())
    if ic_kutu:
        print('IC DELIK  %.2f%%  kutu x%d..%d  y%d..%d'
              % (ic_oran * 100, ic_kutu[0], ic_kutu[2], ic_kutu[1], ic_kutu[3]))
    else:
        print('ic delik  yok')

    kutu_alfa = panel.getchannel('A').crop(
        (PAY_SOL, PAY_UST, PAY_SOL + EN, PAY_UST + BOY))
    kapla = sum(1 for v in kutu_alfa.tobytes() if v > 20) / float(EN * BOY)
    print('\npanel kaplama %.0f%%   kalan kutu %d/%d' % (kapla * 100, kalan, len(rapor)))

    # IKINCI YUKSEKLIK. Butun garanti 857 px'lik tek bir gorunume
    # cakiliydi; #menu artik 100dvh ve darbeler yuzde konumlu, yani
    # daha uzun ekranda boya geriliyor ama yazi yerinde kaliyor.
    ikinci = 980
    rapor2 = gerilmis_olc(panel, ikinci)
    kalan2 = sum(1 for r in rapor2
                 if r['dusuk'] < TABAN or r['kontrast'] < KONTRAST_TABAN)
    print('%d px yukseklikte  kalan kutu %d/%d' % (ikinci, kalan2, len(rapor2)))
    if kalan2:
        for r in rapor2:
            if r['dusuk'] < TABAN or r['kontrast'] < KONTRAST_TABAN:
                print('   %-12s opaklik %.0f%%  kontrast %.2f:1'
                      % (r['ad'], r['dusuk'] * 100, r['kontrast']))

    # KAPI IHRACTAN ONCE. Eskiden disari()+css_yaz() bu kontrolden once
    # kosuyordu: olcum dusse bile varliklar diske yaziliyordu.
    if kalan or kalan2 or ic_oran > 0.001:
        raise SystemExit('HATA: %d kutu (857px), %d kutu (%dpx), ic delik %%%.2f'
                         ' -- VARLIKLAR YAZILMADI'
                         % (kalan, kalan2, ikinci, ic_oran * 100))

    satirlar = disari(parcalar)
    print('sag tasma        %%%5.1f  (gorunur alfa >= %d)'
          % (max(r['sag_gor'] for r in satirlar) - 100.0, GORUNUR_ESIK))
    taban = taban_uret()
    css_yaz(satirlar, taban)
    if taban:
        print('taban.webp        %5.1f%% x %5.1f%%  %6d bayt'
              % (taban['en'], taban['boy'], taban['bayt']))

    print('\n%-16s %8s %8s %8s %8s %7s %8s'
          % ('darbe', 'sol', 'ust', 'en', 'boy', 'yon', 'bayt'))
    for i, r in enumerate(satirlar, 1):
        print('%-16s %7.1f%% %7.1f%% %7.1f%% %7.1f%% %7s %8d'
              % (os.path.basename(r['dosya']), r['sol'], r['ust'], r['en'],
                 r['boy'], r['yon'], r['bayt']))
    print('\ntoplam %d KB   ->  %s  +  firca.css'
          % (sum(r['bayt'] for r in satirlar) // 1024, VARLIK))

    # gorsel dogrulama ciktilari (kaynak/ depoya girmiyor)
    zem = os.path.join(KOK, 'varlik', 'zemin', 'galeri.webp')
    tab = (Image.open(zem).convert('RGB').resize((EN + 340, BOY), Image.LANCZOS)
           if os.path.exists(zem) else Image.new('RGB', (EN + 340, BOY), (28, 26, 30)))
    tab.paste(panel, (0, 0), panel)
    tab.save(os.path.join(OLCUM, 'panel.png'))




if __name__ == '__main__':
    main()
