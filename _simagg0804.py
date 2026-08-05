import json, glob, unicodedata, os


def nrm(s):
    s = unicodedata.normalize('NFD', str(s).lower())
    return ' '.join(''.join(c for c in s if unicodedata.category(c) != 'Mn').split())


cands = json.load(open('data/similaridade_candidatos.json'))
# indice por par de nomes normalizados -> k original
by_pair = {}
for p in cands:
    by_pair[frozenset((nrm(p['a']), nrm(p['b'])))] = p['k']

verdicts = []
for f in sorted(glob.glob('data/_extract/simverd_*.json')):
    verdicts += json.load(open(f))

validacoes = []
incertos_novos = {}
sem_k = []
for v in verdicts:
    a, b, ver = v.get('a'), v.get('b'), v.get('veredito')
    if not a or not b:
        continue
    if ver in ('mesmo', 'diferente'):
        validacoes.append({'a': a, 'b': b, 'veredito': ver})
    else:  # incerto / duvida
        k = v.get('k') or by_pair.get(frozenset((nrm(a), nrm(b))))
        if k:
            incertos_novos[k] = '2026-08-04'
        else:
            sem_k.append((a, b))

# 1) grava inbox de validacoes (pares certos)
os.makedirs('data/validacoes_inbox', exist_ok=True)
json.dump({'validacoes': validacoes},
          open('data/validacoes_inbox/auto_2026-08-04.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)

# 2) acrescenta incertos ao objeto existente
inc = json.load(open('data/similaridade_incertos.json'))
antes = len(inc)
inc.update(incertos_novos)
json.dump(inc, open('data/similaridade_incertos.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)

print('validacoes (certos) gravadas:', len(validacoes))
print('  mesmo   :', sum(1 for x in validacoes if x['veredito'] == 'mesmo'))
print('  diferente:', sum(1 for x in validacoes if x['veredito'] == 'diferente'))
print('incertos novos:', len(incertos_novos), '| incertos antes:', antes, '-> agora:', len(inc))
if sem_k:
    print('SEM K (incertos sem chave):', sem_k)
