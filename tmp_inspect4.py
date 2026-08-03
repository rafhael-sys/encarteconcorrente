import json
a = json.load(open('data/actions.json'))
prods = json.load(open('data/products.json'))

def npro(action):
    t = 0
    for pg in action.get('paginas', []):
        key = pg[:-4] if pg.endswith('.jpg') else pg
        t += len(prods.get(key, []))
    return t

# Actions with fim >= 2026-08-01, sorted by inicio
recent = [x for x in a if x.get('fim','') >= '2026-08-01']
recent.sort(key=lambda x: (x.get('inicio',''), x.get('fim','')))
print('=== ações com fim >= 2026-08-01 ===')
for x in recent:
    print(f"{x['banner']!r:26} {x.get('inicio')}->{x.get('fim')} id={x['id']:34} fonte={x.get('fonte','ig'):7} npag={len(x.get('paginas',[])):2} nprod={npro(x)}")
