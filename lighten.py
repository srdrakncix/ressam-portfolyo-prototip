# -*- coding: utf-8 -*-
"""24 Inness eserinin tamamini isle, EN ACIK 18'ini sec."""
import json, io, os, base64, urllib.request, concurrent.futures as cf
from PIL import Image, ImageFilter

UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
      'Accept': 'image/avif,image/webp,image/apng,image/*,*/*;q=0.8',
      'Referer': 'https://www.artic.edu/', 'Accept-Language': 'en-US,en;q=0.9'}
IIIF = 'https://www.artic.edu/iiif/2/{}/full/1686,/0/default.jpg'
CACHE = 'cache'; os.makedirs(CACHE, exist_ok=True)
FULL_W, FULL_Q, LQIP_W, LQIP_Q = 1500, 72, 20, 40

pool = {a['id']: a for a in json.load(io.open('aic_pool.json', encoding='utf-8'))['George Inness']}

def fetch(aid):
    p = os.path.join(CACHE, f'{aid}.jpg')
    if os.path.exists(p) and os.path.getsize(p) > 50000: return p
    req = urllib.request.Request(IIIF.format(pool[aid]['image_id']), headers=UA)
    with urllib.request.urlopen(req, timeout=180) as r, open(p, 'wb') as f: f.write(r.read())
    return p

def enc(im, w, q, blur=0):
    im = im.copy(); im.thumbnail((w, w*10), Image.LANCZOS)
    if blur: im = im.filter(ImageFilter.GaussianBlur(blur))
    b = io.BytesIO(); im.save(b, 'WEBP', quality=q, method=6)
    return base64.b64encode(b.getvalue()).decode(), len(b.getvalue())

def avg(im):
    s = im.copy(); s.thumbnail((1,1)); return s.convert('RGB').getpixel((0,0))

def work(aid):
    try:
        im = Image.open(fetch(aid)).convert('RGB')
    except Exception as e:
        return None
    r,g,b = avg(im)
    lum = 0.2126*r + 0.7152*g + 0.0722*b
    full, sz = enc(im, FULL_W, FULL_Q)
    lq, _ = enc(im, LQIP_W, LQIP_Q, blur=1)
    a = pool[aid]
    return {'id':aid,'src_title':a['title'],'src_artist':a['artist_title'],'src_date':a['date_display'],
            'src_medium':a['medium_display'],'src_dim':a['dimensions'],'w':im.width,'h':im.height,
            'ratio':round(im.width/im.height,4),'tone':f'#{r:02x}{g:02x}{b:02x}','lum':round(lum,1),
            'full':full,'lqip':lq,'_kb':round(sz/1024)}

ids = list(pool.keys())
with cf.ThreadPoolExecutor(max_workers=4) as ex:
    res = [r for r in ex.map(work, ids) if r]

res.sort(key=lambda r: -r['lum'])
keep = res[:18]
keep.sort(key=lambda r: -r['lum'])
for r in keep:
    print(f"{r['id']:7} {r['src_title'][:36]:38} parlaklik {r['lum']:5.1f}  {r['tone']}  {r['_kb']:4}KB")
print(f"\nELENEN (en koyu {len(res)-18}):")
for r in res[18:]:
    print(f"  {r['src_title'][:40]:42} parlaklik {r['lum']:5.1f}  {r['tone']}")
print(f"\ntoplam {sum(r['_kb'] for r in keep)} KB webp")
for r in keep: r.pop('lum', None); r.pop('_kb', None)
json.dump(keep, io.open('images.json','w',encoding='utf-8'))
