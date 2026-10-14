# -*- coding: utf-8 -*-
"""icerik/site.json — panelden düzenlenen bütün site içeriği.

Eser kayıtları ayrı (icerik/eserler/*.json); burada geri kalan her şey var:
sanatçının adı ve iletişimi, ana sayfa eserleri, seriler, sanatçı sayfaları
(biyografi, atölye notu, sergiler, koleksiyonlar, yayınlar, basın), menü
başlıkları ve sitedeki yazılar, sitenin açık/kapalı durumu.

TEK KAYNAK. build.py, yayinla.py ve site_ek.py bu dosyayı yalnızca buradan
okuyor; panel de yalnızca bu dosyayı yazıyor. Önceden bu bilgiler
content.py / ceviri.py / build.py'de Python kodu olarak duruyordu ve panel
.py düzenleyemediği için ressam hiçbirini değiştiremiyordu.

Bozuk bir dosya derlemeyi DURDURUR (açık bir mesajla): Pages son başarılı
yayını sunmaya devam eder, yani panelde yapılan bir hata siteyi bozamaz.
"""
import io
import json
import os
import sys

KOK = os.path.dirname(os.path.abspath(__file__))
DOSYA = os.path.join(KOK, 'icerik', 'site.json')
DILLER = ('tr', 'en', 'fr')
SERGI_TURLERI = ('kisisel', 'karma')

# Panelde "Menü ve yazılar" altında düzenlenen arayüz dizgeleri, panelin
# gösterdiği sırayla. Geri kalanı (erişilebilir adlar, yakınlaştırma
# ipuçları …) ceviri.UI'da kalıyor; ressamın görmesi gereken bir şey değil.
# Boş bırakılan alan ceviri.UI'daki varsayılana düşer.
YAZILAR = (
    # menü
    'nav_gallery', 'nav_recent', 'nav_about_grp', 'nav_studio', 'nav_bio',
    'nav_exh', 'nav_coll', 'nav_pub', 'nav_press', 'nav_contact',
    # site geneli
    'site_sub', 'medium', 'meta_desc',
    # ana sayfadaki galeri kartı ve galeri sayfası
    'gal_label', 'gal_title', 'gal_sub', 'gal_works',
    # sanatçı sayfaları
    'exh_solo', 'exh_group', 'contact_body',
    # eser durum satırları
    'avail_studio', 'avail_private', 'avail_gone',
)


def _hata(m):
    sys.exit('site.json: ' + m)


def _dilli(x, ad):
    """{'tr': .., 'en': .., 'fr': ..} -> her dil için temiz dizge."""
    if x is None:
        x = {}
    if isinstance(x, str):          # tek dilli yazılmışsa Türkçe say
        x = {'tr': x}
    if not isinstance(x, dict):
        _hata(f'{ad} dil sözlüğü olmalı (tr/en/fr)')
    return {d: temizle(x.get(d) or '') for d in DILLER}


def temizle(s):
    """Kullanıcı metni sayfaya innerHTML ile de giriyor: '<' bir etiket
    açıp düzeni bozmasın. Açılı ayraçlar tipografik karşılığına döner;
    başka hiçbir karaktere dokunulmuyor."""
    return str(s).replace('<', '‹').replace('>', '›').strip()


def dilde(sozluk, dil):
    """İstenen dil boşsa ilk dolu dile düş (tr → en → fr). Ressam bir
    metni yalnız bir dilde yazabilir; öteki dillerde sayfa boş kalmasın."""
    for d in (dil,) + DILLER:
        if sozluk.get(d):
            return sozluk[d]
    return ''


def _yil(metin):
    """'2023', '2023–2024', 'Mart 2021' -> ilk dört haneli sayı; yoksa 0."""
    import re
    m = re.search(r'\d{4}', str(metin))
    return int(m.group(0)) if m else 0


def paragraflar(metin):
    """Boş satırla ayrılmış paragraflar; tek satır sonu paragraf içinde kalır."""
    parca = [p.strip() for p in metin.replace('\r\n', '\n').split('\n\n')]
    return [' '.join(p.split('\n')) for p in parca if p]


def oku(yol=DOSYA):
    try:
        ham = json.load(io.open(yol, encoding='utf-8'))
    except FileNotFoundError:
        _hata('dosya yok -> ' + yol)
    except Exception as e:
        _hata(f'okunamadı ({e})')
    if not isinstance(ham, dict):
        _hata('kök bir nesne olmalı')

    s = {}
    s['acik'] = bool((ham.get('yayin') or {}).get('acik'))

    sn = ham.get('sanatci') or {}
    s['sanatci'] = {k: temizle(sn.get(k) or '')
                    for k in ('ad', 'eposta', 'telefon', 'adres', 'instagram')}
    if not s['sanatci']['ad']:
        _hata('sanatçı adı boş olamaz')
    # Instagram: "@ad", "ad" ya da tam adres — hepsi kullanıcı adına iner.
    ig = s['sanatci']['instagram']
    for on in ('https://', 'http://', 'www.', 'instagram.com/'):
        if ig.lower().startswith(on):
            ig = ig[len(on):]
    s['sanatci']['instagram'] = ig.strip('/@ ')

    ana = ham.get('ana_sayfa') or []
    if not isinstance(ana, list) or not all(isinstance(x, str) for x in ana):
        _hata('ana_sayfa eser adlarından oluşan bir liste olmalı')
    s['ana_sayfa'] = ana

    seriler = []
    for i, x in enumerate(ham.get('seriler') or []):
        anahtar = str((x or {}).get('anahtar') or '').strip()
        if not anahtar:
            _hata(f'{i + 1}. serinin anahtarı yok')
        if any(y['anahtar'] == anahtar for y in seriler):
            _hata(f'seri anahtarı iki kez var -> {anahtar}')
        ad = _dilli(x.get('ad'), f'seri {anahtar} adı')
        if not any(ad.values()):
            _hata(f'seri {anahtar}: ad boş')
        seriler.append({'anahtar': anahtar, 'ad': ad,
                        'aciklama': _dilli(x.get('aciklama'), f'seri {anahtar} açıklaması')})
    if not seriler:
        _hata('en az bir seri olmalı')
    s['seriler'] = seriler

    s['biyografi'] = _dilli(ham.get('biyografi'), 'biyografi')
    s['atolye_notu'] = _dilli(ham.get('atolye_notu'), 'atölye notu')

    sergiler = []
    for i, x in enumerate(ham.get('sergiler') or []):
        ad = temizle((x or {}).get('ad') or '')
        if not ad:
            continue                      # yarım satır: panelde boş bırakılmış
        tur = x.get('tur') or 'kisisel'
        if tur not in SERGI_TURLERI:
            _hata(f'{i + 1}. sergi: tür kisisel ya da karma olmalı')
        sergiler.append({'yil': temizle(x.get('yil') or ''), 'ad': ad,
                         'tur': tur, 'yer': temizle(x.get('yer') or '')})
    s['sergiler'] = sergiler

    s['koleksiyonlar'] = [temizle(x) for x in (ham.get('koleksiyonlar') or [])
                          if temizle(x or '')]

    s['yayinlar'] = [
        {'yil': temizle(x.get('yil') or ''), 'ad': temizle(x.get('ad') or ''),
         'aciklama': _dilli(x.get('aciklama'), 'yayın açıklaması')}
        for x in (ham.get('yayinlar') or []) if temizle((x or {}).get('ad') or '')]

    s['basin'] = [
        {'yil': temizle(x.get('yil') or ''), 'baslik': temizle(x.get('baslik') or ''),
         'kunye': _dilli(x.get('kunye'), 'basın künyesi')}
        for x in (ham.get('basin') or []) if temizle((x or {}).get('baslik') or '')]

    # Özgeçmiş geleneği: yeniden eskiye. Panelde hangi sırayla girildiği
    # önemli değil; aynı yıl içinde girilen sıra korunur. Yılı olmayan
    # satır sona düşer.
    for liste in ('sergiler', 'yayinlar', 'basin'):
        s[liste].sort(key=lambda x: -_yil(x['yil']))

    yz = ham.get('yazilar') or {}
    s['yazilar'] = {d: {k: temizle(v) for k, v in (yz.get(d) or {}).items()
                        if k in YAZILAR and isinstance(v, str) and v.strip()}
                    for d in DILLER}
    return s


def arayuz(site, varsayilan):
    """ceviri.UI ⊕ site.json yazıları: boş alan varsayılana düşer."""
    return {d: dict(varsayilan[d], **site['yazilar'][d]) for d in DILLER}
