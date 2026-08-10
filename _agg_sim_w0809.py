import json, glob, sys

# candidatos originais (com a/b/k)
cand = json.load(open('_tmp_sim_novos.json'))
by_k = {c['k']: c for c in cand}

# Overrides do orquestrador: rebaixar p/ incerto quando o veredito do subagente
# tem risco de unir grupos canônicos de VARIANTES diferentes (Diet/Zero/Light).
FORCE_INCERTO = {
    'cappuccino 3 coracoes 150g || cappuccino 3 coracoes diet pt 150g',
}

verd = {}  # k -> veredito
dups = []
for f in sorted(glob.glob('data/_extract/simres_w0809_*.json')):
    d = json.load(open(f))
    for r in d.get('resultados', []):
        k = r.get('k'); v = r.get('veredito')
        if k in verd and verd[k] != v:
            dups.append((k, verd[k], v))
        verd[k] = v
for k in FORCE_INCERTO:
    if k in verd:
        verd[k] = 'incerto'

faltando = [k for k in by_k if k not in verd]
extras = [k for k in verd if k not in by_k]
print('candidatos:', len(by_k), '| vereditos:', len(verd))
print('faltando veredito:', len(faltando))
for k in faltando:
    print('   FALTA:', k)
print('chaves extras (não bate com candidato):', len(extras))
for k in extras:
    print('   EXTRA:', k[:80])
if dups:
    print('conflitos entre lotes:', dups)

from collections import Counter
print('distribuição:', Counter(verd.values()))

if '--write' in sys.argv:
    # monta validacoes (mesmo/diferente) e incertos
    validacoes = []
    incertos_novos = {}
    for k, v in verd.items():
        if k not in by_k:
            continue
        c = by_k[k]
        if v in ('mesmo', 'diferente'):
            validacoes.append({'a': c['a'], 'b': c['b'], 'veredito': v})
        else:  # incerto ou qualquer outra coisa -> dúvida
            incertos_novos[k] = '2026-08-09'
    # pares sem veredito também viram incertos (não reavaliar à toa)
    for k in faltando:
        incertos_novos[k] = '2026-08-09'
    json.dump({'validacoes': validacoes},
              open('data/validacoes_inbox/auto_2026-08-09.json', 'w'),
              ensure_ascii=False, indent=1)
    inc = json.load(open('data/similaridade_incertos.json'))
    antes = len(inc)
    inc.update(incertos_novos)
    json.dump(inc, open('data/similaridade_incertos.json', 'w'),
              ensure_ascii=False, indent=1)
    print(f'GRAVADO: {len(validacoes)} validações (mesmo/diferente), '
          f'incertos {antes}->{len(inc)} (+{len(inc)-antes})')
