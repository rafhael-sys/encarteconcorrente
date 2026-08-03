import json
p = json.load(open('data/products.json'))
# find a non-empty entry
for k, v in p.items():
    if v:
        print('=== chave:', k, '=== num produtos:', len(v))
        print(json.dumps(v[:3], ensure_ascii=False, indent=1))
        break

# Check the banners in queue against existing actions for dedup
a = json.load(open('data/actions.json'))
banners_fila = ['Mar Vermelho Atacado', 'Super Nordestão', 'Corte Fácil Atacarejo',
                'Assaí Atacadista', 'Atacadão', 'Mirassol Atacado', 'Rede Mais']
print('\n=== ações existentes por banner da fila (banner | inicio | fim | id | npaginas) ===')
for x in a:
    if x.get('banner') in banners_fila:
        print(f"{x['banner']!r:30} {x.get('inicio')} -> {x.get('fim')}  id={x['id']}  fonte={x.get('fonte','ig')}  npag={len(x.get('paginas',[]))}")
