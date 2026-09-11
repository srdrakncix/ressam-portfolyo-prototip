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
  return { sat: say('--satir-doygunluk', 0.40),
           lig: say('--satir-parlaklik', 0.90),
           adim: say('--satir-adim', 0.015) };
}

function paintMenu(pal) {
  const a = satirAyari();
  document.querySelectorAll('#menu .nav-item').forEach((el, i) => {
    if (el.classList.contains('ozel') || el.classList.contains('cikis')) return;
    if (!pal.length) { el.style.color = '#e9e9e4'; return; }
    const [h, sRaw] = hsl(pal[i % pal.length]);
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
  const yillar = SITE.works.map((w) => w.year);
  const aralik = Math.min(...yillar) + ' — ' + Math.max(...yillar);

  if (!route) {
    return { ust: SITE.artist.mark, ad: SITE.artist.name,
             alt: SITE.works.length + ' eser · ' + SITE.series.length + ' seri · ' + aralik,
             img: yeniEser() };
  }
  if (route === '/galeri') {
    return { ust: t('gal_label'), ad: t('gal_title'), alt: kisalt(t('gal_sub'), 150), img: yeniEser() };
  }
  if (route === '/son') {
    return { ust: t('nav_recent'), ad: SITE.works.length + ' eser · ' + SITE.series.length + ' seri',
             alt: aralik + ' · ' + t('medium'), img: yeniEser() };
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
    document.getElementById('mon-ust').textContent = d.ust || '';
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
    if (it.sep) { li.className = 'sep'; ul.appendChild(li); return; }
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
function kagidiKacir() {
  const shell = document.getElementById('shell');
  if (!shell) return;

  const kapali = matchMedia('(max-width: 760px)').matches ||
                 matchMedia('(prefers-reduced-motion: reduce)').matches;
  const acik = menuEl && menuEl.matches('.open, :popover-open');
  if (kapali || !acik) {
    shell.style.removeProperty('--kac');
    shell.style.removeProperty('--kucul');
    return;
  }

  const bosluk = 26;
  const menuSag = menuEl.getBoundingClientRect().right;
  const sol = shell.offsetLeft;
  const en = shell.offsetWidth;
  if (!en) return;

  /* Çevrilince kâğıdın izdüşümü daralıyor: yaklaşık en × cos(açı).
     Açı CSS'ten okunuyor, burada ikinci kez yazılmıyor. */
  const aci = parseFloat(getComputedStyle(shell).getPropertyValue('--don')) || 0;
  const daralma = Math.cos(aci * Math.PI / 180) || 1;

  /* Sert kural: kâğıt EKRANDAN TAŞMAYACAK. Tercih menünün altından tam
     çıkmak, ama 600 px'lik menü ile tam genişlikte kâğıt dar ekranda
     yan yana sığmıyor (ölçüldü: 1024 px'te 82 px taşıyordu). O zaman
     kurtulmadan vazgeçiliyor, taşmadan asla. */
  const enAz = 0.78, enCok = 0.94;
  let hedefSol = menuSag + bosluk;
  let kucul = Math.min(enCok, Math.max(enAz,
    (window.innerWidth - bosluk - hedefSol) / (en * daralma)));
  const genislik = en * daralma * kucul;
  if (hedefSol + genislik > window.innerWidth - bosluk) {
    hedefSol = Math.max(bosluk, window.innerWidth - bosluk - genislik);
  }
  shell.style.setProperty('--kac', Math.max(0, hedefSol - sol).toFixed(1) + 'px');
  shell.style.setProperty('--kucul', kucul.toFixed(4));
}

addEventListener('resize', kagidiKacir, { passive: true });

function openMenu() {
  buildMenu();
  document.documentElement.classList.add('menuacik');
  kOniz(null, true);
  if (menuEl.showPopover) menuEl.showPopover();
  else { menuEl.classList.add('open'); trapRelease = K.trap(menuEl); }
  btn.setAttribute('aria-expanded', 'true');
  /* Menü görünür OLDUKTAN sonra ölçülüyor: kapalı popover'ın sağ
     kenarı 0 gelir ve kâğıt hiç kaçmaz. */
  kagidiKacir();
  arkaPlanDondur(true);
  const first = menuEl.querySelector('a');
  if (first) first.focus({ preventScroll: true });
}
/* Menü GÖRSEL OLARAK kipli: perde sahneyi karartıyor ve üst katman
   arkadaki tıklamaları yiyor. Ama popover=auto KİPLİ DEĞİL — odağı
   tutmaz ve arka içeriği ekran okuyucudan gizlemez. Sonuç eşitsizlik:
   fare kullanıcısı için sayfa kilitli, klavye ve ekran okuyucu kullanıcısı
   için tamamen gezilebilir; son menü satırından Tab'a basınca odak
   çevrilmiş kâğıdın içindeki bağlantılara kaçıyordu.

   inert ikisini birden çözüyor: odak dışarı çıkmıyor ve arka içerik
   erişilebilirlik ağacından düşüyor. */
function arkaPlanDondur(kapat) {
  const hedefler = [document.getElementById('shell'),
                    document.getElementById('bgA'),
                    document.getElementById('bgB')];
  hedefler.forEach((el) => { if (el) el.inert = !!kapat; });
}

/* Kapanışta yapılacak toparlama: hangi jestle kapanırsa kapansın (düğme,
   Escape, dışına tıklama) burası çalışıyor. */
function toparla() {
  document.documentElement.classList.remove('menuacik');
  btn.setAttribute('aria-expanded', 'false');
  arkaPlanDondur(false);
  kagidiKacir();
  if (trapRelease) { trapRelease(); trapRelease = null; }
}

function closeMenu() {
  document.documentElement.classList.remove('menuacik');
  if (menuEl.hidePopover && menuEl.matches(':popover-open')) menuEl.hidePopover();
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
btn.addEventListener('click', () =>
  (menuEl.matches('.open, :popover-open') ? closeMenu() : openMenu()));
const kapatBtn = document.getElementById('mkapat');
if (kapatBtn) kapatBtn.addEventListener('click', closeMenu);
/* Esc, disina tiklama ve ust katman popover'dan geliyor; elle yazilmasina
   gerek yok. Yalnizca popover desteklenmeyen tarayicida yedek gerekiyor. */
if (!menuEl.showPopover) {
  addEventListener('keydown', (e) => { if (e.key === 'Escape') closeMenu(); });
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
