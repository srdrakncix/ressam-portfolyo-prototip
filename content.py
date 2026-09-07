# -*- coding: utf-8 -*-
"""Türkçe içerik katmanı.

Gerçek eserler geldiğinde SADECE bu dosya ve cache/ klasörü değişir.
Tasarım dosyalarına hiç dokunulmaz.
"""

ARTIST = {
    'name': 'Cemal Sağlam',
    'mark': 'CEMAL SAĞLAM',
    'role': 'Ressam',
    'based': 'İstanbul',
    'born': '1987',
    'birthplace': 'İzmir',
    'tagline': 'Işığın çekildiği anı boyuyorum.',
    'lede': 'Tuval üzerine yağlı boya. Katman katman, sabırla — aceleye gelmeyen bir iş.',
    'email': 'atolye@cemalsaglam.com',
    'phone': '+90 212 000 00 00',
    'studio': 'Bomonti, Şişli · İstanbul',
    'ig': '@cemalsaglam',
}

BIO = [
    # Doğum cümlesi üstteki künyede zaten var; burada tekrarlanmıyor.
    'Mimar Sinan Güzel Sanatlar Üniversitesi Resim Bölümü’nü bitirdi, ardından Viyana’da '
    'iki yıl klasik boya teknikleri üzerine çalıştı.',

    'Yağlı boyayı yavaşlığı için seçtiğini söylüyor. Bir tuval üzerinde aylarca çalışıyor, '
    'katmanları kurumaya bırakıyor, üzerine dönüyor. İşin büyük kısmı beklemekle geçiyor.',

    '2016’dan bu yana İstanbul Bomonti’deki atölyesinde üretiyor. Çalışmaları Türkiye, '
    'Avusturya ve Hollanda’da özel koleksiyonlarda yer alıyor.',
]

# Kurum adları KURGUDUR. Gerçek galeri isimleri kasten kullanılmadı —
# kurgu bir sanatçıya gerçek kurumlarla sergi geçmişi uydurmak yanlış olur.
CV = [
    ('2024', 'Alacakaranlık', 'Kişisel sergi · Ardıç Sanat, İstanbul'),
    ('2023', 'Hava Raporu', 'Kişisel sergi · Payas Galeri, İstanbul'),
    ('2023', 'Uzun Pozlama', 'Karma sergi · Kule Sanat Alanı, Ankara'),
    ('2022', 'Yeni Manzara', 'Karma sergi · Liman Kültür Merkezi, İzmir'),
    ('2021', 'Sessiz Topografya', 'Kişisel sergi · Ardıç Sanat, İstanbul'),
    ('2020', 'Katman', 'Karma sergi · Batı Kanat, İstanbul'),
    ('2019', 'Slow Paint', 'Karma sergi · Atelier Nordbahn, Viyana'),
    ('2018', 'İlk Katman', 'Kişisel sergi · Payas Galeri, İzmir'),
]

# Eserlerin bulunduğu koleksiyonlar. Povey'in "Selected Collections" bölümü gibi.
COLLECTIONS = [
    'Ardıç Sanat Koleksiyonu, İstanbul',
    'Batı Kanat Çağdaş Sanat Koleksiyonu, İstanbul',
    'Liman Kültür Merkezi, İzmir',
    'Atelier Nordbahn Koleksiyonu, Viyana',
    'Van Doorn Koleksiyonu, Rotterdam',
    'Özel koleksiyonlar · Türkiye, Avusturya, Hollanda',
]

# Yayınlar ve katalog. Sadelik ancak arkasında külliyat varsa güven verir.
PUBLICATIONS = [
    ('2024', 'Alacakaranlık', 'Sergi kataloğu, 96 sayfa. Metin: Nihal Erkut. Ardıç Sanat.'),
    ('2023', 'Hava Raporu', 'Sergi kataloğu, 64 sayfa. Payas Galeri.'),
    ('2022', 'Yavaş Boya', 'Söyleşi · Sanat Dünyamız, sayı 189, s. 44–51.'),
    ('2021', 'Sessiz Topografya', 'Sergi kataloğu, 72 sayfa. Metin: Kaan Bilen. Ardıç Sanat.'),
    ('2019', 'Katmanın Sabrı', 'Deneme · Kunstraum Yıllığı, Viyana. Almanca ve İngilizce.'),
]

PRESS = [
    ('2024', '“Işığın çekildiği yerde durmak”',
     'Ayşe Tunca · Cumhuriyet Kitap, Kasım 2024'),
    ('2024', '“Bir tuval kaç kış bekler?”',
     'Deniz Aksoy · Argonotlar, Ekim 2024'),
    ('2023', '“Manzara değil, basınç”',
     'Selim Arer · Sanat Dünyamız, Mart 2023'),
    ('2021', '“Sessiz Topografya üzerine”',
     'Kaan Bilen · e-skop, Aralık 2021'),
]

# Atölye notu — Povey'deki "Press Release" bölümünün karşılığı.
STATEMENT = [
    'Bir tuvale başlarken neye benzeyeceğini bilmiyorum. Yalnızca hangi ışığı '
    'aradığımı biliyorum: günün bittiği, henüz gece olmadığı o yarım saat. '
    'Onu bulana kadar üstünü örtüyorum.',

    'Katmanlar kurudukça renk değişiyor. Bu yüzden acele edilemiyor. Bir resmin '
    'üzerinde ortalama dört ay çalışıyorum ve bu sürenin belki üçte biri fiilen '
    'boya sürmekle geçiyor. Kalanı bakmak ve beklemek.',

    'Manzara resmi yaptığımı düşünmüyorum. Manzara bahane; asıl mesele havanın '
    'ağırlığı. Bir fırtınanın rengi vardır, yağmurdan sonranın başka bir rengi. '
    'Onları tarif etmeye çalışıyorum.',
]

# Seriler: gerçek bir ressam portfolyosu eserleri seriler halinde düzenler,
# tek düz bir "galeri" olarak değil. Sitenin omurgası bu.
SERIES = [
    {'key': 'alacakaranlik', 'title': 'Alacakaranlık', 'years': '2021 — 2024',
     'blurb': 'Günün bittiği, gecenin başlamadığı o kısa aralığın resimleri. '
              'Renk burada bir şeyi tarif etmiyor; bir şeyin kayboluşunu tutuyor.'},
    {'key': 'hava', 'title': 'Hava', 'years': '2019 — 2023',
     'blurb': 'Fırtına, yağmur, basınç. Manzaradan çok atmosferin kendisi. '
              'Tuvale önce havayı koyuyorum, yeri sonra.'},
    {'key': 'topografya', 'title': 'Sessiz Topografya', 'years': '2018 — 2024',
     'blurb': 'İnsansız araziler. İçinde kimsenin olmadığı ama birinin geçtiği belli olan yerler.'},
    {'key': 'sabah', 'title': 'Sabah', 'years': '2020 — 2024',
     'blurb': 'Gümüş ışık serisi. Sabahın ilk yarım saati, henüz renk yerine oturmadan.'},
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

# Hangi eser hangi koleksiyonda. Üstteki COLLECTIONS listesi altı kurum adı
# sayıyordu ama hiçbiri hiçbir esere bağlı değildi — kayıt tutuluyor ama
# kontrol edilmiyor izlenimi veriyordu.
# (eser id) -> (koleksiyon adı, edinme yılı)
COLLECTION_OF = {
    64772: ('Ardıç Sanat Koleksiyonu, İstanbul', 2024),
    69844: ('Van Doorn Koleksiyonu, Rotterdam', 2022),
}

# 360Artwork'te kurulan gezilebilir sanal salonun paylasim adresi.
# BOS ise sergi sayfasinda salon karti hic cikmiyor. Adres degisirse
# yalnizca burasi degisir; sablonlara dokunulmuyor.
SANAL_SALON = 'https://www.360artwork.com/show/gallery/view?u=kp_a3cb376a0e9445ff80278527fba61bc7&g=cmtrit6780005l704z1c2pjis'

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

# Prototiplerde görünecek yer tutucu uyarısı — müşteri sunumunda karışıklık olmasın.
PLACEHOLDER_NOTICE = (
    'Bu bir tasarım prototipidir. Sanatçı kimliği ve metinler kurgudur; '
    'görseller Art Institute of Chicago açık erişim arşivinden alınmış kamu malı '
    'George Inness tablolarıdır. Yayına geçmeden önce tümü gerçek eserlerle değiştirilecektir.'
)
