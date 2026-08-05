import json, glob, os
prods = json.load(open('data/products.json'))
existing = set(prods.keys())
problemas = []
tot_prod = 0
tot_pg = 0
collide = []
for f in sorted(glob.glob('data/_extract/w0804_*.json')):
    d = json.load(open(f))
    for pk, items in d.items():
        tot_pg += 1
        if pk in existing:
            collide.append(pk)
        for it in items:
            tot_prod += 1
            faltou = [k for k in ('n', 'p', 'u', 'x', 'y', 'w', 'h') if k not in it]
            if faltou:
                problemas.append((os.path.basename(f), pk, 'falta ' + ','.join(faltou), it.get('n')))
                continue
            if not isinstance(it['p'], str):
                problemas.append((os.path.basename(f), pk, 'p nao-str', it['n']))
            for c in ('x', 'y', 'w', 'h'):
                v = it[c]
                if not isinstance(v, (int, float)) or v < 0 or v > 100:
                    problemas.append((os.path.basename(f), pk, '%s=%s fora 0-100' % (c, v), it['n']))
print('paginas total:', tot_pg, '| produtos total:', tot_prod)
print('colisao com products.json:', len(collide), collide[:5])
print('problemas de estrutura/range:', len(problemas))
for p in problemas[:30]:
    print('  ', p)
