import json, os
c = json.load(open('data/similaridade_candidatos.json'))
print('pares:', len(c))
faltando = set()
for par in c:
    for fk in ('foto_a', 'foto_b'):
        img = par[fk]['imagem']
        if not os.path.exists(img):
            faltando.add(img)
print('imagens faltando:', len(faltando))
for f in list(faltando)[:30]:
    print('  FALTA', f)
rs = [par.get('r', 0) for par in c]
print('r min/max:', min(rs), max(rs))
# salva os pares em lotes para os subagentes
import math
N = 5
lotes = [[] for _ in range(N)]
for i, par in enumerate(c):
    slim = {'k': par['k'], 'a': par['a'], 'b': par['b'],
            'foto_a': par['foto_a'], 'foto_b': par['foto_b']}
    lotes[i % N].append(slim)
for i, lote in enumerate(lotes):
    json.dump(lote, open(f'data/_extr/sim_lote_{i}.json', 'w'), ensure_ascii=False, indent=1)
    print(f'lote {i}: {len(lote)} pares')
