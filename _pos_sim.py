import json
import unicodedata
from collections import Counter

canon = json.load(open('data/canon.json'))
prods = json.load(open('data/products.json'))

# integridade
pset = set()
for k, lst in prods.items():
    for i in range(len(lst)):
        pset.add(f'{k}#{i}')
orf = sum(1 for g in canon for m in g.get('m', []) if m not in pset)
c = Counter(m for g in canon for m in g.get('m', []))
dups = [m for m, n in c.items() if n > 1]
print('total grupos canon:', len(canon))
print('refs orfas:', orf, '| refs em >1 grupo:', len(dups))


def nrm(s):
    s = unicodedata.normalize('NFD', str(s).lower())
    return ' '.join(''.join(ch for ch in s if unicodedata.category(ch) != 'Mn').split())


def grupo_de(nome):
    for gi, g in enumerate(canon):
        if nrm(g['n']) == nrm(nome):
            return gi
    return None


# checar pares DIFERENTES nao estao no mesmo grupo
pares_dif = [
    ("Toalhas Umedecidas Mili Love & Care C/48", "Toalhas Umedecidas Mili Love & Care C/96"),
    ("Coxinha da Asa Lar IQF 1kg", "Coxinha da Asa Seara IQF 1kg"),
]
print('\n=== pares DIFERENTES devem estar em grupos distintos ===')
for a, b in pares_dif:
    ga, gb = grupo_de(a), grupo_de(b)
    ok = 'OK (distintos)' if ga != gb else 'PROBLEMA (mesmo grupo!)'
    print(f'  {a[:40]!r} g={ga} | {b[:40]!r} g={gb} -> {ok}')

# amostra: onde caiu o Cerveja Spaten novo
print('\n=== grupo do Spaten novo ===')
for g in canon:
    if 'story_supernordestaonatal_3950894964116750691#0' in g.get('m', []):
        print('  grupo:', g['n'], '| membros:', len(g['m']))
        break
