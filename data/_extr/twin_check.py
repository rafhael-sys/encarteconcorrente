import json, os
acts = json.load(open('data/actions.json'))
allc = json.load(open('data/_extr/_ALL.json'))
fila = json.load(open('data/fila_novos.json'))
meta = {p['shortcode']: p for p in fila}
prods = json.load(open('data/products.json'))

# indexa ações existentes por (perfil, inicio, fim)
from collections import defaultdict
bykey = defaultdict(list)
for a in acts:
    bykey[(a['perfil'], a['inicio'], a['fim'])].append(a)

print('=== TWIN CHECK (feed posts novos vs actions.json por perfil+periodo) ===')
for sc, r in allc.items():
    if r.get('classificacao') != 'encarte':
        continue
    m = meta[sc]
    if (m.get('fonte') or 'feed') != 'feed':
        continue
    per = r.get('periodo_impresso', {})
    ini, fim = per.get('inicio'), per.get('fim')
    twins = bykey.get((m['perfil'], ini, fim), [])
    if twins:
        for t in twins:
            nprod = sum(len(prods.get(pg.replace('.jpg',''), [])) for pg in t['paginas'])
            print('  TWIN? {} (perfil={}, {}..{}) <-> existente {} com {} produtos'.format(sc, m['perfil'], ini, fim, t['id'], nprod))
    else:
        print('  ok {} sem gemea (perfil={}, {}..{})'.format(sc, m['perfil'], ini, fim))
