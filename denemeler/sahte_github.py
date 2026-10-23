# -*- coding: utf-8 -*-
"""Bellekte sahte GitHub deposu: panelin kullandigi REST uclari.

Git nesneleri gercek kurallarla: blob sha'si = sha1("blob <boy>\\0" + bayt),
yani panelin ve yayinla.py'nin hesapladigi parmak izleri gercek depodakiyle
ayni. Agaclar burada duz sozluk (yol -> blob sha) olarak tutuluyor; alt agac
(icerik/) istenince ondan turetiliyor.
"""
import base64
import hashlib
import json
import time
from urllib.parse import urlparse, parse_qs

DEPO = 'srdrakncix/ressam-portfolyo-prototip'
CORS = {'access-control-allow-origin': '*', 'access-control-allow-headers': '*',
        'access-control-allow-methods': 'GET, POST, PATCH, DELETE, OPTIONS'}


class Depo:
    def __init__(self, dosyalar, jeton):
        self.jeton = jeton
        self.blob, self.agac, self.commit = {}, {}, {}
        self.istekler = []
        self.patch_sayisi = 0
        self.dallar = {}           # main disindaki dallar (kayit-...)
        kok = {p: self.blob_yaz(b) for p, b in dosyalar.items()}
        self.bas = self.commit_yaz(self.agac_yaz(kok), [], 'İlk hâl')

    # ── nesneler ──
    def blob_yaz(self, b):
        sha = hashlib.sha1(b'blob %d\x00' % len(b) + b).hexdigest()
        self.blob[sha] = b
        return sha

    def agac_yaz(self, duz):
        sha = hashlib.sha1(json.dumps(sorted(duz.items())).encode()).hexdigest()
        self.agac[sha] = dict(duz)
        return sha

    def commit_yaz(self, agac, ebeveyn, mesaj):
        sha = hashlib.sha1(f'{agac}{ebeveyn}{mesaj}{time.time()}{len(self.commit)}'.encode()).hexdigest()
        self.commit[sha] = {'tree': agac, 'parents': ebeveyn, 'message': mesaj,
                            'date': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}
        return sha

    def dosyalar(self, commit=None):
        """commit'teki yol -> bayt"""
        duz = self.agac[self.commit[commit or self.bas]['tree']]
        return {p: self.blob[s] for p, s in duz.items()}

    def izler(self, onek='icerik/'):
        duz = self.agac[self.commit[self.bas]['tree']]
        return {p: s for p, s in sorted(duz.items()) if p.startswith(onek)}

    # ── uç noktalar ──
    def agac_yaniti(self, sha, ozyineli):
        duz = self.agac[sha]
        if ozyineli:
            return {'sha': sha, 'truncated': False,
                    'tree': [{'path': p, 'type': 'blob', 'mode': '100644', 'sha': s} for p, s in sorted(duz.items())]}
        girdiler, dizinler = [], {}
        for p, s in sorted(duz.items()):
            if '/' in p:
                d = p.split('/', 1)[0]
                dizinler.setdefault(d, {})[p.split('/', 1)[1]] = s
            else:
                girdiler.append({'path': p, 'type': 'blob', 'mode': '100644', 'sha': s})
        for d, alt in dizinler.items():
            girdiler.append({'path': d, 'type': 'tree', 'mode': '040000', 'sha': self.agac_yaz(alt)})
        return {'sha': sha, 'truncated': False, 'tree': girdiler}

    def isle(self, yontem, adres, govde, yetki):
        u = urlparse(adres)
        q = parse_qs(u.query)
        yol = u.path.split('/repos/' + DEPO, 1)[1].strip('/') if ('/repos/' + DEPO) in u.path else None
        self.istekler.append((yontem, u.path + ('?' + u.query if u.query else '')))
        if yetki != 'Bearer ' + self.jeton:
            return 401, {'message': 'Bad credentials'}
        if yol is None:
            return 404, {'message': 'Not Found'}
        if yol == '' and yontem == 'GET':
            return 200, {'full_name': DEPO, 'permissions': {'push': True}}
        if yol == 'git/matching-refs/heads/kayit-' and yontem == 'GET':
            return 200, [{'ref': 'refs/heads/' + d, 'object': {'sha': h, 'type': 'commit'}}
                         for d, h in sorted(self.dallar.items()) if d.startswith('kayit-')]
        if yol == 'git/refs' and yontem == 'POST':
            g = json.loads(govde)
            d = g['ref'].replace('refs/heads/', '')
            if d in self.dallar or d == 'main' or g['sha'] not in self.commit:
                return 422, {'message': 'Reference already exists'}
            self.dallar[d] = g['sha']
            return 201, {'ref': g['ref'], 'object': {'sha': g['sha']}}
        if yol.startswith('git/refs/heads/') and yol != 'git/refs/heads/main' and yontem == 'DELETE':
            d = yol[len('git/refs/heads/'):]
            if d not in self.dallar:
                return 422, {'message': 'Reference does not exist'}
            del self.dallar[d]
            return 204, None
        if yol.startswith('git/ref/heads/') and yol != 'git/ref/heads/main' and yontem == 'GET':
            d = yol[len('git/ref/heads/'):]
            if d not in self.dallar:
                return 404, {'message': 'Not Found'}
            return 200, {'ref': 'refs/heads/' + d, 'object': {'sha': self.dallar[d]}}
        if yol == 'git/ref/heads/main' and yontem == 'GET':
            return 200, {'ref': 'refs/heads/main', 'object': {'sha': self.bas, 'type': 'commit'}}
        if yol.startswith('git/commits/') and yontem == 'GET':
            c = self.commit.get(yol.split('/')[-1])
            if not c:
                return 404, {'message': 'Not Found'}
            return 200, {'sha': yol.split('/')[-1], 'tree': {'sha': c['tree']}, 'message': c['message'],
                         'author': {'date': c['date'], 'name': 'test'},
                         'parents': [{'sha': x} for x in c['parents']]}
        if yol.startswith('git/trees/') and yontem == 'GET':
            sha = yol.split('/')[-1]
            if sha not in self.agac:
                return 404, {'message': 'Not Found'}
            return 200, self.agac_yaniti(sha, q.get('recursive') == ['1'])
        if yol.startswith('git/blobs/') and yontem == 'GET':
            b = self.blob.get(yol.split('/')[-1])
            if b is None:
                return 404, {'message': 'Not Found'}
            return 200, {'sha': yol.split('/')[-1], 'size': len(b), 'encoding': 'base64',
                         'content': base64.encodebytes(b).decode()}
        if yol == 'git/blobs' and yontem == 'POST':
            g = json.loads(govde)
            b = base64.b64decode(g['content']) if g.get('encoding') == 'base64' else g['content'].encode('utf-8')
            return 201, {'sha': self.blob_yaz(b)}
        if yol == 'git/trees' and yontem == 'POST':
            g = json.loads(govde)
            duz = dict(self.agac[g['base_tree']])
            for x in g['tree']:
                if x.get('sha') is None:
                    if x['path'] not in duz:
                        return 422, {'message': 'GitRPC::BadObjectState (silinecek yol yok: %s)' % x['path']}
                    del duz[x['path']]
                else:
                    if x['sha'] not in self.blob:
                        return 422, {'message': 'blob yok: ' + x['sha']}
                    duz[x['path']] = x['sha']
            return 201, {'sha': self.agac_yaz(duz)}
        if yol == 'git/commits' and yontem == 'POST':
            g = json.loads(govde)
            return 201, {'sha': self.commit_yaz(g['tree'], g['parents'], g['message'])}
        if yol == 'git/refs/heads/main' and yontem == 'PATCH':
            g = json.loads(govde)
            if self.bas not in self.commit[g['sha']]['parents']:
                return 422, {'message': 'Update is not a fast forward'}
            self.bas = g['sha']
            self.patch_sayisi += 1
            return 200, {'object': {'sha': self.bas}}
        if yol == 'commits' and yontem == 'GET':
            onek = (q.get('path') or [''])[0]
            out, c = [], self.bas
            while c:
                cc = self.commit[c]
                once = cc['parents'][0] if cc['parents'] else None
                bu = {p: s for p, s in self.agac[cc['tree']].items() if p.startswith(onek)}
                oc = {p: s for p, s in self.agac[self.commit[once]['tree']].items() if p.startswith(onek)} if once else None
                if bu != oc:
                    out.append({'sha': c, 'commit': {'message': cc['message'], 'author': {'date': cc['date'], 'name': 'test'}}})
                c = once
            return 200, out[:int((q.get('per_page') or ['30'])[0])]
        if yol.startswith('actions/runs') and yontem == 'GET':
            return 200, {'total_count': 0, 'workflow_runs': []}
        return 404, {'message': 'tanımsız uç: %s %s' % (yontem, yol)}

    def playwright_yolu(self, route, request):
        if request.method == 'OPTIONS':
            return route.fulfill(status=204, headers=CORS)
        kod, veri = self.isle(request.method, request.url, request.post_data,
                              request.headers.get('authorization', ''))
        route.fulfill(status=kod, headers=dict(CORS, **{'content-type': 'application/json'}),
                      body='' if kod == 204 else json.dumps(veri, ensure_ascii=False))
