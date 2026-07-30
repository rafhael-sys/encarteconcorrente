import json, glob, os
d = '/Users/teste/encarteconcorrente/data/_extr'
cand = json.load(open('data/similaridade_candidatos.json'))
bykey = {p['k']: p for p in cand}

vereditos = {}
for fp in sorted(glob.glob(os.path.join(d, 'sim_out_*.json'))):
    data = json.load(open(fp))
    for r in data.get('resultados', []):
        k = r.get('k'); v = r.get('veredito')
        if k in bykey and v in ('mesmo', 'diferente', 'incerto'):
            vereditos[k] = v

falt = [k for k in bykey if k not in vereditos]
print('pares candidatos:', len(bykey))
print('com veredito:', len(vereditos), '| sem veredito (tratar como incerto):', len(falt))
from collections import Counter
c = Counter(vereditos.values())
print('distribuição:', dict(c))

# monta inbox (mesmo/diferente) usando os NOMES a/b (dados) dos candidatos
validacoes = []
for k, v in vereditos.items():
    if v in ('mesmo', 'diferente'):
        p = bykey[k]
        validacoes.append({'a': p['a'], 'b': p['b'], 'veredito': v})

json.dump({'validacoes': validacoes},
          open('data/validacoes_inbox/auto_2026-07-29.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('inbox auto_2026-07-29.json:', len(validacoes), 'validações (mesmo/diferente)')

# incertos: acrescenta ao similaridade_incertos.json (chave k -> data). inclui falt.
inc_path = 'data/similaridade_incertos.json'
incertos = json.load(open(inc_path)) if os.path.exists(inc_path) else {}
add = 0
for k in list(vereditos.keys()) + falt:
    if vereditos.get(k, 'incerto') == 'incerto':
        if k not in incertos:
            incertos[k] = '2026-07-29'
            add += 1
json.dump(incertos, open(inc_path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('incertos acrescentados:', add, '| total incertos:', len(incertos))

# mostra os "mesmo" para conferência
print('\n--- MESMO (fusões que serão aplicadas) ---')
for x in validacoes:
    if x['veredito'] == 'mesmo':
        print('  ==', x['a'], '||', x['b'])
print('--- DIFERENTES (registrados) ---')
for x in validacoes:
    if x['veredito'] == 'diferente':
        print('  !=', x['a'], '||', x['b'])
