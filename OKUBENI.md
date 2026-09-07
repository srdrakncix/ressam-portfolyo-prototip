# Cemal Sağlam — Ressam Portfolyosu

Tek sanatçı yağlı boya portfolyo sitesi. **edwardpovey.com** tarzı: beyaz zemin,
Helvetica, solda düz metin menü, devasa resimler, küçük künye. Süs yok.

**Canlı:** https://srdrakncix.github.io/ressam-portfolyo-prototip/

---

## Sergi sayfası: şato duvarı rafa kalktı (2026-09)

`sergi.html` bir Fransız salonu duvarıydı: yaldız çerçeveler, damask, avize,
yatay kaydırma, gerçek 3B perspektif. Teknik olarak çalışıyordu ama yanlış
şeyi satıyordu — lüksü süsle satın almaya çalışıyordu ve eserin önüne
geçiyordu.

Yerine galerilerin kendi çözümü kuruldu (David Zwirner'ın *survey*
sayfasındaki ilke): her eser **aynı boyutta nötr bir alanın** içinde, ama
**kendi gerçek santimetre ölçüsüyle**. 200 cm'lik bir tuval alanı doldurur,
40 cm'lik bir etüt aynı alanın ortasında küçücük kalır. Tek gölge onu
duvara asılmış bir nesne yapar. Çerçeve yok.

Neden bu daha iyi:

- **Ölçek süs değil, bilgi.** Eski duvarda on bir eser aynı barok yaldızda ve
  neredeyse aynı büyüklükteydi; bağımsız incelemelerin ikisi de bunu yazmıştı.
- **Müşterinin fotoğraflarında ayakta kalıyor.** Yaldız çerçeve, düzgün
  çekilmemiş bir reprodüksiyonu daha da kötü gösteriyordu.
- **Detay katmanıyla aynı dünyada.** Eskiden koyu yeşilden beyaza sıçranıyordu.

Karşılaştırılan siteler: David Zwirner (nötr sahne + gerçek ölçek), Gagosian
(tek renk, serif, karışık boyutlu mozaik), Ruprecht von Kaufmann (seri başına
kare karo), Sadie Coles (sabit görsel sütunu + liste/ızgara geçişi).

**Ölçek nasıl hesaplanıyor:** `EN_GENIS`/`EN_YUKSEK` bütün koleksiyondan
alınıyor, süzgeçten geçen listeden değil — yoksa aynı eser "Tümü" ile "Hava"
görünümünde iki farklı boyutta çıkar ve karşılaştırma anlamını yitirirdi.
`EN_KUCUK` (%10) bir güvenlik tabanı: koleksiyona 250 cm'lik bir tuval
girerse 20 cm'lik etüt 2 piksele inmesin.

**Ortam görseli** (Smartist maketi) ızgarada duruşta görünmüyor; imleç
kartın üstüne gelince nötr alanı doldurup eseri bir evin duvarına taşıyor.
Dokunmatikte hover yok — orada karşılığı detaydaki **EV ORTAMI** karesi.

Duvarın kendisi silinmedi: `varlik/duvar/`, `varlik/cerceve/` ve onları üreten
`duvar.py` / `_cerceve.py` duruyor, aşağıdaki bölümler de nasıl yapıldıklarını
anlatıyor. Geri dönmek istenirse kaynak elde.

---

## Dosyalar

    content.py           Türkçe kaynak içerik: sanatçı, biyografi, CV,
                         koleksiyonlar, yayınlar, basın, atölye notu, seriler,
                         eser başlıkları. Gerçek eserler gelince burası değişir.
    ceviri.py            İngilizce ve Fransızca çeviriler. content.py'ye paralel.
    images.json          Gömülü görsel verisi (WebP base64 + renk/oran ölçümleri).
    kendi_eserlerim.py   Kendi tablolarını images.json'a çeviren araç.
    lighten.py           Yer tutucu havuzundan en açık tonluları seçen araç.
    build.py             Şablon + veri -> yayına hazır dosya.
    kit.js               Davranış katmanı: yönlendirme, tembel yükleme, odak tuzağı.
    duz.html             Sitenin tasarım şablonu. Base64 veri burada DURMAZ.
    site/index.html      Derlenmiş site (~45 KB). Kendi git deposu.
    site/assets/*.webp   18 eser, ~2 MB.
    arsiv/               Elenen üç prototip (Askı, Fasikül, Kütük). Referans için.

---

## Derleme

    python build.py duz.html site/index.html --standalone   # yayındaki site
    python build.py duz.html out_duz.html                   # Artifact sürümü

`--standalone` görselleri `assets/` altına ayrı `.webp` olarak çıkarır ve
`<!doctype html>` sarmalayıcısını ekler. Onsuz her şey base64 gömülür.

---

## Gerçek eserleri yerleştirmek

1. Yüksek çözünürlüklü fotoğrafları bir klasöre koy: `01-ad.jpg`, `02-ad.jpg` …
2. `python kendi_eserlerim.py C:\yol\eserler`
3. `content.py` içindeki `WORKS` anahtarlarını çıkan id'lerle eşle.
   Satır biçimi: `id: (başlık, seri, sanatçı notu, durum)`.
   Durum: `'satilik' | 'koleksiyonda' | 'ayrildi'`.
4. **Ölçüler `src_dim` alanında `"76.2 × 115.2 cm"` biçiminde olmalı** — künyedeki
   santimetre ve inç değerleri buradan üretiliyor.
5. `python build.py duz.html site/index.html --standalone`
6. `content.py` içindeki `PLACEHOLDER_NOTICE` metnini sil.
7. `cd site && git add -A && git commit -m "guncelleme" && git push`

---

## Diller

Site üç dilli: **TR · EN · FR**. Anahtar menünün altında, düz metin.
İlk ziyarette tarayıcı dili denenir, sonra tercih `localStorage`'da tutulur.

Çeviri kuralı — sanat dünyasında standart olan budur:

- **Eser adları çevrilmez.** Tablo adı bir isimdir. "Dağ Sırtı" üç dilde de
  "Dağ Sırtı" kalır; altına küçük ve italik çevirisi düşer ("La crête").
- **Sergi ve yayın adları da isimdir**, özgün hâlleriyle kalır. Yalnızca
  tanımlayıcıları çevrilir: "Kişisel sergi" → "Solo exhibition".
- **Kurum adları çevrilmez.**
- **Ölçüler değişmez**: metrik önce, inç parantezde.
- Çevrilen şeyler: arayüz, seri adları ve açıklamaları, biyografi, atölye
  notu, sanatçı notları, teknik satır ("Huile sur toile"), durum satırları.

Yeni dil eklemek: `ceviri.py` içindeki her sözlüğe kodu ekle, `duz.html`
içindeki `LANGS` dizisine yaz. Başka yere dokunmaya gerek yok.

---

## Kararlar ve nedenleri

- **Tek tema: beyaz.** Karanlık mod eklemek bu tasarımın reddettiği rafineliğin
  ta kendisi olurdu. Referans site de tek temalı.
- **Web yazı tipi yüklenmiyor.** Helvetica Neue sistem yığını; referans site de öyle.
- **Vurgu rengi referanstan farklı.** Onun camgöbeği tonu o sitenin kimliği;
  aynı sektörde birebir almak müşteriye zarar verirdi. Bizimki `#1B3FCC`.
- **Eser adı ayrı renkte** (`#7a3418`). Gezinme mavisiyle aynı olunca her eser
  adı tıklanabilir vaat ediyordu.
- **Kurum adları kurgudur.** Gerçek galeri isimleriyle sahte sergi geçmişi
  uydurulmadı.
- **`#nav ul` gibi seçici YAZMA.** Özgüllüğü (1,0,1) olur ve mobildeki
  `#navlist { display:none }` kuralını (1,0,0) ezer; menü kapalıyken açık kalır.
  Bu hata bir kez yapıldı, `duz.html` içinde yorumla işaretli.
- **LQIP'in 1200 ms zaman aşımı yedeği var.** Yağlı boyada "yüklenmedi" ile
  "eser bu" ayırt edilemiyor; bulanık dikdörtgen kalıcı olamaz.

---

## Dokular ve kaynakları

Sergi duvarındaki malzemeler **gerçek fotoğraflanmış dokulardır**, prosedürel
desen değil:

- `site/assets/duvar/ipek.webp` — ambientCG **Fabric066**, kusursuz döşenebilir
  dokuma kumaş taraması. Fransız yeşiline boyandı; dokuma detayı korundu.
- `site/assets/duvar/boiserie.webp` — ambientCG **Wood095**, krem boyalı
  boiserie'ye çevrildi; ahşap damarı altından belli belirsiz görünüyor.

İkisi de **CC0 1.0** (kamu malı, ticari kullanım serbest, atıf zorunlu değil).
Kaynak: ambientcg.com. `zemin.py` ile aynı mantıkta, `doku` üretimi elle yapıldı.

Salon duvarı (`site/assets/duvar/salon.webp`) müşterinin ürettiği Fransız salon
görselinden `duvar.py` ile kesiliyor.

**Karo rastgele bir x'ten kesilemez.** Öyle kesilirse karonun sağ kenarı bir
sonraki karonun sol kenarının devamı olmaz: silmeler karşıya geçmez, süs
motifleri ikiye bölünür, parke kırılır. Bu geometrik bir hatadır; kenar
parlaklığını eşitlemek onu gizlemez (denendi — ton farkı 6'ya indi ama ek
yeri hâlâ görünüyordu).

Doğru yöntem iki kuraldan ibaret:

1. Kesim **düz duvara** düşsün (pilastr süslerinin ortasına değil), ek yeri
   desensiz bir alana gelsin. Seçilen nokta `XA = 428`.
2. Karonun sağ ucuna, sol ucun hemen **solundaki** şerit kopyalansın. O zaman
   `karo_N[-1] = kaynak[XA-1]` ve `karo_N+1[0] = kaynak[XA]` olur — kaynakta
   yan yana iki piksel, yani ek yeri matematiksel olarak yoktur.

Tekrar periyodu elle tahmin edilmiyor: iki pilastr arası çapraz korelasyonla
ölçülüyor (`L = 777 px`, korelasyon 0.79). Yapıştırma sınırındaki ışık farkı
kosinüs katsayısıyla düzeltiliyor ama katsayı karonun **son sütununda tam
1.0**, yoksa tam eşleşme bozulur.

Ölçülen sonuç: ek yerindeki sütun farkı **0.94**, duvarın kendi sütun
farklarının ortancası 1.67. Ek, dokunun kendi gürültüsünden daha sessiz.

> Bu yüzden bu karoya **kenar parlaklığı rampası uygulanmaz.** Rampa iki ucu
> farklı katsayılarla çarpar ve piksel eşleşmesini bozar.

`sergi.html` içindeki `BIRIM.salon` ölçüleri (`en`, `boy`, `yuvalar`) `duvar.py`
çıktısından gelir — elle değiştirilmemeli.

### Tablo çerçevesi

`site/assets/cerceve/yaldiz-{a,b,c}.webp` — gerçek bir **Louis XV oyma yaldız
çerçeve**. CSS gradyanıyla çerçeve taklidi yapmak ucuz duruyordu; oyma köşe
kartuşu ve istiridye kabuğu gradyanla üretilemez.

- Kaynak damalı zeminli JPG'di. Damalı zemin saf gri (R=G=B, chroma 0),
  yaldız 40–90 chroma taşıdığı için **doygunluk eşiğiyle** temiz ayrıldı.
  Oymanın koyu çatlakları da düşük doygunlukta olduğundan delik açıyordu;
  dışarıdan ve iç açıklıktan taşma-doldurma yapılıp kalan her boşluk
  çerçevenin kendisi sayıldı (`_cerceve.py`).
- **9-dilim `border-image`, dilim 132/140.** Köşe kartuşları bozulmadan
  kalır, yalnız kenar pervazı gerilir — bu yüzden aynı çerçeve her en-boy
  oranındaki tabloya doğru oturur. Tek parça `<img>` olarak gerilseydi
  köşeler eziliyordu.
- Çerçeve bandı tuvalin **dışına** ekleniyor (`--bw`, tablo genişliğinin
  %7.5'i): tuval kendi gerçek oranını korur, çerçeve etrafını sarar.
- Üç ton (özgün / koyu antika / sıcak bol altını) eserlere dönüşümlü
  dağıtılıyor; gerçek bir salonda bütün çerçeveler birebir aynı değildir.

## Yayın dosyaları

`site_ek.py` üretiyor: `favicon.svg`, `apple-touch-icon.png`, `robots.txt`,
`sitemap.xml`, `404.html`. Favicon **harf içermiyor** — monogram koysaydık
müşterinin gerçek adı gelince değişmesi gerekirdi; çerçeveli manzara işareti
hem ada bağlı değil hem 16 px'te okunuyor. Alan adı değişirse `site_ek.py`
içindeki `KOK` ve şablonlardaki `canonical` / `og:image` güncellenmeli.

**Kalan tek yayın adımı:** kendi alan adı. GitHub Pages için `site/CNAME`
dosyası ve alan adının DNS'inde `srdrakncix.github.io` kaydı gerekiyor.

## Dil

Üç dil: TR / EN / FR. Seçim `localStorage['cs-lang']` içinde tutuluyor ve
sayfalar arasında taşınıyor. **Üç sayfanın da kendi dil anahtarı var.**

> Galeri sayfası bir süre yarı çevrilmiş kaldı: kayıtlı dili okuyup künyeyi
> çeviriyordu ama sabit metinler ("Galeriden çık", "Başa dön", "Kapat",
> okların aria-label'ları, ipucu satırı) Türkçe gömülüydü. Şablona doğrudan
> metin yazmak yerine `t()` kullanmak kural.

Dar ekranda (<560 px) üst bardaki uzun etiketler iki satıra kırılıp dil
anahtarını eziyordu — özellikle Fransızcada. `gal_exit_k` / `gal_top_k`
kısaltmaları devreye giriyor; erişilebilir ad tam hâliyle kalıyor.

## Dikey format

Şu andaki on bir eserin on biri de yatay — seçim en-boy oranına göre
daraltıldığı için (1.49–1.57) o bantta dikey eser kalmadı. Müşterinin gerçek
işlerinde dikey tuval olacağı için `dikey_test.py` var: depo verisine
dokunmadan, bellekte bir dikey eser ekleyip test sayfaları üretiyor.

Bu testle bir tavan bulundu ve kapatıldı: duvardaki ölçek yalnız **genişliğe**
göre kuruluyordu, dolayısıyla ~197 cm'den uzun bir tuval panonun silmelerini
taşıyordu. `boyutla()` artık iki boyutu birden gözetiyor —
`ppc = min(genişlikten, yükseklikten)`. 230 cm'lik bir tuvalle sınandı:
pano içinde kalıyor, komşuları orantılı küçülüyor.

Gerçek eserler girildiğinde `python dikey_test.py` çalıştırılıp duvara
bakılmalı.

## Seri yıl aralıkları

`content.SERIES` içindeki `years` alanı artık **kullanılmıyor**: build.py
aralığı o serideki eserlerin kendi yıllarından türetiyor. Eskiden elle
yazılıydı ve eser kümesi değişince bayatlıyordu (18 eserden 11'e inilince
dördü birden yanlış oldu). Elle değer yazmayın, eserin yılını düzeltin.

## Ana menü

Menü artık elle yönetilen bir `div` değil, **gerçek bir popover**: üst katman,
Esc, dışına tıklayınca kapanma ve odak yönetimi tarayıcıdan geliyor. `#scrim`,
`K.trap` çağrısı ve `keydown` dinleyicisi bu yüzden kalktı.

**Hareketin gerekçesi.** Bir galeride önce ışıklar söner, sonra etiketler
aydınlanır: `::backdrop` zemini karartıyor, sonra satırlar sırayla netleşerek
geliyor. Sitenin açılışı da aynı dili konuşuyor — panel bir tabaka gibi yerine
konuyor, ışık ilk tablonun üzerinden bir kez geçiyor. (Daha önce reddedilen
"kapı gibi dönme" fikri, hareketin fiziksel bir karşılığı olmadığı için
çökmüştü; her jestin bir sebebi olmalı.)

**Karşılık sütunu vitrin değil.** 13 satırın 7'si metin sayfası. Saf vitrin
yapılsaydı o yedisinde sağ sütun boş kalırdı; saf metin yapılsaydı ressamın işi
menüde hiç görünmezdi. Sütun satırın türüne göre değişiyor: seri satırında o
serinin eseri, Sergiler'de sürmekte olan sergi, İletişim'de atölye satırı.

**Telefonda perde değil alt tabaka.** Ekranı kaplayan bir örtü yerine alttan
gelen, başparmakla ulaşılan bir tabaka; satırlar aşağıda, karşılık üstte ince
bir şerit. Dokunma hedefleri 46 px, `env(safe-area-inset-bottom)` hesaba
katılıyor.

### Ölçülen tarayıcı yetenekleri

Chromium 152'de 22 özelliğin 22'si de var (View Transitions, Popover,
`@starting-style`, `allow-discrete`, `interpolate-size`, anchor positioning,
scroll-driven animations, container queries…). **Ama yalnız Chromium ölçüldü.**
Safari ve Firefox burada sınanamadığı için hepsi **ilerlemeli iyileştirme**
olarak kuruldu: menü bu API'lerin hiçbiri olmadan da eksiksiz çalışır.
`interpolate-size` ve anchor positioning bilerek **hiç kullanılmadı** (şu an
yalnız Chromium'da).

> **Kural: gezinme bir animasyon API'sine bağlı olamaz.** `startViewTransition`
> geri çağrısı başlamazsa menü açık kalıyor ve tıklama hiçbir şey yapmıyordu —
> donmuş zaman çizelgesinde ölçüldü. `menuGit()` içinde 250 ms'lik zaman aşımı
> yedeği var: geçiş başlamazsa gezinme yine olur, yalnızca animasyon kaybolur.
> Aynı ders `kit.js`'teki `img.decode()` için de geçerliydi.

Açılış animasyonu **opaklık kullanmıyor**, yalnızca yükselme: `opacity: 0`'dan
başlasaydı animasyonun donduğu bir bağlamda (arka plan sekmesi) içerik görünmez
kalırdı. Açılış oturumda bir kez çalışır (`sessionStorage`).

## Bilinmesi gerekenler

- Yer tutucu görseller Art Institute of Chicago açık erişim arşivinden kamu malı
  George Inness tabloları. Seçim ölçütü **en-boy oranı** (`secim.py`), parlaklık
  değil: önceki "en açık 18" seçimi duvarda pazar reyonu gibi duruyordu — 40
  cm'lik eserin yanında 184 cm'lik eser, dikeyin yanında yatay. Artık yalnızca
  **1.50–1.59** bandındaki 11 eser alınıyor ve hepsine **aynı genişlik (132 cm)**
  veriliyor; yükseklik her eserin kendi gerçek oranından geldiği için hiçbir eser
  kırpılmıyor, yükseklik farkı en fazla %6. Tek formatta çalışan bir ressam.
- Detay görünümü tam ekran beyaz zemin olduğu için `full` genişliği **1686 px**
  (kaynağın tavanı). Müşterinin kendi fotoğrafları geldiğinde `secim.py` içindeki
  `FULL_W` yükseltilmeli.
- Sanatçı kimliği (Cemal Sağlam), biyografi, sergi ve basın listesi **kurgudur**.
- Depo public (GitHub Pages'in ücretsiz çalışması için). Kaldırmak:
  `gh repo delete srdrakncix/ressam-portfolyo-prototip`
