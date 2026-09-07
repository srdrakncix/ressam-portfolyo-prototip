/* Şifreli girişin kripto denemesi.  node panel/kilit-deneme.mjs
   Panelin KENDİ kaynağından kesip çalıştırıyor — kopya bir uygulamayı değil,
   sitede duran kodu deniyor. Node 18+ aynı WebCrypto'yu sağlıyor. */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const kok = path.dirname(fileURLToPath(import.meta.url));
const kaynak = fs.readFileSync(path.join(kok, 'index.html'), 'utf8');

const bas = kaynak.indexOf('const KILIT_DONGU');
const son = kaynak.indexOf('/* ── giriş / çıkış ');
if (bas < 0 || son < 0 || son < bas) {
  console.error('HATA: kripto bölümü panel/index.html içinde bulunamadı.');
  process.exit(1);
}
const kod = kaynak.slice(bas, son);

const modul = await import(
  'data:text/javascript;base64,' +
  Buffer.from(kod + '\nexport { kilitUret, kilitCoz, b64, b64coz, KILIT_DONGU };', 'utf8')
    .toString('base64'));

let gecti = 0, kaldi = 0;
const ol = (ad, kosul, ek) => {
  if (kosul) { gecti++; console.log('  OK   ' + ad); }
  else { kaldi++; console.log('  HATA ' + ad + (ek === undefined ? '' : '  -> ' + ek)); }
};

const ANAHTAR = 'github_pat_SAHTE_11AAAAAA0abcdefghijklmnopqrstuvwxyz0123456789';
const SIFRE = 'demo1234';

ol('döngü sayısı en az 300.000', modul.KILIT_DONGU >= 300000, modul.KILIT_DONGU);

let t0 = Date.now();
const kilit = await modul.kilitUret('cemalsaglam', SIFRE, ANAHTAR);
const sureUret = Date.now() - t0;

const metin = JSON.stringify(kilit);
ol('alanlar tam',
   ['kullanici', 'dongu', 'tuz', 'iv', 'kapali'].every((a) => kilit[a] !== undefined),
   Object.keys(kilit).join(','));
ol('ANAHTAR düz metinde YOK', !metin.includes('github_pat'));
ol('Şifre düz metinde YOK', !metin.includes(SIFRE));

t0 = Date.now();
const cozulen = await modul.kilitCoz(SIFRE, kilit);
const sureCoz = Date.now() - t0;
ol('doğru şifre anahtarı aynen çözüyor', cozulen === ANAHTAR);

for (const yanlis of ['demo1233', 'Demo1234', 'demo1234 ', '', 'demo12345']) {
  let hata = '';
  try { await modul.kilitCoz(yanlis, kilit); } catch (e) { hata = e.message; }
  ol('yanlış şifre reddediliyor: ' + JSON.stringify(yanlis), hata.length > 0);
}

/* Tuz her kurulumda farklı olmalı: aynı şifre iki kez aynı şifreli metni
   üretirse aynı şifrenin kullanıldığı dışarıdan anlaşılır. */
const kilit2 = await modul.kilitUret('cemalsaglam', SIFRE, ANAHTAR);
ol('tuz her kurulumda farklı', kilit2.tuz !== kilit.tuz);
ol('şifreli metin her kurulumda farklı', kilit2.kapali !== kilit.kapali);
ol('ikinci kilit de çözülüyor', (await modul.kilitCoz(SIFRE, kilit2)) === ANAHTAR);

/* Kurcalanmış şifreli metin: AES-GCM doğrulaması düşmeli. */
{
  const bozuk = { ...kilit };
  const b = modul.b64coz(kilit.kapali);
  b[0] = b[0] ^ 1;
  bozuk.kapali = modul.b64(b);
  let hata = '';
  try { await modul.kilitCoz(SIFRE, bozuk); } catch (e) { hata = e.message; }
  ol('kurcalanmış kilit reddediliyor', hata.length > 0);
}

console.log('\n  şifreleme ' + sureUret + ' ms, çözme ' + sureCoz +
            ' ms  (girişte kullanıcının beklediği süre)');
console.log('\n' + gecti + ' geçti, ' + kaldi + ' kaldı');
process.exit(kaldi ? 1 : 0);
