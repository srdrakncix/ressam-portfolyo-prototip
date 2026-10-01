# -*- coding: utf-8 -*-
"""Türkçe içerik katmanı.

Gerçek eserler geldiğinde SADECE bu dosya ve cache/ klasörü değişir.
Tasarım dosyalarına hiç dokunulmaz.
"""

ARTIST = {
    # Ad müşteri kararıyla bu (30 Eylül 2026) — gerçek ad değil, kalıyor.
    'name': 'Cemal Sağlam',
    'mark': 'CEMAL SAĞLAM',
    'role': 'Ressam',
    # İletişim: yalnızca ressamın sitede görünmesini ONAYLADIĞI gerçek bilgi.
    # Boşken İletişim sayfası menüde yok, eser sayfası e-posta satırı basmıyor.
    'email': '',
    'studio': '',
}

# ── sanatçı sayfaları ─────────────────────────────────────────────────────
# KURGU İÇERİK KALDIRILDI (1 Ekim 2026). Biyografi, atölye notu, sergiler,
# koleksiyonlar, yayınlar ve basın uydurmaydı: kurum adları, katalog sayfa
# sayıları, basın künyeleri, doğum yeri — hiçbiri ressama ait değildi.
# Yayındaki bir sitede bunlar ressam adına yalan söylemek olurdu.
#
# Kural: BOŞ LİSTE = O SAYFA YOK. Menü satırı da rota da kendiliğinden
# kalkıyor (kabuk.js icerikVar). Ressam gerçek bilgiyi verince buraya
# yazılır, çevirisi ceviri.py'deki aynı adlı sözlüğe; sayfa geri gelir.
BIO = []            # paragraflar
STATEMENT = []      # atölye notu, paragraflar
CV = []             # (yıl, sergi adı, 'Kişisel sergi · Mekân, Şehir' | 'Karma sergi · …')
COLLECTIONS = []    # kurum adları
PUBLICATIONS = []   # (yıl, ad, açıklama)
PRESS = []          # (yıl, yazı başlığı, 'Yazar · Yayın, Ay Yıl')

# Seriler: gerçek bir ressam portfolyosu eserleri seriler halinde düzenler,
# tek düz bir "galeri" olarak değil. Sitenin omurgası bu.
# Eski dört seri manzara temalıydı (Alacakaranlık, Hava, Sessiz Topografya,
# Sabah) ve yer tutucu George Inness manzaralarına göre yazılmıştı. Gelen
# gerçek eserler figüratif: iç mekânlar, kalabalıklar, portreler. O seri
# adları artık hiçbir şeyi tarif etmiyor.
#
# Serileri ben ADLANDIRMIYORUM — hangi resmin hangi seriye girdiğini ve o
# serinin ne olduğunu ressam bilir. Şimdilik tek geçici grup var; müşteri
# seri isimlerini verince buraya yazılacak.
SERIES = [
    {'key': 'eserler', 'title': 'Eserler', 'years': '', 'blurb': ''},
]

# id -> (başlık, seri, sanatçı notu, durum)
# durum: 'satilik' | 'koleksiyonda' | 'ayrildi'
WORKS = {
    # Eserlerin hepsi 132 cm genişliğinde; yükseklik 83–88 cm arasında değişiyor.
    # Tek formatta çalışan bir ressam — duvarda çerçeveler eşit boyda duruyor.
    # (Seçim `secim.py` ile en-boy oranına göre yapılıyor, parlaklığa göre değil.)

    # Sabah — gümüş ışık serisi
    68784:  ('Yaz Sabahı',        'sabah',         'Yeşili yeşille değil, sarıyla açtım.', 'satilik'),
    64764:  ('Kırda Sabah',       'sabah',         'Bulut kalın ama ışık yine de geçiyor. Zor olan o.', 'satilik'),
    64748:  ('Işıklı Vadi',       'sabah',         'Uzaktaki ışık yakındakinden daha sıcak olmalı.', 'satilik'),

    # Hava — atmosfer ve basınç
    64732:  ('Bastıran',          'hava',          'Bir saat içinde bitti. Nadiren öyle olur.', 'satilik'),
    65353:  ('Fırtına',           'hava',          'Üstünde iki kış çalıştım. İkisi de aralıkta.', 'satilik'),
    68792:  ('Kıyı',              'hava',          'Denizi bir kez boyadım. Karadan zor çıktı.', 'satilik'),

    # Sessiz Topografya — insansız araziler
    64736:  ('Güz Ormanı',        'topografya',    'Sonbaharı kırmızıyla anlatmamaya çalıştığım bir deneme.', 'satilik'),
    69844:  ('Issız Çiftlik',     'topografya',    'Boş bir ev, boş bir arazi. Yine de biri var gibi.', 'ayrildi'),
    68388:  ('Dağ Sırtı',         'topografya',    'Sırtın arkasında ne olduğunu bilmeden çalıştım.', 'satilik'),

    # Alacakaranlık — ışığın çekildiği aralık
    64772:  ('Alacakaranlık',     'alacakaranlik', 'Seriye adını veren resim.', 'koleksiyonda'),
    64724:  ('Balıkçıl',          'alacakaranlik', 'Suyun üstündeki tek hareket. Onu en son koydum.', 'satilik'),
}

# Yonetim panelinin giris sunucusu (Cloudflare Worker).
# BOS ise panel GitHub anahtarini dogrudan kullanicidan ister — teknik
# olmayan biri icin anlasilmaz. Adres yazilirsa panel kullanici adi + sifre
# soruyor, anahtar sunucuda kaliyor. Kurulum: sunucu/OKUBENI.md
PANEL_SUNUCU = ''

MEDIUM_TR = 'Tuval üzerine yağlı boya'

STATUS_TR = {
    'satilik':      'Müsait',
    'koleksiyonda': 'Özel koleksiyonda',
    'ayrildi':      'Ayrıldı',
}
