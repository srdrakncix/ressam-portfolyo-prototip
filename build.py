# -*- coding: utf-8 -*-
"""Şablon HTML + eser verisi -> yayına hazır tek dosya.

Kullanım:  python build.py <sablon.html> <cikti.html>

Şablonda   /*__SITE_DATA__*/   token'ı bulunur; yerine `const SITE = {...}` yazılır.
Base64 görseller asla şablonda durmaz — böylece tasarım dosyası okunabilir kalır.
"""
import json, re, sys, io, os, base64
from PIL import Image, ImageFilter
import content as C
try:
    import ceviri as T
except ImportError:            # çeviri dosyası yoksa site tek dilli çalışır
    T = None

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


def inches(cm):
    """Santimi gerçek adi kesirle inç'e çevirir — tombstone geleneği böyle."""
    v = cm / 2.54
    whole = int(v)
    frac = v - whole
    eighths = round(frac * 8)
    if eighths == 8:
        whole, eighths = whole + 1, 0
    glyph = {0: '', 1: '⅛', 2: '¼', 3: '⅜', 4: '½', 5: '⅝', 6: '¾', 7: '⅞'}[eighths]
    return f'{whole}{glyph}'


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
        kayitlar.append(k)
    kayitlar.sort(key=lambda k: (k.get('sira') or 999, k['slug']))
    return kayitlar


def build_data():
    works = []
    for idx, k in enumerate(eserleri_oku()):
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

        # Kunye olcusu ile fotografin orani uyusmazsa duvarda eser KIRPILIR
        # (.eser img object-fit: cover). Sessiz kalmasin: panel de uyariyor
        # ama biri JSON'u elle duzenlerse tek uyari burasi olur.
        bek, ger = cw / ch, im.width / im.height
        if olcu_var and abs(ger - bek) / bek > 0.03:
            print(f'UYARI  {k["slug"]}: gorsel orani {ger:.2f}, kunye {cw}x{ch} cm '
                  f'({bek:.2f}). Duvarda kirpilacak.')

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
            'medium': C.MEDIUM_TR,
            # Olcu yoksa BOS. Arayuz bos olcuyu hic basmiyor.
            'size':   f'{ch}{NB}×{NB}{cw}{NB}cm' if olcu_var else '',
            'sizeIn': f'{inches(ch)}{NB}×{NB}{inches(cw)}{NB}in' if olcu_var else '',
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
    seriler = [dict(x) for x in C.SERIES]
    for sr in seriler:
        yillar = sorted({w['year'] for w in works if w['series'] == sr['key']})
        if yillar:
            sr['years'] = (str(yillar[0]) if len(yillar) == 1
                           else f'{yillar[0]} — {yillar[-1]}')

    data = {
        'artist':       C.ARTIST,
        'bio':          C.BIO,
        'cv':           C.CV,
        'collections':  getattr(C, 'COLLECTIONS', []),
        'publications': getattr(C, 'PUBLICATIONS', []),
        'press':        getattr(C, 'PRESS', []),
        'statement':    getattr(C, 'STATEMENT', []),
        'series':       seriler,
        'works':        works,
        'notice':       C.PLACEHOLDER_NOTICE,
    }
    data['i18n'] = build_i18n(works)

    # Sayfa zeminleri: ressamın kendi tablolarından makro kırpıntılar (zemin.py).
    # Yoksa site tek renk zeminle çalışır.
    zp = os.path.join(HERE, 'zeminler.json')
    data['backdrops'] = json.load(io.open(zp, encoding='utf-8')) if os.path.exists(zp) else {}
    return data


def build_i18n(works):
    """Her dil için yalnızca DEĞİŞEN alanları üretir.

    Eser adı ve ölçüler her dilde aynı kalır — ad bir isimdir, ölçü bir olgudur.
    Çeviri yalnızca arayüz, açıklama ve teknik satırlar için.
    """
    if T is None:
        return {'tr': {'ui': {}}}

    out = {'tr': {'ui': T.UI['tr'], 'bio': C.BIO, 'statement': C.STATEMENT,
                  'collections': getattr(C, 'COLLECTIONS', []),
                  'series': {s['key']: {'title': s['title'], 'blurb': s['blurb']} for s in C.SERIES},
                  'works': {w['id']: {'gloss': '', 'note': w['_not'].get('tr', '')} for w in works},
                  'cv': [list(r) for r in C.CV],
                  'publications': [list(r) for r in C.PUBLICATIONS],
                  'press': [list(r) for r in getattr(C, 'PRESS', [])],
                  'notice': C.PLACEHOLDER_NOTICE}}

    for lang in ('en', 'fr'):
        # seriler
        series = {}
        for s in C.SERIES:
            tr = T.SERIES.get(s['key'], {}).get(lang)
            series[s['key']] = {'title': tr[0], 'blurb': tr[1]} if tr else \
                               {'title': s['title'], 'blurb': s['blurb']}
        # eserler: ad çevrilmez, altına gloss düşer; not çevrilir
        # Eser adi CEVRILMEZ: kaydin icinde dile gore baslik alani YOK.
        # gloss = adin altinda gosterilen aciklayici karsilik.
        wmap = {}
        for w in works:
            wmap[w['id']] = {'gloss': w['_gloss'].get(lang, ''),
                             'note': w['_not'].get(lang) or w['_not'].get('tr', '')}
        # CV: ad korunur, tanımlayıcı çevrilir
        cv = []
        for year, title, venue in C.CV:
            v = venue
            for src, tgt in T.DESCRIPTORS.items():
                if v.startswith(src):
                    v = tgt[lang] + v[len(src):]
                    break
            cv.append([year, title, v])
        # yayınlar: ad korunur, açıklama çevrilir
        pubs = getattr(C, 'PUBLICATIONS', [])
        pl = T.PUBLICATIONS.get(lang, [])
        publications = [[r[0], r[1], pl[i] if i < len(pl) else r[2]] for i, r in enumerate(pubs)]
        # basın: başlık korunur, künye satırı çevrilir
        press = getattr(C, 'PRESS', [])
        bl = T.PRESS_BYLINE.get(lang, [])
        press_out = [[r[0], r[1], bl[i] if i < len(bl) else r[2]] for i, r in enumerate(press)]

        out[lang] = {
            'ui':           T.UI[lang],
            'bio':          T.BIO[lang],
            'statement':    T.STATEMENT[lang],
            'collections':  T.COLLECTIONS[lang],
            'series':       series,
            'works':        wmap,
            'cv':           cv,
            'publications': publications,
            'press':        press_out,
            'notice':       T.NOTICE[lang],
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

        # Ortam gorseli (Smartist ev maketi): eserin YERINE gecmiyor, yanina
        # dusuyor. Detay sayfasinda ikinci kare olarak gosteriliyor.
        if w.get('ortamSrc'):
            ham = base64.b64decode(w['ortamSrc'].split(',', 1)[1])
            oad = f"ortam-{w['id']}.webp"
            with open(os.path.join(adir, oad), 'wb') as f:
                f.write(ham)
            total += len(ham)
            w['ortam'] = 'assets/' + oad
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
    tpl = io.open(tpl_path, encoding='utf-8').read()
    for token in ('/*__SITE_DATA__*/', '/*__KIT__*/'):
        if token not in tpl:
            sys.exit(f'HATA: {tpl_path} içinde {token} yok.')

    payload = 'const SITE = ' + json.dumps(data, ensure_ascii=False, separators=(',', ':')) + ';'
    kit = io.open(os.path.join(HERE, 'kit.js'), encoding='utf-8').read()
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
        isler = data.get('works') or []
        if not isler:
            sys.exit('HATA: eser yok, paylasim gorseli uretilemedi.')
        yol = isler[0].get('ortam') or isler[0].get('src')
        if not yol:
            sys.exit('HATA: ilk eserde gorsel yok, og:image uretilemedi.')
        # Denetim: gorselin KAYNAGI gercekten var mi. Kusurun sebebi
        # tam olarak bu denetimin olmamasiydi -- silinmis bir esere
        # bakan sabit bir yol kimseyi uyarmadan yayina gidiyordu.
        temel = os.path.splitext(os.path.basename(yol))[0]
        gdizin = os.path.join(HERE, 'icerik', 'gorseller')
        varmi = any(os.path.splitext(f)[0] == temel
                    for f in os.listdir(gdizin)) if os.path.isdir(gdizin) else False
        if not varmi:
            sys.exit('HATA: paylasim gorseli kaynakta yok -> %s' % temel)
        tam = kok_url + '/' + yol
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
    # Firca darbelerinin on yuklemesi: liste varlik dosyalarindan
    # uretiliyor, elle tutulmuyor. Sayi degisince kendiliginden guncel.
    if '<!--__FIRCA_ONYUK__-->' in out:
        fdizin = os.path.join(HERE, 'varlik', 'firca')
        adlar = sorted((f for f in os.listdir(fdizin)
                        if f.startswith('panel-') and f.endswith('.webp')),
                       key=lambda f: int(f.split('-')[1].split('.')[0])) \
            if os.path.isdir(fdizin) else []
        if not adlar:
            sys.exit('HATA: varlik/firca bos, on yukleme uretilemedi.')
        out = out.replace('<!--__FIRCA_ONYUK__-->', '\n'.join(
            '<link rel="preload" as="image" type="image/webp"'
            ' fetchpriority="low" href="assets/firca/%s">' % a for a in adlar))

    # Sira onemli: KABUK_CSS once giriyor ve icinde FIRCA_CSS belirteci
    # var; sonraki tur onu yakaliyor.
    for belirtec, dosya in (('/*__KABUK_CSS__*/', 'kabuk.css'),
                            ('/*__FIRCA_CSS__*/', 'firca.css'),
                            ('/*__KABUK_JS__*/', 'kabuk.js')):
        if belirtec in out:
            yol = os.path.join(HERE, dosya)
            if not os.path.exists(yol):
                sys.exit(f'HATA: {tpl_path} {belirtec} istiyor ama {dosya} yok.')
            out = out.replace(belirtec, io.open(yol, encoding='utf-8').read())

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
