# -*- coding: utf-8 -*-
"""Sabit ayarlar.

SİTE İÇERİĞİ ARTIK BURADA DEĞİL: sanatçının adı, iletişimi, sanatçı
sayfaları, seriler, ana sayfa eserleri, menü başlıkları ve yazılar
icerik/site.json'da; eserler icerik/eserler/*.json'da. İkisini de ressam
panelden (saglam.fr/panel/) düzenliyor. Okuyan tek yer site_veri.py.
"""

# ESKİ (yer tutucu George Inness dönemi). Yalnız tasima.py okuyor; site
# derlemesi kullanmıyor.
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

# Panelde eser durumu seçenekleri (secenekler.json).
STATUS_TR = {
    'satilik':      'Müsait',
    'koleksiyonda': 'Özel koleksiyonda',
    'ayrildi':      'Ayrıldı',
}
