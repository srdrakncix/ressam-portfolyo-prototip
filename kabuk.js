/* ═══════════════════════════════════════════════════════════════════════════
   KABUK — her sayfada aynı olan davranış: dil, tablo zemini, hamburger ve
   menü. Derlemede mekan.html ve sergi.html içine enjekte ediliyor
   (__KABUK_JS__ belirteci; burada kasten yorum imi olmadan yazılı).

   Sayfa ile kabuk arasındaki sözleşme, sayfanın bu dosyadan ÖNCE tanımladığı
   window.KABUK nesnesi:

     sayfa   'mekan' | 'sergi'   — menü hangi sayfada olduğunu bilsin diye
     git     (route) => {}       — bir menü satırına tıklanınca ne olacak
     yenile  () => {}            — dil değişince sayfa kendini yeniden çizsin

   Neden ortak dosya: galeri "başka bir site" gibi durmasın diye iki sayfa
   aynı kabuğu paylaşıyor. Kopyalanmış olsalardı biri değişip öteki kalırdı;
   tam da kaçındığımız şey o.
   ═══════════════════════════════════════════════════════════════════════════ */

const KABUK = window.KABUK || {};

/* Element.matches() GECERSIZ SECICIDE ISTISNA ATAR. ':popover-open'i
   tanimayan bir tarayicida matches('.open, :popover-open') cagrisi
   SyntaxError firlatiyor, yani hamburgere her basis patliyor ve menu HIC
   acilmiyordu. Ustelik bu, yedek yolu duzeltmek icin yazdigim kodun tam
   kendisiydi.

   Destek bir kez sorulup saklaniyor; secici dizesi bir daha kurulmuyor. */
const POPOVER_VAR = typeof HTMLElement !== 'undefined' &&
                    'popover' in HTMLElement.prototype;
/* Menudeki karsilik sutunu kabugun kendi isi: iki sayfada da ayni menu
   dursun diye buraya tasindi. */
const kOniz = (r, hemen) => { if (hemen) onizSon = '\u0000'; onizYaz(r, hemen); };

/* ── dil ─────────────────────────────────────────────────────────────────── */

const LANGS = ['tr', 'en', 'fr'];
const LANG_KEY = 'cs-lang';

function initialLang() {
  try { const s = localStorage.getItem(LANG_KEY); if (LANGS.includes(s)) return s; } catch (e) {}
  const n = (navigator.language || '').slice(0, 2).toLowerCase();
  return LANGS.includes(n) ? n : 'tr';
}
let LANG = initialLang();
const L = () => SITE.i18n[LANG] || SITE.i18n.tr;
const t = (k) => (L().ui && L().ui[k]) || SITE.i18n.tr.ui[k] || k;
const fill = (s, v) => s.replace(/\{(\w+)\}/g, (_, k) => v[k]);
const upTR = (s) => s.toLocaleUpperCase('tr-TR');

/* ── zemin: iki katman, çapraz geçiş ─────────────────────────────────────── */

const BG = SITE.backdrops || {};
const bgEls = [document.getElementById('bgA'), document.getElementById('bgB')];
let bgTurn = 0, bgKey = null;

function setBackdrop(key) {
  const b = BG[key] || BG.acilis;
  if (!b || key === bgKey) return;
  bgKey = key;
  const next = bgEls[bgTurn % 2], prev = bgEls[(bgTurn + 1) % 2];
  next.style.backgroundImage = 'url(' + b.src + ')';
  next.classList.add('on');
  prev.classList.remove('on');
  bgTurn++;
  paintMenu(b.palette || []);
  paintBurger(b.src);
}

/* Menü satırlarının rengi o sayfanın zemininden geliyor — her satır ayrı ton.
   Eskiden dolgu ve çerçeve de bu paletten besleniyordu; satırlar hap
   biçiminde kapsüllerdi. Kapsüller kalktı, geriye yalnızca yazı rengi kaldı. */
function hsl(hex) {
  const n = parseInt(hex.slice(1), 16);
  const r = ((n >> 16) & 255) / 255, g = ((n >> 8) & 255) / 255, b = (n & 255) / 255;
  const mx = Math.max(r, g, b), mn = Math.min(r, g, b), d = mx - mn;
  const l = (mx + mn) / 2;
  let h = 0;
  if (d) {
    if (mx === r) h = ((g - b) / d) % 6;
    else if (mx === g) h = (b - r) / d + 2;
    else h = (r - g) / d + 4;
    h *= 60; if (h < 0) h += 360;
  }
  return [h, d === 0 ? 0 : d / (1 - Math.abs(2 * l - 1)), l];
}

/* Doygunluk ve parlaklık sayıları firca.css'ten geliyor (onu firca.py
   yazıyor). Sebebi: aynı sayılar panelin okunurluk ölçümünde de
   kullanılıyor. Burada elle tutulsalardı panelin tonu bir değiştiğinde
   ölçüm artık gerçeği ölçmez olurdu — nitekim bir kez öyle oldu:
   ölçüm 0.88 ile geçerken çalışan kod 0.72 kullanıyordu. */
function satirAyari() {
  const cs = getComputedStyle(document.documentElement);
  const say = (ad, yedek) => {
    const v = parseFloat(cs.getPropertyValue(ad));
    return isNaN(v) ? yedek : v;
  };
  return { tonMerkez: say('--satir-ton-merkez', 33),
           tonPay: say('--satir-ton-pay', 11),
           sat: say('--satir-doygunluk', 0.40),
           lig: say('--satir-parlaklik', 0.90),
           adim: say('--satir-adim', 0.015) };
}

function paintMenu(pal) {
  const a = satirAyari();
  document.querySelectorAll('#menu .nav-item').forEach((el, i) => {
    if (el.classList.contains('ozel') || el.classList.contains('cikis')) return;
    if (!pal.length) { el.style.color = '#e9e9e4'; return; }
    const [hRaw, sRaw] = hsl(pal[i % pal.length]);
    /* Ton SICAK PENCEREYE kelepceleniyor. Olculdu: tonlar 29-94 derece
       arasinda geziniyordu ve uc satir zeytin yesiline kaciyordu.
       Degerler firca.css'ten -- olcum ile calisan kod ayni sayiyi
       kullanmak zorunda, bu hata uc kez tekrarlandi. */
    const h = Math.max(a.tonMerkez - a.tonPay,
                       Math.min(a.tonMerkez + a.tonPay, hRaw));
    const sat = Math.min(sRaw, a.sat);
    const lig = a.lig + ((i * 3) % 7) * a.adim;        /* satır satır ayrışsın */
    el.style.color = 'hsl(' + h.toFixed(0) + ',' + (sat * 100).toFixed(0) + '%,' +
                     (lig * 100).toFixed(1) + '%)';
  });
}

/* Hamburger'in üç çubuğu: gerçek boyadan kesilmiş şeritler. */
function paintBurger(src) {
  document.querySelectorAll('#menubtn i').forEach((el) => {
    el.style.backgroundImage = 'url(' + src + ')';
  });
}

/* == KARSILIK SUTUNU =======================================================
   Vitrin degil: her satirin turune gore karsiligini gosteriyor. Seri
   satirinda o serinin eseri, Sergiler'de surmekte olan sergi, Iletisim'de
   atolye satiri. 13 satirin 7'si metin sayfasi; saf vitrin yapilsaydi o
   yedisinde bos kalirdi, saf metin yapilsaydi ressamin isi menude hic
   gorunmezdi. */
const monEl = () => document.getElementById('mon');

function kisalt(x, n) {
  const t = String(x || '');
  return t.length > n ? t.slice(0, n - 1).replace(/\s+\S*$/, '') + '…' : t;
}

function seriEserleri(key) { return SITE.works.filter((w) => w.series === key); }
/* Menü önizlemesi: sergi karesi olan eserlerin en yenisi. Yalnızca yıla
   bakılırken, sergi karesi olmayan bir kayıt hep öne çıkıyordu. */
function yeniEser() {
  const sirali = SITE.works.slice().sort((a, b) => b.year - a.year);
  return sirali.find((w) => w.ortam) || sirali[0];
}

function onizlemeIcin(route) {
  const cv = (L().cv || SITE.cv || []);
  const yay = (L().publications || SITE.publications || []);
  const bas = (L().press || SITE.press || []);
  /* Yıllar henüz girilmedi (künye bilgileri müşteriden gelmedi) ve bu
     hesap sıfırdan yapılıp menüde "0 — 0" yazıyordu. Sıfır basmak
     eksiklikten kötü: koleksiyoner bunu görünce kataloğun geri kalanına
     da güvenmez. Yıl yoksa aralık da yok. */
  const yillar = SITE.works.map((w) => w.year).filter(Boolean);
  const aralik = yillar.length
    ? Math.min(...yillar) + ' — ' + Math.max(...yillar) : '';

  if (!route) {
    return { ust: SITE.artist.mark, ad: SITE.artist.name,
             alt: [SITE.works.length + ' eser',
                   SITE.series.length + ' seri',
                   aralik || null].filter(Boolean).join(' · '),
             img: yeniEser() };
  }
  if (route === '/galeri') {
    return { ust: t('gal_label'), ad: t('gal_title'), alt: kisalt(t('gal_sub'), 150), img: yeniEser() };
  }
  if (route === '/son') {
    return { ust: t('nav_recent'), ad: SITE.works.length + ' eser · ' + SITE.series.length + ' seri',
             alt: [aralik || null, t('medium')].filter(Boolean).join(' · '),
             img: yeniEser() };
  }
  const m = route.match(/^\/seri\/(.+)$/);
  if (m) {
    const key = m[1];
    const base = K.seriesOf(key) || {};
    const cev = (L().series || {})[key] || base;
    const es = seriEserleri(key);
    return { ust: es.length + ' eser · ' + (base.years || ''), ad: cev.title || base.title,
             alt: kisalt(cev.blurb || base.blurb, 160), img: es[0] };
  }
  if (route === '/atolye')    return { ust: t('nav_studio'),  ad: kisalt((L().statement || SITE.statement || [''])[0], 62),
                                       alt: kisalt((L().statement || SITE.statement || ['', ''])[1] || '', 150) };
  if (route === '/biyografi') return { ust: t('nav_bio'), ad: SITE.artist.name,
                                       alt: kisalt((L().bio || SITE.bio || [''])[0], 165) };
  if (route === '/sergiler' && cv[0])
    return { ust: t('nav_exh') + ' · ' + cv[0][0], ad: cv[0][1], alt: cv[0][2] };
  if (route === '/koleksiyon') {
    const k = SITE.works.filter((w) => w.status === 'koleksiyonda').length;
    const kl = (L().collections || SITE.collections || []);
    return { ust: t('nav_coll'), ad: k + ' / ' + SITE.works.length, alt: kisalt(kl.slice(0, 3).join(' · '), 150) };
  }
  if (route === '/yayinlar' && yay[0])
    return { ust: t('nav_pub') + ' · ' + yay[0][0], ad: yay[0][1], alt: yay[0][2] };
  if (route === '/basin' && bas[0])
    return { ust: t('nav_press') + ' · ' + bas[0][0], ad: bas[0][1], alt: bas[0][2] };
  if (route === '/iletisim')
    return { ust: t('nav_contact'), ad: SITE.artist.email, alt: SITE.artist.studio };
  return { ust: SITE.artist.mark, ad: SITE.artist.name, alt: '', img: yeniEser() };
}

let onizSon = '\u0000';
/* Telefonda karşılık sütunu hiç gösterilmiyor. Gizli bir <img>'e src yazmak
   tarayıcıya o görseli yine de indirtiyor — mobil bağlantıda bedava yük. */
const onizVarMi = () => !matchMedia('(max-width: 760px)').matches;

function onizYaz(route, hemen) {
  const mon = monEl();
  if (!mon || !onizVarMi() || route === onizSon) return;
  onizSon = route;
  /* Üst satır ile başlık aynı metne düşebiliyor: varsayılan önizlemede
     ust = sanatçının imzası, ad = sanatçının adı ve ikisi aynı kelimeler.
     Galeri sayfasında "CEMAL SAĞLAM / Cemal Sağlam" diye iki kez
     yazıyordu. Aynıysa üst satır düşüyor. */
  const d = onizlemeIcin(route);
  /* Menu acilirken ilk yazim beklemesin: solma gecikmesi orada bosluk
     olarak goruluyordu. Capraz gecis yalniz satirdan satira gecerken. */
  const yaz = () => {
    const img = document.getElementById('mon-img');
    // Önizlemede de asıl kare sergi duvarı.
    if (d.img) { img.hidden = false; img.src = d.img.ortam || d.img.src;
                 img.alt = d.img.title; }
    else { img.hidden = true; img.removeAttribute('src'); }
    mon.classList.toggle('yazi-only', !d.img);
    const ayni = (d.ust || '').toLocaleUpperCase('tr-TR').trim() ===
                 (d.ad || '').toLocaleUpperCase('tr-TR').trim();
    document.getElementById('mon-ust').textContent = ayni ? '' : (d.ust || '');
    document.getElementById('mon-ad').textContent = d.ad || '';
    document.getElementById('mon-alt').textContent = d.alt || '';
    mon.classList.remove('degisiyor');
  };
  if (hemen) return yaz();
  mon.classList.add('degisiyor');
  setTimeout(yaz, 170);
}

/* ── menü ────────────────────────────────────────────────────────────────── */

const menuEl = document.getElementById('menu');
const btn = document.getElementById('menubtn');
let trapRelease = null;

function menuModel() {
  /* Galerideyken listenin başına "Ana sayfa" geliyor. Galeri artık ayrı bir
     HTML dosyası, o yüzden yalnızca adrese bakmak yetmiyor. */
  const inGallery = KABUK.sayfa === 'sergi' ||
                    location.hash.replace(/^#/, '').indexOf('/galeri') === 0;
  const items = [];
  if (inGallery) items.push({ href: '/', label: t('gal_exit'), cikis: true });
  items.push({ href: '/galeri', label: t('nav_gallery'), ozel: true });
  items.push({ sep: true });
  items.push({ href: '/son', label: t('nav_recent') });
  SITE.series.forEach(s => items.push({ href: '/seri/' + s.key, label: L().series[s.key].title, indent: true }));
  items.push({ group: t('nav_about_grp') });
  items.push({ href: '/atolye', label: t('nav_studio') });
  items.push({ href: '/biyografi', label: t('nav_bio') });
  items.push({ href: '/sergiler', label: t('nav_exh') });
  items.push({ href: '/koleksiyon', label: t('nav_coll') });
  items.push({ href: '/yayinlar', label: t('nav_pub') });
  items.push({ href: '/basin', label: t('nav_press') });
  items.push({ href: '/iletisim', label: t('nav_contact') });
  return items;
}

/* Bulunduğumuz rota. Galeri ayrı bir sayfa olduğu için oradaki karşılığı
   sayfanın kendisi söylüyor (KABUK.sayfa), ötekilerde adres çıpası. */
function suAnkiRota() {
  if (KABUK.sayfa === 'sergi') return '/galeri';
  const h = location.hash.replace(/^#/, '');
  return h || '/';
}

function buildMenu() {
  const kutu = document.getElementById('msol');
  kutu.innerHTML = '';
  const ul = K.el('ul');
  menuModel().forEach((it) => {
    const li = K.el('li');
    /* Ici bos ayirici: ekran okuyucu bunu bos bir liste ogesi olarak
       sayiyordu. */
    if (it.sep) {
      li.className = 'sep';
      li.setAttribute('aria-hidden', 'true');
      ul.appendChild(li);
      return;
    }
    if (it.group) { li.className = 'grouplbl'; li.textContent = it.group; ul.appendChild(li); return; }
    const a = K.el('a', 'nav-item' + (it.ozel ? ' ozel' : '') + (it.cikis ? ' cikis' : ''),
                   it.label);
    a.href = '#' + it.href;
    a.dataset.route = it.href;
    /* CSS'te #menu a[aria-current="page"]::before kuralı vardı ama bunu
       kimse yazmıyordu: işaret hiç görünmüyor, ekran okuyucu da 13 satır
       içinde hangisinin açık olduğunu söyleyemiyordu. */
    if (it.href === suAnkiRota()) a.setAttribute('aria-current', 'page');
    if (it.indent) a.style.paddingLeft = '34px';   // seri satirlari bir kademe icerde
    li.appendChild(a);
    ul.appendChild(li);
  });

  const lang = K.el('div');
  lang.id = 'lang';
  LANGS.forEach((code, i) => {
    if (i) lang.appendChild(K.el('span', 'sep2', '·'));
    const b = K.el('button', null, code.toUpperCase());
    b.type = 'button';
    b.setAttribute('aria-current', String(code === LANG));
    b.setAttribute('aria-label', SITE.i18n[code].ui.lang_name);
    /* Dugmenin kendi dili. lang="tr" bir belgede "English" ve
       "Français" Turkce fonetikle okunuyordu -- etiketleriYaz'in gomulu
       Turkce etiketler icin duzelttigi hatanin ters yonu. */
    b.lang = code;
    b.addEventListener('click', () => setLang(code));
    lang.appendChild(b);
  });
  kutu.appendChild(ul);
  kutu.appendChild(lang);

  /* Satirlar sirayla netlessin: etiketlerin aydinlanmasi. */
  let n = 0;
  kutu.querySelectorAll('li, .grouplbl').forEach((el) => {
    if (el.classList.contains('sep')) return;
    el.style.setProperty('--d', (190 + (n++) * 14) + 'ms');
  });
  lang.style.setProperty('--d', (190 + n * 14) + 'ms');

  /* satir uzerine gelince karsilik sutunu degissin */
  kutu.querySelectorAll('a[data-route]').forEach((a) => {
    a.addEventListener('pointerenter', () => kOniz(a.dataset.route));
    a.addEventListener('focus', () => kOniz(a.dataset.route));
    a.addEventListener('click', (e) => {
      e.preventDefault();
      menuGit(a.dataset.route);
    });
  });
  kutu.addEventListener('pointerleave', () => kOniz(null));

  const b = BG[bgKey] || BG.acilis;
  paintMenu((b && b.palette) || []);
}

/* == GECIS ================================================================
   Tiklanan satirin gorseli, gidilen sayfanin ilk eserine DONUSEREK geciyor
   (View Transitions). Bakilan sey sayfanin kendisi oluyor; gecis bir kesme
   degil, surekli bir hareket. Desteklenmeyen tarayicida ayni gezinme
   gecissiz calisir. */
function menuGit(route) {
  const kaynak = document.getElementById('mon-img');
  const gorselli = kaynak && !kaynak.hidden;
  const uygula = () => { closeMenu(); KABUK.git(route); };
  /* GEZINME ANIMASYONA BAGLI KALAMAZ. startViewTransition'in geri cagrisi
     baslamazsa (arka plan sekmesi, ust uste gecis, olculdu: donmus zaman
     cizelgesinde hic calismiyor) menu acik kalir ve tiklama hicbir sey
     yapmaz. Zaman asimi yedegi: 250 ms icinde gecis baslamadiysa gezinme
     yine de olur, yalnizca animasyon kaybolur. */
  let calisti = false;
  const birKez = () => { if (calisti) return; calisti = true; uygula(); };

  if (!document.startViewTransition || K.reduced()) return birKez();
  if (gorselli) kaynak.style.viewTransitionName = 'eser';
  let vt;
  try { vt = document.startViewTransition(birKez); }
  catch (e) { birKez(); return; }
  setTimeout(birKez, 250);
  vt.finished.catch(() => {}).then(() => {
    if (gorselli) kaynak.style.viewTransitionName = '';
    if (KABUK.gecisBitti) KABUK.gecisBitti();
  });
}

/* Boya katmani markup'a degil buraya konuyor: iki sayfa da ayni menuyu
   kullaniyor, markup'a yazilsaydi iki yerde durur ve zamanla ayrisirdi.
   Kac darbe oldugunu firca.css soyluyor (--darbe), boylece darbe sayisi
   degisince burayi duzeltmek gerekmiyor. */
(function boyaKur() {
  if (!menuEl || document.getElementById('boya')) return;
  const boya = document.createElement('div');
  boya.id = 'boya';
  boya.setAttribute('aria-hidden', 'true');
  menuEl.insertBefore(boya, menuEl.firstChild);
  const n = parseInt(getComputedStyle(boya).getPropertyValue('--darbe'), 10);
  for (let i = 0; i < (n > 0 ? n : 0); i++) boya.appendChild(document.createElement('i'));
})();

/* ── MENÜ AÇILINCA KÂĞIT ÇEVRİLİP KENARA ÇEKİLİR ──────────────────────────
   Menü panelinin kâğıdın üstüne binmemesi için. Kayma miktarı elle
   yazılmıyor: menünün gerçek sağ kenarı ve kâğıdın YERLEŞİM ölçüleri
   okunuyor.

   offsetLeft/offsetWidth kullanılıyor, getBoundingClientRect DEĞİL —
   rect dönüşüm uygulanmış hâli verir, yani menü ikinci kez açıldığında
   kâğıdın çevrilmiş hâlini ölçüp üstüne bir daha kaydırırdı. offset*
   değerleri yerleşimden gelir, transform onları etkilemez. */
/* Menu acik mi? Secici yerine duruma bakiyor: bkz. POPOVER_VAR notu. */
function menuAcikMi() {
  if (!menuEl) return false;
  if (POPOVER_VAR && menuEl.showPopover) {
    try { return menuEl.matches(':popover-open'); } catch (e) { /* yut */ }
  }
  return menuEl.classList.contains('open');
}

function kagidiKacir() {
  const shell = document.getElementById('shell');
  if (!shell) return;

  /* Hareket azaltma kaymayi KAPATMIYOR: panelin iceriğin ustune binmemesi
     bir islev, donme ise gosteri. CSS tarafinda --don ve --kucul
     sifirlaniyor, gecis de kapali; yani kagit zipliyor ama yerini
     birakiyor. Onceden burada erken cikilıyordu ve panel iceriğin
     ustunde kaliyordu -- CSS yorumu bunun tersini soyluyordu. */
  /* Telefonda ERKEN CIKIS KALKTI. Once "kart kucuk, kagidin ustune
     binmiyor" diye burada donuluyordu; olcum bunu curuttu (boya ekranin
     %96'sini kapliyordu). Artik telefonda da ayni hesap kosuyor. */
  const acik = menuAcikMi();
  if (!acik) {
    shell.style.removeProperty('--kac');
    shell.style.removeProperty('--kucul');
    shell.style.removeProperty('--mentese-y');
    return;
  }

  /* Kâğıda açılacak boşluk ÖLÇÜLEN taşmadan geliyor. Eskiden burada
     `bosluk = 56` yazıyordu ("taşma 40 + 16 temiz") ve kabuk.css'te de
     kırpma ayrıca -40 px yazılıydı: aynı varlığı tarif eden iki ayrı
     tahmin, ikisi de yanlış. Gerçek taşma panel eninin %29'u
     (firca.py ölçüyor, firca.css --tasma-oran ile yayınlıyor).
     Sağ pay ayrı bir şey: o boyayla ilgili değil, yalnız ekrandan
     taşmayı engelliyor. */
  const TEMIZ = 16;
  const boyaEl = document.getElementById('boya');
  const menuSag = menuEl.getBoundingClientRect().right;
  /* Tasma GERCEK OLCUMLE. Once firca.py'nin yayinladigi sabit bir oran
     kullaniliyordu; kutular kaynagin oranina baglandiktan sonra tasma
     panel YUKSEKLIGINE bagli hale geldi ve tek oranla ifade
     edilemiyor. Olculdu: sabit oranla bosluk yetmiyordu ve boya kagida
     28.6 px biniyordu. Darbelerin kendi kutulari okunuyor, yani hangi
     geometri olursa olsun dogru. */
  let darbeSag = menuSag;
  if (boyaEl) {
    for (const d of boyaEl.children) {
      const r = d.getBoundingClientRect();
      if (r.right > darbeSag) darbeSag = r.right;
    }
  }
  const bosluk = (darbeSag - menuSag) + TEMIZ;
  const sagPay = 26;
  const sol = shell.offsetLeft;
  const en = shell.offsetWidth;
  if (!en) return;

  /* Açı ve perspektif CSS'ten okunuyor, burada ikinci kez yazılmıyor. */
  const aci = parseFloat(getComputedStyle(shell).getPropertyValue('--don')) || 0;
  const A = Math.abs(aci) * Math.PI / 180;
  const derin =
    parseFloat(getComputedStyle(shell).getPropertyValue('--derinlik')) || 2200;

  /* Taban KIPE BAGLI. Donme varken cos(38) daralmasi izdusumu kendisi
     daraltiyor, o yuzden 0.72 yetiyor (0.78'de boya kagidin alt
     kosesindeki kunyeye biniyordu -- olculdu). Hareket azaltmada ise
     donme kapali, yani o daralma KAZANCI YOK ve olcegin isi tek basina
     yapmasi gerekiyor.
     Uc ayri degerlendirici bunu bagimsiz olarak olctu: 0.72 tabani
     hareket azaltmada kagidi menunun altindan cikaramiyor, 1381 px'te
     270 px, 1440 px'te 212 px binisme kaliyor -- yani hareketten
     rahatsiz olan, tam da bu ayari acan kullanicida panelin icerigin
     ustune binmemesi islevi cokuyor. 1440'ta gereken 0.53, 1381'de
     0.42; taban 0.40'a cekiliyor.
     Not: kabuk.css'teki `--kucul: 1` bildirimi OLU koddu, cunku burada
     satir ici yaziliyor ve satir ici her medya kuralini yener. Orada
     silindi, karar tek yerde: burada. */
  /* Taban uc kipe ayriliyor. Donme varken cos(38) daralmasi izdusumu
     kendisi daraltiyor; hareket azaltmada o kazanc yok; telefonda ise
     ekran o kadar dar ki kagidin menunun altindan cikmasi icin daha da
     kuculmesi gerekiyor -- 390 px'te hesap 0.536 veriyor, masaustunun
     0.72 tabani orada kagidi menunun altinda birakirdi. */
  const dar = window.innerWidth <= 760;
  /* Telefon tabani 0.52 denendi ve YANLISTI: hesabin USTUNDE kaldigi
     icin kelepceliyor, yani kagit gerekenden buyuk kaliyor ve menunun
     altindan cikamiyordu (olculdu: 360 px'te 12.5, 320 px'te 37 px
     binisme). Taban hesabin ALTINDA olmali ki gercek geometri kullanilsin:
     390 px'te hesap 0.463, 360'ta 0.39 veriyor. 0.36 ikisini de serbest
     birakiyor; 320 px gibi uc dar ekranda yine kelepceliyor ve orada
     kurtulmadan vazgeciliyor -- tasmamak pazarlik disi, kurtulmak degil. */
  /* A===0 dali `dar`i SORMUYORDU: hareketsiz telefon tabani 0.40,
     hareketli telefon tabani 0.36 idi -- tam tersi olmali, cunku donme
     kapaliyken cos(38) daralma kazanci da yok. Olculdu: hareket
     azaltmali 390 px'te boya icerige 13.4 px biniyordu. */
  /* Dar taban 0.36'dan 0.26'ya: 320 px'te bosluk yetmiyordu ve boya
     kagida 15.8 px biniyordu (olculdu). 390 ve uzeri etkilenmiyor,
     orada hesap tabanin ustunde kaliyor. */
  const enAz = A === 0 ? (dar ? 0.20 : 0.40) : (dar ? 0.26 : 0.72),
        enCok = 0.94;
  const hedefSol = menuSag + bosluk;
  const sagSinir = window.innerWidth - sagPay;
  const sagYerli = sol + en;              /* dönüşümsüz sağ kenar = menteşe */

  /* MENTEŞE SAĞ KENARDA, ve bu bütün hesabı değiştiriyor. Dönüşüm
     menteşeye göre uygulanıyor, perspective()'in izdüşüm merkezi de o:
     sağ kenar z=0'da kalıyor, yani --kac onu BİREBİR kaydırıyor ve
     kâğıdın en sağdaki noktası o. Sert kural ("kâğıt ekrandan
     TAŞMAYACAK") böylece tek kelepçeye iniyor — eski sol menteşede
     tahmin-ve-kırp hesabıydı ve 1024 px'te 82 px taşımıştı.

     Sol kenar ise arkaya gittiği için perspektif onu menteşeye doğru
     ÇEKİYOR; kâğıt en×cos(A) tahmininden daha da dar görünüyor:
       u = en*kucul,  F = derin/(derin + u*sin A)
       sol kenar L = sagYerli + (kac - u*cos A) * F              */
  const D = hedefSol - sagYerli;
  const F = (u) => derin / (derin + u * Math.sin(A));

  /* Kaydırma GEREKTİĞİ kadar, azami kadar değil. Sağ kenarı her zaman
     sınıra dayamak taşmayı sıfırlıyordu ama jesti bozuyordu: ölçüldü,
     1920 px'te kâğıt sağa yapışıp menüyle arasında 545 px boşluk
     bırakıyordu (hedef 56). Menteşe sağa geçtiğinden dönme ve ölçek
     sol kenarı kendiliğinden sağa çekiyor; geniş ekranda kaydırmaya
     hiç gerek kalmıyor. L = hedefSol'dan gereken kac çözülüyor:
       kac = D/F + u*cos A
     Kelepçe: 0 ile sağ sınır arası. Sınır eksiyse (kâğıt zaten
     taşıyorsa) kaydırma sola dönüyor, çünkü taşmama pazarlık dışı. */
  const u0 = en * enCok;
  const kac = Math.min(sagSinir - sagYerli,
                       Math.max(0, D / F(u0) + u0 * Math.cos(A)));

  /* Ölçek: o kac ile L >= hedefSol eşitliğinden. L, kucul'de azalan.
       u <= derin*(kac - D) / (derin*cos A + D*sin A)
     A=0 (hareket azaltma) halinde (sagSinir - hedefSol)/en'e düşüyor,
     yani dönmesiz oturtma — sınır değeri doğru. */
  const bol = derin * Math.cos(A) + D * Math.sin(A);
  let kucul = bol > 0 ? derin * (kac - D) / (bol * en) : enCok;
  /* Menünün altından tam çıkmak tercih; sığmıyorsa kurtulmadan
     vazgeçiliyor (enAz), taşmadan asla — taşmayı kac zaten kesiyor. */
  kucul = Math.min(enCok, Math.max(enAz, kucul));

  /* DIKEY mentese yeri. CSS'te %50 yaziliydi ve o shell'in KENDI
     yuksekliginin ortasi demek -- kisa sayfada tesadufen goruntu
     alaninin ortasina denk geliyordu, uzun sayfada degil. Olculdu:
     galeri sayfasinda shell 2795 px, mentese y=1397 ve kagit ekranin
     tamamen disina savruluyordu (ust 825, ekran 780).
     Dogrusu goruntu alaninin ortasi; menu acikken kayma kilitli oldugu
     icin bu deger acilis anindaki konuma gore sabit. */
  const menteseY = (window.scrollY + window.innerHeight / 2) - shell.offsetTop;
  shell.style.setProperty('--mentese-y', menteseY.toFixed(1) + 'px');
  shell.style.setProperty('--kac', kac.toFixed(1) + 'px');
  shell.style.setProperty('--kucul', kucul.toFixed(4));
}

/* Firca darbeleri hamburgere ILK TEMASTA yukleniyor. Onceden dokuzu
   da <link rel=preload> ile her sayfada iniyordu (324 KB) ve Chrome
   "preloaded but not used" uyarisi veriyordu: panel display:none bir
   popover, ziyaretcilerin cogu hic acmiyor. Temas anindan menunun
   acilmasina kadar gecen sure (hover -> tik) darbelerin inmesine
   yetiyor; dokunmatikte pointerdown ile tik arasinda yine bir pay var.
   Tek kaynak korunuyor: liste derlemede varlik dosyalarindan uretiliyor
   (window.FIRCA_LISTE). */
/* KAYDIRMA KILIDI SAYACLI. Onceden `durdur` sinifi tek boole idi ve
   uc sahibi vardi (menu, isik kutusu, yakinlastirma): en ustteki katman
   kapaninca alttaki hala acikken kilidi biraktiriyordu -- uc yoldan
   tekrar uretildi. Sayac her sahibi kendi adiyla tutuyor. */
const kilitSahipleri = new Set();
window.KABUK_KILIT = {
  al(sahip) {
    kilitSahipleri.add(sahip);
    document.documentElement.classList.add('durdur');
  },
  birak(sahip) {
    kilitSahipleri.delete(sahip);
    if (!kilitSahipleri.size) {
      document.documentElement.classList.remove('durdur');
    }
  },
};

let fircaYuklendi = false;
function fircayiYukle() {
  if (fircaYuklendi) return;
  fircaYuklendi = true;
  const liste = (typeof window !== 'undefined' && window.FIRCA_LISTE) || [];
  for (const yol of liste) { const g = new Image(); g.src = yol; }
}
if (btn) {
  for (const olay of ['pointerenter', 'focus', 'pointerdown']) {
    btn.addEventListener(olay, fircayiYukle, { once: true, passive: true });
  }
}
/* Temas TEK basina yetmiyor: dokunmatikte pointerdown ile tik arasi
   ~50-100 ms ve 324 KB o surede inmez. Onyukleme tam bu yuzden
   eklenmisti ("panel boyasiz acilabiliyordu"). Cozum ikisini birlestirmek:
   tarayici BOSTA kalinca sessizce yukle -- ilk boyamayi etkilemiyor ama
   menu acilmadan once hazir oluyor. Destegi yoksa gecikmeli zamanlayici. */
if (typeof requestIdleCallback === 'function') {
  requestIdleCallback(fircayiYukle, { timeout: 2500 });
} else {
  setTimeout(fircayiYukle, 1800);
}

addEventListener('resize', kagidiKacir, { passive: true });

function openMenu() {
  buildMenu();
  /* Kayma kilidi. Menu gorsel olarak kipli, `inert` ile fiilen kipli --
     ama kiplilgin ucuncu ayagi olan kayma kilidi eksikti: olculdu, menu
     acikken document.scrollingElement.scrollTop = 400 yazmak TUTUYORDU.
     popover=auto kaymayi kilitlemiyor, inert de yalniz pointer-events'i
     kesiyor; tekerlek perdenin ustunden goruntu alanina gidiyordu ve
     kullanici menuyu kaydirirken kagit altindan kayip gidiyordu.
     Orunru sergi.html'de detay katmani icin zaten vardi, menuye
     uygulanmamisti. */
  window.KABUK_KILIT.al('menu');
  document.documentElement.classList.add('menuacik');
  kOniz(null, true);
  if (menuEl.showPopover) menuEl.showPopover();
  else { menuEl.classList.add('open'); trapRelease = K.trap(menuEl); }
  btn.setAttribute('aria-expanded', 'true');
  /* Menü görünür OLDUKTAN sonra ölçülüyor: kapalı popover'ın sağ
     kenarı 0 gelir ve kâğıt hiç kaçmaz. */
  kagidiKacir();
  arkaPlanDondur(true);
  /* Odak ilk satıra değil PANELE veriliyor. Eskiden ilk bağlantı
     odaklanıyordu ve üstünde tarayıcının odak dikdörtgeni kalıyordu:
     elle boyanmış bir panelde tek geometrik-dijital unsur oydu ve
     "dışarıdan eklenmiş" duruyordu. Panele odaklanmak klavye erişimini
     bozmuyor — Tab ilk satıra gidiyor — ama gereksiz halkayı kaldırıyor.
     Kipli bir katmanda odağı kabın kendisine vermek yaygın ve doğru
     örüntü. */
  menuEl.setAttribute('tabindex', '-1');
  menuEl.focus({ preventScroll: true });
}
/* Menü GÖRSEL OLARAK kipli: perde sahneyi karartıyor ve üst katman
   arkadaki tıklamaları yiyor. Ama popover=auto KİPLİ DEĞİL — odağı
   tutmaz ve arka içeriği ekran okuyucudan gizlemez. Sonuç eşitsizlik:
   fare kullanıcısı için sayfa kilitli, klavye ve ekran okuyucu kullanıcısı
   için tamamen gezilebilir; son menü satırından Tab'a basınca odak
   çevrilmiş kâğıdın içindeki bağlantılara kaçıyordu.

   inert ikisini birden çözüyor: odak dışarı çıkmıyor ve arka içerik
   erişilebilirlik ağacından düşüyor. */
/* INERT SAYACLI. Onceden her cagri butun durumu tek basina
   belirliyordu: menuyu acip kapatmak, isik kutusu hala acikken
   `arkaPlanDondur(false)` cagirip butun inert'i siliyordu (olculdu:
   kacis hedefi 1 -> 9). Uc katman ayni kaynagi paylasiyor, o yuzden
   sahip listesi tutuluyor: en az bir sahip varken inert aktif ve
   BUTUN sahiplerin katmani muaf. */
const inertSahipleri = new Map();       /* ad -> muaf oge (ya da null) */

function arkaPlanDondur(kapat, haric, ad) {
  const anahtar = ad || (haric && haric.id) || 'menu';
  if (kapat) inertSahipleri.set(anahtar, haric || null);
  else inertSahipleri.delete(anahtar);
  _inertUygula();
}

function _inertUygula() {
  /* Sabit liste eksik kaliyordu: sergi sayfasindaki #detay (tam ekran
     eser katmani) #shell'in KARDESI ve listede yoktu; o katman acikken
     menu acilirsa odak oradaki yedi dugmeye kaciyordu. Artik govdenin
     butun ust duzey cocuklari kapsaniyor -- menunun kendisi ve ekran
     okuyucu duyuru bolgesi haric.

     Ozellik degil NITELIK yaziliyor: [inert] bir CSS kancasi olarak da
     kullanilabiliyor ve destegi olmayan tarayicida en azindan
     pointer-events kapatilabiliyor. */
  const kapat = inertSahipleri.size > 0;
  const birak = new Set([menuEl, document.getElementById('duyuru'),
                         document.getElementById('menubtn')]);
  /* BUTUN sahiplerin katmani muaf: menu acikken isik kutusu acilirsa
     ikisi de acik kalmali, biri otekini oldurmemeli. */
  for (const oge of inertSahipleri.values()) {
    if (oge) birak.add(oge);
  }
  Array.prototype.forEach.call(document.body.children, (el) => {
    if (el.tagName === 'SCRIPT' || el.tagName === 'STYLE') return;
    /* Muaf oge ATLANMIYOR, inert'i DUSURULUYOR. Onceki hali `return`
       ediyordu ve gercek akista yakinlastirma katmanini olduruyordu:
       karta tiklaninca #detay aciliyor ve govdenin butun cocuklarini
       inert ediyor (#zoom dahil); sonra gorsele tiklaninca zoomAc
       #zoom'u muaf listesine koyuyor, dongu onu ATLIYOR ve daha once
       aldigi inert hic silinmiyor. Sonuc: katman ekranda kusursuz
       gorunuyor ama surukleme, tekerlek, pinch, cift tik ve kapatma
       dugmesi CALISMIYOR ([inert]{pointer-events:none}), ekran okuyucu
       agacinda da yok. Tek cikis Escape'ti (o window'da yakalama
       fazinda oldugu icin hayatta kalmis).
       Kendi testlerim bunu kacirdi: dispatchEvent ile gonderilen
       sentetik olaylar pointer-events:none'i ATLIYOR ve dinleyiciyi
       yine calistiriyor. Yani "kod dogru" olcumu "kullanici yapabilir"
       demiyor -- isabet denetimi elementFromPoint ile yapilmali. */
    el.toggleAttribute('inert', !!kapat && !birak.has(el));
  });
}
/* Sayfa tarafina aciliyor. KABUK nesnesi SAYFADAN kabuga dogru bilgi
   tasiyor; ters yon icin ayri bir ad kullaniliyor ki ikisi karismasin. */
window.KABUK_INERT = arkaPlanDondur;

/* Kapanışta yapılacak toparlama: hangi jestle kapanırsa kapansın (düğme,
   Escape, dışına tıklama) burası çalışıyor. */
function toparla() {
  window.KABUK_KILIT.birak('menu');
  document.documentElement.classList.remove('menuacik');
  btn.setAttribute('aria-expanded', 'false');
  arkaPlanDondur(false);
  kagidiKacir();
  if (trapRelease) { trapRelease(); trapRelease = null; }
}

function closeMenu() {
  /* Toparlama popover yolunda `toggle` olayindan da geliyor; burada
     tekrar cagirmak onu iki kez kosturuyordu. Bu yuzden closeMenu yalniz
     KAPATIYOR, toparlamayi olaya birakiyor. Yedek yolda olay hic
     atesenmedigi icin orada elle cagriliyor. */
  if (POPOVER_VAR && menuEl.hidePopover && menuAcikMi()) {
    menuEl.hidePopover();
    return;                     /* toparlama toggle olayindan gelecek */
  }
  menuEl.classList.remove('open');
  /* Toparlama menü GERÇEKTEN kapandıktan sonra: daha önce önce
     çağrılıyordu ve ölçüm menüyü hâlâ açık görüp --kac'ı yeniden
     yazıyordu (ölçüldü: kapandıktan sonra 508 px kalıyordu). */
  toparla();
}
/* Düğme GERÇEK açık durumuna bakıyor. Eskiden yalnızca .open sınıfına
   bakıyordu; o sınıf ise popover DESTEKLENMEYEN yolda ekleniyor. Yani
   normal tarayıcıda menü açıkken düğmeye basmak closeMenu yerine
   openMenu çağırıyor, showPopover açık bir popover'da hata atıyor ve
   menü kapanmıyordu. Hamburger görsel olarak ✕'e dönüştüğü için
   kullanıcı ona basıp kapanmasını bekliyor. Ölçerek yakalandı:
   ikinci tıklamadan sonra popover=true kalıyordu. */
btn.addEventListener('click', () => (menuAcikMi() ? closeMenu() : openMenu()));
const kapatBtn = document.getElementById('mkapat');
if (kapatBtn) kapatBtn.addEventListener('click', closeMenu);
/* Esc, disina tiklama ve ust katman popover'dan geliyor; elle yazilmasina
   gerek yok. Yalnizca popover desteklenmeyen tarayicida yedek gerekiyor. */
if (!POPOVER_VAR || !menuEl.showPopover) {
  addEventListener('keydown', (e) => { if (e.key === 'Escape') closeMenu(); });
  /* Yedek yolda `toggle` olayi hic atesenmiyor, yani hafif kapanma da
     yoktu: menu yalniz iki dugmeyle kapaniyordu. */
  addEventListener('pointerdown', (e) => {
    if (!menuAcikMi()) return;
    if (menuEl.contains(e.target) || btn.contains(e.target)) return;
    closeMenu();
  }, true);
}
/* Menü Escape ya da dışına tıklamayla da kapanıyor (popover'ın hafif
   kapanması) ve o yol closeMenu'dan GEÇMİYORDU: geriye --kac satır içi
   kalıyor, kâğıt kalıcı olarak sağa kaymış duruyordu. Temizlik yalnızca
   düğmeye basılınca çalışıyordu.

   Artık tek kapanış yolu var: hangi jestle kapanırsa kapansın toparlama
   aynı yerden geçiyor. */
menuEl.addEventListener('toggle', (e) => {
  const acik = e.newState === 'open';
  btn.setAttribute('aria-expanded', acik ? 'true' : 'false');
  if (!acik) toparla();
});

/* Statik Türkçe aria-label'lar markup'a gömülüydü ve dil değişince
   güncellenmiyordu: lang="en" iken ekran okuyucu Türkçe metni İngilizce
   fonetikle okuyordu. Kapatma düğmesinin ise hiç adı yoktu — içi iki boş
   <i>, ekran okuyucu sadece "düğme" diyordu. */
function etiketleriYaz() {
  btn.setAttribute('aria-label', t('menu_open'));
  menuEl.setAttribute('aria-label', t('menu_label'));
  /* Menu artik fiilen kipli: perde sahneyi karartiyor, arka icerik
     inert. Ama yardimci teknolojiye bunu soyleyen bir sey yoktu,
     yani ekran okuyucu kullanicisi kipe girdigini duymuyordu. */
  menuEl.setAttribute('role', 'dialog');
  menuEl.setAttribute('aria-modal', 'true');
  const kapatBtn = document.getElementById('mkapat');
  if (kapatBtn) kapatBtn.setAttribute('aria-label', t('menu_close'));
}

function setLang(next) {
  if (!LANGS.includes(next) || next === LANG) return;
  LANG = next;
  try { localStorage.setItem(LANG_KEY, next); } catch (e) {}
  document.documentElement.lang = LANG;
  const d = document.querySelector('meta[name="description"]');
  if (d) d.setAttribute('content', t('meta_desc'));
  buildMenu();
  etiketleriYaz();
  KABUK.yenile();
}

/* Erişilebilir adlar sayfa açılışında da yazılıyor: menü ilk kez
   açılana kadar buildMenu çalışmıyor, o yüzden hamburger adsız
   kalıyordu. */
etiketleriYaz();
