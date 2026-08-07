import json

actions = json.load(open('data/actions.json'))
prods = json.load(open('data/products.json'))

banners = [
    "Mar Vermelho Atacado", "Super Nordestão", "Assaí Atacadista",
    "Atacadão", "Rede Mais", "Atacarejo Santo Antônio", "Corte Fácil Atacarejo",
]

def nprod(a):
    t = 0
    for pg in a.get('paginas', []):
        key = pg[:-4] if pg.endswith('.jpg') else pg
        t += len(prods.get(key, []))
    return t

for b in banners:
    print("=====", b, "=====")
    rows = [a for a in actions if a.get('banner') == b]
    # sort by fim
    rows.sort(key=lambda a: a.get('fim', ''))
    for a in rows[-8:]:
        print(f"  id={a.get('id')} per={a.get('inicio')}..{a.get('fim')} tit={a.get('titulo')!r} prods={nprod(a)} add={a.get('adicionado_em')} fonte={a.get('fonte')}")
    print(f"  (total {len(rows)} acoes)")
