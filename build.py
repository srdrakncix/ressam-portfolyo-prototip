# -*- coding: utf-8 -*-
"""Şablon HTML + eser verisi -> yayına hazır tek dosya.

Kullanım:  python build.py <sablon.html> <cikti.html>

Şablonda   /*__SITE_DATA__*/   token'ı bulunur; yerine `const SITE = {...}` yazılır.
Base64 görseller asla şablonda durmaz — böylece tasarım dosyası okunabilir kalır.
"""
import json, re, sys, io, os, base64
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


def build_data():
    images = json.load(open(os.path.join(HERE, 'images.json'), encoding='utf-8'))
    counters = {k: 0 for k in SERIES_YEARS}
    works = []

    for idx, im in enumerate(images):
        wid = im['id']
        if wid not in C.WORKS:
            continue
        title, series, note, status = C.WORKS[wid]
        pool = SERIES_YEARS[series]
        year = pool[counters[series] % len(pool)]
        counters[series] += 1

        ch, cw = cm_pair(im.get('src_dim'))          # yükseklik, genişlik (cm)
        # Bölünmez boşluk: mobilde ölçü "83 × 132 / CM | 32⅝ × 52 in" diye
        # ortadan kopuyordu. Bir ölçü ifadesi hiçbir zaman ikiye ayrılmamalı.
        NB = ' '
        size_tr = f'{ch}{NB}×{NB}{cw}{NB}cm' if ch else '—'
        size_en = f'{inches(ch)}{NB}×{NB}{inches(cw)}{NB}in' if ch else '—'

        works.append({
            'id':     str(wid),
            'no':     f'{idx + 1:02d}',              # katalog numarası
            'slug':   slugify(title),
            'title':  title,
            'series': series,
            'note':   note,
            'status': status,
            # hangi koleksiyonda ve hangi yıl edinildi (varsa)
            'collection': (C.COLLECTION_OF.get(wid) or ('', 0))[0],
            'collYear':   (C.COLLECTION_OF.get(wid) or ('', 0))[1],
            'year':   year,
            'medium': C.MEDIUM_TR,
            'size':   size_tr,
            'sizeIn': size_en,
            'cw':     cw,                            # gerçek genişlik, cm
            'ch':     ch,                            # gerçek yükseklik, cm
            'area':   (cw * ch) if cw else 0,        # fiziksel alan — indeks ölçeklemesi
            'ratio':  im['ratio'],
            'px':     [im['w'], im['h']],
            'portrait': im['ratio'] < 1,
            'tone':   im['tone'],
            'lqip':   'data:image/webp;base64,' + im['lqip'],
            'src':    'data:image/webp;base64,' + im['full'],
            'credit': f"{im['src_artist']}, “{im['src_title']}”, {im['src_date']} · "
                      f"Art Institute of Chicago, kamu malı",
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
                  'works': {w['id']: {'gloss': '', 'note': w['note']} for w in works},
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
        wmap = {}
        for w in works:
            tr = T.WORKS.get(int(w['id']), {}).get(lang)
            wmap[w['id']] = {'gloss': tr[0], 'note': tr[1]} if tr else {'gloss': '', 'note': w['note']}
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
    return total


def render(tpl_path, data, standalone):
    tpl = io.open(tpl_path, encoding='utf-8').read()
    for token in ('/*__SITE_DATA__*/', '/*__KIT__*/'):
        if token not in tpl:
            sys.exit(f'HATA: {tpl_path} içinde {token} yok.')

    payload = 'const SITE = ' + json.dumps(data, ensure_ascii=False, separators=(',', ':')) + ';'
    kit = io.open(os.path.join(HERE, 'kit.js'), encoding='utf-8').read()
    out = tpl.replace('/*__KIT__*/', kit).replace('/*__SITE_DATA__*/', payload)

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
