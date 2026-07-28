import json

acts = json.load(open('data/actions.json'))
prods = json.load(open('data/products.json'))
canon = json.load(open('data/canon.json'))

novos = ['atacadao_3b9105b675', 'atacadao_806f2b524a', 'atacadao_dc70699b7b',
         'story_supernordestaonatal_20260728']
print('total acoes:', len(acts))
for a in acts:
    if a['id'] in novos:
        tot = sum(len(prods.get(pg[:-4] if pg.endswith('.jpg') else pg, [])) for pg in a['paginas'])
        print(f"\n[{a['id']}] {a['inicio']}->{a['fim']} fonte={a.get('fonte')} add={a.get('adicionado_em')}"
              f" carrossel={a.get('carrossel')} npag={len(a['paginas'])} nprod={tot}")
        print('   link:', a.get('link', ''))
        print('   paginas:', a['paginas'])

# checar refs canon apontam p/ produtos existentes (amostra dos novos)
print('\n=== checagem de integridade canon (refs orfas) ===')
pset = set()
for k, lst in prods.items():
    for i in range(len(lst)):
        pset.add(f'{k}#{i}')
orf = 0
for g in canon:
    for m in g.get('m', []):
        if m not in pset:
            orf += 1
print('refs canon orfas (total banco):', orf)

# duplicidade de pid#idx no canon
from collections import Counter
c = Counter()
for g in canon:
    for m in g.get('m', []):
        c[m] += 1
dups = [m for m, n in c.items() if n > 1]
print('refs duplicadas em >1 grupo canon:', len(dups))

# fila vazia?
fila = json.load(open('data/fila_novos.json'))
print('\nfila_novos.json agora tem', len(fila), 'itens')
