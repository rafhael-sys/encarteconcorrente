"""Consolida os 5 lotes w0826_sim_*.json da janela 2026-08-26.

Gera data/validacoes_inbox/auto_2026-08-26.json (so pares de certeza total),
acrescenta os incertos a data/similaridade_incertos.json e esvazia
data/similaridade_candidatos.json. Roda depois: aplica_validacoes.py.
"""
import glob
import json
import os

BASE = '/Users/teste/encarteconcorrente'
HOJE = '2026-08-26'

cands = json.load(open(os.path.join(BASE, 'data/similaridade_candidatos.json'), encoding='utf-8'))
byk = {c['k']: c for c in cands}

certos = []
incertos = []
vistos = set()
lotes = sorted(glob.glob(os.path.join(BASE, 'data/_extract/w0826_sim_*.json')))
for fp in lotes:
    d = json.load(open(fp, encoding='utf-8'))
    for c in d.get('certos', []):
        k = c['k']
        if k not in byk:
            print(f'[aviso] k fora dos candidatos: {k[:60]}')
            continue
        if k in vistos:
            continue
        vistos.add(k)
        certos.append({'a': byk[k]['a'], 'b': byk[k]['b'], 'veredito': c['veredito']})
    for k in d.get('incertos', []):
        if k in byk and k not in vistos:
            vistos.add(k)
            incertos.append(k)

faltam = [k for k in byk if k not in vistos]
print(f'lotes: {len(lotes)} | certos: {len(certos)} | incertos: {len(incertos)} | sem veredito: {len(faltam)}')
for k in faltam[:10]:
    print('  falta:', k[:80])

if faltam:
    raise SystemExit('ha pares sem veredito — nao consolidar ainda')

os.makedirs(os.path.join(BASE, 'data/validacoes_inbox'), exist_ok=True)
out = os.path.join(BASE, 'data/validacoes_inbox', f'auto_{HOJE}.json')
with open(out, 'w', encoding='utf-8') as f:
    json.dump({'validacoes': certos}, f, ensure_ascii=False, indent=1)

inc_path = os.path.join(BASE, 'data/similaridade_incertos.json')
inc = json.load(open(inc_path, encoding='utf-8')) if os.path.exists(inc_path) else {}
for k in incertos:
    inc[k] = HOJE
with open(inc_path, 'w', encoding='utf-8') as f:
    json.dump(inc, f, ensure_ascii=False, indent=1)

with open(os.path.join(BASE, 'data/similaridade_candidatos.json'), 'w', encoding='utf-8') as f:
    json.dump([], f)

n_mesmo = sum(1 for c in certos if c['veredito'] == 'mesmo')
print(f'gravado {out}: {len(certos)} validacoes ({n_mesmo} mesmo / {len(certos)-n_mesmo} diferente)')
print(f'incertos agora: {len(inc)} | candidatos esvaziados')
