import glob
import os
import json
import re

fila = json.load(open('data/fila_novos.json'))
byshort = {p['shortcode']: p for p in fila}
posts = {}
for f in glob.glob('data/_extract_win2_20260817/*.json'):
    if os.path.basename(f).startswith('sim_'):
        continue
    d = json.load(open(f))
    if isinstance(d, dict):
        d = [d]
    for p in d:
        posts[p['shortcode']] = p

orphans = []
for sc, p in posts.items():
    if p.get('decision') != 'keep':
        continue
    src = byshort[sc]
    filakeys = set(x[:-4] for x in src['paginas'])
    for pg in p.get('paginas', []):
        if pg['key'] not in filakeys:
            orphans.append((sc, pg['key'], len(pg.get('produtos', []))))
print('ORPHAN keys (produtos perdidos):', orphans if orphans else 'nenhum')

bad_price = []
pat = re.compile(r'^[0-9]{1,4},[0-9]{2}$')
for sc, p in posts.items():
    if p.get('decision') != 'keep':
        continue
    for pg in p.get('paginas', []):
        for pr in pg.get('produtos', []):
            if not pat.match(str(pr.get('p', ''))):
                bad_price.append((sc, str(pr.get('n', ''))[:35], pr.get('p')))
print('precos fora do padrao X,YY:', len(bad_price))
for b in bad_price[:25]:
    print('   ', b)
