# -*- coding: utf-8 -*-
"""Şablon HTML + eser verisi -> yayına hazır tek dosya.

Kullanım:  python build.py <sablon.html> <cikti.html>

Şablonda   /*__SITE_DATA__*/   token'ı bulunur; yerine `const SITE = {...}` yazılır.
Base64 görseller asla şablonda durmaz — böylece tasarım dosyası okunabilir kalır.
"""
import json, re, sys, io, os, base64
from PIL import Image, ImageFilter
import ceviri as T
import site_veri as V

HERE = os.path.dirname(os.path.abspath(__file__))

TR_MAP = str.maketrans({
    'ç': 'c', 'ğ': 'g', 'ı': 'i', 'ö': 'o', 'ş': 's', 'ü': 'u',
    'Ç': 'c', 'Ğ': 'g', 'İ': 'i', 'Ö': 'o', 'Ş': 's', 'Ü': 'u', 'I': 'i',
})


def slugify(s):
    s = s.translate(TR_MAP).lower()
    return re.sub(r'[^a-z0-9]+', '-', s).strip('-')


def cm_pair(dim):
    """'76.2 × 115.2 cm (30 × 45 in.)' -> (76, 115)  [yükseklik, genişlik]"""
    m = re.search(r'([\d.]+)\s*[×x]\s*([\d.]+)\s*cm', dim or '')
    if not m:
        return None, None
    return round(float(m.group(1))), round(float(m.group(2)))


# inches() KALDIRILDI: santimi adi kesirle inc'e ceviriyordu (muze
# kunyesi gelenegi) ama musteri inc istemiyor. Tek cagiran yeri de
# (works[].sizeIn) kalkti.


# Seri bazlı, deterministik yıl ataması — çağdaş bir ressamın külliyatı gibi okunsun.
SERIES_YEARS = {
    'alacakaranlik': [2024, 2023, 2023, 2022, 2021],
    'hava':          [2023, 2022, 2021, 2019],
    'topografya':    [2024, 2023, 2022, 2020, 2018],
    'sabah':         [2024, 2023, 2022, 2020],
}


ESER_DIZIN = os.path.join(HERE, 'icerik', 'eserler')
GORSEL_DIZIN = os.path.join(HERE, 'icerik', 'gorseller')
TAM_EN, TAM_KALITE, LQIP_EN, LQIP_KALITE = 1686, 78, 20, 40

# Duyarli boylar. Olculdu: tek boy (1080) her cihaza gidiyordu ve 390 px
# telefon ile 1440 px masaustu BIREBIR ayni bayti indiriyordu. Gerekli
# olanlar: izgara masaustunde 479 CSS px (DPR1), telefonda 310 CSS px x
# DPR2 = 620, isik kutusu ~970, yakinlastirma tam ekran.
# Orijinaller 1080 px oldugu icin bu uc boy hicbir buyutme yapmiyor.
# En buyuk boy ayrica uretilmiyor: ana dosya (eser-N.webp) zaten
# orijinal olcude ve isik kutusu/yakinlastirma onu kullaniyor. Ikinci kez
# yazilinca site/ 2.54 MB'dan 3.69 MB'a cikmisti -- ayni gorsel iki kez.
DUYARLI_BOYLAR = (540, 810)

# Ana sayfada gosterilen eserler artik icerik/site.json'da (ana_sayfa):
# ressam panelden seciyor. Hem sayfa hem paylasim gorseli oradan okuyor --
# og:image bir kez elle yazilmisti ve silinmis bir esere bakip 404
# vermisti.


def yorumsuz(metin, dil):
    """TAM SATIR yorumlarini dusurur. Satir ici yorumlara DOKUNMAZ.

    Neden naif degil: bir dizge ya da regex icindeki `/*` veya `//`
    dizisi naif bir siyiriciyi bozar (`'http://x'` gibi). Belirtecleyici
    yazmak yerine yalniz satirin BASINDA baslayan yorumlar kaldiriliyor
    -- oyle bir satir kod olamaz. Kazancin neredeyse tamami zaten tam
    satir bloklarda: kabuk.css 38.221 -> 12.469 bayt.

    dil: 'css' yalniz /* */ bloklarini, 'js' ayrica // satirlarini alir.
    """
    cikti = []
    blokta = False
    for satir in metin.split('\n'):
        kirp = satir.strip()
        # DERLEME BELIRTECLERI yorum bicimindedir
        # (/*__FIRCA_CSS__*/) ve bu siyirici onlari YEDI:
        # firca.css hic gomulmedi, --darbe kayboldu, kabuk.js tek
        # <i> uretmedi, yani menude hic boya kalmadi. Yayina da
        # gitti. Belirtec = icinde __ olan yorum; aynen korunuyor.
        if '__' in kirp and kirp.startswith('/*'):
            cikti.append(satir.rstrip())
            continue
        if blokta:
            if '*/' in kirp:
                blokta = False
                # Kapanistan SONRA kod varsa satiri koru.
                kalan = kirp.split('*/', 1)[1].strip()
                if kalan:
                    cikti.append(kalan)
            continue
        if kirp.startswith('/*'):
            if '*/' not in kirp:
                blokta = True
                continue
            kalan = kirp.split('*/', 1)[1].strip()
            if kalan:
                cikti.append(satir.split('*/', 1)[1].rstrip())
            continue
        if dil == 'js' and kirp.startswith('//'):
            continue
        if not kirp:
            # Bos satirlar da dusuyor: yorumlar gidince geride
            # bosluk yiginlari kaliyor.
            continue
        cikti.append(satir.rstrip())
    return '\n'.join(cikti)


def html_kacir(s):
    """HTML metni ve nitelik degeri icin."""
    return (str(s).replace('&', '&amp;').replace('<', '&lt;')
            .replace('>', '&gt;').replace('"', '&quot;'))


def _kodla(im, en, kalite, bulanik=0):
    """Gorseli webp'e cevirip base64 dondurur."""
    k = im.copy()
    k.thumbnail((en, en * 10), Image.LANCZOS)
    if bulanik:
        k = k.filter(ImageFilter.GaussianBlur(bulanik))
    b = io.BytesIO()
    k.save(b, 'WEBP', quality=kalite, method=6)
    return base64.b64encode(b.getvalue()).decode()


def _baskin_renk(im):
    k = im.copy(); k.thumbnail((1, 1))
    r, g, b = k.convert('RGB').getpixel((0, 0))
    return f'#{r:02x}{g:02x}{b:02x}'


def eserleri_oku():
    """icerik/eserler/*.json -> sira'ya gore listelenmis kayitlar.

    Panelin yazdigi tek yer burasi. Bozuk bir kayit sessizce gecmesin diye
    zorunlu alanlar burada denetleniyor: eksikse derleme DURUR, yarim bir
    site yayinlanmaz.
    """
    if not os.path.isdir(ESER_DIZIN):
        return []
    kayitlar = []
    for ad in sorted(os.listdir(ESER_DIZIN)):
        if not ad.endswith('.json'):
            continue
        yol = os.path.join(ESER_DIZIN, ad)
        try:
            k = json.load(io.open(yol, encoding='utf-8'))
        except Exception as e:
            sys.exit(f'BOZUK KAYIT {ad}: {e}')
        # olcu ve yil ZORUNLU DEGIL. Musterinin gercek eserleri geldi ama
        # kunye bilgileri (ad, yil, olcu) henuz gelmedi. Bunlari uydurmak
        # prototipi gorene gercek olcu gibi gorunur; o yuzden bos kalabilir
        # ve arayuz eksik alani hic basmaz.
        for alan in ('slug', 'baslik', 'seri', 'gorsel'):
            if not k.get(alan):
                sys.exit(f'{ad}: zorunlu alan eksik -> {alan}')
        o = k.get('olcu') or {}
        if o and (not o.get('yukseklik_cm') or not o.get('genislik_cm')):
            sys.exit(f'{ad}: olcu yarim (yukseklik_cm / genislik_cm)')
        if not os.path.exists(os.path.join(GORSEL_DIZIN, k['gorsel'])):
            sys.exit(f'{ad}: gorsel bulunamadi -> icerik/gorseller/{k["gorsel"]}')
        # Panelde "Gizle" denmis eser: kayit ve gorsel depoda duruyor,
        # sitede hicbir yerde yok. Silmeden kaldirmanin yolu.
        if k.get('gizli'):
            continue
        kayitlar.append(k)
    kayitlar.sort(key=lambda k: (k.get('sira') or 999, k['slug']))
    return kayitlar


def build_data():
    S = V.oku()
    UI = V.arayuz(S, T.UI)
    seri_anahtarlari = [x['anahtar'] for x in S['seriler']]
    works = []
    for idx, k in enumerate(eserleri_oku()):
        # Silinmis bir seriye bakan eser derlemeyi durdurmuyor: ilk seriye
        # dusuyor. Panel seriyi silerken eserlerini zaten tasiyor; bu
        # yalniz elle duzenlenmis kayitlar icin emniyet.
        if k['seri'] not in seri_anahtarlari:
            print(f'UYARI  {k["slug"]}: seri yok ({k["seri"]}), '
                  f'"{seri_anahtarlari[0]}" serisine kondu.')
            k['seri'] = seri_anahtarlari[0]
        im = Image.open(os.path.join(GORSEL_DIZIN, k['gorsel'])).convert('RGB')
        o0 = k.get('olcu') or {}
        olcu_var = bool(o0.get('yukseklik_cm') and o0.get('genislik_cm'))
        if olcu_var:
            ch = int(o0['yukseklik_cm'])
            cw = int(o0['genislik_cm'])
        else:
            # Olcu bilinmiyor. Duzen gene bir sayi istiyor (tuval gercek
            # cm'den ciziliyor); fotografin kendi oranindan nominal bir
            # kutu turetiliyor. Bu sayi HICBIR YERDE BASILMIYOR -- yalnizca
            # yerlesim icin. Uzun kenar 120 kabul ediliyor.
            if im.width >= im.height:
                cw, ch = 120, max(1, round(120 * im.height / im.width))
            else:
                ch, cw = 120, max(1, round(120 * im.width / im.height))
        # Bolunmez bosluk: mobilde olcu "83 × 132 / CM | 32⅝ × 52 in" diye
        # ortadan kopuyordu. Bir olcu ifadesi hicbir zaman ikiye ayrilmamali.
        NB = '\u00a0'
        kol = (k.get('koleksiyon') or {})
        ortam = (k.get('ortam_gorseli') or '').strip()

        # Kunye olcusu ile fotografin orani uyusmuyor mu? Artik EKRANDA
        # bir sey bozmuyor -- galeri gorseli kendi oraninda ciziyor, ne
        # kirpiyor ne geriyor (bkz. sergi.html .tuval). Ama sayilardan
        # biri yanlis demektir: ya olcu yanlis girilmis ya fotograf
        # kirpilmis. Ikisi de sessiz gecmemeli, cunku olcu satiri
        # koleksiyonerin okudugu bir iddia.
        bek, ger = cw / ch, im.width / im.height
        if olcu_var and abs(ger - bek) / bek > 0.03:
            ima = round(ch * ger)
            print(f'UYARI  {k["slug"]}: fotograf orani {ger:.3f}, kunye '
                  f'{cw}x{ch} cm ({bek:.3f}) -- %{abs(ger-bek)/bek*100:.0f} '
                  f'sapma. Fotografa gore {ch} cm yuksekligin karsiligi '
                  f'{ima} cm genislik.')

        works.append({
            'id':     k['slug'],
            'no':     f'{idx + 1:02d}',
            'slug':   k['slug'],
            'title':  k['baslik'],
            'series': k['seri'],
            'note':   (k.get('not') or {}).get('tr', ''),
            'status': k['durum'],
            'collection': kol.get('ad') or '',
            'collYear':   kol.get('yil') or 0,
            'year':   int(k['yil']) if k.get('yil') else 0,
            'medium': UI['tr']['medium'],
            # Olcu yoksa BOS. Arayuz bos olcuyu hic basmiyor.
            # INC KARSILIGI KALDIRILDI (musteri karari: "inc ibarelerini
            # kaldir her yerden"). Alti yerde basiliyordu; uretimi de
            # kalkti, yoksa okunmayan bir alan uretilmeye devam ederdi.
            'size':   f'{ch}{NB}×{NB}{cw}{NB}cm' if olcu_var else '',
            'taslak': bool(k.get('taslak')),
            'cw':     cw,
            'ch':     ch,
            'area':   cw * ch,
            'ratio':  round(im.width / im.height, 4),
            'px':     [im.width, im.height],
            'portrait': im.width < im.height,
            'tone':   _baskin_renk(im),
            'lqip':   'data:image/webp;base64,' + _kodla(im, LQIP_EN, LQIP_KALITE, 1),
            'src':    'data:image/webp;base64,' + _kodla(im, TAM_EN, TAM_KALITE),
            'ortam':  '',
            # Sergi karesinin kendi orani: hero onu 4:3'e ya da eserin
            # oranina zorlamasin diye gerekiyor.
            'ortamRatio': (lambda p: round(Image.open(p).width /
                                           Image.open(p).height, 4))(
                os.path.join(GORSEL_DIZIN, ortam))
                if ortam and os.path.exists(
                    os.path.join(GORSEL_DIZIN, ortam)) else 0,
            'ortamSrc': ('data:image/webp;base64,' + _kodla(
                Image.open(os.path.join(GORSEL_DIZIN, ortam)).convert('RGB'),
                TAM_EN, TAM_KALITE)) if ortam and os.path.exists(
                    os.path.join(GORSEL_DIZIN, ortam)) else '',
            'credit': k.get('kaynak_kredisi', ''),
            '_gloss': k.get('gloss') or {},
            '_not':   k.get('not') or {},
        })

    # ── seri yıl aralıkları ESERLERDEN türetiliyor ──────────────────────
    # Elle yazılıydı ve eser kümesi değişince bayatlıyordu: content.SERIES
    # "2018 — 2024" diyordu, seride en eski eser 2022'ydi; dört serinin dördü
    # de yanlıştı. Artık kaynak tek — eserlerin kendi yılları.
    seriler = [{'key': x['anahtar'], 'title': V.dilde(x['ad'], 'tr'),
                'years': '', 'blurb': V.dilde(x['aciklama'], 'tr')}
               for x in S['seriler']]
    for sr in seriler:
        yillar = sorted({w['year'] for w in works if w['series'] == sr['key'] and w['year']})
        if yillar:
            sr['years'] = (str(yillar[0]) if len(yillar) == 1
                           else f'{yillar[0]} — {yillar[-1]}')
    # Eseri olmayan seri menude bos bir satir olurdu (panelden yeni acilmis
    # ya da eserleri gizlenmis seri). En az bir seri her zaman kalir.
    seriler = [sr for sr in seriler if any(w['series'] == sr['key'] for w in works)] or seriler[:1]

    sn = S['sanatci']
    i18n = build_i18n(S, UI, works)
    tr = i18n['tr']
    data = {
        # Arayuzun okudugu adlar (name/email/studio) korunuyor; kaynak
        # site.json'daki Turkce alan adlari.
        'artist':       {'name': sn['ad'], 'mark': sn['ad'], 'email': sn['eposta'],
                         'phone': sn['telefon'], 'studio': sn['adres'],
                         'instagram': sn['instagram']},
        'bio':          tr['bio'],
        'cv':           tr['cv'],
        'collections':  tr['collections'],
        'publications': tr['publications'],
        'press':        tr['press'],
        'statement':    tr['statement'],
        'series':       seriler,
        'works':        works,
        'i18n':         i18n,
        # render() bunlari sayfa verisine yazmadan once cekip aliyor.
        '_ana':         S['ana_sayfa'],
        '_belirtec':    {'__AD__': sn['ad'], '__ALT__': UI['tr']['site_sub'],
                         '__META__': UI['tr']['meta_desc'],
                         '__TEKNIK__': UI['tr']['medium'],
                         '__ESERLER__': UI['tr']['gal_works']},
    }

    # Sayfa zeminleri: ressamın kendi tablolarından makro kırpıntılar (zemin.py).
    # Yoksa site tek renk zeminle çalışır.
    zp = os.path.join(HERE, 'zeminler.json')
    data['backdrops'] = json.load(io.open(zp, encoding='utf-8')) if os.path.exists(zp) else {}
    return data


# Sergi satirinin tanimlayicisi. Arayuz kisisel/karma ayrimini Turkce
# satirin basindan okuyor (mekan.html viewSergiler); yabanci dillerde
# ceviri.DESCRIPTORS karsiligi yaziliyor.
SERGI_TR = {'kisisel': 'Kişisel sergi', 'karma': 'Karma sergi'}


def build_i18n(S, UI, works):
    """Her dil için sayfa metinleri. Kaynak icerik/site.json.

    Bir metin o dilde boşsa ilk dolu dile düşer (site_veri.dilde): ressam
    yalnız Fransızca yazdıysa Türkçe sayfa boş kalmıyor.
    Eser adı ve ölçüler her dilde aynı kalır — ad bir isimdir, ölçü bir olgudur.
    """
    out = {}
    for lang in V.DILLER:
        cv = []
        for x in S['sergiler']:
            tanim = SERGI_TR[x['tur']]
            if lang != 'tr':
                tanim = T.DESCRIPTORS[tanim][lang]
            cv.append([x['yil'], x['ad'], tanim + (' · ' + x['yer'] if x['yer'] else '')])
        out[lang] = {
            'ui':           UI[lang],
            'bio':          V.paragraflar(V.dilde(S['biyografi'], lang)),
            'statement':    V.paragraflar(V.dilde(S['atolye_notu'], lang)),
            'collections':  list(S['koleksiyonlar']),
            'series':       {x['anahtar']: {'title': V.dilde(x['ad'], lang),
                                            'blurb': V.dilde(x['aciklama'], lang)}
                             for x in S['seriler']},
            # Eser adi CEVRILMEZ; gloss adin altinda duran aciklayici karsilik.
            'works':        {w['id']: {'gloss': '' if lang == 'tr' else w['_gloss'].get(lang, ''),
                                       'note': w['_not'].get(lang) or w['_not'].get('tr', '')}
                             for w in works},
            'cv':           cv,
            'publications': [[x['yil'], x['ad'], V.dilde(x['aciklama'], lang)]
                             for x in S['yayinlar']],
            'press':        [[x['yil'], x['baslik'], V.dilde(x['kunye'], lang)]
                             for x in S['basin']],
        }
    return out


STANDALONE_OPEN = '''<!doctype html>
<html lang="tr">
<head>
'''
STANDALONE_TAIL = '<style>img{max-width:100%}[hidden]{display:none!important}</style>\n'
VIEWPORT = '<meta name="viewport" content="width=device-width, initial-scale=1">\n'


def write_assets(data, out_dir):
    """Gömülü base64'ü ayrı .webp dosyalarına çıkarır ve src'leri yola çevirir.

    Artifact'te CSP dış görseli engellediği için gömmek zorundaydık; gerçek
    sunucuda gerek yok. Sayfa 2.8 MB yerine ~35 KB iniyor, görseller tembel
    ve önbelleklenebilir yükleniyor.
    """
    adir = os.path.join(out_dir, 'assets')
    os.makedirs(adir, exist_ok=True)
    total = 0
    for w in data['works']:
        raw = base64.b64decode(w['src'].split(',', 1)[1])
        name = f"{w['id']}.webp"
        with open(os.path.join(adir, name), 'wb') as f:
            f.write(raw)
        total += len(raw)
        w['src'] = 'assets/' + name          # lqip veri-URI kalır: 160 bayt, istek yok

        # Duyarli boylar. Kucultme ORIJINALDEN yapiliyor; gomulu webp'den
        # yapilsa ikinci bir kayipli kodlama olurdu. Orijinal bulunamazsa
        # (gomulu derleme, elle konmus varlik) srcset uretilmiyor ve
        # sayfa tek boyla calismaya devam ediyor.
        kaynak = None
        for uz in ('.jpg', '.jpeg', '.png', '.webp', '.JPG', '.JPEG'):
            aday = os.path.join(GORSEL_DIZIN, w['id'] + uz)
            if os.path.exists(aday):
                kaynak = aday
                break
        if kaynak:
            with Image.open(kaynak) as ana:
                ana = ana.convert('RGB')
                parcalar = []
                for boy in DUYARLI_BOYLAR:
                    if boy > ana.width:
                        continue
                    k = ana.copy()
                    k.thumbnail((boy, boy * 10), Image.LANCZOS)
                    ad2 = f"{w['id']}-{boy}.webp"
                    k.save(os.path.join(adir, ad2), 'WEBP',
                           quality=TAM_KALITE, method=6)
                    total += os.path.getsize(os.path.join(adir, ad2))
                    parcalar.append('assets/%s %dw' % (ad2, k.width))
                if parcalar:
                    # Ana dosya en buyuk aday: ayri bir kopya yazmaya
                    # gerek yok, zaten orijinal olcude.
                    parcalar.append('%s %dw' % (w['src'], ana.width))
                    w['srcset'] = ', '.join(parcalar)

        # Ortam gorseli (Smartist ev maketi): eserin YERINE gecmiyor, yanina
        # dusuyor. Detay sayfasinda ikinci kare olarak gosteriliyor.
        if w.get('ortamSrc'):
            ham = base64.b64decode(w['ortamSrc'].split(',', 1)[1])
            oad = f"ortam-{w['id']}.webp"
            with open(os.path.join(adir, oad), 'wb') as f:
                f.write(ham)
            total += len(ham)
            w['ortam'] = 'assets/' + oad
            # Oda kurgusu ana sayfadaki giris kartinda 310x200'e
            # ciziliyor; 1672 px'lik dosya orada gereksiz.
            okaynak = None
            for uz in ('.webp', '.jpg', '.jpeg', '.png'):
                aday = os.path.join(GORSEL_DIZIN, 'ortam-' + w['id'] + uz)
                if os.path.exists(aday):
                    okaynak = aday
                    break
            if okaynak:
                with Image.open(okaynak) as oa:
                    oa = oa.convert('RGB')
                    op = []
                    for boy in (540, 810):
                        if boy > oa.width:
                            continue
                        k = oa.copy()
                        k.thumbnail((boy, boy * 10), Image.LANCZOS)
                        ad3 = 'ortam-%s-%d.webp' % (w['id'], boy)
                        k.save(os.path.join(adir, ad3), 'WEBP',
                               quality=TAM_KALITE, method=6)
                        total += os.path.getsize(os.path.join(adir, ad3))
                        op.append('assets/%s %dw' % (ad3, k.width))
                    if op:
                        op.append('%s %dw' % (w['ortam'], oa.width))
                        w['ortamSrcset'] = ', '.join(op)
        w.pop('ortamSrc', None)
    return total


def render(tpl_path, data, standalone):
    # Gomulu derlemede write_assets calismaz ve ortam gorseli 'ortamSrc'
    # icinde kalirdi: sayfa yalnizca 'ortam' alanini okudugu icin gorunmezdi
    # (ustelik base64 bosuna sayfaya gomulurdu).
    for w in data['works']:
        veri = w.pop('ortamSrc', None)
        if veri and not w.get('ortam'):
            w['ortam'] = veri
    # Salon kurgusu ARTIK HERO DEGIL (musteri karari: ana sayfada
    # eserin kendisi duruyor). Kaynak varlik/hero altinda kaliyor ama
    # yayina kopyalanmiyor (bkz. yayinla.py ATLA).
    # Ana sayfa eserleri: sirasi site.json'dan (panel), verisi works'ten.
    # Silinmis ya da gizlenmis bir eser listede kaldiysa derleme DURMUYOR,
    # o eser atlaniyor: ressam bir eseri silince site yayinlanamaz hale
    # gelmemeli. Hic kalmazsa ilk eser ana sayfaya cikar.
    _hepsi = {w['slug']: w for w in (data.get('works') or [])}
    ana = data.pop('_ana', [])
    data['anaEserler'] = [s for s in ana if s in _hepsi]
    for s in ana:
        if s not in _hepsi:
            print('UYARI  ana sayfa eseri sitede yok (silinmis/gizli) -> ' + s)
    if not data['anaEserler'] and data.get('works'):
        data['anaEserler'] = [data['works'][0]['slug']]

    belirtec = data.pop('_belirtec', {})
    tpl = io.open(tpl_path, encoding='utf-8').read()
    for token in ('/*__SITE_DATA__*/', '/*__KIT__*/'):
        if token not in tpl:
            sys.exit(f'HATA: {tpl_path} içinde {token} yok.')
    # Ad ve site yazilari sablonun basliginda / meta'sinda (panelden
    # degisiyor). Sayfa verisinden ONCE yerlestiriliyor: kullanici metni
    # icinde tesadufen bir belirtec gecse bile ikinci kez degismesin.
    for k, v in belirtec.items():
        tpl = tpl.replace(k, html_kacir(v))

    payload = 'const SITE = ' + json.dumps(data, ensure_ascii=False, separators=(',', ':')) + ';'
    # Yorumlar KAYNAKTA kaliyor, derlemede dusuyor. Olculdu: kit.js
    # 7.894 -> 5.539, kabuk.css 36.274 -> 12.758, kabuk.js 33.100 ->
    # 16.700 bayt. Bu belge render'i blokeleyen tek kaynak.
    kit = yorumsuz(io.open(os.path.join(HERE, 'kit.js'),
                           encoding='utf-8').read(), 'js')
    out = tpl.replace('/*__KIT__*/', kit).replace('/*__SITE_DATA__*/', payload)

    # Paylasim gorseli. Elle yazilinca sessizce kirildi: silinmis bir
    # esere bakiyordu, yani paylasilan her link bos kart aciyordu ve
    # hicbir sey hata vermiyordu. Artik ilk eserin ORTAM gorselinden
    # uretiliyor (oda kurgusu duz eserden daha iyi kart veriyor ve
    # 1672x941 ile og:image'in 1200x630 alt sinirini gecen tek olcu o),
    # kok URL de sablonun kendi canonical'indan okunuyor. Eksik olan
    # her sey derlemeyi DURDURUYOR -- kusurun sebebi bu denetimin
    # olmamasiydi.
    if '__OG_GORSEL__' in out:
        m = re.search(r'<link rel="canonical" href="([^"]+)"', out)
        if not m:
            sys.exit('HATA: canonical yok, paylasim gorseli uretilemedi.')
        kok_url = m.group(1).rstrip('/')
        # PAYLASIM GORSELI HERO. Once ilk eserin oda kurgusuydu; tek
        # eser sitenin tamamini temsil etmiyor. Hero sekiz eseri ayni
        # mekanda gosteriyor, yani paylasilan link sanatcinin isini
        # topluca gosteriyor. Hero yoksa yine ilk esere dusuyor.
        # Paylasim gorseli: ana sayfanin ILK eseri. Salon kurgusu artik
        # kullanilmadigi icin ondan aliniyordu, simdi sayfanin gercekten
        # gosterdigi seyden aliniyor. Tam olcu (srcset'in en buyugu
        # degil, ana dosya) -- 1080 px genislik og:image icin yeterli.
        isler = data.get('works') or []
        _hepsi2 = {w['slug']: w for w in isler}
        _ilk = _hepsi2.get((data.get('anaEserler') or [None])[0])
        yol = _ilk.get('src') if _ilk else None
        if not yol:
            if not isler:
                sys.exit('HATA: eser yok, paylasim gorseli uretilemedi.')
            yol = isler[0].get('src')
        if not yol:
            sys.exit('HATA: paylasim gorseli uretilemedi.')
        # Denetim: gorselin KAYNAGI gercekten var mi. Kusurun sebebi
        # tam olarak bu denetimin olmamasiydi -- silinmis bir esere
        # bakan sabit bir yol kimseyi uyarmadan yayina gidiyordu.
        # Kaynak IKI yerde olabilir: eser gorselleri icerik/gorseller'de,
        # hero gibi uretilmis varliklar varlik/ altinda. Once yalniz
        # ilkine bakiliyordu ve hero'ya geciste derleme patlardi.
        temel = os.path.splitext(os.path.basename(yol))[0]
        varmi = False
        for kok in (os.path.join(HERE, 'icerik', 'gorseller'),
                    os.path.join(HERE, 'varlik')):
            if not os.path.isdir(kok):
                continue
            for dizin, _, dosyalar in os.walk(kok):
                if any(os.path.splitext(f)[0] == temel for f in dosyalar):
                    varmi = True
                    break
            if varmi:
                break
        if not varmi:
            sys.exit('HATA: paylasim gorseli kaynakta yok -> %s' % temel)
        # Varlik yolu SITE KOKUNE gore mutlak olmali. Onceden sayfanin
        # kendi canonical'i kullaniliyordu ve alt dizindeki sayfa
        # /galeri/assets/... uretip 404 veriyordu (olculdu, canlida).
        # Site koku ana sablonun canonical'i: derlenirken index.html
        # oluyor, yani tanimi geregi kok.
        ana = os.path.join(HERE, 'mekan.html')
        am = re.search(r'<link rel="canonical" href="([^"]+)"',
                       io.open(ana, encoding='utf-8').read()) \
            if os.path.isfile(ana) else None
        if not am:
            sys.exit('HATA: mekan.html canonical yok, site koku bulunamadi.')
        site_kok = am.group(1).rstrip('/')
        tam = site_kok + '/' + yol
        out = out.replace('__OG_GORSEL__', tam)
        out = out.replace(
            '<meta property="og:image" content="%s">' % tam,
            '<meta property="og:image" content="%s">%s'
            '<meta name="twitter:image" content="%s">%s'
            '<meta property="og:url" content="%s/">'
            % (tam, chr(10), tam, chr(10), kok_url), 1)

    # Kabuk: tablo zemini, hamburger, menu paneli ve beyaz kagit. Iki sayfa
    # da ayni kabugu kullaniyor; kopyalanmis olsalardi zamanla ayrisirlardi.
    # Belirteci olmayan sablon da derlenir - her sayfanin kabugu olmasi
    # gerekmiyor.
    # FIRCA_ONYUK ve FIRCA_CSS belirtecleri KALKTI: menu paneli artik duz
    # krem, indirilecek darbe yok (musteri karari). firca.py ve
    # varlik/firca depoda duruyor, yayina kopyalanmiyor.
    for belirtec, dosya in (('/*__KABUK_CSS__*/', 'kabuk.css'),
                            ('/*__KABUK_JS__*/', 'kabuk.js')):
        if belirtec in out:
            yol = os.path.join(HERE, dosya)
            if not os.path.exists(yol):
                sys.exit(f'HATA: {tpl_path} {belirtec} istiyor ama {dosya} yok.')
            dil = 'css' if dosya.endswith('.css') else 'js'
            out = out.replace(belirtec, yorumsuz(
                io.open(yol, encoding='utf-8').read(), dil))

    if standalone:
        # Artifact ortamı <html>/<head>/<body> sarmalayıcısını kendi ekliyordu.
        # Bağımsız sitede onu biz kurmalıyız: ilk </style> head'in sonudur.
        cut = out.index('</style>') + len('</style>')
        head = STANDALONE_OPEN
        if 'name="viewport"' not in out[:cut]:      # şablon kendi veriyorsa tekrarlama
            head += VIEWPORT
        head += STANDALONE_TAIL
        out = head + out[:cut] + '\n</head>\n<body>\n' + out[cut:] + '\n</body>\n</html>\n'
    return out


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    standalone = '--standalone' in sys.argv

    data = build_data()
    if standalone:
        out_dir = os.path.dirname(os.path.abspath(args[1])) or '.'
        kb = write_assets(data, out_dir) / 1024
        print(f'assets/  {len(data["works"])} webp  ·  {kb/1024:.2f} MB')

    tpl_path, out_path = args[0], args[1]
    out = render(tpl_path, data, standalone)
    io.open(out_path, 'w', encoding='utf-8').write(out)

    mb = len(out.encode('utf-8')) / 1024 / 1024
    print(f'{os.path.basename(out_path):22} {mb:6.3f} MB  ·  {len(data["works"])} eser  ·  '
          f'{len(data["series"])} seri' + ('' if standalone else
          f'  ·  limit 16 MB {"OK" if mb < 15 else "ASILDI"}'))


if __name__ == '__main__':
    main()
