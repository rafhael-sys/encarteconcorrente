import json, glob, os, unicodedata
d = '/Users/teste/encarteconcorrente/data/_extr'
lote1 = json.load(open(os.path.join(d, 'sim_lote_1.json')))
lote1_keys = {p['k'] for p in lote1}
print('lote 1 pares:', len(lote1_keys))

# sim_out_1.json existe e tem verdicts?
p1 = os.path.join(d, 'sim_out_1.json')
if os.path.exists(p1):
    o1 = json.load(open(p1))
    res = o1.get('resultados', [])
    print('sim_out_1.json existe com', len(res), 'resultados')
    from collections import Counter
    print('  distribuição lote1:', dict(Counter(r.get('veredito') for r in res)))
else:
    print('sim_out_1.json AINDA NÃO EXISTE')

# quais pares foram parar em incertos hoje que na verdade pertencem ao lote 1?
inc = json.load(open('data/similaridade_incertos.json'))
lote1_em_incertos = [k for k in lote1_keys if inc.get(k) == '2026-07-29']
print('pares do lote 1 marcados incerto hoje:', len(lote1_em_incertos))
