import json, unicodedata

a = json.load(open('data/actions.json'))
p = json.load(open('data/products.json'))
pg2ac = {}
for x in a:
    for fn in x.get('paginas', []):
        pg2ac[fn.replace('.jpg', '')] = x


def norm(s):
    s = unicodedata.normalize('NFD', s.lower())
    return ''.join(c for c in s if unicodedata.category(c) != 'Mn')


alvos = {
    'cha de dentro': 'RedeMais Chã de Dentro',
    'pampers': 'Fralda Pampers',
    'skalinha': 'Skalinha bebe',
    'bob esponja': 'Leite Ferm Elege Bob Esponja',
    'elege': 'Elege',
}
for chave, lbl in alvos.items():
    print('=== busca:', lbl, '(', chave, ') ===')
    hits = 0
    for pgkey, lst in p.items():
        ac = pg2ac.get(pgkey)
        for pr in lst:
            if chave in norm(pr.get('n', '')):
                b = ac['banner'] if ac else '??'
                aid = ac['id'] if ac else '?'
                ini = ac.get('inicio') if ac else ''
                fim = ac.get('fim') if ac else ''
                print('   [%s] %s %s..%s :: %s = %s %s' % (b, aid, ini, fim, pr['n'], pr['p'], pr.get('u', '')))
                hits += 1
    if not hits:
        print('   (nenhum)')
