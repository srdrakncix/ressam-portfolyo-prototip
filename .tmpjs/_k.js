
const SITE={works:[],series:[],artist:{}};
/* ── KIT ───────────────────────────────────────────────────────────────────
   Üç prototipin de paylaştığı davranış katmanı. Tasarımdan bağımsız:
   burada hiçbir görsel karar yok, sadece mekanik. Görünüm tamamen CSS'te.
   ────────────────────────────────────────────────────────────────────────── */

const K = (() => {

  /* ── tercihler ─────────────────────────────────────────────────────────── */

  const reduced = () =>
    window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  const store = {
    get(k) { try { return localStorage.getItem(k); } catch { return null; } },
    set(k, v) { try { localStorage.setItem(k, v); } catch { /* yok say */ } },
  };

  /* ── tema ──────────────────────────────────────────────────────────────────
     Üç durum: 'light' | 'dark' | null (sistem). Kök öğeye data-theme basar.   */

  const Theme = {
    KEY: 'da-theme',
    init() {
      const saved = store.get(this.KEY);
      if (saved === 'light' || saved === 'dark') {
        document.documentElement.dataset.theme = saved;
      } else {
        /* Varsayılan AÇIK: sistemi karanlıkta olan ziyaretçi de krem zemin
           görsün. Sistem tercihine uymak yerine bilinçli bir karar —
           düğme yine duruyor, isteyen koyuya geçer. */
        document.documentElement.dataset.theme = 'light';
      }
      return this;
    },
    current() {
      return document.documentElement.dataset.theme ||
        (matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
    },
    toggle() {
      const next = this.current() === 'dark' ? 'light' : 'dark';
      document.documentElement.dataset.theme = next;
      store.set(this.KEY, next);
      document.dispatchEvent(new CustomEvent('themechange', { detail: next }));
      return next;
    },
  };

  /* ── ilerlemeli görsel ─────────────────────────────────────────────────────
     LQIP (20px bulanık) anında görünür, tam çözünürlük görünür alana
     girince yüklenir ve decode() bittikten SONRA geçiş yapar — böylece
     yarım boyanmış kare hiç görünmez.                                        */

  const io = 'IntersectionObserver' in window
    ? new IntersectionObserver((entries, obs) => {
        for (const e of entries) {
          if (!e.isIntersecting) continue;
          obs.unobserve(e.target);
          load(e.target);
        }
      }, { rootMargin: '600px 0px' })
    : null;

  function load(fig) {
    const src = fig.dataset.src;
    if (!src || fig.dataset.loaded) return;
    fig.dataset.loaded = '1';
    const img = new Image();
    img.decoding = 'async';
    img.alt = fig.dataset.alt || '';
    img.src = src;
    let gosterildi = false;
    const show = () => {
      if (gosterildi) return;
      gosterildi = true;
      img.className = 'k-full';
      fig.appendChild(img);
      requestAnimationFrame(() => fig.classList.add('is-loaded'));
    };
    /* decode() TEK dayanak olamaz: bazı ortamlarda sözü hiç sonuçlanmıyor
       (ölçtüm — headless sanal zamanda onload çalışıyor ama decode ne
       çözülüyor ne reddediliyor) ve eser kalıcı olarak bulanık LQIP'te
       kalıyor. onload ve gecikmeli bir tamamlanma kontrolü yedek. */
    if (img.decode) img.decode().then(show).catch(show);
    img.onload = show;
    setTimeout(() => { if (img.complete && img.naturalWidth) show(); }, 1200);
  }

  /**
   * Bir eser için <figure> üretir.
   * @param {object} w   SITE.works elemanı
   * @param {object} opt {eager:boolean, sizes:string, cls:string}
   */
  function figure(w, opt = {}) {
    const fig = document.createElement('figure');
    fig.className = 'k-fig ' + (opt.cls || '');
    fig.style.setProperty('--ratio', w.ratio);
    fig.style.setProperty('--tone', w.tone);
    fig.dataset.src = w.src;
    fig.dataset.alt = `${w.title}, ${w.year} — ${w.medium}, ${w.size}`;

    const lq = document.createElement('img');
    lq.className = 'k-lqip';
    lq.src = w.lqip;
    lq.alt = '';
    lq.setAttribute('aria-hidden', 'true');
    fig.appendChild(lq);

    if (opt.eager) load(fig);
    else if (io) io.observe(fig);
    else load(fig);

    return fig;
  }

  /* ── görünüme girince açığa çıkma ─────────────────────────────────────── */

  const revealIO = 'IntersectionObserver' in window
    ? new IntersectionObserver((entries, obs) => {
        for (const e of entries) {
          if (!e.isIntersecting) continue;
          obs.unobserve(e.target);
          e.target.classList.add('is-in');
        }
      }, { rootMargin: '0px 0px -12% 0px', threshold: 0.05 })
    : null;

  function reveal(root = document) {
    const els = root.querySelectorAll('[data-reveal]:not(.is-in)');
    if (reduced() || !revealIO) {
      els.forEach(el => el.classList.add('is-in'));
      return;
    }
    els.forEach(el => revealIO.observe(el));
  }

  /* ── hash yönlendirici ─────────────────────────────────────────────────────
     #/                 ana sayfa
     #/seri/<key>       seri
     #/eser/<slug>      tek eser
     #/hakkinda #/iletisim                                                    */

  const Router = {
    routes: [],
    on(re, fn) { this.routes.push([re, fn]); return this; },
    parse() {
      const h = location.hash.replace(/^#/, '') || '/';
      for (const [re, fn] of this.routes) {
        const m = h.match(re);
        if (m) return { fn, args: m.slice(1), path: h };
      }
      return { fn: this.routes[0][1], args: [], path: '/' };
    },
    go(path, opts = {}) {
      if (opts.replace) location.replace('#' + path);
      else location.hash = path;
    },
    start() {
      const run = () => {
        const { fn, args, path } = this.parse();
        fn(...args);
        this.last = path;
      };
      addEventListener('hashchange', run);
      run();
      return this;
    },
  };

  /* ── odak tuzağı (katman/lightbox için) ────────────────────────────────── */

  const SELECTOR =
    'a[href],button:not([disabled]),input,select,textarea,[tabindex]:not([tabindex="-1"])';

  function trap(node) {
    const prev = document.activeElement;
    const onKey = (e) => {
      if (e.key !== 'Tab') return;
      const f = [...node.querySelectorAll(SELECTOR)].filter(el => el.offsetParent !== null);
      if (!f.length) return;
      const first = f[0], last = f[f.length - 1];
      if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
      else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
    };
    node.addEventListener('keydown', onKey);
    return () => {
      node.removeEventListener('keydown', onKey);
      if (prev && prev.focus) prev.focus();
    };
  }

  /* ── küçük yardımcılar ─────────────────────────────────────────────────── */

  const el = (tag, cls, html) => {
    const n = document.createElement(tag);
    if (cls) n.className = cls;
    if (html != null) n.innerHTML = html;
    return n;
  };

  const bySeries = (key) => SITE.works.filter(w => w.series === key);
  const seriesOf = (key) => SITE.series.find(s => s.key === key);
  const workBySlug = (slug) => SITE.works.find(w => w.slug === slug);
  const neighbours = (w) => {
    const list = SITE.works;
    const i = list.indexOf(w);
    return {
      prev: list[(i - 1 + list.length) % list.length],
      next: list[(i + 1) % list.length],
    };
  };

  return { reduced, store, Theme, figure, load, reveal, Router, trap, el,
           bySeries, seriesOf, workBySlug, neighbours };
})();


const main = document.getElementById('main');

/* ── dil ─────────────────────────────────────────────────────────────────── */

const LANGS = ['tr', 'en', 'fr'];
const LANG_KEY = 'cs-lang';

function initialLang() {
  try {
    const saved = localStorage.getItem(LANG_KEY);
    if (LANGS.includes(saved)) return saved;
  } catch (e) { /* yok say */ }
  const nav = (navigator.language || '').slice(0, 2).toLowerCase();
  return LANGS.includes(nav) ? nav : 'tr';
}

let LANG = initialLang();

/* L(): o dilin içerik paketi. t(): arayüz dizgesi, eksikse Türkçeye düşer. */
const L = () => SITE.i18n[LANG] || SITE.i18n.tr;
const t = (k) => (L().ui && L().ui[k]) || SITE.i18n.tr.ui[k] || k;
const fill = (s, vals) => s.replace(/\{(\w+)\}/g, (_, k) => vals[k]);

/* Türkçe büyük harf: JS'in toUpperCase()'i i → I veriyor, İ değil. */
const upTR = (s) => s.toLocaleUpperCase('tr-TR');

function applyLang() {
  document.documentElement.lang = LANG;
  const d = document.querySelector('meta[name="description"]');
  if (d) d.setAttribute('content', t('meta_desc'));
  document.querySelector('.skip').textContent = t('skip');
  burger.setAttribute('aria-label', t('menu'));
  buildNav();
  document.querySelectorAll('#lang button').forEach((b) => {
    b.setAttribute('aria-current', String(b.dataset.lang === LANG));
  });
}

function setLang(next) {
  if (!LANGS.includes(next) || next === LANG) return;
  LANG = next;
  try { localStorage.setItem(LANG_KEY, next); } catch (e) { /* yok say */ }
  applyLang();
  K.Router.parse().fn(...K.Router.parse().args);   /* aynı sayfayı yeniden çiz */
}

{
  const parts = SITE.artist.name.split(' ');
  document.getElementById('navname').innerHTML =
    parts[0] + ' <b>' + upTR(parts.slice(1).join(' ')) + '</b>';
}

/* ── menü ────────────────────────────────────────────────────────────────── */

const navlistEl = document.getElementById('navlist');

function navItems() {
  return [
    { href: '/son', label: t('nav_recent') },
    ...SITE.series.map(s => ({ href: '/seri/' + s.key, label: L().series[s.key].title })),
    { gap: true },
    { href: '/atolye',     label: t('nav_studio') },
    { href: '/biyografi',  label: t('nav_bio') },
    { href: '/sergiler',   label: t('nav_exh') },
    { href: '/koleksiyon', label: t('nav_coll') },
    { href: '/yayinlar',   label: t('nav_pub') },
    { href: '/basin',      label: t('nav_press') },
    { gap: true },
    { href: '/iletisim',   label: t('nav_contact') },
  ];
}

function buildNav() {
  navlistEl.innerHTML = '';
  navItems().forEach((n) => {
    const li = K.el('li');
    if (n.gap) { li.className = 'gap'; navlistEl.appendChild(li); return; }
    const a = K.el('a', null, n.label);
    a.href = '#' + n.href;
    a.dataset.route = n.href;
    li.appendChild(a);
    navlistEl.appendChild(li);
  });

  const li = K.el('li');
  const box = K.el('div');
  box.id = 'lang';
  LANGS.forEach((code, i) => {
    if (i) box.appendChild(K.el('span', 'sep', '·'));
    const b = K.el('button', null, code.toUpperCase());
    b.type = 'button';
    b.dataset.lang = code;
    b.setAttribute('aria-current', String(code === LANG));
    b.setAttribute('aria-label', SITE.i18n[code].ui.lang_name);
    b.addEventListener('click', () => setLang(code));
    box.appendChild(b);
  });
  li.appendChild(box);
  navlistEl.appendChild(li);
}

function markNav(path) {
  document.querySelectorAll('#navlist a').forEach((a) => {
    const on = a.dataset.route === path;
    a.classList.toggle('on', on);
    if (on) a.setAttribute('aria-current', 'page');
    else a.removeAttribute('aria-current');
  });
}

const burger = document.getElementById('burger');

function closeNav() {
  navlistEl.classList.remove('is-open');
  burger.setAttribute('aria-expanded', 'false');
}
burger.addEventListener('click', () => {
  const open = !navlistEl.classList.contains('is-open');
  navlistEl.classList.toggle('is-open', open);
  burger.setAttribute('aria-expanded', String(open));
  if (open) navlistEl.querySelector('a').focus({ preventScroll: true });
});
navlistEl.addEventListener('click', (e) => { if (e.target.closest('a')) closeNav(); });
document.getElementById('navname').addEventListener('click', closeNav);
addEventListener('keydown', (e) => { if (e.key === 'Escape') closeNav(); });

/* ── eser bloğu ──────────────────────────────────────────────────────────── */

function availLine(status) {
  return status === 'satilik' ? t('avail_studio')
       : status === 'koleksiyonda' ? t('avail_private')
       : t('avail_gone');
}

function workBlock(w, opts = {}) {
  const d = K.el('figure', 'work');
  const fig = K.figure(w, opts);

  /* LQIP güvenlik ağı: decode() takılırsa tablonun yerinde kalıcı olarak
     bulanık bir dikdörtgen kalıyordu. Yağlı boyada "yüklenmedi" ile
     "eser bu" ayırt edilemez — 1200 ms sonra koşulsuz göster. */
  setTimeout(() => fig.classList.add('is-loaded'), 1200);
  d.appendChild(fig);

  /* Eser ADI çevrilmez: bir isimdir. Çevirisi altına, küçük ve italik düşer. */
  const gloss = (L().works[w.id] || {}).gloss || '';
  const note  = (L().works[w.id] || {}).note || w.note;

  const cap = K.el('figcaption', 'cap');
  cap.innerHTML =
    '<div class="t">' + w.title + '</div>' +
    (gloss ? '<div class="gloss">' + gloss + '</div>' : '') +
    '<div>' + w.year + '</div>' +
    '<div>' + t('medium') + '</div>' +
    '<div>' + w.size + ' | ' + w.sizeIn + '</div>';

  const av = K.el('div', 'avail');
  av.textContent = availLine(w.status);
  cap.appendChild(av);

  d.appendChild(cap);
  return d;
}

function setTitle(sec) {
  document.title = sec ? sec + ' — ' + SITE.artist.name
                       : SITE.artist.name + ' — ' + t('site_sub');
}

function listView(works, lede, title) {
  main.innerHTML = '';
  if (lede) main.appendChild(lede);
  works.forEach((w, i) => main.appendChild(workBlock(w, { eager: i < 2 })));
  setTitle(title);
  scrollTo(0, 0);
}

function pageShell(h1) {
  const p = K.el('div', 'page');
  p.appendChild(K.el('h1', null, h1));
  return p;
}

function rowList(items) {
  const dl = K.el('dl', 'rows');
  items.forEach(([a, b, c]) => {
    const r = K.el('div', 'row');
    r.appendChild(K.el('dt', null, a));
    r.appendChild(K.el('dd', null, c ? '<b>' + b + '</b><span>' + c + '</span>' : b));
    dl.appendChild(r);
  });
  return dl;
}

/* mekân adı: "Kişisel sergi · Ardıç Sanat" -> "Ardıç Sanat". Dilden bağımsız. */
const venueOf = (s) => s.split(' · ').slice(1).join(' · ') || s;

/* ── görünümler ──────────────────────────────────────────────────────────── */

function viewHome() {
  markNav(null);
  main.innerHTML = '';
  const wrap = K.el('div');
  wrap.id = 'home';

  const w = SITE.works.find(x => x.slug === 'dag-sirti') || SITE.works[0];
  const lead = K.el('div', 'lead');
  const h1 = K.el('h1', null, SITE.artist.name + ' — ' + t('site_sub'));
  h1.style.cssText = 'position:absolute;width:1px;height:1px;overflow:hidden;clip-path:inset(50%)';
  lead.appendChild(h1);
  lead.appendChild(workBlock(w, { eager: true }));
  wrap.appendChild(lead);

  const cv = L().cv;
  const side = K.el('div', 'side');
  side.innerHTML =
    '<div class="blk"><div class="lbl">' + t('home_now') + '</div>' +
    '<b>' + cv[0][1] + '</b><br>' + venueOf(cv[0][2]) + '<br>2024</div>' +
    '<div class="blk"><div class="lbl">' + t('home_next') + '</div>' +
    '<b>' + cv[1][1] + '</b><br>' + venueOf(cv[1][2]) + '<br>2025</div>';
  wrap.appendChild(side);

  main.appendChild(wrap);
  setTitle(null);
  scrollTo(0, 0);
}

function viewSon() {
  markNav('/son');
  const lede = K.el('div', 'lede');
  lede.appendChild(K.el('h1', null, t('nav_recent')));
  lede.appendChild(K.el('p', null,
    fill(t('recent_lede'), { n: SITE.works.length, s: SITE.series.length })));
  listView([...SITE.works].sort((a, b) => b.year - a.year), lede, t('nav_recent'));
}

function viewSeri(key) {
  const base = K.seriesOf(key);
  if (!base) return viewSon();
  const s = L().series[key] || { title: base.title, blurb: base.blurb };
  markNav('/seri/' + key);
  const lede = K.el('div', 'lede');
  lede.appendChild(K.el('h1', null, s.title));
  lede.appendChild(K.el('div', 'yr', base.years));
  lede.appendChild(K.el('p', null, s.blurb));
  listView(K.bySeries(key), lede, s.title);
}

function viewAtolye() {
  markNav('/atolye');
  main.innerHTML = '';
  const p = pageShell(t('nav_studio'));
  L().statement.forEach(x => p.appendChild(K.el('p', null, x)));
  p.appendChild(K.el('p', null,
    '<span style="color:var(--soft)">' + SITE.artist.name + ', ' + SITE.artist.studio + '</span>'));
  main.appendChild(p);
  setTitle(t('nav_studio'));
  scrollTo(0, 0);
}

function viewBio() {
  markNav('/biyografi');
  main.innerHTML = '';
  const p = pageShell(t('nav_bio'));
  p.appendChild(K.el('div', 'formula',
    fill(t('bio_born'), { y: SITE.artist.born, p: SITE.artist.birthplace }) + '<br>' +
    fill(t('bio_lives'), { c: SITE.artist.based })));
  L().bio.forEach(x => p.appendChild(K.el('p', null, x)));
  main.appendChild(p);
  setTitle(t('nav_bio'));
  scrollTo(0, 0);
}

function viewSergiler() {
  markNav('/sergiler');
  main.innerHTML = '';
  const p = pageShell(t('nav_exh'));
  /* Tür ayrımı Türkçe kaynaktan yapılır, gösterim seçili dilden. */
  const solo = [], group = [];
  SITE.cv.forEach((row, i) => {
    (row[2].startsWith('Kişisel') ? solo : group).push(L().cv[i]);
  });
  p.appendChild(K.el('h2', null, t('exh_solo')));
  p.appendChild(rowList(solo.map(r => [r[0], r[1], venueOf(r[2])])));
  p.appendChild(K.el('h2', null, t('exh_group')));
  p.appendChild(rowList(group.map(r => [r[0], r[1], venueOf(r[2])])));
  main.appendChild(p);
  setTitle(t('nav_exh'));
  scrollTo(0, 0);
}

function viewKoleksiyon() {
  markNav('/koleksiyon');
  main.innerHTML = '';
  const p = pageShell(t('nav_coll'));
  const ul = K.el('ul', 'plainlist');
  L().collections.forEach(c => ul.appendChild(K.el('li', null, c)));
  p.appendChild(ul);

  const held = SITE.works.filter(w => w.status !== 'satilik');
  p.appendChild(K.el('h2', null, t('coll_record')));
  p.appendChild(K.el('p', null,
    '<span style="font-size:var(--t-cap);color:var(--muted)">' +
    fill(t('coll_sentence'), { n: SITE.works.length, h: held.length }) + '</span>'));
  p.appendChild(rowList(held.map(w =>
    [String(w.year), w.title, w.size + ' · ' + availLine(w.status)])));
  main.appendChild(p);
  setTitle(t('nav_coll'));
  scrollTo(0, 0);
}

function viewYayinlar() {
  markNav('/yayinlar');
  main.innerHTML = '';
  const p = pageShell(t('nav_pub'));
  p.appendChild(rowList(L().publications));
  main.appendChild(p);
  setTitle(t('nav_pub'));
  scrollTo(0, 0);
}

function viewBasin() {
  markNav('/basin');
  main.innerHTML = '';
  const p = pageShell(t('nav_press'));
  p.appendChild(rowList(L().press));
  main.appendChild(p);
  setTitle(t('nav_press'));
  scrollTo(0, 0);
}

function viewIletisim() {
  markNav('/iletisim');
  main.innerHTML = '';
  const p = pageShell(t('nav_contact'));
  p.appendChild(K.el('p', null,
    '<a href="mailto:' + SITE.artist.email + '" style="color:var(--link)">' +
    SITE.artist.email + '</a>'));
  p.appendChild(K.el('p', null,
    '<span style="color:var(--muted)">' + SITE.artist.studio + '</span>'));
  p.appendChild(K.el('p', null, t('contact_body')));
  p.appendChild(K.el('div', 'note', L().notice + ' ' + SITE.works[0].credit));
  main.appendChild(p);
  setTitle(t('nav_contact'));
  scrollTo(0, 0);
}

/* ── yönlendirme ─────────────────────────────────────────────────────────── */

applyLang();

K.Router
  .on(/^\/$/,             viewHome)
  .on(/^\/son$/,          viewSon)
  .on(/^\/seri\/(.+)$/,   viewSeri)
  .on(/^\/atolye$/,       viewAtolye)
  .on(/^\/biyografi$/,    viewBio)
  .on(/^\/sergiler$/,     viewSergiler)
  .on(/^\/koleksiyon$/,   viewKoleksiyon)
  .on(/^\/yayinlar$/,     viewYayinlar)
  .on(/^\/basin$/,        viewBasin)
  .on(/^\/iletisim$/,     viewIletisim)
  .start();
