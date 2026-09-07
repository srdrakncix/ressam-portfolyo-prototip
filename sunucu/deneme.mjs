/* Giriş sunucusunun yerel denemesi.  node sunucu/deneme.mjs
   Cloudflare hesabı gerekmiyor: Worker düz bir fetch(istek, ortam) işlevi,
   Node 24 de Request/Response/crypto.subtle sağlıyor. GitHub'a giden istek
   yakalanıyor — gerçek bir anahtar kullanılmıyor. */
import worker from './index.js';

const ORTAM = {
  GITHUB_ANAHTAR: 'gizli-anahtar-DENEME',
  KULLANICI: 'cemalsaglam',
  SIFRE: 'demo1234',
  IMZA_GIZLI: 'cok-uzun-rastgele-dize-DENEME',
};
const KOKEN = 'https://srdrakncix.github.io';

let gecti = 0, kaldi = 0;
function ol(ad, kosul, ek) {
  if (kosul) { gecti++; console.log('  OK   ' + ad); }
  else { kaldi++; console.log('  HATA ' + ad + (ek ? '  -> ' + ek : '')); }
}

const cagir = (yol, secim) =>
  worker.fetch(new Request('https://sunucu.example' + yol, secim), ORTAM);

/* GitHub'a giden isteği yakala; ağa çıkma. */
let sonIstek = null;
globalThis.fetch = async (adres, secim) => {
  sonIstek = { adres: String(adres), secim: secim };
  return new Response(JSON.stringify({ sahte: true }), { status: 200 });
};

/* 1) sağlık */
{
  const y = await cagir('/durum');
  const g = await y.json();
  ol('durum 200 ve depo bildiriliyor', y.status === 200 && g.tamam === true);
  ol('CORS tek adrese açık',
     y.headers.get('access-control-allow-origin') === KOKEN,
     y.headers.get('access-control-allow-origin'));
}

/* 2) ön uçuş */
{
  const y = await cagir('/gh/contents/icerik/eserler', { method: 'OPTIONS' });
  ol('OPTIONS 204', y.status === 204);
  ol('izinli başlıklar Authorization + Content-Type',
     (y.headers.get('access-control-allow-headers') || '').includes('Authorization'));
}

/* 3) yanlış şifre */
{
  const y = await cagir('/giris', {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ kullanici: 'cemalsaglam', sifre: 'yanlis' }),
  });
  const g = await y.json();
  ol('yanlış şifre 401', y.status === 401);
  ol('hangisinin yanlış olduğu söylenmiyor',
     /Kullanıcı adı ya da şifre hatalı/.test(g.hata || ''), g.hata);
}

/* 4) yanlış kullanıcı */
{
  const y = await cagir('/giris', {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ kullanici: 'baskasi', sifre: 'demo1234' }),
  });
  ol('yanlış kullanıcı 401', y.status === 401);
}

/* 5) doğru giriş */
let jeton = '';
{
  const y = await cagir('/giris', {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ kullanici: 'cemalsaglam', sifre: 'demo1234' }),
  });
  const g = await y.json();
  jeton = g.jeton || '';
  ol('doğru giriş 200 + jeton', y.status === 200 && jeton.includes('.'));
  ol('jeton içinde şifre/anahtar YOK',
     !jeton.includes('demo1234') && !jeton.includes(ORTAM.GITHUB_ANAHTAR));
  ol('süre bildiriliyor', typeof g.sona === 'number' && g.sona > Date.now() / 1000);
}

const yetki = (j) => ({ headers: { Authorization: 'Bearer ' + j } });

/* 6) jetonsuz erişim */
{
  const y = await cagir('/gh/contents/icerik/eserler');
  ol('jetonsuz istek 401', y.status === 401);
}

/* 7) kurcalanmış jeton */
{
  const bozuk = jeton.slice(0, -3) + 'AAA';
  const y = await cagir('/gh/contents/icerik/eserler', yetki(bozuk));
  ol('imzası bozuk jeton 401', y.status === 401);
}

/* 8) geçerli jetonla izinli yol */
{
  sonIstek = null;
  const y = await cagir('/gh/contents/icerik/eserler', yetki(jeton));
  ol('izinli yol geçiyor', y.status === 200);
  ol('GitHub adresi doğru kuruluyor',
     sonIstek && sonIstek.adres ===
     'https://api.github.com/repos/srdrakncix/ressam-portfolyo-prototip/contents/icerik/eserler',
     sonIstek && sonIstek.adres);
  ol('gizli anahtar GitHub isteğinde kullanılıyor',
     sonIstek.secim.headers.Authorization === 'Bearer ' + ORTAM.GITHUB_ANAHTAR);
  const govde = await y.text();
  ol('gizli anahtar tarayıcıya SIZMIYOR', !govde.includes(ORTAM.GITHUB_ANAHTAR));
}

/* 9) boş yol = depo denetimi */
{
  sonIstek = null;
  const y = await cagir('/gh', yetki(jeton));
  ol('boş yol depo köküne gidiyor',
     y.status === 200 && sonIstek.adres ===
     'https://api.github.com/repos/srdrakncix/ressam-portfolyo-prototip',
     sonIstek && sonIstek.adres);
}

/* 10) yetki alanı dışı yollar */
for (const [yol, yontem] of [
  ['/gh/actions/workflows', 'GET'],
  ['/gh/contents/.github/workflows/yayinla.yml', 'PUT'],
  ['/gh/collaborators/birisi', 'PUT'],
  ['/gh/contents/icerik/../../ayarlar', 'GET'],
  ['/gh/git/refs/heads/main', 'DELETE'],
]) {
  sonIstek = null;
  const y = await cagir(yol, { method: yontem, ...yetki(jeton) });
  ol('reddediliyor: ' + yontem + ' ' + yol, y.status === 403 && sonIstek === null, y.status);
}

/* 11) tek commit için gereken uçlar açık */
for (const [yol, yontem] of [
  ['/gh/git/ref/heads/main', 'GET'],
  ['/gh/git/blobs', 'POST'],
  ['/gh/git/trees', 'POST'],
  ['/gh/git/commits', 'POST'],
  ['/gh/git/refs/heads/main', 'PATCH'],
  ['/gh/contents/icerik/gorseller/kiyi.webp', 'PUT'],
  ['/gh/contents/icerik/eserler/kiyi.json', 'DELETE'],
]) {
  const govde = (yontem === 'GET' || yontem === 'DELETE') ? undefined : '{}';
  const y = await cagir(yol, { method: yontem, body: govde, ...yetki(jeton) });
  ol('açık: ' + yontem + ' ' + yol, y.status === 200, y.status);
}

/* 12) eksik yapılandırma */
{
  const y = await worker.fetch(new Request('https://s.example/durum'), { KULLANICI: 'a' });
  ol('eksik gizli değer 500 ve hangisi olduğu söyleniyor',
     y.status === 500 && (await y.json()).hata.includes('GITHUB_ANAHTAR'));
}

console.log('\n' + gecti + ' geçti, ' + kaldi + ' kaldı');
process.exit(kaldi ? 1 : 0);
