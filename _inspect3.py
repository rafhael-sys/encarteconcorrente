import json

prods = json.load(open('data/products.json'))
# achar uma pagina recente com produtos
for key in ['DbUGqN-G8NE_p1', 'DbUEf7Djik8_p1', 'DbJzQS-G14k_p2', 'DbLoDwGm6-q_p2']:
    if key in prods and prods[key]:
        print('=== pagina', key, '(', len(prods[key]), 'produtos ) ===')
        print(json.dumps(prods[key][:3], ensure_ascii=False, indent=1))
        break

# Ver quais paginas da fila JÁ existem em products.json
fila_pages = []
import glob, os
fila = json.load(open('data/fila_novos.json'))
for post in fila:
    for pg in post['paginas']:
        fila_pages.append(pg[:-4] if pg.endswith('.jpg') else pg)
print()
print('=== paginas da fila que JA estao em products.json ===')
for p in fila_pages:
    if p in prods:
        print(' ', p, '->', len(prods[p]), 'produtos')
print('(fim)')

# canon: procurar campos
canon = json.load(open('data/canon.json'))
allk = set()
for g in canon:
    allk |= set(g.keys())
print()
print('canon chaves por grupo:', sorted(allk))
