import json
acts = json.load(open('data/actions.json'))
prods = json.load(open('data/products.json'))

def pcount(a):
    tot = 0
    for pg in a.get('paginas', []):
        key = pg[:-4] if pg.endswith('.jpg') else pg
        tot += len(prods.get(key, []))
    return tot

# All Favorito actions in the last ~40, with caption snippet + product count
print('=== Existing Favorito actions (banner match) ===')
for a in acts:
    if a.get('banner') == 'Favorito Super / Atacado Favorito':
        cap = (a.get('caption') or '').replace('\n',' ')[:90]
        print(a.get('shortcode'), '|', a.get('inicio'), a.get('fim'), '| npag', len(a.get('paginas',[])), '| nprod', pcount(a), '|', cap)
