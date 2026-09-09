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
   * @param {object} opt {eager, sizes, cls, src, ratio}
   *   src/ratio verilirse eserin duz reproduksiyonu yerine baska bir
   *   kare gosteriliyor (orn. sergi karesi). Oran da onunla gelmeli,
   *   yoksa kare eserin oranina zorlanip kirpiliyor.
   */
  function figure(w, opt = {}) {
    const fig = document.createElement('figure');
    fig.className = 'k-fig ' + (opt.cls || '');
    fig.style.setProperty('--ratio', opt.ratio || w.ratio);
    fig.style.setProperty('--tone', w.tone);
    fig.dataset.src = opt.src || w.src;
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
