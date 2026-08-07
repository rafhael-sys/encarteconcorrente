import json, glob, os
BASE = os.path.dirname(os.path.abspath(__file__))
cand = json.load(open(os.path.join(BASE, 'data/similaridade_candidatos.json')))
kset = {c['k'] for c in cand}
seen_i = set()
seen_k = set()
counts = {'mesmo':0,'diferente':0,'incerto':0,'outro':0}
for fp in sorted(glob.glob(os.path.join(BASE,'data/_extract/sim0807_verd_*.json'))):
    rows = json.load(open(fp))
    print(os.path.basename(fp), 'linhas', len(rows))
    for r in rows:
        seen_i.add(r.get('i'))
        seen_k.add(r.get('k'))
        v = r.get('veredito')
        counts[v] = counts.get(v,0)+1 if v in counts else counts.get('outro',0)
        if v not in ('mesmo','diferente','incerto'):
            counts['outro']+=1
print('indices vistos:', len(seen_i), 'esperado 65 (0..64)')
faltam_i = [i for i in range(65) if i not in seen_i]
print('indices faltando:', faltam_i)
print('chaves batendo com candidatos:', len(seen_k & kset), 'de', len(kset))
print('chaves em verd que NAO existem em candidatos:', [k for k in seen_k if k not in kset][:5])
print('counts:', counts)
