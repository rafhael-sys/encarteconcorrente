import json

with open('data/products.json') as f:
    prods = json.load(f)
with open('data/actions.json') as f:
    acts = json.load(f)

ids = set(a['id'] for a in acts)
for sc in ['DbHadmtm6ZV', 'DcMLkbbFFFz', 'Db5_sATn3Re', 'DboNiOUoMml']:
    print(sc, 'em actions?', sc in ids)

for pg in ['DcMvjcfmRcY_p2', 'DcQ0GK4HDhe_p6', 'DcTcpz_HDtc_p2', 'DcTcpz_HDtc_p6', 'DcMvjcfmRcY_p1']:
    v = prods.get(pg)
    print(pg, '->', (len(v) if v is not None else 'AUSENTE'), 'produtos')
    if v:
        for it in v[:3]:
            print('   ', it['n'], it['p'])

fav = [a for a in acts if a['banner'].startswith('Favorito')
       and a.get('inicio') == '2026-08-19' and a.get('fim') == '2026-08-25']
print()
print('acoes Favorito 19-25:')
for a in fav:
    npr = sum(len(prods.get(p[:-4], [])) for p in a.get('paginas', []))
    print(' ', a['id'], '|', a.get('titulo', '')[:50], '| pags', len(a.get('paginas', [])), '| prods', npr)

# MV 21-27 e 25-26 existentes, p/ dedup por conteudo
mv = [a for a in acts if a['banner'] == 'Mar Vermelho Atacado' and a.get('fim', '') >= '2026-08-24']
print()
print('acoes MV vigentes/futuras:')
for a in mv:
    npr = sum(len(prods.get(p[:-4], [])) for p in a.get('paginas', []))
    print(' ', a['id'], '|', a.get('titulo', '')[:50], '|', a.get('inicio'), '->', a.get('fim'), '| pags', len(a.get('paginas', [])), '| prods', npr)
