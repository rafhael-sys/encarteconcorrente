import json

acts = json.load(open('data/actions.json'))
extra = set()
for a in acts:
    extra |= set(a.keys())
print('todas as chaves vistas:', sorted(extra))
print()

for a in acts:
    if a.get('fonte') == 'web':
        print('--- exemplo web ---')
        print(json.dumps(a, ensure_ascii=False, indent=1)[:900])
        break
print()

for a in acts:
    if 'adicionado_em' in a:
        keys = ('id', 'banner', 'inicio', 'fim', 'adicionado_em', 'fonte', 'link', 'shortcode', 'perfil')
        print('--- exemplo adicionado_em ---')
        print(json.dumps({k: a[k] for k in a if k in keys}, ensure_ascii=False, indent=1))
        break
print()

# Banners relevantes na fila
targets = ['Mar Vermelho Atacado', 'Atacadão', 'Miramar Supermercado', 'Rede Supercop',
           'Rede Mais', 'Corte Fácil Atacarejo', 'Super Nordestão']
print('=== acoes existentes desses banners (id, inicio, fim, shortcode, npaginas) ===')
for a in acts:
    if a.get('banner') in targets:
        print(a.get('banner'), '|', a.get('id'), '|', a.get('inicio'), '->', a.get('fim'),
              '| sc=', a.get('shortcode'), '| pgs=', len(a.get('paginas', [])), '| fonte=', a.get('fonte', '-'))
