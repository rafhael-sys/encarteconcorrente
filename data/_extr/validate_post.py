import json, re, unicodedata
acts = json.load(open('data/actions.json'))
prods = json.load(open('data/products.json'))
canon = json.load(open('data/canon.json'))

print('total ações:', len(acts))
hoje = [a for a in acts if a.get('adicionado_em') == '2026-07-29']
print('ações com adicionado_em=hoje:', len(hoje))

# 1) toda página referenciada por ação de hoje existe em products.json?
faltap = []
for a in hoje:
    for pg in a['paginas']:
        k = pg.replace('.jpg', '')
        if k not in prods:
            faltap.append((a['id'], k))
print('páginas de ações-hoje ausentes em products.json:', len(faltap), faltap[:5])

# 2) refs do canon: pagekey#idx válidos? (amostra dos grupos que ganharam refs novos hoje é caro; checa consistência geral leve)
bad = 0
ok = 0
for g in canon:
    for m in g['m']:
        if '#' not in m:
            bad += 1; continue
        key, idx = m.rsplit('#', 1)
        if key in prods:
            try:
                if int(idx) < len(prods[key]):
                    ok += 1
                else:
                    bad += 1
            except ValueError:
                bad += 1
print('refs canon: ok(em products)=%d, quebrados(idx fora)=%d [refs antigos arquivados contam como nao-checados]' % (ok, bad))

# 3) DIFERENTES do regras_similaridade.md não podem estar no mesmo grupo
NOISE = {"lata","lta","pct","pcte","pacote","pet","tb","gf","cada","un","und","unid","unidade","sabores","sabor","fragrancias","fragrancia","tipos","tipo"}
def nrm_tokens(s):
    s = unicodedata.normalize("NFD", str(s).lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    s = re.sub(r"[^a-z0-9 ]"," ",s)
    return tuple(sorted(t for t in s.split() if t and t not in NOISE))

# grupo canônico de cada token-key
by_key = {}
for g in canon:
    by_key.setdefault(nrm_tokens(g['n']), []).append(g)

import os
difs = []
if os.path.exists('data/regras_similaridade.md'):
    for line in open('data/regras_similaridade.md', encoding='utf-8'):
        if line.strip().startswith('- DIFERENTES:'):
            m = re.findall(r'«([^»]*)»', line)
            if len(m) == 2:
                difs.append((m[0], m[1]))
viol = []
for a, b in difs:
    ka, kb = nrm_tokens(a), nrm_tokens(b)
    if ka == kb:  # colisão de tokens = cairiam no mesmo grupo pelo canon_add
        viol.append((a, b))
print('pares DIFERENTES que colidem por tokens (risco de fusão indevida):', len(viol))
for v in viol[:10]:
    print('   !!', v)
