import json, os
d = '/Users/teste/encarteconcorrente/data/_extr'
cand = json.load(open('data/similaridade_candidatos.json.bak_fix')) if os.path.exists('data/similaridade_candidatos.json.bak_fix') else None
# candidatos já foram esvaziados; recupero os pares do lote 1 pelo arquivo de lote
lote1 = json.load(open(os.path.join(d, 'sim_lote_1.json')))
bykey = {p['k']: p for p in lote1}
out1 = json.load(open(os.path.join(d, 'sim_out_1.json')))['resultados']

# 1) monta inbox suplementar com mesmo/diferente do lote 1
validacoes = []
incerto_reais = []
for r in out1:
    k = r.get('k'); v = r.get('veredito')
    if k not in bykey:
        continue
    if v in ('mesmo', 'diferente'):
        validacoes.append({'a': bykey[k]['a'], 'b': bykey[k]['b'], 'veredito': v})
    else:
        incerto_reais.append(k)
json.dump({'validacoes': validacoes},
          open('data/validacoes_inbox/auto_2026-07-29b.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('inbox suplementar (lote1):', len(validacoes), 'validações;', len(incerto_reais), 'incertos reais')

# 2) remove os 13 keys do lote 1 que foram marcados incerto=2026-07-29 por engano,
#    exceto os que são genuinamente incertos agora
inc = json.load(open('data/similaridade_incertos.json'))
removidos = 0
for k in bykey:
    if inc.get(k) == '2026-07-29' and k not in incerto_reais:
        del inc[k]; removidos += 1
# garante que incertos reais do lote1 fiquem registrados
for k in incerto_reais:
    inc.setdefault(k, '2026-07-29')
json.dump(inc, open('data/similaridade_incertos.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('incertos removidos (corrigidos):', removidos, '| total incertos agora:', len(inc))
for x in validacoes:
    print('  ', x['veredito'], x['a'], '||', x['b'])
