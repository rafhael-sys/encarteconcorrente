import json
actions=json.load(open('data/actions.json'))
products=json.load(open('data/products.json'))

def prodcount(act):
    total=0
    for pg in act.get('paginas',[]):
        key=pg[:-4] if pg.endswith('.jpg') else pg
        total+=len(products.get(key,[]))
    return total

# banners na fila
banners=['Favorito Super / Atacado Favorito','Rede Super Show','Mar Vermelho Atacado',
'Super Nordestão','SuperFácil Atacado','Queiroz Atacadão','Corte Fácil Atacarejo',
'Rede Supercop','Atacadão']

for b in banners:
    print('==== BANNER:',b,'====')
    matches=[a for a in actions if a.get('banner')==b]
    # ordenar por fim desc
    matches.sort(key=lambda a:a.get('fim',''),reverse=True)
    for a in matches[:6]:
        print(f"  {a.get('shortcode')} perfil={a.get('perfil')} {a.get('inicio')}->{a.get('fim')} prods={prodcount(a)} titulo={a.get('titulo','')[:40]}")
    print()
