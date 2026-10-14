/* Panelin kapıcısının yerel denemesi.  node panel/kapici-deneme.mjs
   Cloudflare hesabı gerekmiyor: Pages Function düz bir onRequest(bağlam)
   işlevi, Node 18+ Request/Response/crypto.subtle sağlıyor. GitHub'a giden
   istek yakalanıyor — gerçek bir anahtar kullanılmıyor. Derlemede de
   koşuyor (denetim.py): bir kusur yayına çıkamıyor. */
import { onRequest } from '../functions/api/[[yol]].js';

const ORTAM = {
  GITHUB_ANAHTAR: 'gizli-anahtar-DENEME',
  KULLANICI: 'saglam',
  SIFRE: 'deniz-orman-mavi-bulut-kalem-123',
  IMZA_GIZLI: 'cok-uzun-rastgele-dize-DENEME-0123456789',
};

let gecti = 0, kaldi = 0;
function ol(ad, kosul, ek) {
  if (kosul) { gecti++; console.log('  OK   ' + ad); }
  else { kaldi++; console.log('  HATA ' + ad + (ek === undefined ? '' : '  -> ' + ek)); }
}

let ip = 1;
function cagir(yol, secim = {}, ortam = ORTAM) {
  const h = Object.assign({ 'CF-Connecting-IP': '10.0.0.' + (secim.ip || ip) }, secim.headers || {});
  if (secim.method && secim.method !== 'GET' && !('X-Panel' in h) && !secim.panelsiz) h['X-Panel'] = '1';
  const istek = new Request('https://saglam.fr/api/' + yol, { method: secim.method || 'GET', headers: h, body: secim.body });
  const parca = yol.split('?')[0].split('/').filter(Boolean);
  return onRequest({ request: istek, env: ortam, params: { yol: parca } });
}

/* GitHub'a giden isteği yakala; ağa çıkma. */
let sonIstek = null, ghDurum = 200;
globalThis.fetch = async (adres, secim) => {
  sonIstek = { adres: String(adres), secim: secim };
  return new Response(JSON.stringify({ sahte: true }), { status: ghDurum });
};

const giris = (sifre, kullanici = 'saglam', ek = {}) => cagir('giris', Object.assign({
  method: 'POST', headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ kullanici: kullanici, sifre: sifre }) }, ek));

/* 1) durum */
{
  const g = await (await cagir('durum')).json();
  ol('durum: kapıcı var ve kurulu', g.sunucu === true && g.kurulu === true);
  const y = await cagir('durum', {}, { KULLANICI: 'saglam' });
  const g2 = await y.json();
  ol('eksik gizli değer bildiriliyor', g2.kurulu === false && g2.eksik.includes('GITHUB_ANAHTAR'), JSON.stringify(g2));
  const kucuk = Object.fromEntries(Object.entries(ORTAM).map(([k, v]) => [k === 'GITHUB_ANAHTAR' ? 'github_anahtar' : k, v]));
  ol('küçük harfle kaydedilmiş gizli değer de tanınıyor', (await (await cagir('durum', {}, kucuk)).json()).kurulu === true);
  ol('kurulmamışken giriş 503', (await cagir('giris', { method: 'POST', body: '{}' }, { KULLANICI: 'saglam' })).status === 503);
}

/* 2) giriş */
{
  const y = await giris('yanlis');
  ol('yanlış şifre 401', y.status === 401);
  ol('hangisinin yanlış olduğu söylenmiyor', /Kullanıcı adı ya da şifre hatalı/.test((await y.json()).hata || ''));
  ol('yanlış girişte çerez yok', !y.headers.get('set-cookie'));
  const p = await cagir('giris', { method: 'POST', panelsiz: true, body: JSON.stringify({ kullanici: 'saglam', sifre: ORTAM.SIFRE }) });
  ol('panel başlığı olmadan yazan istek 403', p.status === 403);
  const d = await giris(ORTAM.SIFRE, 'Saglam');
  ol('doğru giriş 200 (kullanıcı adı büyük/küçük harf duyarsız)', d.status === 200);
  const c = d.headers.get('set-cookie') || '';
  ol('çerez HttpOnly + Secure + SameSite=Strict + Path=/api',
     /HttpOnly/.test(c) && /Secure/.test(c) && /SameSite=Strict/.test(c) && /Path=\/api/.test(c), c);
  ol('çerez 30 gün', /Max-Age=2592000/.test(c));
  globalThis.CEREZ = c.split(';')[0];
}

/* 3) oturum */
{
  const ok = await cagir('oturum', { headers: { Cookie: globalThis.CEREZ } });
  ol('çerezle oturum 200', ok.status === 200 && (await ok.json()).kullanici === 'saglam');
  ol('çerezsiz oturum 401', (await cagir('oturum')).status === 401);
  const bozuk = globalThis.CEREZ.slice(0, -3) + 'abc';
  ol('kurcalanmış çerez 401', (await cagir('oturum', { headers: { Cookie: bozuk } })).status === 401);
  const baska = await cagir('oturum', { headers: { Cookie: globalThis.CEREZ } },
                              Object.assign({}, ORTAM, { IMZA_GIZLI: 'baska-gizli' }));
  ol('başka imzayla üretilmiş çerez 401', baska.status === 401);
  const cik = await cagir('cikis', { method: 'POST' });
  ol('çıkış çerezi siler', /Max-Age=0/.test(cik.headers.get('set-cookie') || ''));
}

/* 4) GitHub vekili */
{
  const C = { Cookie: globalThis.CEREZ };
  ol('oturumsuz vekil 401', (await cagir('gh/git/ref/heads/main')).status === 401);
  sonIstek = null;
  const y = await cagir('gh/git/ref/heads/main', { headers: C });
  ol('izinli istek GitHub’a gidiyor', y.status === 200 && sonIstek &&
     sonIstek.adres === 'https://api.github.com/repos/srdrakncix/ressam-portfolyo-prototip/git/ref/heads/main');
  ol('anahtar GitHub’a gidiyor', sonIstek.secim.headers.Authorization === 'Bearer ' + ORTAM.GITHUB_ANAHTAR);
  ol('anahtar tarayıcıya dönmüyor', ![...y.headers.values()].some((v) => v.includes(ORTAM.GITHUB_ANAHTAR)) &&
     !(await y.text()).includes(ORTAM.GITHUB_ANAHTAR));
  const q = await cagir('gh/commits?path=icerik&per_page=25&sha=main', { headers: C });
  ol('sorgu dizesi korunuyor', q.status === 200 && sonIstek.adres.endsWith('/commits?path=icerik&per_page=25&sha=main'));
  ol('yayın durumu okunabiliyor', (await cagir('gh/actions/runs?head_sha=abc&per_page=10', { headers: C })).status === 200 &&
     sonIstek.adres.endsWith('/actions/runs?head_sha=abc&per_page=10'));
  ol('yayın yeniden başlatılamıyor', (await cagir('gh/actions/runs/1/rerun', { method: 'POST', headers: C, body: '{}' })).status === 403);
  const sha = 'a'.repeat(40);
  for (const u of ['git/commits/' + sha, 'git/trees/' + sha + '?recursive=1', 'git/blobs/' + sha])
    ol('izinli okuma: ' + u.split('?')[0].slice(0, 12), (await cagir('gh/' + u, { headers: C })).status === 200);
  for (const [u, m] of [['contents/functions/api/x.js', 'GET'], ['contents/icerik/site.json', 'PUT'],
                         ['git/trees/../../../user', 'GET'], ['actions/workflows', 'GET'],
                         ['git/refs/heads/baska', 'PATCH'], ['hooks', 'POST'], ['git/ref/heads/main', 'DELETE']])
    ol('izinsiz: ' + m + ' ' + u, (await cagir('gh/' + u, { method: m, headers: C, body: m === 'GET' ? undefined : '{}' })).status === 403);
  const agac = (yollar) => cagir('gh/git/trees', { method: 'POST', headers: C,
    body: JSON.stringify({ base_tree: sha, tree: yollar.map((p) => ({ path: p, mode: '100644', type: 'blob', sha: sha })) }) });
  ol('içerik ağacı yazılabiliyor', (await agac(['icerik/site.json', 'icerik/eserler/eser-1.json'])).status === 200);
  ol('kod dosyası yazılamıyor', (await agac(['icerik/site.json', 'functions/api/[[yol]].js'])).status === 403);
  ol('iş akışı yazılamıyor', (await agac(['.github/workflows/yayinla.yml'])).status === 403);
  ol('icerik/.. kaçışı yazılamıyor', (await agac(['icerik/../build.py'])).status === 403);
  const zorla = await cagir('gh/git/refs/heads/main', { method: 'PATCH', headers: C, body: JSON.stringify({ sha: sha, force: true }) });
  ol('zorla dal güncellemesi 403', zorla.status === 403);
  ghDurum = 401;
  const s = await cagir('gh/git/ref/heads/main', { headers: C });
  ol('anahtarın süresi dolmuşsa 424 (oturum bitti sanılmasın)', s.status === 424 && /Serdar/.test((await s.json()).hata));
  ghDurum = 200;
}

/* 5) hatalı deneme sınırı */
{
  ip = 99;
  for (let i = 0; i < 8; i++) await giris('yanlis');
  const y = await giris(ORTAM.SIFRE);
  ol('8 hatadan sonra doğru şifre bile 429', y.status === 429);
  ip = 98;
  ol('başka IP etkilenmiyor', (await giris(ORTAM.SIFRE)).status === 200);
}

/* 6) vekil kipi: anahtar başka projede, istek olduğu gibi oraya */
{
  const VEKIL = { KAPICI_ADRESI: 'https://kapici.example/' };
  let giden = null;
  globalThis.fetch = async (adres, secim) => {
    giden = { adres: String(adres), secim: secim };
    return new Response('{"kullanici":"saglam"}', { status: 200,
      headers: { 'Content-Type': 'application/json', 'Set-Cookie': 'saglam_oturum=abc; Path=/api; HttpOnly' } });
  };
  const y = await cagir('giris?x=1', { method: 'POST', headers: { Cookie: 'a=b', 'Content-Type': 'application/json' },
                                        body: '{"kullanici":"saglam"}' }, VEKIL);
  ol('vekil: adres + sorgu korunuyor', giden && giden.adres === 'https://kapici.example/api/giris?x=1', giden && giden.adres);
  ol('vekil: çerez, panel başlığı ve gövde gidiyor', giden.secim.headers.get('Cookie') === 'a=b' &&
     giden.secim.headers.get('X-Panel') === '1' && new TextDecoder().decode(giden.secim.body) === '{"kullanici":"saglam"}');
  ol('vekil: oturum çerezi tarayıcıya dönüyor', (y.headers.get('set-cookie') || '').startsWith('saglam_oturum=abc'));
  ol('vekil: GitHub anahtarı istemiyor', y.status === 200);
  const dongu = await cagir('durum', { headers: { 'X-Vekil': '1' } }, VEKIL);
  ol('vekil: kendine dönen istek durduruluyor', dongu.status === 508);
}

console.log('\n' + gecti + ' geçti, ' + kaldi + ' kaldı');
process.exit(kaldi ? 1 : 0);
