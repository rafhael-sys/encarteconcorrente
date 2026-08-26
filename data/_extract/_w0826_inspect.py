import json

with open('data/canon.json') as f:
    canon = json.load(f)
print('canon: list de', len(canon))
for g in canon[:3]:
    print(json.dumps(g, ensure_ascii=False)[:300])
print('...')
print(json.dumps(canon[-1], ensure_ascii=False)[:300])

# formato do regras_similaridade.md (primeiras linhas)
with open('data/regras_similaridade.md') as f:
    lines = f.readlines()
print('\nregras_similaridade.md:', len(lines), 'linhas')
for ln in lines[:12]:
    print(repr(ln[:150]))

# products.json: exemplo de valor
with open('data/products.json') as f:
    prods = json.load(f)
k = 'DccKp1lFs6R_p1'
print('\nproducts exemplo:', json.dumps(prods[k][0], ensure_ascii=False))
