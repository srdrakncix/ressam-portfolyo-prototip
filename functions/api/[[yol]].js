/* ═══════════════════════════════════════════════════════════════════════════
   PANELİN KAPICISI — Cloudflare Pages Function (saglam.fr/api/*)

   Panel GitHub'a yazmak için bir erişim anahtarına ihtiyaç duyuyor. Bu
   fonksiyon anahtarı KENDİNDE tutuyor: ressam yalnızca kullanıcı adı ve
   şifre gönderiyor, karşılığında bir oturum çerezi alıyor. Anahtar hiçbir
   zaman tarayıcıya inmiyor, hiçbir dosyada durmuyor.

        panel ──(kullanıcı + şifre)──▶ /api/giris ──▶ oturum çerezi
        panel ──(çerez + istek)──────▶ /api/gh/…  ──(gizli anahtar)──▶ GitHub

   Sitenin KENDİ ADRESİNDE çalışıyor (Pages Functions): ayrı bir sunucu,
   ayrı bir alan adı, CORS yok.

   Gizli değerler koda GİRMEZ (Cloudflare → proje → Settings → Variables and
   Secrets, ya da `wrangler pages secret put`):
       GITHUB_ANAHTAR   yalnız bu depoya yetkili fine-grained PAT
       KULLANICI        panele giriş adı (ör. saglam)
       SIFRE            panele giriş şifresi
       IMZA_GIZLI       oturum çerezini imzalayan uzun rastgele dize
   GITHUB_API yalnız denemede (sahte GitHub'a yönlendirmek için).

   ÇALINMIŞ BİR OTURUM BİLE İÇERİKTEN ÖTESİNE DOKUNAMAZ: yalnız panelin
   kullandığı uçlar açık ve yazılan ağaçta her yol icerik/ altında olmalı —
   sitenin kodu, bu fonksiyonun kendisi, iş akışları panelden değiştirilemez.
   ═══════════════════════════════════════════════════════════════════════════ */

const DEPO = 'srdrakncix/ressam-portfolyo-prototip';
const DAL = 'main';
const CEREZ = 'saglam_oturum';
const OMUR = 30 * 24 * 60 * 60;        /* oturum: 30 gün ("bu cihazda hatırla") */
const DENEME_SINIRI = 8;               /* aynı IP'den art arda hatalı giriş */
const DENEME_PENCERE = 10 * 60;        /* saniye */

/* ── küçük yardımcılar ──────────────────────────────────────────────────── */

function b64url(baytlar) {
  let s = '';
  for (const b of baytlar) s += String.fromCharCode(b);
  return btoa(s).split('+').join('-').split('/').join('_').split('=').join('');
}

/* Sabit süreli karşılaştırma: uzunluk ve ilk farklı harf bilgisi sızmasın. */
function esit(a, b) {
  const x = String(a), y = String(b);
  let fark = x.length ^ y.length;
  for (let i = 0; i < Math.max(x.length, y.length); i++)
    fark |= (x.charCodeAt(i) || 0) ^ (y.charCodeAt(i) || 0);
  return fark === 0;
}

async function imzala(veri, gizli) {
  const kod = new TextEncoder();
  const anahtar = await crypto.subtle.importKey(
    'raw', kod.encode(gizli), { name: 'HMAC', hash: 'SHA-256' }, false, ['sign']);
  return b64url(new Uint8Array(await crypto.subtle.sign('HMAC', anahtar, kod.encode(veri))));
}

async function jetonUret(kullanici, gizli) {
  const govde = b64url(new TextEncoder().encode(JSON.stringify({
    k: kullanici, b: Math.floor(Date.now() / 1000) + OMUR,
  })));
  return govde + '.' + (await imzala(govde, gizli));
}

/* Geçerliyse kullanıcı adını, değilse null döner. */
async function jetonCoz(jeton, gizli) {
  if (!jeton || jeton.indexOf('.') < 0) return null;
  const [govde, imza] = jeton.split('.');
  if (!esit(imza, await imzala(govde, gizli))) return null;
  try {
    const g = JSON.parse(new TextDecoder().decode(
      Uint8Array.from(atob(govde.split('-').join('+').split('_').join('/')), (c) => c.charCodeAt(0))));
    return g.b > Math.floor(Date.now() / 1000) ? g.k : null;
  } catch (e) { return null; }
}

function cerezOku(istek) {
  for (const parca of (istek.headers.get('Cookie') || '').split(';')) {
    const i = parca.indexOf('=');
    if (i > 0 && parca.slice(0, i).trim() === CEREZ) return parca.slice(i + 1).trim();
  }
  return '';
}

function cerez(deger, omur) {
  /* HttpOnly: sayfadaki hiçbir betik okuyamaz. Strict: başka bir siteden
     gelen istekte gönderilmez. Path=/api: yalnız kapıcıya gider. */
  return CEREZ + '=' + deger + '; Path=/api; HttpOnly; Secure; SameSite=Strict; Max-Age=' + omur;
}

function cevap(nesne, durum, ek) {
  return new Response(JSON.stringify(nesne), {
    status: durum || 200,
    headers: Object.assign({ 'Content-Type': 'application/json; charset=utf-8',
                             'Cache-Control': 'no-store' }, ek || {}),
  });
}

/* ── GitHub yol izni ────────────────────────────────────────────────────────
   Yalnız panelin gerçekten kullandığı uçlar. Düzenli ifadeler sha'ya kadar
   sabit: "git/trees/../.." gibi bir yol hiçbirine uymaz. */
const SHA = '[0-9a-f]{40}';
function izinli(yol, yontem) {
  if (yol === '') return yontem === 'GET';
  if (yol === 'git/ref/heads/' + DAL) return yontem === 'GET';
  if (yol === 'git/refs/heads/' + DAL) return yontem === 'PATCH';
  if (new RegExp('^git/(commits|trees|blobs)/' + SHA + '$').test(yol)) return yontem === 'GET';
  if (yol === 'git/commits' || yol === 'git/trees' || yol === 'git/blobs') return yontem === 'POST';
  if (yol === 'commits') return yontem === 'GET';
  return false;
}

/* Yazma isteklerinin İÇERİĞİ de denetleniyor: ağaçta her yol icerik/
   altında, dal güncellemesi zorla (force) değil. */
function govdeIzinli(yol, govde) {
  let g;
  try { g = JSON.parse(govde || '{}'); } catch (e) { return 'Gövde okunamadı.'; }
  if (yol === 'git/trees') {
    const l = Array.isArray(g.tree) ? g.tree : [];
    const disari = l.filter((x) => typeof x.path !== 'string' || x.path.indexOf('icerik/') !== 0 ||
                                   x.path.indexOf('..') >= 0 || (x.type && x.type !== 'blob'));
    if (!l.length || disari.length) return 'Panel yalnızca içerik dosyalarını değiştirebilir.';
  }
  if (yol === 'git/refs/heads/' + DAL && g.force) return 'Zorla güncelleme kapalı.';
  return '';
}

/* Hatalı giriş sayacı. İzolatlar geçici olduğu için en iyi gayret bir
   yavaşlatma — asıl koruma şifrenin uzunluğu. */
const denemeler = new Map();
function denemeAsildi(ip) {
  const s = denemeler.get(ip);
  if (!s) return false;
  if (Date.now() - s.ilk > DENEME_PENCERE * 1000) { denemeler.delete(ip); return false; }
  return s.n >= DENEME_SINIRI;
}
function denemeYaz(ip) {
  const s = denemeler.get(ip);
  if (!s || Date.now() - s.ilk > DENEME_PENCERE * 1000) denemeler.set(ip, { n: 1, ilk: Date.now() });
  else s.n += 1;
}

/* ── istek ──────────────────────────────────────────────────────────────── */

export async function onRequest(baglam) {
  const istek = baglam.request;
  const ortam = baglam.env || {};
  const parca = baglam.params && baglam.params.yol;
  const yol = Array.isArray(parca) ? parca.join('/') : (parca || '');
  const eksik = ['GITHUB_ANAHTAR', 'KULLANICI', 'SIFRE', 'IMZA_GIZLI'].filter((a) => !ortam[a]);

  /* 1) panel buradan "kapıcı var mı, kurulu mu" diye bakıyor */
  if (yol === 'durum') return cevap({ sunucu: true, kurulu: !eksik.length, eksik: eksik });
  if (eksik.length) return cevap({ hata: 'Kapıcı kurulmamış: ' + eksik.join(', ') }, 503);

  /* Yazan istekler panelin kendi başlığını taşımalı: başka bir sayfanın
     formu bu başlığı ekleyemez (ekleyebilmek için CORS izni gerekir, yok). */
  if (istek.method !== 'GET' && istek.headers.get('X-Panel') !== '1')
    return cevap({ hata: 'İstek panelden gelmiyor.' }, 403);

  /* 2) giriş / çıkış / oturum */
  if (yol === 'giris' && istek.method === 'POST') {
    const ip = istek.headers.get('CF-Connecting-IP') || 'bilinmiyor';
    if (denemeAsildi(ip)) return cevap({ hata: 'Çok fazla hatalı deneme. On dakika sonra tekrar deneyin.' }, 429);
    let g = {};
    try { g = await istek.json(); } catch (e) { /* boş */ }
    const kTamam = esit(String(g.kullanici || '').trim().toLowerCase(), String(ortam.KULLANICI).toLowerCase());
    const sTamam = esit(String(g.sifre || ''), ortam.SIFRE);
    if (!kTamam || !sTamam) {
      denemeYaz(ip);
      await new Promise((r) => setTimeout(r, 500));
      return cevap({ hata: 'Kullanıcı adı ya da şifre hatalı.' }, 401);
    }
    denemeler.delete(ip);
    return cevap({ kullanici: ortam.KULLANICI }, 200,
                 { 'Set-Cookie': cerez(await jetonUret(ortam.KULLANICI, ortam.IMZA_GIZLI), OMUR) });
  }
  if (yol === 'cikis' && istek.method === 'POST')
    return cevap({ tamam: true }, 200, { 'Set-Cookie': cerez('', 0) });

  const kullanici = await jetonCoz(cerezOku(istek), ortam.IMZA_GIZLI);
  if (yol === 'oturum')
    return kullanici ? cevap({ kullanici: kullanici }) : cevap({ hata: 'Oturum yok.' }, 401);

  /* 3) GitHub vekili */
  if (yol === 'gh' || yol.indexOf('gh/') === 0) {
    if (!kullanici) return cevap({ hata: 'Oturum geçersiz ya da süresi doldu.' }, 401);
    const alt = yol === 'gh' ? '' : yol.slice(3);
    if (!izinli(alt, istek.method))
      return cevap({ hata: 'Bu istek panelin yetki alanı dışında: ' + istek.method + ' ' + alt }, 403);
    const govde = (istek.method === 'GET' || istek.method === 'HEAD') ? undefined : await istek.text();
    const ret = govde === undefined ? '' : govdeIzinli(alt, govde);
    if (ret) return cevap({ hata: ret }, 403);

    const taban = String(ortam.GITHUB_API || 'https://api.github.com').replace(/\/+$/, '');
    const hedef = taban + '/repos/' + DEPO + (alt ? '/' + alt : '') + new URL(istek.url).search;
    let ileri;
    try {
      ileri = await fetch(hedef, {
        method: istek.method,
        headers: {
          Authorization: 'Bearer ' + ortam.GITHUB_ANAHTAR,
          Accept: 'application/vnd.github+json',
          'X-GitHub-Api-Version': '2022-11-28',
          'Content-Type': 'application/json',
          'User-Agent': 'saglam-panel',
        },
        body: govde,
      });
    } catch (e) {
      return cevap({ hata: 'GitHub’a ulaşılamadı.' }, 502);
    }
    /* Anahtarın süresi dolduysa 401 OLARAK GEÇMİYOR: panel 401'i "oturum
       bitti" diye okuyup ressamı boşuna giriş ekranına döndürürdü. */
    if (ileri.status === 401)
      return cevap({ hata: 'Panelin GitHub anahtarı geçersiz ya da süresi dolmuş. Serdar’a haber verin.' }, 424);
    /* Gövde aynen geçiyor; başlıklar GEÇMİYOR — anahtarla ilgili hiçbir
       şey tarayıcıya ulaşmasın. */
    return new Response(await ileri.text(), {
      status: ileri.status,
      headers: { 'Content-Type': 'application/json; charset=utf-8', 'Cache-Control': 'no-store' },
    });
  }

  return cevap({ hata: 'Bilinmeyen adres.' }, 404);
}
