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


def busca(chave, only_banner=None):
    print('=== busca:', chave, ('| banner~ ' + only_banner) if only_banner else '', '===')
    hits = 0
    for pgkey, lst in p.items():
        ac = pg2ac.get(pgkey)
        b = ac['banner'] if ac else '??'
        if only_banner and only_banner not in b:
            continue
        for pr in lst:
            if chave in norm(pr.get('n', '')):
                aid = ac['id'] if ac else '?'
                print('   [%s] %s %s..%s :: %s = %s %s' % (b, aid, ac.get('inicio'), ac.get('fim'), pr['n'], pr['p'], pr.get('u', '')))
                hits += 1
    if not hits:
        print('   (nenhum)')


print('##### QUEIROZ HPE (Mês dos Pais, 07-10/08) #####')
for c in ['clear men', 'rexona men', 'salutaris', 'bozzano', 'comfort 3', 'gillette prest', 'prestobarba']:
    busca(c, 'Queiroz')

print()
print('##### CORTE FACIL Bom Todo (07-09/08) #####')
for c in ['sobrecoxa', 'pao de alho', 'lombo suino', 'panceta', 'ancho suino']:
    busca(c, 'Corte')
