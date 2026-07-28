import json

acts = json.load(open('data/actions.json'))
prods = json.load(open('data/products.json'))


def prods_da_acao(a):
    out = []
    for pg in a.get('paginas', []):
        key = pg[:-4] if pg.endswith('.jpg') else pg
        for p in prods.get(key, []):
            if isinstance(p, dict) and p.get('n'):
                out.append((p.get('p', '?'), p['n']))
    return out


print('=== Super Nordestao: acoes recentes (fim >= 2026-07-24) ===')
for a in acts:
    if a.get('banner') == 'Super Nordestão' and a.get('fim', '') >= '2026-07-24':
        pn = prods_da_acao(a)
        print(f"\n[{a['id']}] {a.get('inicio')}->{a.get('fim')} fonte={a.get('fonte','-')} n={len(pn)}")
        for pr, n in pn:
            print(f'     {pr:>10}  {n}')

print('\n=== Busca global por "Spaten" em Super Nordestao ===')
for a in acts:
    if a.get('banner') != 'Super Nordestão':
        continue
    for pr, n in prods_da_acao(a):
        if 'spaten' in n.lower():
            print(f"  {a['id']} {a.get('inicio')}->{a.get('fim')}: {pr}  {n}")
