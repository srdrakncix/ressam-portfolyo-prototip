# Kullanıcı Araştırması — Altı Ajanın Raporları

**Tarih:** 6 Eylül 2026
**Site:** https://srdrakncix.github.io/ressam-portfolyo-prototip/ (`/`, `/mekan.html`, `/sergi.html`)
**Amaç:** Gerçek kullanıcı gözüyle "ne eksik, ne değişmeli, ne eklenmeli" sorusunun cevabı.

---

## Yöntem

Altı ajan, altı farklı meslek gözüyle siteyi dolaştı. Her birine sanat dünyasından
gerçekçi bir kimlik, o kimliğin gerçek ihtiyaçları ve ortak bir çıktı iskeleti verildi
(sayfa sayfa "ne gördüm / ne istiyorum" + öncelik etiketi, en çok istediği üç şey,
"beni siteden uzaklaştıran şey", "mobilde özellikle").

**Ekran görüntüleri:** 14 rotanın hepsi ayrı ayrı, hem masaüstü (1440 px) hem gerçek
mobil (390 px) — toplam **46 görüntü**. Etkileşim hâlleri dahil: menü açık, eser
detayı açık, yan liste açık, İngilizce ve Fransızca sürümler, 404, ve park edilmiş
sade sürümden üç rota. Üretici betik: `_cek.py`.

> **Mobil ölçüm tuzağı:** Edge'e `--window-size=390` demek Windows'un %125 ölçeklemesi
> yüzünden **492 px** viewport veriyor; `--force-device-scale-factor=1` de düzeltmiyor.
> Gerçek 390 px için iframe sarmalayıcı şart. Ajanların gördüğü mobil görüntüler
> gerçekten 390 px.

**Ajanlar:**

| # | Kim | Neye bakıyor |
|---|---|---|
| 1 | Koleksiyoner (15 yıldır çağdaş Türk resmi topluyor) | yüzey, empasto, hangisi satılık, ölçü, nasıl görürüm, kime ulaşırım |
| 2 | Galerici / küratör (Karaköy, yılda 6 sergi, 2 fuar) | iş bütünlüğü, seri tutarlılığı, CV derinliği, baskı kalitesinde görsel |
| 3 | Sanat eleştirmeni (dergi + katalog yazarı) | sanatçı metni klişe mi, alıntılanabilir mi, basın kiti, çeviri kalitesi |
| 4 | Ressam meslektaş (15 yıldır yağlı boya) | resim nasıl fotoğraflanmış, detay görebiliyor muyum, süreç anlatılıyor mu |
| 5 | Kıdemli koleksiyoner (70 yaş, gözleri zayıf, klavyeyle geziyor) | okunabilirlik, kontrast, tıklama hedefi, klavye gezinmesi |
| 6 | Sanat danışmanı (eski müzayede uzmanı) | künye eksiksiz mi, ölçüler sayfalar arası tutarlı mı, envanter mantığı |

**Ajanlara kapsam dışı denilenler:** sanatçı kimliği/biyografi/CV/sergi-basın listeleri
ve bütün görseller yer tutucu (gerçekleri yayın öncesi girilecek); alan adı henüz
bağlanmadı; ekran görüntüleri durağan olduğu için animasyonlar değerlendirilemez.

---

## DOĞRULAMA GÜNLÜĞÜ

Ajan raporları ham veridir; her somut iddia bağımsız olarak kontrol edildi.
**Bu bölüm benim doğrulamalarım, ajanların sözü değil.**

### Doğru çıkanlar

**1. Koleksiyon sayımı yanlış.**
Sayfa "11 eserin 2 tanesi koleksiyonlarda" diyor.
```
DURUMLAR: {'satilik': 9, 'ayrildi': 1, 'koleksiyonda': 1}
```
Gerçek: koleksiyonda **1**, ayrıldı **1**. "Ayrıldı" ile "koleksiyonda" aynı şey değil.

**2. Altı koleksiyon adı var, hiçbiri hiçbir esere bağlı değil.**
```
- Ardıç Sanat Koleksiyonu, İstanbul
- Batı Kanat Çağdaş Sanat Koleksiyonu, İstanbul
- Liman Kültür Merkezi, İzmir
- Atelier Nordbahn Koleksiyonu, Viyana
- Van Doorn Koleksiyonu, Rotterdam
- Özel koleksiyonlar · Türkiye, Avusturya, Hollanda
```
`WORKS` demeti (başlık, seri, not, durum) koleksiyon alanı taşımıyor.

**3. Dört serinin de yıl aralığı yanlış.** — *bu bir regresyon, aşağıya bak*
```
alacakaranlik  ilan: 2021 — 2024    gerçek: [2023, 2024]
hava           ilan: 2019 — 2023    gerçek: [2021, 2022, 2023]
topografya     ilan: 2018 — 2024    gerçek: [2022, 2023, 2024]
sabah          ilan: 2020 — 2024    gerçek: [2022, 2023, 2024]
```

**4. "52 İN" hatası gerçek.** Künyede `text-transform: uppercase` var; Türkçe locale'de
"in" → "İN" oluyor (Türkçe'de küçük i'nin büyüğü İ'dir). EN ve FR'de doğru çıkıyor.
Ayrıca birim yazımı sayfadan sayfaya değişiyor: ana sitede `88 × 132 cm | 34⅝ × 52 in`
(küçük harf), sergi duvarında `85 × 132 CM | 33½ × 52 İN` (büyük harf).

**5. `--link: #1B3FCC` sabit kodlanmış parlak mavi.**
```
mekan.html:34   --link:   #1B3FCC;
mekan.html:715  '" style="color:var(--link)">' + SITE.artist.email + '</a>'
duz.html:30     --link:   #1B3FCC;
```
E-posta bağlantısında ve odak halkasında kullanılıyor. Sitenin paletine ait değil.

**6. Telefon ve Instagram veride dolu, hiçbir sayfada basılmıyor.**
```
content.ARTIST.phone      +90 212 000 00 00
content.ARTIST.ig         @cemalsaglam
```

**7. Biyografide tekrar var.** `ARTIST.born = 1987`, `birthplace = İzmir`; `BIO`'nun ilk
paragrafı da "Cemal Sağlam 1987'de İzmir'de doğdu…" diye başlıyor. Aynı cümle üst üste.

**8. `statusLabel` veride var ama sergi sayfası kullanmıyor** — ekrandaki metin çeviri
dosyasından geliyor. İki kaynaklı veri: biri `statusLabel`'ı düzeltirse ekranda hiçbir
şey değişmez.

**9. `@media print` bloğu yok.** Sayfa yazdırılırsa duvar dokusu ve arka plan
görselleriyle çıkar.

**10. Tek esere kalıcı bağlantı yok.** `kit.js:130` yönlendirici yorumunda
`#/eser/<slug>` rotası *belgelenmiş* ve `K.workBySlug` yardımcısı yazılmış — ama hiçbir
sayfa bu rotayı kaydetmiyor. Yardımcı fonksiyon boşta duruyor.

**11. On bir eserin on biri de yatay.**
```
{'yatay': 11}
```
Dikey formatta tek eser yok. — *bu da bir regresyon, aşağıya bak*

### Yanlış çıkanlar

**A. "İnç dönüşümleri hatalı" (Ajan 3 — eleştirmen).** YANLIŞ.
```
83 cm = 32.6772 in  →  32⅝   ✓ yayında 32⅝
85 cm = 33.4646 in  →  33½   ✓ yayında 33½
86 cm = 33.8583 in  →  33⅞   ✓ yayında 33⅞
87 cm = 34.2520 in  →  34¼   ✓ yayında 34¼
88 cm = 34.6457 in  →  34⅝   ✓ yayında 34⅝
132 cm = 51.9685 in →  52    ✓ yayında 52
```
On birinin de en yakın 1/8'e yuvarlaması doğru. Ajan küçük ekran görüntüsünde **⅝ ile
⅞'i karıştırmış** — 86 cm'in doğru karşılığı olan 33⅞'i görüp 88 cm'e atfetmiş.
(Ajan 6 — danışman — aynı veriyi kontrol edip "on birinin de doğru" demiş; o haklı.)

**B. "Basın kalitesinde görsel yok" (Ajan 2 — galerici).** YARIM DOĞRU.
Aritmetik doğru: 1686 px / 132 cm = **32,4 dpi** gerçek boyutta. Ama kimse bir tabloyu
1:1 basmaz. Dergide yarım sayfa (≈12 cm) için 300 dpi'da 1417 px yeter — mevcut dosya o
iş için **yeterli**. Yetmediği yer tam sayfa veya çift sayfa reprodüksiyon (~2500–3500 px).
Yani "basın kalitesi yok" değil, "büyük reprodüksiyon için yok".

### Benim kırdıklarım (regresyon)

Bu ikisi ajanların bulduğu ama **benim yol açtığım** sorunlar:

1. **Seri yıl aralıkları bayat.** Eser sayısını 18'den 11'e indirirken `content.SERIES`
   içindeki `years` alanlarını güncellemedim. Dördü de artık yanlış.
2. **Bütün eserler yatay.** Çerçeveleri eşitlemek için seçimi en-boy oranına göre
   (1.49–1.57) daralttım; bu bantta dikey eser yok, dolayısıyla hepsi elendi. Sonuç:
   **duvar ve kartlar dikey tuvalle hiç denenmedi.** Müşterinin gerçek işlerinde
   kesinlikle dikey formatlar olacak — bu yayın öncesi test edilmesi gereken bir risk.

---

## ÇAPRAZ SAYIM — kaç ajan aynı şeyi istedi

| # | İstek | Kaç ajan |
|---|---|---|
| 1 | Yan liste tablonun üstünden çekilsin | **6 / 6** |
| 2 | Koleksiyonlar'da "Kayıt" başlığı listeye yapışık, boşluk gerek | **6 / 6** |
| 3 | Eserde yakınlaştırma / yüzey detayı | **5 / 6** |
| 4 | Basın ve yayın kayıtları bağlantılı olsun | **5 / 6** |
| 5 | Mobilde tabloya daha çok yer | **5 / 6** |
| 6 | Eser panelinde "bu eseri sor" eylemi | 4 / 6 |
| 7 | Park edilmiş sade sürüm silinmesin | 4 / 6 |
| 8 | Bağlantı rengi siteye ait değil | 4 / 6 |
| 9 | Atölye Notu'na atölye fotoğrafları | 3 / 6 |
| 10 | Tek esere kalıcı bağlantı | 3 / 6 |
| 11 | Müsait eserler listesi / duruma göre filtre | 3 / 6 |
| 12 | Mobilde yan liste tamamen kaldırılmış, geri gelsin | 3 / 6 |
| 13 | Punto büyütülsün (özellikle sergi künyesi) | 3 / 6 |
| 14 | Ana sayfaya "Sürüyor / Sırada" bloğu | 2 / 6 |
| 15 | CV (PDF) indirme | 3 / 6 |

### Uzlaşma olmayan konu

**Fransız salonu dekoru ve tek tip yaldız çerçeve:**

- **Reddeden 3:** Ajan 1 (koleksiyoner) — *"Bomonti'de dört ayda bir tuval bitiren bir
  ressamla ilgisi yok; sonradan takılmış ihtişam"*; Ajan 4 (ressam) — *"dekoratif ve
  biraz da uydurma bir sahne"*; Ajan 2 (galerici) — *"işi 1880'e ait bir nesne gibi
  okutuyor; beyaz küp seçeneği şart"*.
- **Beğenen 2:** Ajan 5 (kıdemli koleksiyoner) — *"bunu yapan adam ne yaptığını
  biliyor"*; Ajan 6 (danışman) — *"duvar fikri gerçekten iyi"*.
- **Değinmeyen 1:** Ajan 3 (eleştirmen).

**Eşit çerçeve boyutu** için de üç ajan çeşitlilik istedi — ama bu tam olarak
müşterinin/Serdar'ın açıkça talep ettiği şeydi ("pazar reyonu gibi büyüklü küçüklü
çerçeveler olmasın"). Karar sahibinin bilmesi gereken bir gerilim; ajan çoğunluğu
otomatik olarak haklı değil.

---
---

# HAM RAPORLAR

Aşağıdakiler ajanların döndürdüğü metinlerin **tamamı, geldiği gibi**. Düzeltilmedi,
kısaltılmadı. Doğru/yanlış ayrımı için yukarıdaki doğrulama günlüğüne bakın.

---

## AJAN 4 — Ressam meslektaş
*(ilk dönen rapor)*

### KİM

On beş yıldır yağlı boya çalışan, kendi atölyesi olan bir ressamım; bir meslektaşın sitesine bakarken önce boyanın yüzeyini, sonra fotoğrafın dürüstlüğünü, en son tasarımı görürüm.

### SAYFA SAYFA

**pc_sergi_17-ESER-DETAY — Eser detayı (sergi duvarı içinden)**
- GÖRDÜĞÜM: Resim 1440 px'lik ekranda yaklaşık 980 px genişlikte duruyor, sağda kocaman boş bir künye sütunu var ve resmin üstüne tıklayınca yakınlaşacağına dair hiçbir işaret yok — bir tabloya bakıp da burnumu yaklaştıramıyorum.
- İSTEK: Resmin üzerine imleç gelince büyüteç açılsın; en az 2500 px'lik bir dosyadan serbest zoom yapabileyim ve künye sütununun altına ressamın kendi seçtiği 3 detay kadrajı gelsin (fırça izinin en kalın olduğu yer, ışığın kırıldığı geçiş, imza köşesi). **[YÜKSEK]**

**pc_sergi_16-DUVAR — Sergi duvarı**
- GÖRDÜĞÜM: On bir eserin hepsi aynı altın yaldızlı barok çerçevede ve duvarda hepsi neredeyse aynı genişlikte asılı; künyede 83, 85, 86, 88 cm yazıyor ama gözümle hiçbir ölçü farkı görmüyorum.
- İSTEK: Çerçeveler tek kalıp olmaktan çıksın — hiç değilse üç seçenek (ince siyah amerikan çıtası, çıplak tuval, ahşap) ve eserler duvara gerçek santimetre oranıyla ölçeklensin; yanlarına 170 cm'lik silik bir insan silueti koyun ki 132 cm'nin ne demek olduğunu anlayayım. **[YÜKSEK]**

**pc_sergi_18-YAN-LISTE-ACIK — Duvar yan listesi**
- GÖRDÜĞÜM: Eser listesi kapalıyken bile yarı saydam biçimde soldaki tablonun tam üstüne biniyor; "Alacakaranlık", "Güz Ormanı", "Balıkçıl" yazıları resmin göğünün içinde yüzüyor.
- İSTEK: Liste kapalıyken tablonun üstünden tamamen çekilsin (ya sadece bir sekme ucu kalsın), açıkken de resmin dışına, duvar boşluğuna otursun — bir tablonun yüzüne yazı bindirilmez. **[YÜKSEK]**

**pc_mekan_07-atolye-notu — Atölye Notu**
- GÖRDÜĞÜM: "Bir resmin üzerinde ortalama dört ay çalışıyorum, katmanlar kurudukça renk değişiyor" diye yazmış ama sayfada tek bir görsel yok; kartın sağ yarısı bomboş beyaz.
- İSTEK: Bu metnin yanına gerçek atölye kanıtı gelsin: sehpadaki yarım tuval, palet, aynı resmin üç aşaması (imprimatura → ana kütleler → son glazeler) yan yana; hangi keten, hangi astar, hangi medium, verniği ne zaman çektiği yazsın. **[YÜKSEK]**

**pc_mekan_02-son-resimler — Son Resimler**
- GÖRDÜĞÜM: Sayfayı açtığımda ilk eser tamamen bulanık bir renk lekesi olarak geliyor; üstelik "11 eser, 4 seri" diyor ama tek sütun halinde alt alta akıyor, hiçbir eseri diğeriyle yan yana koyup karşılaştıramıyorum.
- İSTEK: Bulanık ara aşama kalksın (ressamın resmi hiçbir an bulanık görünmemeli); ayrıca sayfanın başına 11 eserin küçük ızgarası konsun, ordan istediğime atlayayım. **[YÜKSEK]**

**pc_mekan_03-seri-alacakaranlik — Alacakaranlık serisi**
- GÖRDÜĞÜM: Seri metni güzel ("renk bir şeyi tarif etmiyor, kayboluşunu tutuyor") ama altındaki eserlerin hangi sırayla, hangi yılda yapıldığı görsel olarak okunmuyor; seri bir yığın gibi duruyor.
- İSTEK: Seri içindeki eserler kronolojik bir şeritte gösterilsin ve her birinin altına "bu seride bu kaçıncı, ne değişti" diye bir cümle düşülsün — bir seri gelişerek doğar, bu site onu düz liste yapmış. **[ORTA]**

**pc_mekan_08-biyografi — Biyografi**
- GÖRDÜĞÜM: Metin "Viyana'da iki yıl klasik boya teknikleri üzerine çalıştı" diyor, arka planda da bir tablonun empastolu bir kırpımı duvar kağıdı gibi büyütülmüş; ama ne ressamın kendi fotoğrafı var ne atölyesinin.
- İSTEK: Metnin yanına atölyede çalışırken çekilmiş tek bir dürüst kare konsun ve arka plandaki dev tablo kırpımı kaldırılsın — bir resmi duvar kağıdı yapmak o resme yapılmış en büyük saygısızlık. **[ORTA]**

**pc_mekan_10-koleksiyonlar — Koleksiyonlar**
- GÖRDÜĞÜM: "Kayıt" başlığı bir önceki listenin son satırına yapışmış, arada nefes yok; ayrıca kayıttaki tüm eserler 83×132, 88×132, 85×132, 86×132 — on bir resmin hepsi tam 132 cm genişliğinde.
- İSTEK: "Kayıt" başlığının üstüne ayırıcı boşluk gelsin; ve ölçüler gerçek atölye ölçüleriyle değiştirilsin, çünkü hep aynı genişlik kopyala-yapıştır kokuyor ve bir ressam bunu ilk bakışta fark eder. **[ORTA]**

**pc_mekan_09-sergiler — Sergiler**
- GÖRDÜĞÜM: Dört kişisel, dört karma sergi düzgünce listelenmiş, ama hiçbirinin kurulum fotoğrafı yok ve hangi eserlerin o sergide asıldığı belli değil.
- İSTEK: Her sergi satırı tıklanır olsun; açılınca iki kurulum karesi ve "bu sergide asılan eserler" bağlantısı gelsin — ben bir ressamın işini duvarda nasıl kurduğunu görmek isterim. **[ORTA]**

**pc_mekan_13-iletisim — İletişim**
- GÖRDÜĞÜM: E-posta adresi tarayıcının varsayılan mavisiyle duruyor (sitenin hiçbir yerinde o mavi yok) ve alttaki prototip notu cümlenin ortasında "…kamu malı" diye kesiliyor.
- İSTEK: Bağlantı rengi sitenin toprak/altın paletine çekilsin, kırpılan not düzeltilsin; bir de "eser edinme" için ayrı bir satır konsun — fiyat aralığı, ödeme, nakliye ve sertifika hakkında tek cümle bile yeter. **[YÜKSEK]**

**pc_mekan_15-MENU-ACIK — Menü açık**
- GÖRDÜĞÜM: Menü açılınca beyaz kart sağa kayıyor ve "Cemal SAĞLAM" yazısının başı menünün altında kalıyor; kartın sağ üst köşesinde de kâğıt kıvrımı gibi tuhaf bir üçgen beliriyor.
- İSTEK: Kart menü açıkken kırpılmayacak kadar kaysın ya da kararsın; kâğıt kıvrımı efekti tamamen kalksın — burada kâğıt yok, tuval var, metafor tutmuyor. **[ORTA]**

**pc_duz_01-acilis — Sade sürüm açılış**
- GÖRDÜĞÜM: Açılışta tek büyük eser var ama tamamen bulanık geliyor; ayrıca sayfanın alt yarısı bomboş beyaz.
- İSTEK: Bulanık ara kare kalksın ve açılış eserinin altına "detayları gör" bağlantısı konsun; sade sürümün en büyük avantajı resmi büyük gösterebilmesi, bu avantaj şu an kullanılmıyor. **[ORTA]**

**pc_19-404 — Bulunamayan sayfa**
- GÖRDÜĞÜM: Üç dilde temiz bir hata sayfası, tek bağlantıyla ana sayfaya dönüyor.
- İSTEK: Buraya küçük bir eser kırpımı konsun ve "Sergi duvarına git" ikinci bağlantısı eklensin — kaybolmuş ziyaretçi boş bir sayfaya değil bir resme düşsün. **[DÜŞÜK]**

### EN ÇOK İSTEDİĞİM 3 ŞEY

1. **Yakınlaşma.** Her eserde serbest zoom ve ressamın seçtiği detay kadrajları. Şu an tuvalin dokusunu, empastonun kalınlığını, glazenin altındaki katmanı göremiyorum — yani resmin nasıl yapıldığını göremiyorum. Bir ressamın sitesinde en çok bunu ararım ve burada hiç yok.
2. **Ölçek ve çerçeve dürüstlüğü.** Sergi duvarında on bir eser aynı barok yaldızda ve aynı büyüklükte asılı. Çerçeveler çeşitlensin, eserler gerçek santimetre oranıyla ölçeklensin, yanına insan boyu referansı gelsin. 132 cm'lik bir tuval karşısında ne hissedeceğimi bilmek isterim.
3. **Atölye kanıtı.** Atölye Notu'nda "dört ay, katmanlar, bekleme" yazıyor ama tek bir fotoğraf yok. Sehpa, palet, yarım tuval, aynı eserin üç aşaması ve malzeme künyesi (keten, astar, medium, vernik, süre) gelsin. Meslektaş merakımı doyuran tek şey bu olur.

### BENİ BU SİTEDEN UZAKLAŞTIRAN ŞEY

Site resimleri gösteriyor ama resimlere dokunmama izin vermiyor. Her eser tek bir düz cepheden, tek bir ölçekte, tek bir kadrajda duruyor; ne kenarını görüyorum (tuvalin yan yüzü boyanmış mı, çıplak mı?), ne yüzeyini (mat mı, verniklenmiş mi, nerede parlıyor?), ne de fotoğrafın renk açısından güvenilir olup olmadığına dair bir söz var. Üstüne bir de sayfalar açılırken resimler bulanık bir aşamadan geçiyor — bir ressamın kendi işini önce bulanık göstermesi kadar ters bir şey az bulunur. Sergi duvarı ise bambaşka bir sorun: bir Fransız salonu kurgulanmış, panolarda Eyfel Kulesi motifleri var, şamdanlar yanıyor ama o ışığın hiçbiri tabloların üstüne düşmüyor, çerçevelerin duvara gölgesi yok. Ortaya İstanbul Bomonti'de yavaş yağlı boya çalışan bir ressamın işine hiç benzemeyen, dekoratif ve biraz da uydurma bir sahne çıkmış. Ayrıca ana site ile sergi duvarı iki ayrı elden çıkmış gibi: birinde sistem sans yazısıyla bembeyaz, soğuk kartlar, ötekinde altın serifli barok bir salon. Bir de tüm eserlerin genişliğinin tam 132 cm çıkması ve TR'de inç kısaltmasının "İN" diye yazılması gibi küçük ayrıntılar var; bunlar tek başına önemsiz ama üst üste gelince "buraya gerçekten bir ressam dokunmamış" hissi veriyor.

### MOBİLDE ÖZELLİKLE

Mobilde en can sıkıcı yer eser detayı: 390 px'lik telefonda resim ekranın ancak dörtte birini kaplıyor, üstünde ve altında geniş krem boşluklar duruyor, üstelik iki parmakla açıp büyütemiyorum — telefonda bir tabloya bakmanın tek anlamlı yolu tam ekran ve zoom'dur, ikisi de yok. Sergi duvarı da mobilde küçük bir pencereye sıkışmış; duvar ekranın üst yarısında, altta koyu künye kartı ve arkasından da bomboş siyah bir alan var, o alan resme verilse tablo iki katı büyüklükte görünürdü. Yatay çevirince tam ekran duvara geçen bir mod olmalı. Mobil menü ekranın neredeyse tamamını kaplıyor ve TR/EN/FR seçimi en alt kenara sıkışmış, başparmakla zor yakalanıyor. İletişim sayfasında kırpılan prototip notu mobilde daha da göze batıyor, e-posta yine varsayılan mavi. Bir de mobilde açılış sayfasında "Galeriye gir" kartı, üstündeki tek eser kadar yer kaplıyor — telefonda ilk gördüğüm şey bir buton değil, bir resim olmalı.

---

## AJAN 3 — Sanat eleştirmeni

### KİM

Bir sanat dergisi ve iki gazete için yazan, ayrıca sergi kataloglarına metin veren bir sanat yazarıyım; bu siteye "bu ressam hakkında yazılacak bir şey var mı" sorusuyla girdim.

### SAYFA SAYFA

**pc_mekan_07-atolye-notu — Atölye Notu**
- GÖRDÜĞÜM: Üç paragraflık, klişeden uzak, gerçekten bir üretim biçimini anlatan bir metin — "manzara bahane, asıl mesele havanın ağırlığı" cümlesi tek başına bir yazının girişi olabilir; ama metnin tarihi, kaynağı ve kimin ağzından yazıldığı belirtilmemiş.
- İSTEK: Metnin altına künye koyun — "Atölye notu, İstanbul, Mart 2024" ve gerekirse "Söyleşiden derlenmiştir, bkz. *Yavaş Boya*, Sanat Dünyamız 189" gibi; ayrıca 200 kelimelik bu kısa nottan ayrı, alıntılanabilir 600–800 kelimelik uzun bir sanatçı metni ekleyin. **[YÜKSEK]**

**pc_mekan_08-biyografi — Biyografi**
- GÖRDÜĞÜM: "1987'de İzmir'de doğdu" cümlesi üstteki kısa künyede ve hemen altındaki uzun paragrafın ilk cümlesinde birebir tekrarlanıyor; Viyana'daki iki yılın hangi kurumda geçtiği yazılmamış.
- İSTEK: Kısa biyografi (3 satır) ile uzun biyografiyi tekrarsız iki ayrı blok hâline getirin, Viyana'daki kurumun adını ekleyin ve sayfanın altına "Tam CV (PDF)" ile "Kısa biyografi — TR/EN/FR, kopyalanabilir" bağlantısı koyun. **[YÜKSEK]**

**pc_mekan_03-06 — Seri sayfaları (Alacakaranlık / Hava / Sessiz Topografya / Sabah)**
- GÖRDÜĞÜM: Dört serinin yıl aralıkları neredeyse tamamen üst üste biniyor (2018–24, 2019–23, 2020–24, 2021–24) ve her seriyi iki cümle tanımlıyor; bu hâliyle seriler bir üretim mantığından çok atmosfer başlıkları gibi duruyor.
- İSTEK: Her seri başlığının altına "11 eserin 4'ü · 2021–2024" gibi bir eser sayısı ve serideki işlerin künyeli listesini ekleyin; serilerin neden ayrı olduğunu bir paragrafla açıklayın. **[YÜKSEK]**

**pc_mekan_04-seri-hava — Hava**
- GÖRDÜĞÜM: Menüde ve sayfa başlığında seri "Hava", ama Sergiler ve Yayınlar sayfalarında aynı iş kümesi "Hava Raporu" olarak geçiyor.
- İSTEK: Seri adını tek bir biçimde sabitleyin ve seri sayfasına "2023'te *Hava Raporu* adıyla Payas Galeri'de sergilendi · katalog" satırını ekleyip Sergiler/Yayınlar kayıtlarına bağlayın. **[YÜKSEK]**

**pc_mekan_09-sergiler — Sergiler**
- GÖRDÜĞÜM: Kişisel/karma ayrımı doğru yapılmış ama yalnızca yıl var — ay yok, küratör yok, karma sergilerde diğer sanatçılar yok, hiçbir satır tıklanabilir değil.
- İSTEK: Her sergiye ay aralığı ve varsa küratör adı ekleyin, sergi adını o serinin sayfasına ve katalog kaydına bağlayın. **[ORTA]**

**pc_mekan_10-koleksiyonlar — Koleksiyonlar**
- GÖRDÜĞÜM: "Kayıt" başlığı üstteki listeye yapışmış (üst boşluk yok) ve altında kurumsal koleksiyon bilgisi değil bir satış envanteri var: "11 eserin 2 tanesi koleksiyonlarda. Kalanlar atölyeden temin edilebilir", *Issız Çiftlik* için de durum olarak "Ayrıldı".
- İSTEK: "Ayrıldı" gibi örtmeceleri kaldırıp her eser için "Özel koleksiyon, Rotterdam, 2022" biçiminde provenans satırı yazın; stok/temin bilgisini bu sayfadan çıkarıp ayrı bir yere alın ve "Kayıt" başlığına üst boşluk verin. **[YÜKSEK]**

**pc_mekan_11-yayinlar — Yayınlar**
- GÖRDÜĞÜM: Katalog metin yazarları adıyla anılmış (Nihal Erkut, Kaan Bilen) — bu iyi; ama ISBN, yayınevi/editör ayrımı, dil bilgisi ve hiçbir bağlantı yok, kataloglara nasıl ulaşılacağı yazmıyor.
- İSTEK: Her kayda ISBN, dil ve "Katalogdan bölüm (PDF)" ya da "Temin: yayinevi.com" satırı ekleyin; Kaan Bilen'in 2021 katalog metnini Basın'daki e-skop yazısına çapraz bağlayın. **[YÜKSEK]**

**pc_mekan_12-basin — Basın**
- GÖRDÜĞÜM: Dört künye var, hiçbiri bağlantı değil; yazı başlıkları tırnak içinde duruyor ama okunacak hiçbir şey yok — benim için bu sayfa şu an sadece bir iddia listesi.
- İSTEK: Her satırı yazının çevrimiçi adresine bağlayın; çevrimiçi olmayanlar için PDF/tarama koyun ve her kaydın altına iki satırlık alıntılanabilir bir pasaj ekleyin. **[YÜKSEK]**

**pc_mekan_13-iletisim — İletişim**
- GÖRDÜĞÜM: Tek bir e-posta var ve altındaki prototip açıklaması kutunun içinde kesiliyor — "...Art Institute of Chicago, kamu malı" diye yarım kalıyor (mobilde de aynı); basın için ayrı bir kanal, temsil eden galeri ve yüksek çözünürlüklü görsel talebi için bir yol yok.
- İSTEK: Kesilen metni düzeltin ve sayfaya ayrı bir "Basın" bloğu ekleyin: basın e-postası, temsil eden galeri, "Basın kiti (yüksek çözünürlüklü görseller + künye + fotoğraf kredisi + kullanım izni)" indirme bağlantısı. **[YÜKSEK]**

**pc_sergi_17-ESER-DETAY — Eser detayı**
- GÖRDÜĞÜM: Yıl / Teknik / Ölçü künyesi temiz ve seri etiketi ("ALACAKARANLIK") var; ama fotoğraf kredisi, imza-tarih bilgisi, bulunduğu koleksiyon ve esere ait kalıcı bağlantı yok — buna karşılık "ATÖLYEDEN TEMİN EDİLEBİLİR" satırı künyenin içinde duruyor.
- İSTEK: Künyeye "Fotoğraf: …", "Sağ altta imzalı ve tarihli", "Koleksiyon: …" satırlarını ekleyin, eser başına kalıcı URL verin ve satış satırını künyeden görsel olarak ayırın. **[YÜKSEK]**

**pc_sergi_16-DUVAR — Sergi duvarı**
- GÖRDÜĞÜM: Sol taraftaki eser listesi arkasında panel olmadan doğrudan tablonun üzerine düşüyor; yazılar resmin içinde kayboluyor, resim de yazının altında kalıyor. Ayrıca bu sayfada sanatçının adı hiçbir yerde yazmıyor.
- İSTEK: Yan listeye kapalı hâldeyken de opak bir zemin verin (18-YAN-LISTE-ACIK'taki gibi) ya da tablonun dışına taşıyın; üst şeride "Cemal Sağlam" adını ekleyin. **[YÜKSEK]**

**pc_mekan_20-DIL-EN / 20-DIL-FR — İngilizce ve Fransızca**
- GÖRDÜĞÜM: Eser adı orijinal hâliyle versal ("DAĞ SIRTI"), çevirisi altında italik ("The Ridge" / "La crête") — yani tipografik hiyerarşi ters: müze ve katalog teamülünde italik olan orijinal addır, çeviri köşeli parantez içinde ve düz yazılır.
- İSTEK: Künyeyi "*Dağ Sırtı* [The Ridge], 2023" biçimine çevirin; ayrıca EN'de "Sonbaharı kırmızıyla anlatmamaya çalıştığım bir deneme" cümlesi "not explaining autumn with red" olmuş — burada "anlatmak" *explain* değil *tell/describe*; "An attempt not to tell autumn in red" daha doğru. **[ORTA]**

**pc_sergi_21-DIL-* — Üç dilde duvar künyesi**
- GÖRDÜĞÜM: Türkçe sürümde inç birimi "52 İN" olarak çıkıyor (EN ve FR'de doğru şekilde "52 IN") — Türkçe locale'de büyük harfe çevirme hatası. Daha kötüsü, santim–inç dönüşümleri tutmuyor: 88 cm "34⅞ in" yazılmış (doğrusu 34⅝), 83 cm "32⅞ in" yazılmış (doğrusu 32⅝); 85 ve 86 cm doğru.
- İSTEK: Birim kısaltmasını `text-transform` dışında bırakın ve tüm inç değerlerini yeniden hesaplatın — bu rakamları katalog künyesine olduğu gibi kopyalıyorum. **[YÜKSEK]**
  > **NOT (doğrulama):** İnç dönüşümü iddiası YANLIŞ — on birinin de doğru. Yalnızca "İN" hatası gerçek.

**pc_duz_08-biyografi — Park edilmiş sade sürüm**
- GÖRDÜĞÜM: Sol sütunda kalıcı gezinme ve dil seçici duruyor; çalışırken asıl işime yarayan sürüm bu — ama içinde Galeri'ye hiç bağlantı yok.
- İSTEK: Bu sade sürümü silmeyin; "Basın / araştırma görünümü" olarak yayında tutun, içine Galeri bağlantısını ve bir "Yazdır" stilini ekleyin. **[ORTA]**

**pc_19-404 — 404**
- GÖRDÜĞÜM: Üç dilde, sakin, doğru kurulmuş; tek bağlantısı ana sayfaya dönüyor.
- İSTEK: Altına "Sergiler · Yayınlar · Basın · İletişim" satırı ekleyin ki kırık bir bağlantıdan gelen okur aradığı künyeye ulaşabilsin. **[DÜŞÜK]**

### EN ÇOK İSTEDİĞİM 3 ŞEY

1. **Basın kiti.** Tek bir sayfa/ZIP: 8–10 eserin baskı çözünürlüğünde görseli, her birinin tam künyesi (ad, yıl, teknik, ölçü — cm ve inç doğru), fotoğraf kredisi, kullanım izni cümlesi, kısa ve uzun biyografi ile sanatçı metni üç dilde. Şu anda yazıya koyacağım tek bir görseli yasal olarak nereden alacağımı bilmiyorum.
2. **"Eserler" dizini.** 11 işin tamamının tek sayfada, künyeli, yazdırılabilir listesi; her eser serisine, sergisine, koleksiyonuna ve varsa hakkında yazılana bağlı. Bugün bir eserin hangi sergide gösterildiğini öğrenmek için üç sayfa arasında zihnimde eşleştirme yapıyorum.
3. **Künye doğruluğu.** İnç dönüşümlerinin düzeltilmesi, Türkçedeki "İN" hatası, eser detayına fotoğraf kredisi ve provenans satırı, "Ayrıldı" yerine gerçek koleksiyon bilgisi.

### BENİ BU SİTEDEN UZAKLAŞTIRAN ŞEY

Atölye Notu'nu okuduğumda yazmak istedim — "katmanlar kurudukça renk değişiyor, bu yüzden acele edilemiyor" cümlesi klişe değil, bir yöntem beyanı; "manzara bahane, asıl mesele havanın ağırlığı" da öyle. Yani turnusol kâğıdı geçti. Beni uzaklaştıran şey metin değil, metnin etrafındaki boşluk: bu iddianın işlerde nasıl karşılık bulduğunu takip edemiyorum. Seriler adlandırılmış ama yıl aralıkları birbirinin içinde, hangi eserin hangi seriye ait olduğu ancak duvar sayfasında tek tek tıklayarak anlaşılıyor, "Alacakaranlık" aynı anda bir seri, bir sergi, bir katalog ve bir eser adı — bir yazıda bu dört şeyi ayırt etmem gerekir, site bana bunu vermiyor. Basın sayfasında dört yazı adı var ama hiçbirini okuyamıyorum; Yayınlar'da beş katalog var ama hiçbirine ulaşamıyorum. Ve en can sıkıcısı: Koleksiyonlar sayfası kurumsal bir provenans listesi gibi başlayıp "11 eserin 2 tanesi koleksiyonlarda, kalanlar atölyeden temin edilebilir" diye bir stok bildirimine dönüşüyor, eser detayının künyesinin içine de "atölyeden temin edilebilir" satırı yerleşmiş. O satırı gördüğüm anda sayfanın beni bir okur olarak değil, potansiyel bir alıcı olarak muhatap aldığını anlıyorum — ve bir ressam hakkında yazarken en istemediğim şey, galeri fiyat listesinden alıntı yapıyormuş hissidir. Satış tarafı olsun, ama künyeden ayrı bir yerde olsun.

### MOBİLDE ÖZELLİKLE

Metin sayfaları mobilde masaüstünden daha iyi: 390 px'te beyaz kart tam genişliği kullanıyor, satır uzunluğu 40–45 karakter civarında, Atölye Notu ve Yayınlar rahat okunuyor — masaüstünde ise aynı metin geniş kartın yalnızca sol yarısında sıkışıyor, sağ yarı boş duruyor. Buna karşılık sergi duvarı mobilde ciddi biçimde budanmış: yan eser listesi tamamen kaybolmuş, dolayısıyla 11 işin arasında sıçrayamıyorum, aradığım eseri bulmak için tek tek kaydırmam gerekiyor — telefonda bir sergiyi tararken en çok ihtiyaç duyduğum şey tam da o listedir. Duvar künyesindeki ölçü satırı da mobilde iki satıra bölünüyor ve "83 × 132 / CM | 32⅞ × 52 İN" diye kopuyor; hem yanlış dönüşüm hem de kırık dizgi aynı karede. İletişim sayfasındaki prototip açıklaması mobilde de aynı yerden kesiliyor, yani sorun dar ekran değil, kutunun sabit yüksekliği. Son olarak mekan sayfalarının hiçbirinde altta bir künye şeridi yok: telefonda bir seri sayfasını okuyup bitirdiğimde iletişime ya da basın bilgisine gitmek için tekrar yukarı çıkıp hamburger menüyü açmam gerekiyor — sayfa sonuna "İletişim · Basın · Yayınlar" satırı koymak bunu çözer.

---

## AJAN 5 — Kıdemli koleksiyoner (erişilebilirlik)

### KİM

Kırk yıldır resim toplayan, gözü iyi ama gözleri artık zayıf, klavyeyle gezinen, on saniyede aradığını bulamazsa sekmeyi kapatan yetmiş yaşında bir koleksiyoncuyum.

### SAYFA SAYFA

**pc_mekan_01-acilis — Açılış**
- GÖRDÜĞÜM: Beyaz bir kart içinde tek bir resim, altında künye; arkada aynı resmin dev bir detayı fon olarak akıyor — sakin ve ciddi, bunu beğendim.
- İSTEK: Künye satırlarını (`2023 / Tuval üzerine yağlı boya / 88 × 132 cm`) 12px'ten en az 15px'e çıkarın; şu an başlığın yarısı kadar bile değil ve ilk gördüğüm bilgi bu. **[YÜKSEK]**

**pc_sergi_16-DUVAR — Sergi duvarı**
- GÖRDÜĞÜM: Fransız salonu duvarı çok güzel kurulmuş, ama sol kenardaki eser listesi doğrudan tablonun ÜSTÜNE binmiş; italik, soluk, okunmuyor — tabloyu da kirletiyor.
- İSTEK: Yan listeyi duruş hâlinde `opacity: .5` ile göstermeyin; ya arkasına tam opak koyu bir şerit koyun ya da kapalı tutup "Eserler (11)" diye bir düğmeye alın. Şu hâliyle hem liste okunmuyor hem tablo bozuluyor. **[YÜKSEK]**

**pc_sergi_18-YAN-LISTE-ACIK — Yan liste açık**
- GÖRDÜĞÜM: Fare üstüne gelince liste aydınlanıyor ve gayet okunur oluyor — demek ki doğrusunu zaten yapmışsınız, sadece kapalıyken saklıyorsunuz.
- İSTEK: Bu açık hâli varsayılan yapın; satır yüksekliğini 29px'ten 44px'e çıkarın, elim titrerken "Kıyı" yerine "Balıkçıl"a tıklıyorum. **[YÜKSEK]**

**pc_sergi_17-ESER-DETAY — Eser detayı**
- GÖRDÜĞÜM: Sitenin en iyi sayfası. Açık zemin, net künye tablosu, `4 / 11` sayacı, ok tuşları çalışıyor. Sağ panelin alt yarısı tamamen boş.
- İSTEK: Resme tıklayınca yakınlaştırma (zoom) ekleyin. Ben fırça izini, tuval dokusunu, imzayı görmeden hiçbir eseri ciddiye almam; kodda hiçbir zoom yok ve bu bir resim sitesi için en büyük eksik. **[YÜKSEK]**

**pc_mekan_13-iletisim — İletişim**
- GÖRDÜĞÜM: Bir e-posta adresi, bir semt adı, iki cümle. Hepsi bu.
- İSTEK: Telefon numarası, temsil eden galeri(ler)in adı ve "Bu eseri sormak istiyorum" diyebileceğim bir eser-talep bağlantısı ekleyin. Ciddi bir alıcı e-posta yazmadan önce kiminle muhatap olduğunu bilmek ister. **[YÜKSEK]**

**pc_mekan_15-MENU-ACIK — Menü**
- GÖRDÜĞÜM: Sitenin en iyi düşünülmüş parçası — iri satırlar, rahat hedefler, "Galeri" ayrı vurgulanmış. Burada hiç zorlanmadım.
- İSTEK: En alttaki `TR · EN · FR` 11px ve soluk gri; menünün geri kalanı bu kadar cömertken burası cimri. Diğer satırlarla aynı boyda üç ayrı düğme yapın. **[ORTA]**

**pc_mekan_09-sergiler — Sergiler**
- GÖRDÜĞÜM: Kişisel/Karma ayrımı doğru kurulmuş, kronoloji temiz. Ama 1440px'lik ekranda yazı sadece soldaki 200px'e sıkışmış, kartın sağı bomboş.
- İSTEK: Liste metnini 12px'ten 15px'e çıkarıp metin sütununu genişletin; ekranın dörtte üçü boşken yazıyı küçültmenin bir mazereti yok. **[YÜKSEK]**

**pc_mekan_10-koleksiyonlar — Koleksiyonlar**
- GÖRDÜĞÜM: "11 eserin 2 tanesi koleksiyonlarda" cümlesi tam benim aradığım türden dürüst bilgi — bunu yapan az. Ama "Kayıt" başlığı üstündeki listeye yapışmış, aralık yok.
- İSTEK: "Kayıt" başlığının üstüne boşluk koyun ve müze/kurum koleksiyonlarını özel koleksiyonlardan görsel olarak ayırın — benim için bu ikisi bambaşka şeyler. **[ORTA]**

**pc_mekan_11-yayinlar — Yayınlar**
- GÖRDÜĞÜM: Beş katalog ve söyleşi listelenmiş, sayfa sayıları ve metin yazarları da verilmiş — doğru bilgiler.
- İSTEK: Hiçbirinin bağlantısı yok. Katalogları PDF olarak ya da hiç değilse "temin edilebilir/tükendi" notuyla verin; ayrıca bu sayfada hamburger düğmesi krem zemin üstünde krem kalıyor, kayboluyor. **[ORTA]**

**pc_mekan_12-basin — Basın**
- GÖRDÜĞÜM: Dört yazı, yazar ve yayın adıyla düzgün künyelenmiş.
- İSTEK: Yazıların bağlantısını verin ya da her birinden iki satır alıntı koyun. Şu hâliyle bana "hakkımda yazdılar" diyor ama ne yazdıklarını okuyamıyorum. **[ORTA]**

**pc_mekan_08-biyografi — Biyografi**
- GÖRDÜĞÜM: Kısa, abartısız, iyi yazılmış. "İşin büyük kısmı beklemekle geçiyor" cümlesi hoşuma gitti.
- İSTEK: Sayfanın altına "Tam CV (PDF)" bağlantısı koyun — eğitim, ödül, rezidans, tam sergi listesi. Alacağım işi arşivleyeceğim, bunlar bana lazım. **[ORTA]**

**mb_sergi_16-DUVAR — Sergi duvarı (mobil)**
- GÖRDÜĞÜM: Tablo telefonun ancak yarısını kaplıyor, altındaki künye kutusu diğer yarısını yiyor; künye satırı 10,5px büyük harf ve harf aralıklı — okuyamıyorum.
- İSTEK: Tabloya daha çok yükseklik verin, künye kutusunu aşağı çekilebilir yapın ve `TUVAL ÜZERİNE YAĞLI BOYA · 83 × 132 CM` satırını büyük harften çıkarıp 14px normal yazıya çevirin. **[YÜKSEK]**

**mb_mekan_15-MENU-ACIK — Menü (mobil)**
- GÖRDÜĞÜM: Parmağım kalın ama bu menüde hiç ıskalamadım; satırlar iri ve aralıklı. Örnek alınacak iş.
- İSTEK: En alttaki dil satırı ekranın en dibinde yarı kesik duruyor; menüyü kaydırılabilir yapın ya da dilleri yukarı alın. **[ORTA]**

**pc_duz_01-acilis — Sade sürüm**
- GÖRDÜĞÜM: Solda hep duran bir menü, ortada resim, sağda "Sürüyor / Sırada" sergi bilgisi. Açıkçası benim gibi biri için ana sürümden daha kullanışlı — nerede olduğumu hiç kaybetmiyorum.
- İSTEK: Bu sürümü çöpe atmayın; ana sitede bir yere "Sade görünüm" bağlantısı koyun. Ayrıca sağdaki künye sağa dayalı, okumak zor — sola dayayın. **[ORTA]**

**pc_19-404 — Bulunamadı**
- GÖRDÜĞÜM: Üç dilde tek cümle ve ana sayfaya dönüş bağlantısı. Sade, doğru.
- İSTEK: "Cemal Sağlam — Resim" bağlantısının yanına bir de "Sergi duvarına git" ekleyin; kaybolmuş insanı boş bir sayfaya değil esere götürün. **[DÜŞÜK]**

**pc_mekan_02-son-resimler / seri sayfaları**
- GÖRDÜĞÜM: "11 eser, 4 seri. Yeniden eskiye." iyi bir özet. Ama seri açıklamaları (`Günün bittiği, gecenin başlamadığı o kısa aralığın resimleri...`) 12px soluk gri — sanatçının söylediği en anlamlı şeyler en küçük puntoda.
- İSTEK: Seri açıklamalarını 16px'e çıkarıp koyulaştırın; bunlar dipnot değil, ana metin. **[ORTA]**

### OKUYAMADIĞIM / ZORLANDIĞIM YERLER

- **Sergi duvarı, sol yan liste** — Eser adları tablonun üstünde, yarı saydam, italik serif. Kodda `opacity: .5` ile duruyor; "Kıyı 2023" ve "Balıkçıl 2023" satırlarını hiç okuyamadım.
- **Sergi duvarı, TR/EN/FR** — 10,5px (mobilde 10px) ve yazı rengi %42 saydam. Koyu zeminde neredeyse görünmez, üstelik dokunma hedefi 22×15px kadar; tablette üç kere ıskaladım.
- **Sergi duvarı, "ÖZEL KOLEKSİYONDA" satırı** — mobilde 10px. Bir eserin satılık olup olmadığı benim için sayfadaki en önemli bilgi ve sayfadaki en küçük yazı.
- **Sergi duvarı, alttaki "KAYDIRARAK DUVAR BOYUNCA İLERLEYİN" ipucu** — 11px, %42 saydam. Ne yapmam gerektiğini söyleyen tek cümle ve okunmuyor.
- **Sergi duvarında ok düğmeleri** — mobilde 34×34px. Titreyen elle küçük.
- **Bütün içerik sayfalarında liste ve gövde metni** — 12px. Kontrast fena değil (#4a4a4a), sorun tamamen boyut. Ekranın dörtte üçü boşken bunu anlayamıyorum.
- **Bütün sayfalardaki alt dipnot** — 11px, #6a6a6a. Yakınlaştırmadan okunmuyor.
- **"Yayınlar" sayfasında hamburger düğmesi** — Arkadaki resim açık renk olunca beyaz düğme zemine karışıyor; menünün nerede olduğunu aradım.
- **İletişimdeki e-posta bağlantısı** — Tarayıcının ham mavisi (#1B3FCC). Bu kadar özenli bir sitede rengi ayarlanmamış tek unsur, sırıtıyor.

**Hakkını vereyim:** Sekme tuşuyla gezinme çalışıyor, odak halkası (altın çerçeve) her yerde görünür, sergide sağ/sol ok tuşları ve Esc çalışıyor, hareket azaltma ayarına da uyulmuş. Bu dördünü yapan site az. Sorun erişilebilirlik altyapısında değil, punto ve kontrast tercihlerinde.

### EN ÇOK İSTEDİĞİM 3 ŞEY

1. **Eser detayında yakınlaştırma.** Fırça izini görmeden hiçbir tabloyu ciddiye alamam. Şu an sitede hiçbir zoom yok.
2. **Bütün gövde metnini 12px'ten 15-16px'e çıkarın, dipnotları 11px'ten 13px'e.** Özellikle sergi duvarındaki 10px'lik künye ve durum satırları. Yer yok değil — ekranın yarısı boş.
3. **Sergi duvarındaki yan listeyi kapalıyken de okunur yapın** ve mobil/tablette de gösterin. Şu an 980px altında liste tamamen kaldırılmış; telefonda duvarda ne olduğunu görmek için tek tek kaydırmaktan başka yol yok.

### BENİ BU SİTEDEN UZAKLAŞTIRAN ŞEY

Sergi duvarını açtığımda ilk hissim "bunu yapan adam ne yaptığını biliyor" oldu — o Fransız salonu duvarı, şamdanların ışığı, çerçevelerin oturuşu gerçekten iyi. Sonra sol kenardaki eser listesini okumaya çalıştım ve okuyamadım. Sonra dili değiştirmek istedim, o üç minik harfe iki kere ıskaladım. Sonra tabloya yaklaşmak istedim, yapamadım. Sonra bir eserin satılık olup olmadığına baktım, cevap oradaydı ama sayfadaki en küçük puntoyla yazılmıştı. Beni uzaklaştıran şey tasarımın kötü olması değil — tam tersine, tasarım iyi ve tasarımcı belli ki inceliği "sessizlik" ile eşitlemiş: önemli her bilgi bir tık daha soluk, bir punto daha küçük yapılmış ki atmosfer bozulmasın. Ama ben atmosfer için gelmedim, eser için geldim. Bir müzede duvar etiketini okuyamadığımda "ne zarif" demem, "beni hesaba katmamışlar" derim. Bu site şu hâliyle iyi gören kırk yaşındaki bir küratör için tasarlanmış; parayı ödeyecek olan yetmişindeki adam için değil.

### MOBİLDE ÖZELLİKLE

Şaşırtıcı bir şekilde mobil ana sayfalar masaüstünden daha rahat okunuyor — beyaz kart telefonun genişliğini kullanıyor, yazılar orantılı büyümüş, "Sergiler" ve "Koleksiyonlar" sayfalarını gözlüğümü takmadan okudum. Mobil menü ise sitenin en başarılı parçası: iri, aralıklı, ıskalanmayacak satırlar. Bunlar iyi.

Kötü olan tek yer sergi duvarının mobil hâli. Tablo ekranın ancak yarısını kaplıyor (kodda `54vh - 54px`), diğer yarısını künye kutusu ve boşluk yiyor — yani telefonda tabloyu masaüstünden çok daha küçük görüyorum, oysa telefonda ekran zaten küçük. Üst bardaki ÇIK / TR EN FR / BAŞA düğmeleri 31px yüksekliğinde, dil harfleri onun da yarısı; başparmağımla üçünü de ıskaladım. Yan eser listesi 980px altında tamamen kaldırılmış, dolayısıyla telefonda sergide ne olduğunu bir bakışta göremiyorum, sadece kaydırabiliyorum — sabırsız biri için bu tek başına siteyi kapatma sebebi. Bir de künye kutusundaki "2024 · TUVAL ÜZERİNE YAĞLI BOYA · 83 × 132 CM" satırı büyük harf, harf aralıklı ve 10,5px; büyük harf zaten okumayı yavaşlatır, bu boyutta imkânsız hâle geliyor.

Öneri: mobilde tabloya en az `70vh` verin, künye kutusunu aşağıdan çekilen bir panel yapın, üst bardaki bütün hedefleri 44px'e çıkarın ve yan listeyi mobilde "Eserler (11)" düğmesi olarak geri getirin.

---

## AJAN 1 — Koleksiyoner

### KİM

On beş yıldır çağdaş Türk resmi toplayan, koleksiyonunda otuz kadar iş bulunan bir özel koleksiyoncuyum; satın almadan önce eseri mutlaka atölyede görürüm ama ilk elemeyi internette yaparım.

### SAYFA SAYFA

**pc_mekan_01-acilis — Açılış**
- GÖRDÜĞÜM: Beyaz bir kartın içinde "Cemal SAĞLAM" ve tek bir tablo; kim olduğunu, ne yaptığını, nerede olduğunu söyleyen tek satır yok.
- İSTEK: Adın altına tek satır konum ve tanım koyun — "Ressam · İstanbul · Tuval üzerine yağlı boya" — ve sağ üste açılışta görünecek şekilde "Sürüyor: Alacakaranlık, Ardıç Sanat, İstanbul" / "Sırada: Hava Raporu, Payas Galeri, 2025" bloğunu ekleyin. Bu bilgi sade sürümde (pc_duz_01) var, seçilen sürümde kaybolmuş; benim için en pahalı kayıp bu, çünkü işi canlı nerede göreceğimi buradan öğreniyorum. **[YÜKSEK]**

**pc_mekan_02-son-resimler — Son Resimler**
- GÖRDÜĞÜM: "11 eser, 4 seri" yazıyor ama alt alta tek sütun, her eser için bir ekran; on birini görmek için uzun uzun kaydırmam gerekiyor ve hiçbir yerde bütünü bir arada göremiyorum.
- İSTEK: Sayfanın başına bir kontak baskı ızgarası (3–4 sütun küçük görsel + ad/yıl/ölçü) koyun ve üstüne iki filtre ekleyin: seriye göre ve **duruma göre ("Müsait" / "Koleksiyonda")**. Ben ilk ziyarette "hangileri hâlâ alınabilir" sorusunun cevabını otuz saniyede istiyorum. **[YÜKSEK]**

**pc_mekan_03-seri-alacakaranlik / 04 / 05 / 06 — Seri sayfaları**
- GÖRDÜĞÜM: Seri metni iyi yazılmış, künyeler doğru (yıl, teknik, cm ve inç); ama her eser aynı ölçüde gösteriliyor ve 132 cm'lik bir tuvalle 88 cm'lik bir tuval ekranda aynı büyüklükte duruyor.
- İSTEK: Serideki eserleri gerçek en-boy ORANLARINA göre değil, birbirlerine göre gerçek BÜYÜKLÜK oranıyla dizin (büyük tuval ekranda da büyük görünsün) ve künyeye derinliği/çerçeve durumunu ekleyin: "88 × 132 × 4 cm · çerçevesiz" gibi. Ölçüyü duvarımda hayal edebilmem lazım. **[ORTA]**

**pc_mekan_07-atolye-notu — Atölye Notu**
- GÖRDÜĞÜM: Sitenin en iyi metni burada; "dört ay çalışıyorum, üçte biri boya sürmek" cümlesi bana ressamın ciddi olduğunu anlatan tek şey. Ama tamamen metin, tek bir atölye fotoğrafı yok.
- İSTEK: Bu sayfaya 3–4 atölye kadrajı ekleyin: yarım kalmış bir tuval, palet, kuruyan katman, bir eserin yüzey yakın çekimi. Yağlı boya alan biri için empasto ve vernik görüntüsü, biyografiden daha inandırıcıdır. **[YÜKSEK]**

**pc_mekan_08-biyografi — Biyografi**
- GÖRDÜĞÜM: Sayfanın başında "1987'de İzmir'de doğdu." yazıyor, hemen altındaki ilk paragraf "Cemal Sağlam 1987'de İzmir'de doğdu..." diye tekrar başlıyor — aynı cümle üst üste iki kez.
- İSTEK: Tekrarı temizleyin (üstteki iki satır kalsın, paragraf "Mimar Sinan Güzel Sanatlar Üniversitesi Resim Bölümü'nü bitirdi..." diye başlasın) ve sayfanın altına "Tam özgeçmişi indir (PDF)" bağlantısı koyun. Ciddi bir alım öncesi CV'yi dosyalıyorum. **[ORTA]**

**pc_mekan_09-sergiler — Sergiler**
- GÖRDÜĞÜM: Kişisel/karma ayrımı doğru yapılmış, temiz bir liste; ama sadece yıl var, ay yok ve hiçbir galeriye bağlantı yok.
- İSTEK: Her satıra ay aralığı ekleyin ("Ekim–Aralık 2024") ve galeri adını galerinin sitesine bağlayın; ayrıca satırın yanına o serginin sayfasına/kataloğuna giden bir bağlantı koyun. Bir sanatçının kurumsal geçmişini doğrulamamın yolu bu bağlantılar. **[ORTA]**

**pc_mekan_10-koleksiyonlar — Koleksiyonlar**
- GÖRDÜĞÜM: İki sorun var. Birincisi "Kayıt" başlığı bir üstündeki listeye yapışık, arada hiç boşluk yok — sanki listenin son maddesiymiş gibi duruyor (mobilde de aynı). İkincisi, bu bölüm bana yalnızca ALINAMAYACAK iki eseri gösteriyor; işime yarayacak olan tam tersi.
- İSTEK: "Kayıt" başlığına üstten boşluk verin ve bu tabloyu 11 eserin TAMAMINI kapsayacak şekilde genişletin (no · ad · yıl · ölçü · durum), satırlar eser sayfasına tıklanabilir olsun. Ayrıca "Ayrıldı" ifadesi ne demek anlaşılmıyor — satıldı mı, galeriye mi verildi, rezerve mi? Ya açık yazın ya kaldırın. **[YÜKSEK]**

**pc_mekan_11-yayinlar — Yayınlar**
- GÖRDÜĞÜM: 96 sayfalık katalog, 72 sayfalık katalog, söyleşi — hepsi listelenmiş ama hiçbirine ulaşmanın yolu yok.
- İSTEK: Her yayının yanına ya bir PDF/örnek sayfa bağlantısı ya da "Katalog isteyin" mailto bağlantısı koyun. Elimde katalog olmayan bir sanatçının kataloğunu okumak isterim; listeyi görüp erişememek can sıkıyor. **[ORTA]**

**pc_mekan_12-basin — Basın**
- GÖRDÜĞÜM: Dört başlık, yazar ve mecra var; hiçbiri bağlantılı değil, alıntı da yok.
- İSTEK: Çevrimiçi olanları (e-skop, Argonotlar) doğrudan bağlayın, basılı olanlardan iki üç cümlelik alıntı verin. Bağlantısız basın listesi doğrulanamaz, doğrulanamayan liste beni ikna etmez. **[ORTA]**

**pc_mekan_13-iletisim — İletişim**
- GÖRDÜĞÜM: Sadece bir e-posta adresi, mahalle adı ve iki cümle. Üstelik e-posta bağlantısı tarayıcının varsayılan parlak mavisiyle çıkıyor — sitenin geri kalanının ölçülü paletinin içinde tek başına duruyor ve sayfayı yarım bırakılmış gösteriyor. Sade sürümde (pc_duz_13) durum daha kötü: sol menüdeki "İletişim" mor (ziyaret edilmiş bağlantı rengi) ve alttaki not metninin içindeki bazı kelimeler mavi/mor.
- İSTEK: Bütün bağlantıların rengini siteye uydurun (varsayılan mavi/mor kalmasın); iletişim bloğuna telefon, WhatsApp ve Instagram ekleyin (veride `phone` ve `ig` zaten var ama hiç basılmıyor); "Atölye ziyareti için randevu isteyin" diye konusu önceden dolu bir mailto düğmesi ve "genellikle 2 iş günü içinde dönülür" gibi bir yanıt süresi yazın. Bir de tam adres/kroki isterim — Bomonti tek başına adres değil. **[YÜKSEK]**

**pc_mekan_15-MENU-ACIK — Menü**
- GÖRDÜĞÜM: Menüde seriler ve sanatçı bölümleri var; ama "Eserler" diye tek bir liste yok, "Müsait eserler" diye bir giriş hiç yok.
- İSTEK: Menüye "Müsait Eserler" başlığını ekleyin ve varsayılan olarak yalnızca satılabilir işleri gösteren o listeye bağlayın. Menüde beni doğrudan satın alma niyetime götüren bir kapı olmalı. **[YÜKSEK]**

**pc_sergi_16-DUVAR — Sergi duvarı**
- GÖRDÜĞÜM: Eserler bir Fransız salonunun yeşil lambri duvarına, altın yaldızlı barok çerçevelerle asılmış; panolarda Eyfel Kulesi motifi ve şamdanlar var. Ayrıca sol taraftaki eser listesi doğrudan tablonun ÜZERİNE biniyor, hem listeyi hem tabloyu okunmaz hale getiriyor.
- İSTEK: Salonu sadeleştirin — nötr bir galeri duvarı, sanatçının gerçekten kullandığı çerçeve (ya da çerçevesiz gergi), tek bir yumuşak ışık. Bu Belle Époque dekoru çağdaş bir Türk manzara ressamına ait değil ve bana "hazır şablon" hissi veriyor; ben tam olarak bu tür sonradan takılmış ihtişamdan kaçarım. Yan listeyi de tablonun üstünden çekin, kendi koyu şeridine alın. **[YÜKSEK]**

**pc_sergi_17-ESER-DETAY — Eser detayı**
- GÖRDÜĞÜM: Yıl, teknik, ölçü, sanatçı notu ve "ATÖLYEDEN TEMİN EDİLEBİLİR, İSTANBUL" yazıyor — yani eser satılık. Ama bu sayfada hiçbir iletişim yolu yok; sergi bölümünün tamamında tek bir e-posta bağlantısı bile bulunmuyor, çıkış yalnızca "KAPAT" ve "GALERİDEN ÇIK".
- İSTEK: Bu panele iki şey koyun: (1) "Bu eseri sormak istiyorum" düğmesi — konusu eserin adı ve numarasıyla önceden dolu bir e-posta açsın; (2) bir fiyat aralığı ya da en azından "Fiyat için yazın · KDV dahil · nakliye hariç" satırı. Ayrıca imza/tarih konumu, derinlik, çerçeve durumu, orijinallik belgesi olup olmadığı ve varsa serginin/kaydın geçmişi burada yazmalı. Rakam görmeden ilk elemeyi yapamıyorum. **[YÜKSEK]**

**pc_sergi_17-ESER-DETAY — Eser detayı (yüzey)**
- GÖRDÜĞÜM: Tablo tek bir orta boy görselle gösteriliyor; büyütme, yakınlaştırma veya ayrıntı kadrajı yok. İndirdiğim görsel 1686 piksel ve 60 KB'lık bir webp — yüzeyi okumak için fazla sıkıştırılmış.
- İSTEK: Her esere tıklanabilir yakınlaştırma (en az 3000 piksel genişlik) ve iki adet ayrıntı kadrajı ekleyin: bir yüzey/empasto yakın çekimi, bir de yandan ışıkla çekilmiş doku fotoğrafı. Yağlı boyada aldığım şey yüzeydir; onu göremezsem atölyeye gitmeye gerek duymam. **[YÜKSEK]**

**pc_sergi_18-YAN-LISTE-ACIK — Yan liste açık**
- GÖRDÜĞÜM: Liste açıldığında da tablonun üstünde duruyor, adlar tablonun açık gökyüzünde kayboluyor; hangi eserde olduğumu ancak alttaki künyeden anlıyorum.
- İSTEK: Listeye tam opak bir arka plan ve her satıra 40×28 piksellik küçük bir eser görseli ekleyin; ayrıca satırların yanına durumu (Müsait / Koleksiyonda) yazın ki listeden doğrudan seçebileyim. **[ORTA]**

**pc_mekan_20-DIL-EN / 21-DIL-EN — İngilizce**
- GÖRDÜĞÜM: İngilizceye geçince eser adlarının altına İtalik İngilizce karşılıkları geliyor ("The Ridge", "Autumn Wood") — bu güzel ve doğru bir karar.
- İSTEK: Aynı özeni ölçülere ve fiyata da gösterin: yabancı bir alıcı için inç ölçüsü zaten var, yanına para birimi belirtilmiş bir fiyat aralığı ve "yurt dışı nakliye/sigorta hakkında" tek satırlık bir not ekleyin. Rotterdam ve Viyana koleksiyonlarından bahseden bir sanatçının sitesinde bu eksik olmamalı. **[ORTA]**

**pc_19-404 — 404**
- GÖRDÜĞÜM: Üç dilde temiz bir 404, ana sayfaya tek bağlantı.
- İSTEK: Bağlantının yanına "Son Resimler" ve "Sergi duvarı" kısayollarını da koyun; kırık bir bağlantıdan gelen ziyaretçiyi işlere iki tıkta ulaştırın. **[DÜŞÜK]**

**pc_duz_01-acilis — Park edilmiş sade sürüm**
- GÖRDÜĞÜM: Açıkçası bu sürüm bana daha çok iş görüyor: solda tüm bölümler tek bakışta, sağda "Sürüyor / Sırada" bilgisi, ortada eser. Hiçbir dekor yok ve tam da bu yüzden ciddi duruyor.
- İSTEK: Bu sürümü çöpe atmayın; seçilen sürüme onun iki kazanımını taşıyın — kalıcı sol/üst gezinme ve "Sürüyor / Sırada" bloğu. Hamburger menü, her bölüme gitmek için ekstra bir tıklama demek ve sekiz bölümlü bir sitede bunu masaüstünde ödemek istemem. **[ORTA]**

### EN ÇOK İSTEDİĞİM 3 ŞEY

1. **Her eserin yanında bir eylem ve bir rakam.** Eser detayında ve künyelerde "Bu eseri sormak istiyorum" düğmesi (konusu eser adı ve numarasıyla dolu) ve bir fiyat aralığı. Şu anda "Müsait" yazan bir tabloya bakıp ne yapacağımı bilmiyorum; sergi bölümünde iletişime giden tek bir bağlantı bile yok.
2. **Yüzeyi görebilmek.** Tam ekran yakınlaştırma ve her eser için en az iki ayrıntı kadrajı — biri yandan ışıkla çekilmiş doku fotoğrafı. Bunlar olmadan yağlı boya için ilk elemeyi yapamam.
3. **Müsait eserler listesi.** Menüde ayrı bir başlık, seri ve duruma göre filtrelenebilen, ölçü ve yılı yan yana gösteren bir ızgara. Şu an bunun tam tersi var: "Koleksiyonlar" sayfası sadece alamayacağım iki işi listeliyor.

### BENİ BU SİTEDEN UZAKLAŞTIRAN ŞEY

Sergi duvarı. Altın yaldızlı barok çerçeveler, yeşil Fransız lambrisi, şamdanlar ve panolardaki Eyfel Kulesi motifleri — bunların hiçbiri Bomonti'de dört ayda bir tuval bitiren bir ressamla ilgili değil. Bu bana "eser kendi başına yetmiyor, sahne kuralım" demiş gibi geliyor; oysa Atölye Notu'ndaki "kalanı bakmak ve beklemek" cümlesi tek başına o salonun tamamından daha ikna edici. Üstelik o çerçeveler eserin gerçekte nasıl sunulduğu konusunda beni yanıltıyor — ben o tabloyu alsam duvarıma o çerçeveyle gelmeyecek. Buna bir de tipografik ikilik ekleniyor: ana sitede düz Arial (Windows'ta "Helvetica Neue" yok, doğrudan Arial'a düşüyor), sergide Cormorant Garamond — iki ayrı sanatçının sitesi gibi duruyorlar. Sitenin ciddi yarısı (seri metinleri, künyeler, atölye notu) gerçekten iyi; onu gösterişli yarısı aşağı çekiyor.

### MOBİLDE ÖZELLİKLE

- **mb_sergi_16-DUVAR:** Sergi duvarı mobilde tersine dönüyor. 390 piksellik ekranda tablo yaklaşık 250×160 piksel kalıyor, geri kalan her şeyi lambri, çerçeve ve şamdan yiyor — ekranın belki %15'i esere ayrılmış. Mobilde dekoru tamamen kapatın, tabloyu tam genişlikte gösterin.
- **mb_sergi_17-ESER-DETAY:** Görselin üstünde yalnızca "KAPAT" yazan yüksek ve bomboş bir bant var; telefonda ilk gördüğüm şey boşluk oluyor. Görseli yukarı çekin, kapatmayı küçük bir köşe düğmesine alın.
- **mb_mekan_01-acilis:** Telefonda "Galeriye gir" kartı ilk ekranda ve tek eserin hemen altında duruyor; yani mobilde sitenin vitrini eser değil, dekor oluyor. Kartı serilerin altına indirin.
- **mb_mekan_15-MENU-ACIK:** TR · EN · FR seçici menünün en dibinde, ekranın alt kenarına yapışık duruyor ve kesilme sınırında; masaüstünde bu sorun yok. Dil seçiciyi menünün üstüne alın.
- **mb_mekan_02 / 03–06:** Tek sütun sonsuz kaydırma; 11 eser için mobilde hiçbir atlama noktası yok. Serilerin başına yapışkan bir seri şeridi (Alacakaranlık · Hava · Topografya · Sabah) koyun.
- **mb_mekan_10-koleksiyonlar:** "Kayıt" başlığının üstündeki boşluk sorunu masaüstündekinden daha belirgin; dar sütunda başlık listenin bir maddesi gibi okunuyor.
- **mb_mekan_11 / 09:** Uzun künye satırları iki satıra kırılıyor ("s. 44–51." ikinci satıra düşüyor) — mobilde yıl sütununu kaldırıp yılı başlığın önüne alırsanız satırlar düzelir.

---

## AJAN 2 — Galerici / küratör

*(Ajanın notu: "Ekran görüntülerinin çoğu tepe kırpıklı geldiği için sayfaların tamamını canlı siteden kendim de yakaladım ve veri modelini (`SITE` nesnesi) inceledim.")*

### KİM

Karaköy'de orta ölçekli bir çağdaş sanat galerisi işletiyorum; yılda altı sergi, iki fuar yapıyorum ve bir ressamı temsil etmeden önce iş bütününü, sergi derinliğini ve pratik olarak elimde ne olduğunu görmek isterim.

### SAYFA SAYFA

**pc_mekan_01-acilis — Açılış**
- GÖRDÜĞÜM: Ad, tek bir tablo künyesiyle, altında "Galeriye gir" kartı — hepsi bu; sanatçının nerede yaşadığı, ne yaptığı, şu an bir sergisi olup olmadığı hiçbir yerde yazmıyor.
- İSTEK: Ana sayfaya "Sürüyor / Sırada" bloğunu koyun — park edilmiş sade sürümde (pc_duz_01) zaten var ve orada mükemmel çalışıyor (Alacakaranlık · Ardıç Sanat · 2024 / Hava Raporu · Payas Galeri · 2025); seçilen sürümde düşürülmüş. Fuar başvurusu değerlendirirken ilk baktığım şey bu. **[YÜKSEK]**

**pc_mekan_02-son-resimler — Son Resimler**
- GÖRDÜĞÜM: "11 eser, 4 seri. Yeniden eskiye." dedikten sonra tek sütun, her eser tam genişlikte, hiçbir filtre yok — 11 eseri görmek için 11 ekran kaydırıyorum.
- İSTEK: Üste bir kontak-föy ızgarası (3–4 sütun küçük görsel) ve üç filtre ekleyin: **Seri**, **Yıl**, **Durum (Müsait / Koleksiyonda / Ayrıldı)**. Ben eserlerin %90'ını "müsait olanları göster" diyerek tararım. **[YÜKSEK]**

**pc_mekan_03-seri-alacakaranlik — Seri: Alacakaranlık**
- GÖRDÜĞÜM: Başlık, tarih aralığı, iki satır metin, ardından yalnızca **2 eser** — ve serinin kaç eserden oluştuğu hiçbir yerde yazmıyor; alt tarafta sıradaki seriye geçiş de yok.
- İSTEK: Seri başlığının altına "9 eser · 2021–2024 · sürüyor/tamamlandı" künyesi, sayfanın sonuna da "Sıradaki seri →" bağlantısı koyun; bir seride iki eser görüp o serinin tamamının bu olduğunu sanmak istemem. **[YÜKSEK]**

**pc_mekan_04/05/06 — Hava, Sessiz Topografya, Sabah**
- GÖRDÜĞÜM: Dört serinin dördü de aynı şablon; ama serileri **yan yana** görebileceğim, üretimin kronolojisini ve hacmini tek ekranda okuyabileceğim bir "Seriler" indeksi yok — seriler yalnızca menüde birer satır.
- İSTEK: `#/seriler` diye bir indeks sayfası açın: her seri için kapak görseli, yıl aralığı, eser sayısı ve iki cümle. Bir ressamın "sesi" var mı sorusunun cevabı bu sayfada verilir, tek tek serilerde değil. **[YÜKSEK]**

**pc_mekan_07-atolye-notu — Atölye Notu**
- GÖRDÜĞÜM: Üç paragraf gerçekten iyi bir sanatçı metni — "manzara bahane, asıl mesele havanın ağırlığı" klişe değil, bir şey söylüyor; ama sayfada tek bir atölye görseli yok.
- İSTEK: Metnin arasına 3–4 atölye fotoğrafı serpiştirin: çalışılan tuval, kuruyan katmanlar, palet, mekânın kendisi. Yavaş boya iddiasını metin değil, ıslak tuvalin fotoğrafı kanıtlar. **[ORTA]**

**pc_mekan_08-biyografi — Biyografi**
- GÖRDÜĞÜM: Üstte "1987'de İzmir'de doğdu" yazıyor, hemen altındaki paragraf aynı cümleyle başlıyor — tekrar; sanatçı portresi, CV indirme bağlantısı ve **hangi galeri tarafından temsil edildiği** yok.
- İSTEK: Sayfaya "Temsil" satırı ekleyin (galeri adı + şehir, ya da "temsil edilmiyor") ve "CV'yi indir (PDF)" düğmesi koyun; ayrıca eğitim/rezidans/ödül alanlarını yapıya ayrı blok olarak açın — şu an bunlar için hiç yer yok. Temsil bilgisi olmadan bir sanatçıya yazmam. **[YÜKSEK]**

**pc_mekan_09-sergiler — Sergiler**
- GÖRDÜĞÜM: Kişisel/karma ayrımı doğru yapılmış, okunaklı — ama sekiz satır sayfanın en üstünde duruyor, altında ekranlar boyu bomboş beyaz panel uzuyor; hiçbir sergi tıklanabilir değil.
- İSTEK: Her sergi satırını genişleyebilir yapın — küratör adı, tarih aralığı, sergilenen eserler ve varsa katalog bağlantısı; ayrıca **Fuarlar** için ayrı bir blok açın (bir sanatçının fuar geçmişi, karma sergi geçmişinden farklı okunur). Panelin boyu da içeriğe göre daralsın; boşluk CV'yi olduğundan zayıf gösteriyor. **[YÜKSEK]**

**pc_mekan_10-koleksiyonlar — Koleksiyonlar**
- GÖRDÜĞÜM: Altı koleksiyon adı alt alta, hemen ardından **boşluksuz** yapışık duran "Kayıt" başlığı — yedinci liste maddesi gibi okunuyor; ve "Kayıt"ta yalnızca "83 × 132 cm · Özel koleksiyonda" yazıyor, hangi koleksiyona girdiği yazmıyor.
- İSTEK: Her esere gerçek proveniyans satırı bağlayın (eser → koleksiyon adı → yıl); ayrıca "Ayrıldı" durumundaki eser "koleksiyonlarda" sayılmasın — "11 eserin 2 tanesi koleksiyonlarda" cümlesi şu an biri satılmış/ayrılmış eseri sayıyor. "Kayıt" başlığına da üst boşluk verin. **[YÜKSEK]**

**pc_mekan_11-yayinlar — Yayınlar**
- GÖRDÜĞÜM: Beş yayın, künyeler düzgün (sayfa sayısı, metin yazarı, yayıncı) — ama hiçbiri bağlantılı değil, kapak görseli yok, ISBN yok.
- İSTEK: Katalogların kapak küçük görselleri ve "PDF örnek sayfalar" bağlantısı ekleyin; bir katalog metnini kimin yazdığı kadar, o metni okuyabilmek de önemli. **[DÜŞÜK]**

**pc_mekan_12-basin — Basın**
- GÖRDÜĞÜM: Dört künye satırı, hepsi düz metin — tek bir bağlantı, tek bir alıntı, tek bir PDF yok; sayfanın kalan %85'i boş beyaz.
- İSTEK: Her yazıya URL veya PDF taraması bağlayın, en güçlü iki cümleyi büyük punto alıntı olarak sayfanın üstüne çıkarın ve sayfaya "Basın dosyası indir (yüksek çözünürlüklü görseller + biyografi + künye listesi, ZIP)" düğmesi koyun. Sergi duyurusu hazırlayan herkes ilk bunu arar. **[YÜKSEK]**

**pc_mekan_13-iletisim — İletişim**
- GÖRDÜĞÜM: Yalnızca e-posta, atölye semti ve bir cümle; veride telefon ve Instagram hesabı var ama sayfada gösterilmiyor; e-posta bağlantısı tarayıcının varsayılan mavisinde — sitenin tüm paletinin dışında duruyor.
- İSTEK: Talep tipini ayırın — "Eser talebi / Sergi ve fuar önerisi / Basın" için ayrı satırlar; telefonu ve Instagram'ı gösterin; bağlantı rengini siteye ait tona çekin. Kurumsal bir teklifi genel bir atölye adresine yazmak istemem. **[ORTA]**

**pc_mekan_15-MENU-ACIK — Menü**
- GÖRDÜĞÜM: Menü mimarisi net ve güzel — Galeri en üstte vurgulu, seriler girintili, "Sanatçı" grubu ayrı; dil seçimi (TR · EN · FR) en altta çok küçük punto.
- İSTEK: Menüye iki giriş daha ekleyin: **"Müsait Eserler"** ve **"Eser Listesi (PDF)"**; dil seçimini de menünün içinden çıkarıp üst şeride taşıyın — sergi duvarında zaten öyle yapılmış, ana sitede tutarsız. **[ORTA]**

**pc_sergi_16-DUVAR — Sergi duvarı**
- GÖRDÜĞÜM: Çok iyi yapılmış bir Fransız salonu; ama bu bir 19. yüzyıl boiserie'si — üstelik pilastrlarda **Eyfel Kulesi motifi** var — ve on bir çağdaş yağlı boya, on bir özdeş altın varak barok çerçevede, tek sıra, eşit aralıkla, hepsi aynı merkez hizasında asılı. Bu bir sergi kurgusu değil, bir koridor. Ayrıca eserler envanter sırasında ilerliyor, yani seriler birbirine karışıyor (alacakaranlık → topografya → hava → alacakaranlık…). Sol taraftaki eser listesi de fon paneli olmadan tablonun üstüne binmiş, okunmuyor.
- İSTEK: Üç şey: (1) duvar seçeneği koyun — **Salon / Beyaz Küp / Atölye**; çağdaş bir ressamı satarken beyaz duvar şart. (2) Çerçeve seçeneği koyun — altın varak bir küratöryel karardır, varsayılan olamaz. (3) Duvarı **seriye göre gruplayın**, seri geçişine bir ara boşluk ve seri adı koyun. **[YÜKSEK]**

**pc_sergi_18-YAN-LISTE-ACIK — Duvar yan listesi**
- GÖRDÜĞÜM: Liste açıkken künyeler okunaklı, tıklayınca ilgili esere gidiyor — iyi; ama liste yalnızca ad + yıl veriyor, ölçü ve durum yok, ve sıralamayı değiştiremiyorum.
- İSTEK: Listeye ölçü ve müsaitlik rozeti ekleyin, üstüne de "Seriye göre / Yıla göre / Ölçüye göre" sıralama düğmesi koyun; bir duvar kurgusunu ölçüye göre sıralayamadan okuyamam. **[ORTA]**

**pc_sergi_17-ESER-DETAY — Eser detayı**
- GÖRDÜĞÜM: En iyi sayfa — künye tablosu temiz, sanatçı notu italik, müsaitlik satırı var, 4/11 sayacı var; ama görsele **yakınlaşamıyorum**, sağ panelin üçte ikisi boş ve "Atölyeden temin edilebilir" satırı tıklanamıyor.
- İSTEK: Görsele büyüteç/pinch-zoom ekleyin (yağlı boyada tuş izini göremeden karar veremem) ve müsaitlik satırının altına, eserin adını konu satırına otomatik yazan bir **"Bu eseri sor"** düğmesi koyun. Boş kalan panele de "Sergilendiği yerler" ve "Envanter no" alanlarını yerleştirin. **[YÜKSEK]**

**pc_duz_01-acilis — Park edilmiş sade sürüm**
- GÖRDÜĞÜM: Kalıcı sol menü, sağda "Sürüyor / Sırada" sergi bloğu — bilgiye erişim açısından seçilen sürümden **daha iyi**; seçilen sürüm her şeyi bir hamburgerin arkasına saklamış.
- İSTEK: Sade sürümü çöpe atmayın; masaüstünde (≥1200 px) seçilen sürüme de kalıcı bir yan menü verin — sekiz sayfalık bir sitede her geçişte menü açıp kapatmak yoruyor. **[ORTA]**

**pc_mekan_20-DIL-EN — İngilizce**
- GÖRDÜĞÜM: Eser adı Türkçe kalıp altına italik İngilizce karşılığı ("DAĞ SIRTI / The Ridge") gelmesi doğru bir tercih; arayüz çevirileri de düzgün.
- İSTEK: Dil seçimi tarayıcı diline göre bir kez önerilsin (üstte küçük bir şerit) — yabancı bir küratör Türkçe bir sayfaya düşüp menüyü açmadan EN'i bulamaz. **[ORTA]**

**pc_19-404 — 404**
- GÖRDÜĞÜM: Üç dilde tek satır ve ana sayfaya dönüş — sade ve doğru.
- İSTEK: Altına "Son Resimler" ve "Sergi duvarı" için iki bağlantı daha ekleyin; kırık bir linkten gelen kişiyi eserlere yönlendirin. **[DÜŞÜK]**

### EN ÇOK İSTEDİĞİM 3 ŞEY

1. **Çalışılabilir bir eser dosyası.** Her esere kalıcı bir bağlantı (`#/eser/dag-sirti` — yönlendirici yorumunda tanımlı ama kayıtlı değil, yani şu an ana sitede tek bir eseri meslektaşıma linkleyemiyorum), yüksek çözünürlüklü görsel talebi, sayfada büyüteç, ve **"Eser listesini indir" (PDF künye föyü + CSV)**. Künye alanlarına da şunlar eklenmeli: envanter no, çerçeveli/çerçevesiz, imza yeri ve tarihi, sergi geçmişi, proveniyans, fiyat (ya da "fiyat için sorunuz"). Şu an sitede tek bir indirilebilir dosya, tek bir baskı kalitesinde görsel yok — mevcut görseller 1686 px / ~80 KB, yani 132 cm'lik bir tuval için gerçek boyutta ~32 dpi.
2. **Ölçeği gerçekten göster.** Duvar "gerçek santimetre ölçeğinde" diyor ama ölçeği okuyabileceğim hiçbir çıpa yok — ne zemin çizgisi, ne 150 cm göz hizası, ne insan silueti. Seri sayfalarında da bütün eserler aynı genişlikte diziliyor; 40 cm'lik bir etüt ile 200 cm'lik bir tuval ekranda birebir aynı görünüyor. Seri içinde eserleri **birbirine oranlı** render edin ve duvara ölçek referansı koyun.
3. **İş bütününü bir bakışta okutan bir "Seriler" indeksi + ana sayfada güncellik.** Dört seriyi yan yana, yıl aralıkları, eser sayıları ve kapak görselleriyle gösteren tek bir sayfa; ana sayfada da sade sürümdeki "Sürüyor / Sırada" bloğu. Şu an bir ressamın tutarlı mı dağınık mı ürettiğini anlamak için menüden dört ayrı sayfayı tek tek gezmem gerekiyor.

### BENİ BU SİTEDEN UZAKLAŞTIRAN ŞEY

Site güzel — kaydırıldıkça değişen fon, kâğıt kıvrımı, tipografinin ölçüsü, hepsi tutarlı ve zevkli; sanatçı metni de klişe değil, gerçekten bir şey söylüyor. Ama bu bir *atmosfer*, dosya değil. Yirmi dakika gezip elimde şunlar olmadan çıkıyorum: bir eser listesi, bir fiyat aralığı, bir yüksek çözünürlüklü görsel, sanatçının kim tarafından temsil edildiği, hangi eserin hangi koleksiyona girdiği, şu an açık bir sergisi olup olmadığı. Elimde kalan tek şey bir e-posta adresi ve "yazın" cümlesi. Beni asıl geren şey ise sergi duvarı: on bir çağdaş yağlı boyayı altın varak barok çerçevelerde, Eyfel Kulesi kabartmalı bir Fransız salonunda, tek sıra eşit aralıkla asmak — bu, işi 1880'e ait bir nesne gibi okutuyor ve bir yaşayan ressamın en çok kaçınması gereken şey bu. Üstelik asım kararı hiçbir küratöryel bilgi taşımıyor: seriler birbirine karışmış, ölçü ilişkisi yok, ritim yok. Sergiler ve Basın sayfalarında sekiz satırın altında uzayan ekranlar dolusu boş beyaz panel de sanatçıyı olduğundan zayıf gösteriyor — dolu bir CV bile o boşlukta cılız durur.

### MOBİLDE ÖZELLİKLE

- **Sergi duvarı telefonda amacını yitiriyor** (mb_sergi_16): 390 px'de tek bir tablo görünüyor ve tablo ekranın ancak yarısını kaplıyor; geri kalanı çerçeve, boiserie ve şamdan. Duvarın anlamı eserler arası ilişkiyi görmekti — telefonda o ilişki yok. Dar ekranda duvarı bırakıp doğrudan tam genişlikte bir eser akışına düşürün.
- **Eser detayı telefonda görseli küçültüyor** (mb_sergi_17): tablo üstünde ve altında geniş krem boşluk var, tablo ise 390 px'in ~340'ını kullanıyor. Görsel ekran genişliğine yaslansın; yatay eserler için "çevir/tam ekran" ipucu verin.
- **Koleksiyonlar sayfasındaki "Kayıt" başlığı yapışıklığı mobilde daha da kötü** (mb_mekan_10): koleksiyon listesinin son satırıyla başlık arasında hiç boşluk yok, başlık listenin bir maddesi gibi okunuyor.
- **Menü ekranın tamamını kaplıyor ve dil seçimi en alta, ekran kenarına sıkışıyor** (mb_mekan_15): TR · EN · FR yazısı hem çok küçük hem de gerçek bir telefonda alt gezinme çubuğunun altında kalma riski taşıyor; dokunma hedefi olarak da küçük.
- **Son Resimler'de 11 eser tek sütun** (mb_mekan_02): telefonda bu çok uzun bir kaydırma. 2 sütunlu bir ızgara ve üstte yapışkan bir seri/durum filtresi telefonda masaüstünden bile daha çok gerekiyor.
- İyi taraf: Sergiler ve Biyografi gibi metin sayfaları mobilde masaüstünden **daha iyi** okunuyor — çünkü boş beyaz panel sorunu orada yok, panel içeriğe göre kapanıyor. Masaüstünde de aynı davranış olmalı.

---

## AJAN 6 — Sanat danışmanı

*(Ajanın notu: "Sitenin canlı kaynağını da çekip künye verisini satır satır doğruladım.")*

### KİM

Kurumsal koleksiyonlara ve ailelere eser alan bir sanat danışmanıyım; bir tabloya bakmadan önce künyesine bakarım, çünkü müşterime gönderdiğim her satırın arkasında ben varım.

### SAYFA SAYFA

**pc_mekan_01-acilis — Açılış**
- GÖRDÜĞÜM: Tek bir eser (Dağ Sırtı, 2023, 88 × 132 cm) tam boy açılıyor, altında dört satırlık künye var.
- İSTEK: Açılışta "11 eser · 4 seri · 2021–2024" gibi bir kapsam satırı ve doğrudan "Eser Listesi"ne giden bir bağlantı olsun; ben ilk otuz saniyede kaç eserle karşı karşıya olduğumu bilmek isterim. **[ORTA]**

**pc_mekan_02-son-resimler — Son Resimler (tam sayfa da baktım)**
- GÖRDÜĞÜM: 11 eserin tamamı yıl sırasına göre, her birinde başlık / yıl / teknik / cm | in / durum var; ama eser numarası, seri adı ve imza bilgisi yok.
- İSTEK: Her karta arşiv numarasını ("CS-2024-01" gibi) ve seri adını ekleyin; ayrıca sayfanın başına "Duruma göre süz: Müsait / Koleksiyonda / Ayrıldı" filtresi koyun — 11 eserde katlanılır, 60 eserde bu sayfa kullanılamaz hale gelir. **[YÜKSEK]**

**pc_sergi_17-ESER-DETAY — Eser detayı**
- GÖRDÜĞÜM: Balıkçıl için Yıl / Teknik / Ölçü (86 × 132 cm, 33⅞ × 52 in) alanları düzgün duruyor, altında sanatçı notu ve "Atölyeden temin edilebilir, İstanbul".
- İSTEK: Künyeye şu alanları ekleyin: **arşiv no, imza (imzalı/imzasız – nerede, ör. "sağ alt, kurşun kalem"), çerçeve durumu (çerçeveli/çerçevesiz), sergilenme geçmişi, yayın referansı, fotoğraf kredisi**. Bugünkü haliyle bu panel bir künye değil, bir etiket. **[YÜKSEK]**

**pc_sergi_17-ESER-DETAY — Eser detayı (eylem tarafı)**
- GÖRDÜĞÜM: Panelde tek eylem "KAPAT" ve ileri/geri okları; fiyat sormak, bilgi istemek veya bu eseri paylaşmak için hiçbir düğme yok.
- İSTEK: Panele "Bu eser hakkında bilgi isteyin" düğmesi koyun; tıklayınca konusu otomatik dolu bir e-posta açılsın ("Cemal Sağlam — Balıkçıl, 2023, 86 × 132 cm — bilgi talebi"). Yanına "Bağlantıyı kopyala" ekleyin. **[YÜKSEK]**

**pc_sergi_16-DUVAR — Sergi duvarı**
- GÖRDÜĞÜM: Duvar etiketi "Güz Ormanı · 2024 · TUVAL ÜZERİNE YAĞLI BOYA · 85 × 132 CM | 33½ × 52 İN" yazıyor; birim kısaltmaları büyük harfe çevrilmiş ve inç "İN" olmuş.
- İSTEK: Ölçü satırını `text-transform: uppercase` kapsamı dışına alın. Birim simgeleri her zaman küçük harf yazılır: `cm` ve `in`. "İN" diye bir birim yok, bu satır bir müzayede kataloğuna gitse düzeltme talebi alır. **[YÜKSEK]**

**pc_sergi_18-YAN-LISTE-ACIK — Yan liste**
- GÖRDÜĞÜM: Liste açıkken koyu panelin üstünde okunuyor; kapalı durumda (16-DUVAR) aynı başlıklar soldaki tablonun aydınlık gökyüzünün üzerine biniyor ve "Kıyı", "Balıkçıl", "Işıklı Vadi" okunmuyor.
- İSTEK: Kapalı durumda ya listeyi tamamen gizleyin ya da arkasına aynı koyu zemini koyun; eser görselinin üstüne okunmayan metin binmesin. **[ORTA]**

**pc_mekan_10-koleksiyonlar — Koleksiyonlar**
- GÖRDÜĞÜM: Üstte 6 koleksiyon adı, hemen altında hiç boşluk bırakmadan "Kayıt" başlığı, altında sadece 2 eser (83 × 132 cm ve 88 × 132 cm), inç karşılıkları yok.
- İSTEK: "Kayıt" başlığından önce boşluk verin; kayıt satırlarına inç karşılığını ve tekniği ekleyin; en önemlisi her esere hangi koleksiyona girdiğini yazın ("Ardıç Sanat Koleksiyonu, İstanbul, 2024'te edinildi"). Adı geçen 6 koleksiyonun hiçbiri hiçbir eserle eşleşmiyor. **[YÜKSEK]**

**pc_mekan_09-sergiler — Sergiler**
- GÖRDÜĞÜM: Kişisel ve karma diye ikiye ayrılmış, yıl / sergi adı / mekân var; tarih aralığı ve sergilenen eserler yok.
- İSTEK: Her sergi satırına ay aralığı ekleyin ("Mart–Mayıs 2024") ve satırı tıklanabilir yapıp o sergide yer alan eserleri listeleyin. Bir eserin sergi geçmişi, o eserin değerinin yarısıdır. **[ORTA]**

**pc_mekan_11-yayinlar — Yayınlar**
- GÖRDÜĞÜM: 5 kayıt; katalog sayfa sayısı ve metin yazarı var, ama ISBN, yayıncı bağlantısı, kapak görseli veya PDF yok.
- İSTEK: Katalog satırlarına ISBN ve varsa PDF/temin bağlantısı ekleyin; ayrıca eser künyelerinden bu yayınlara "Yayımlandı: Alacakaranlık, 2024, s. 41" biçiminde atıf verin. **[ORTA]**

**pc_mekan_12-basin — Basın**
- GÖRDÜĞÜM: 4 kayıt; yazar, mecra ve tarih var, ama hiçbiri bağlantı değil.
- İSTEK: Yazı başlıklarını yayına giden bağlantı yapın, çevrimiçi karşılığı yoksa PDF kupürünü koyun. Müşterime "basında yer aldı" demem yetmiyor, göstermem gerekiyor. **[DÜŞÜK]**

**pc_mekan_08-biyografi — Biyografi**
- GÖRDÜĞÜM: Doğum/ikamet satırı ve üç paragraf düz metin; eğitim, ödül, rezidans tarihli satırlar halinde değil.
- İSTEK: Sayfanın altına "CV'yi indir (PDF)" bağlantısı koyun ve eğitim/ödül/rezidansı sergi listesindeki gibi yıl–olay satırlarına dökün. **[ORTA]**

**pc_mekan_03-seri-alacakaranlik — Seri sayfası**
- GÖRDÜĞÜM: Başlık, "2021 — 2024" aralığı ve tanıtım metni; ancak seride kaç eser olduğu ve bunların kaçının gösterildiği yazmıyor.
- İSTEK: Seri başlığının altına "Bu seriden 2 eser gösteriliyor · seride toplam N eser" satırı ekleyin; ilan edilen yıl aralığıyla gösterilen eserlerin yılları örtüşmüyor. **[ORTA]**

**pc_mekan_13-iletisim — İletişim**
- GÖRDÜĞÜM: Tek e-posta bağlantısı, atölye semti ve iki cümle; telefon yok, temsilci galeri yok, form yok.
- İSTEK: Telefon numarasını ve varsa temsilci galeriyi ekleyin (veri dosyasında telefon zaten duruyor ama sayfaya hiç basılmıyor); "Kurumsal / danışman talepleri" için ayrı bir satır açın. **[YÜKSEK]**

**pc_mekan_15-MENU-ACIK — Menü**
- GÖRDÜĞÜM: Galeri, 4 seri, sanatçı bölümü ve diller var; arama, "müsait eserler" kısayolu ve katalog indirme yok.
- İSTEK: Menüye "Müsait Eserler" ve "Katalog (PDF)" girişleri ekleyin. **[ORTA]**

**pc_19-404 — 404**
- GÖRDÜĞÜM: Üç dilde temiz bir mesaj ve ana sayfaya dönüş bağlantısı.
- İSTEK: Bir de "Eser Listesi"ne bağlantı koyun; bozuk bir eser bağlantısıyla buraya düşen kişi doğrudan listeye gitsin. **[DÜŞÜK]**

**mb_sergi_16-DUVAR — Duvar (mobil)**
- GÖRDÜĞÜM: Künye satırı "83 × 132" / "CM | 32⅝ × 52 İN" diye ölçünün ortasından ikiye bölünüyor.
- İSTEK: Ölçü ifadesinin içindeki boşlukları bölünmez boşluk yapın; bir ölçü hiçbir zaman satır sonunda ikiye ayrılmamalı. **[ORTA]**

### TUTARSIZLIK BULDUM MU

Önce iyi haber: **ölçü sırası her yerde tutarlı** (yükseklik × genişlik; 83 × 132'de veri de ch=83, cw=132 diyor) ve **inç dönüşümlerinin on birinin de doğru** — 86 cm → 33⅞ in, 87 → 34¼, 88 → 34⅝ hepsi en yakın 1/8'e doğru yuvarlanmış. Bu kısmı kimse elle bozmasın.

Bulduklarım:

1. **Birim yazımı sayfadan sayfaya değişiyor.** Ana sitede (pc_mekan_02, pc_mekan_01) "88 × 132 cm | 34⅝ × 52 in" — küçük harf. Sergi duvarında ve detayında (pc_sergi_16, pc_sergi_17) "85 × 132 CM | 33½ × 52 İN" — büyük harf. Aynı eserin ölçüsü iki farklı yerde iki farklı biçimde yazılıyor.
2. **Türkçe büyük harf çevirimi inç birimini bozuyor.** TR duvarda "52 İN" (pc_sergi_16-DUVAR), aynı ekran EN'de "52 IN" (pc_sergi_21-DIL-EN). "İN" diye bir ölçü birimi yok.
3. **Koleksiyonlar sayfasında inç yok.** pc_mekan_10'da kayıtlar "83 × 132 cm · Özel koleksiyonda" — sadece cm. Diğer her yüzeyde çift birim veriliyor. Aynı eser (Alacakaranlık) Son Resimler'de "83 × 132 cm | 32⅝ × 52 in", Koleksiyonlar'da yalnız cm.
4. **Künye alan seti üç yüzeyde üç farklı.** Duvar tabelası: başlık + yıl + teknik + ölçü + söz + durum, **seri yok**. Detay paneli: seri **var**, ama **sanatçı adı yok** — o paneli ekran görüntüsü alıp müşterime yollasam kimin eseri olduğu yazmıyor. Son Resimler kartı: seri yok, sanatçı notu yok.
5. **Koleksiyon sayımı yanlış.** pc_mekan_10: "11 eserin 2 tanesi koleksiyonlarda." Ama listelenen iki eserden biri (Issız Çiftlik) "Ayrıldı" durumunda — "ayrıldı" ile "koleksiyonda" aynı şey değil. Doğru cümle "1 eser koleksiyonda, 1 eser ayrıldı" olmalı.
6. **6 koleksiyon adı var, 1 eser koleksiyonda.** Aynı sayfada üstte Ardıç, Batı Kanat, Liman, Nordbahn, Van Doorn ve özel koleksiyonlar sayılıyor; altta koleksiyona girmiş tek bir eser görünüyor ve hiçbiri bu adlarla eşleşmiyor.
7. **Seri yıl aralıkları eserlerle örtüşmüyor.** Alacakaranlık "2021 — 2024" diyor, içindeki eserler 2023 ve 2024. Hava "2019 — 2023" diyor, eserler 2021–2023. Sessiz Topografya "2018 — 2024" diyor, eserler 2022–2024. Sabah "2020 — 2024" diyor, eserler 2022–2024. Dördü de dışarıdan "eksik eser var" gibi okunuyor.
8. **Veride arşiv numarası var, ekranda yok.** Her eserin `no` alanı dolu (01–11) ama hiçbir sayfada basılmıyor. Detaydaki "4 / 11" sayacı ise duvardaki sıra, envanter numarası değil.
9. **Aynı eserin üç farklı sırası var.** Duvar katalog sırasıyla (01→11), Son Resimler yıl sırasıyla, Koleksiyonlar yıl sırasıyla diziliyor. Sabit bir numara olmadığı için "dördüncü eser" demek üç farklı tabloyu işaret ediyor.
10. **İki ayrı durum etiketi var.** Veride her eserin `statusLabel` alanı yazıyor ("Müsait"), ama ekranda çeviri dosyasından gelen başka bir metin görünüyor ("Atölyeden temin edilebilir, İstanbul"). Yarın biri `statusLabel`'ı düzeltirse ekranda hiçbir şey değişmez — iki kaynaklı veri.
11. **Telefon ve Instagram veride dolu, sayfada yok.** İletişim sayfası yalnız e-posta gösteriyor.
12. **Görsel kredisi tek esere sabitlenmiş.** Her eserin kendi kaynak künyesi varken alt bilgide her sayfada birinci eserin kredisi ("Twilight in Italy, 1874") basılıyor; sergi.html'de ise hiçbir kredi satırı yok.
13. **Tek eser bağlantısı hiçbir yerde yok.** Koddaki yönlendirici yorumunda `#/eser/<slug>` yazıyor ama o adres hiç tanımlanmamış; sergi duvarında yönlendirici hiç çalışmıyor. Yani bir eseri gösteren paylaşılabilir bir URL üretmek bugün mümkün değil.
14. **11 eserin 11'i de 132 cm genişliğinde ve hepsi yatay.** Dikey formatta tek bir eser yok; duvarın ve kartların dikey tuvalle ne yapacağı hiç denenmemiş.

### EN ÇOK İSTEDİĞİM 3 ŞEY

1. **Tek eser bağlantısı ve paylaşım.** Her esere kalıcı bir adres (`.../eser/balikcil`) ve detayda "Bağlantıyı kopyala" düğmesi. Bugün bir müşterime tek bir tabloyu gösteremiyorum — "siteye gir, dördüncü tabloya tıkla" demek zorundayım.
2. **Künyenin tamamlanması ve tek biçime oturtulması.** Arşiv no, imza (var/yok – nerede), çerçeve, sergilenme, yayın ve fotoğraf kredisi alanları eklensin; duvar / detay / liste üçünde de **aynı alan seti, aynı sırada, aynı birim yazımıyla** görünsün. Birim simgeleri her yerde `cm` ve `in`.
3. **Paylaşılabilir eser listesi.** Seçtiğim eserleri işaretleyip PDF olarak alabileceğim bir "liste"; en azından baskı için bir `@media print` bloğu — şu an hiç yok, sayfayı yazdırırsam duvar dokusu ve arka plan görselleriyle çıkar.

### BENİ BU SİTEDEN UZAKLAŞTIRAN ŞEY

Site göze çok hoş geliyor, hatta duvar fikri gerçekten iyi — eserleri gerçek santimetre ölçeğinde yan yana görmek işime yarar. Ama ben bir vitrin değil bir kayıt arıyorum ve bu site kaydın yarısını tutmuş, yarısını atmış. Bir eseri açıyorum: yıl, teknik, ölçü var — sonrası boş. İmzalı mı? Arkasında etiket var mı? Nerede sergilendi, hangi katalogda geçti, şu an fiziksel olarak kimde? Hiçbiri yok. Sayfanın altında "Atölyeden temin edilebilir" yazıyor ama temin etmek için basabileceğim bir düğme yok; İletişim'e gidiyorum, orada da tek bir e-posta adresi var, hangi eseri sorduğumu kendim yazmam gerekiyor. Sonra Koleksiyonlar'a giriyorum ve altı kurumsal koleksiyon adı görüyorum, ama tabloda koleksiyona girmiş tek bir eser var ve o da hiçbir koleksiyonla eşleşmiyor — bu benim için ciddi bir güven sorunu, çünkü kayıt tutulmadığını değil, kaydın kontrol edilmediğini gösteriyor. Buna bir de duvarda "52 İN" yazan ölçü satırı eklenince, elimde müşterime iletebileceğim hiçbir şey kalmıyor. Ekranı kapatıp galeriyi arıyorum.

### MOBİLDE ÖZELLİKLE

- **Ölçü satırı ikiye bölünüyor.** mb_sergi_16-DUVAR'da künye "83 × 132" / "CM | 32⅝ × 52 İN" diye satır sonunda kopuyor. Bir ölçü ifadesi asla bölünmemeli; sayı ile birim arasına bölünmez boşluk konmalı.
- **Duvarda yan liste yok.** Masaüstünde eser listesi soldan açılıyor (pc_sergi_18), mobilde hiç görünmüyor — 11 eseri tek tek kaydırarak geçmek zorundayım, "yedinciye dön" diyemiyorum. Mobile de bir liste/atlama menüsü gerekiyor.
- **Koleksiyonlar'daki boşluk hatası mobilde daha kötü.** mb_mekan_10'da "Kayıt" başlığı listenin son satırına yapışmış; ilk bakışta yedinci bir koleksiyon adı sanıyorsunuz.
- **Eser detayında görsel çok küçük.** mb_sergi_17'de tablo ekranın üçte birini kaplıyor, üstünde ve altında geniş boş alan var; fırça dokusuna bakmak için büyütemiyorum. Detayda çift dokunuşla yakınlaştırma şart — bir eseri satın almayı düşünen kimse 470 piksel genişliğinde bir görüntüyle karar vermez.
- **Mobil künye alanı da masaüstüyle aynı eksikleri taşıyor** (arşiv no, imza, sergilenme yok) ve orada da bilgi isteme düğmesi bulunmuyor; oysa bu sayfa büyük ihtimalle galeri kartındaki QR'dan gelen kişinin göreceği ilk ekran.

---
---

## ÖNERİLEN ÜÇ DALGA

Özet çıkarırken başlangıç noktası olsun diye.

### Dalga 1 — ucuz, tartışmasız, hepsi hata düzeltmesi
- Koleksiyonlar'da "Kayıt" başlığına üst boşluk **(6/6 ajan)**
- `İN` → `in` (birim `text-transform` dışına)
- `--link: #1B3FCC` yerine sitenin paletinden bir ton
- Koleksiyon sayımı: "1 koleksiyonda, 1 ayrıldı"
- Dört serinin yıl aralığı gerçek eser yıllarına çekilsin
- Biyografideki tekrar cümlesi
- Telefon + Instagram iletişime basılsın
- `@media print` bloğu
- Ölçü satırında bölünmez boşluk
- 404'e "Son Resimler" + "Sergi duvarı" kısayolları
- `statusLabel` ya kullanılsın ya kaldırılsın (tek kaynak)

### Dalga 2 — asıl eksik işlevler
- Eser detayında **yakınlaştırma** (5/6)
- **Yan listenin çözümü** — kapalıyken tablonun üstünden çekilsin (6/6)
- **Tek esere kalıcı bağlantı** (`#/eser/<slug>` rotasını kaydet)
- **"Bu eseri sor"** düğmesi (konusu önceden dolu mailto)
- **Müsait eserler** listesi + duruma göre filtre
- Basın ve yayın kayıtları **bağlantılı** olsun
- Mobilde tabloya daha çok yer + yan listenin mobilde geri gelmesi
- Punto artışı (özellikle sergi künyesi ve 12px gövde metinleri)

### Dalga 3 — karar gerektirenler
- Salon / Beyaz Küp / Atölye duvar seçeneği *(3 ajan istedi, 2 ajan mevcut hâli beğendi)*
- Çerçeve çeşitliliği *(3 ajan istedi — ama eşit çerçeve müşterinin açık talebiydi)*
- Ana sayfaya "Sürüyor / Sırada" bloğu
- Seriler indeksi (`#/seriler`)
- Atölye fotoğrafları, sanatçı portresi, CV PDF, basın kiti *(gerçek içerik gerektirir)*
- **Dikey formatlı eserle test** — mevcut 11 eserin hepsi yatay, dikey tuval hiç denenmedi
