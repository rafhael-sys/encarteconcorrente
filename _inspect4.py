import json

acts = json.load(open('data/actions.json'))
prods = json.load(open('data/products.json'))

# Ver acao story recente e como suas paginas mapeiam para products.json
for a in acts:
    if a['id'] == 'story_marvermelhoatacado_20260727':
        print('acao:', a['id'], 'periodo', a['inicio'], '->', a['fim'])
        print('paginas (primeiras 3):', a['paginas'][:3])
        for pg in a['paginas'][:3]:
            key = pg.replace('.jpg', '')
            print('  key', key, '-> em products?', key in prods, '| nprod', len(prods.get(key, [])))
        break

# Verificar dedup para hoje: MV story 20260727 (07-24->07-30). A fila tem story_marvermelhoatacado_20260728.
# Ver periodos existentes por banner para checagem de twin.
print()
print('=== resumo: acoes MV com fim >= 2026-07-27 ===')
for a in acts:
    if a['banner'] == 'Mar Vermelho Atacado' and a.get('fim','') >= '2026-07-27':
        # contar produtos totais
        tot = 0
        for pg in a['paginas']:
            tot += len(prods.get(pg.replace('.jpg',''), []))
        print(a['id'], a['inicio'],'->',a['fim'],'| pgs',len(a['paginas']),'| prod',tot,'| fonte',a.get('fonte','-'))
