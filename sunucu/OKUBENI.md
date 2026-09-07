# Giriş sunucusu — kurulum

> **Bunu kurmak zorunda değilsin.** Şifreli girişin kolay yolu panelin
> içinde: erişim anahtarıyla gir, sağ üstteki **“Şifreli giriş kur”**
> bağlantısına bas, kullanıcı adı ve şifre yaz. Terminal, hesap, kurulum yok.
>
> Buradaki Worker daha **sağlam** olanı: orada anahtar tarayıcıya hiç inmiyor.
> Panel içi kurulumda anahtar şifrelenmiş olarak sitenin yanında durur, yani
> şifre çevrimdışı denenebilir. Kısa gösterimler için panel içi kurulum yeter;
> siteyi kalıcı olarak sanatçıya devrederken buraya geç.

Panelin şifreyle açılmasını sağlayan küçük bir Cloudflare Worker. GitHub
anahtarı burada, sunucuda duruyor; sanatçının tarayıcısına hiç inmiyor.

    panel  ──(kullanıcı + şifre)──▶  Worker  ──(gizli anahtar)──▶  GitHub
           ◀──(süreli oturum)─────          ◀──────────────────

Ücretsiz katman fazlasıyla yetiyor (günde 100.000 istek; panel bir eser
kaydederken 6–8 istek yapıyor).

---

## Bir kerelik kurulum

### 1. Cloudflare hesabı

<https://dash.cloudflare.com/sign-up> — ücretsiz, kredi kartı istemiyor.

### 2. Wrangler

    npm install -g wrangler
    wrangler login

Tarayıcı açılır, hesabı onaylarsın.

### 3. GitHub anahtarı

<https://github.com/settings/personal-access-tokens/new>

- **Repository access** → yalnızca `ressam-portfolyo-prototip`
- **Permissions → Contents** → `Read and write`
- **Expiration** → uzun tut (bu anahtar sunucuda duruyor, kimse görmüyor)

Bu anahtar **yalnızca sunucuya** girilecek; kimseye gönderilmeyecek, hiçbir
dosyaya yazılmayacak.

### 4. Gizli değerler

`sunucu/` klasöründeyken sırayla:

    wrangler secret put GITHUB_ANAHTAR      # github_pat_... yapıştır
    wrangler secret put KULLANICI           # cemalsaglam
    wrangler secret put SIFRE               # giriş şifresi
    wrangler secret put IMZA_GIZLI          # rastgele uzun bir dize

`IMZA_GIZLI` için rastgele bir dize üret (bir kez, aklında tutmana gerek yok):

    python -c "import secrets; print(secrets.token_urlsafe(48))"

### 5. Yayınla

    wrangler deploy

Çıktıda bir adres verir:

    https://cemal-saglam-panel.<hesabin>.workers.dev

Çalıştığını gör:

    curl https://cemal-saglam-panel.<hesabin>.workers.dev/durum
    # {"tamam":true,"depo":"srdrakncix/ressam-portfolyo-prototip", ...}

### 6. Paneli sunucuya bağla

`content.py` içinde:

    PANEL_SUNUCU = 'https://cemal-saglam-panel.<hesabin>.workers.dev'

Sonra `git push`. Derleme bittiğinde panel artık **kullanıcı adı + şifre**
soruyor.

---

## Şifreyi değiştirmek

    wrangler secret put SIFRE
    wrangler deploy

Panelde hiçbir değişiklik gerekmiyor. Açık oturumlar sürer; hepsini hemen
kapatmak istersen `IMZA_GIZLI`'yi de değiştir — bütün jetonlar geçersiz olur.

---

## Neler düşünüldü

- **Anahtar tarayıcıya inmiyor.** Panelde duran tek şey süreli bir oturum
  jetonu; onunla yapılabilecekler aşağıdaki listeyle sınırlı.
- **Yol izni dar.** Çalınmış bir oturum bile yalnızca `icerik/eserler`,
  `icerik/gorseller` ve tek bir commit atmak için gereken git uçlarına
  erişebiliyor. Ayarlara, iş akışlarına, başka depolara hayır.
- **CORS tek adrese açık** (`KOKEN`), yıldız değil.
- **Şifre sabit sürede karşılaştırılıyor**, hangisinin yanlış olduğu
  söylenmiyor, hatalı girişte 600 ms bekletiliyor ve aynı IP'den art arda
  8 denemeden sonra 10 dakika kapanıyor.
  Bu sayaç Worker izolatlarında yaşıyor, yani **best-effort**: asıl koruma
  şifrenin gücü. `demo1234` bir gösterim için yeter; işi gerçekten
  devrederken 4–5 kelimelik bir parola kullan.
- **Oturum 8 saat.** Süre dolunca panel kendiliğinden giriş ekranına döner.

## Sunucu olmadan da çalışır

`PANEL_SUNUCU` boşsa panel eski hâline dönüyor: GitHub anahtarını doğrudan
soruyor. Sunucu kurulu olsa bile giriş ekranındaki **"Geliştirici girişi"**
bağlantısı o yolu açık tutuyor — Worker'a bir şey olursa site yönetilemez
duruma düşmüyor.
