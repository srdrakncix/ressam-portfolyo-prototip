/* ═══════════════════════════════════════════════════════════════════════════
   YÖNETİM PANELİ GİRİŞ SUNUCUSU — Cloudflare Worker

   Neden var: panel şimdiye kadar GitHub erişim anahtarını KULLANICIDAN
   istiyordu. Teknik olmayan biri için "github_pat_..." yapıştırmak anlaşılır
   bir şey değil; üstelik anahtar o kişinin tarayıcısında duruyordu.

   Bu sunucu anahtarı kendi üstünde tutuyor. Panel yalnızca kullanıcı adı ve
   şifre gönderiyor, karşılığında süreli bir oturum jetonu alıyor. Sanatçı
   GitHub diye bir şeyin varlığından haberdar olmuyor.

        panel  ──(kullanıcı+şifre)──▶  Worker  ──(gizli anahtar)──▶  GitHub
               ◀──(oturum jetonu)───          ◀──────────────────

   Gizli değerler koda GİRMEZ, `wrangler secret` ile konur:
       GITHUB_ANAHTAR   depoya yazma yetkisi olan fine-grained PAT
       KULLANICI        örn. cemalsaglam
       SIFRE            giriş şifresi
       IMZA_GIZLI       oturum jetonunu imzalayan rastgele dize

   Kurulum adımları: sunucu/OKUBENI.md
   ═══════════════════════════════════════════════════════════════════════════ */

const DEPO = 'srdrakncix/ressam-portfolyo-prototip';

/* Paneli barındıran adres. Yıldız KULLANILMIYOR: oturum jetonu taşıyan
   istekleri herhangi bir sitenin yapabilmesi gerekmiyor. */
const KOKEN = 'https://srdrakncix.github.io';

const OMUR = 8 * 60 * 60;          /* oturum ömrü, saniye */
const DENEME_SINIRI = 8;           /* aynı IP'den art arda hatalı giriş */
const DENEME_PENCERE = 10 * 60;    /* saniye */

/* ── küçük yardımcılar ──────────────────────────────────────────────────── */

function b64url(baytlar) {
  let s = '';
  for (const b of baytlar) s += String.fromCharCode(b);
  return btoa(s).split('+').join('-').split('/').join('_').split('=').join('');
}

/* Şifre karşılaştırması sabit sürede: uzunluk ve ilk farklı harf bilgisi
   sızmasın. */
function esit(a, b) {
  const x = String(a), y = String(b);
  if (x.length !== y.length) return false;
  let fark = 0;
  for (let i = 0; i < x.length; i++) fark |= x.charCodeAt(i) ^ y.charCodeAt(i);
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

async function jetonGecerli(jeton, gizli) {
  if (!jeton || jeton.indexOf('.') < 0) return false;
  const [govde, imza] = jeton.split('.');
  if (!esit(imza, await imzala(govde, gizli))) return false;
  try {
    const g = JSON.parse(new TextDecoder().decode(
      Uint8Array.from(atob(govde.split('-').join('+').split('_').join('/')),
                      (c) => c.charCodeAt(0))));
    return g.b > Math.floor(Date.now() / 1000);
  } catch (e) { return false; }
}

/* ── GitHub yol izni ────────────────────────────────────────────────────────
   Çalınmış bir oturum jetonu bile deponun tamamında istediğini yapamasın:
   yalnızca panelin gerçekten kullandığı uçlar açık. Düzenli ifade yerine
   düz karşılaştırma — okunabilir ve denetlenebilir olsun. */
function izinli(yol, yontem) {
  if (yol.indexOf('..') >= 0) return false;
  if (yol === '') return yontem === 'GET';               /* depoya erişim denetimi */
  if (yol.indexOf('contents/icerik/eserler') === 0 ||
      yol.indexOf('contents/icerik/gorseller') === 0) {
    return yontem === 'GET' || yontem === 'PUT' || yontem === 'DELETE';
  }
  if (yol === 'git/ref/heads/main') return yontem === 'GET';
  if (yol === 'git/refs/heads/main') return yontem === 'PATCH';
  if (yol.indexOf('git/commits') === 0) return yontem === 'GET' || yontem === 'POST';
  if (yol === 'git/blobs' || yol === 'git/trees') return yontem === 'POST';
  return false;
}

function basliklar(ek) {
  return Object.assign({
    'Access-Control-Allow-Origin': KOKEN,
    'Access-Control-Allow-Headers': 'Authorization, Content-Type',
    'Access-Control-Allow-Methods': 'GET, POST, PUT, PATCH, DELETE, OPTIONS',
    'Access-Control-Max-Age': '86400',
    'Cache-Control': 'no-store',
  }, ek || {});
}

function cevap(nesne, durum) {
  return new Response(JSON.stringify(nesne), {
    status: durum || 200,
    headers: basliklar({ 'Content-Type': 'application/json; charset=utf-8' }),
  });
}

/* Hatalı giriş sayacı. Worker izolatları geçici olduğu için bu BEST-EFFORT
   bir yavaşlatmadır, tam bir kilit değil — asıl koruma şifrenin gücü. */
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

export default {
  async fetch(istek, ortam) {
    const adres = new URL(istek.url);
    const yol = adres.pathname;

    if (istek.method === 'OPTIONS') {
      return new Response(null, { status: 204, headers: basliklar() });
    }

    const eksik = ['GITHUB_ANAHTAR', 'KULLANICI', 'SIFRE', 'IMZA_GIZLI']
      .filter((a) => !ortam[a]);
    if (eksik.length) {
      return cevap({ hata: 'Sunucu yapılandırılmamış: ' + eksik.join(', ') }, 500);
    }

    /* 1) giriş */
    if (yol === '/giris' && istek.method === 'POST') {
      const ip = istek.headers.get('CF-Connecting-IP') || 'bilinmiyor';
      if (denemeAsildi(ip)) {
        return cevap({ hata: 'Çok fazla hatalı deneme. Biraz sonra tekrar deneyin.' }, 429);
      }
      let govde = {};
      try { govde = await istek.json(); } catch (e) { /* boş bırak */ }
      const kullaniciTamam = esit(String(govde.kullanici || '').trim(), ortam.KULLANICI);
      const sifreTamam = esit(String(govde.sifre || ''), ortam.SIFRE);
      if (!kullaniciTamam || !sifreTamam) {
        denemeYaz(ip);
        /* Hangisinin yanlış olduğu söylenmiyor. */
        await new Promise((r) => setTimeout(r, 600));
        return cevap({ hata: 'Kullanıcı adı ya da şifre hatalı.' }, 401);
      }
      denemeler.delete(ip);
      return cevap({
        jeton: await jetonUret(ortam.KULLANICI, ortam.IMZA_GIZLI),
        sona: Math.floor(Date.now() / 1000) + OMUR,
        kullanici: ortam.KULLANICI,
      });
    }

    /* 2) GitHub vekili */
    if (yol === '/gh' || yol.indexOf('/gh/') === 0) {
      const bearer = istek.headers.get('Authorization') || '';
      const oturum = bearer.indexOf('Bearer ') === 0 ? bearer.slice(7) : '';
      if (!(await jetonGecerli(oturum, ortam.IMZA_GIZLI))) {
        return cevap({ hata: 'Oturum geçersiz ya da süresi doldu.' }, 401);
      }

      const alt = yol === '/gh' ? '' : yol.slice(4);
      if (!izinli(alt, istek.method)) {
        return cevap({ hata: 'Bu istek panelin yetki alanı dışında: ' + istek.method + ' ' + alt }, 403);
      }

      const hedef = 'https://api.github.com/repos/' + DEPO + (alt ? '/' + alt : '') + adres.search;
      const ileri = await fetch(hedef, {
        method: istek.method,
        headers: {
          Authorization: 'Bearer ' + ortam.GITHUB_ANAHTAR,
          Accept: 'application/vnd.github+json',
          'X-GitHub-Api-Version': '2022-11-28',
          'Content-Type': 'application/json',
          'User-Agent': 'cemal-saglam-panel',
        },
        body: (istek.method === 'GET' || istek.method === 'HEAD') ? undefined : await istek.text(),
      });

      /* GitHub'ın gövdesi aynen geçiyor; başlıkları GEÇMİYOR — anahtarla
         ilgili hiçbir şey tarayıcıya ulaşmasın. */
      return new Response(await ileri.text(), {
        status: ileri.status,
        headers: basliklar({ 'Content-Type': 'application/json; charset=utf-8' }),
      });
    }

    /* 3) sağlık denetimi — kurulumun çalıştığını görmek için */
    if (yol === '/durum') {
      return cevap({ tamam: true, depo: DEPO, koken: KOKEN });
    }

    return cevap({ hata: 'Bilinmeyen adres.' }, 404);
  },
};
