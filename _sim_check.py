import json
import os

inc = json.load(open('data/similaridade_incertos.json'))
print('incertos: tipo', type(inc).__name__, '| n=', len(inc))
for k, v in list(inc.items())[:4]:
    print('  ', repr(k)[:80], '->', v)

cand = json.load(open('data/similaridade_candidatos.json'))
print('\ncandidatos:', len(cand))

faltando = set()
for p in cand:
    for lado in ('foto_a', 'foto_b'):
        img = p[lado]['imagem']
        if not os.path.exists(img):
            faltando.add(img)
print('imagens faltando:', len(faltando))
for f in list(faltando)[:12]:
    print('   MISSING', f)

jarra = sum(1 for p in cand if p['k'] in inc)
print('pares candidatos que ja constam em incertos:', jarra)
