import json
actions = json.load(open('data/actions.json'))
prods = json.load(open('data/products.json'))

def pcount(a):
    return sum(len(prods.get(pg[:-4] if pg.endswith('.jpg') else pg, [])) for pg in a.get('paginas', []))

ids = ['DbWwEQlllCR', 'DbWzd1Vjpb5', 'Dbf1Wp7nNbC', 'DbiXLmOHAHH',
       'Dbb00bzH3Vq', 'DbeZ3I0H8OU', 'Dbg3xa7n-_E', 'DbjO1AhH3Px', 'DbeWKyWoOFv']
byid = {a['id']: a for a in actions}
for i in ids:
    a = byid.get(i)
    if not a:
        print(i, 'NOT FOUND'); continue
    print('--- %s | %s | %s->%s | prods=%d | pgs=%d' % (
        i, a.get('banner'), a.get('inicio'), a.get('fim'), pcount(a), len(a.get('paginas', []))))
    print('    titulo:', a.get('titulo', ''))
    print('    caption:', (a.get('caption', '') or '')[:220].replace('\n', ' '))
