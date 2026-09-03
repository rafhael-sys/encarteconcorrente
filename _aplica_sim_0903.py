import json, os
HOJE = "2026-09-03"
BASE = os.path.dirname(os.path.abspath(__file__))
def p(*x): return os.path.join(BASE, *x)

cands = json.load(open(p('data/similaridade_candidatos.json'), encoding='utf-8'))
verd = json.load(open(p('_sim_verdicts_20260903.json'), encoding='utf-8'))
by_k = {c['k']: c for c in cands}

# checagem de cobertura
faltando = [c['k'] for c in cands if c['k'] not in verd]
extra = [k for k in verd if k not in by_k]
if faltando:
    print("ERRO: pares sem veredito:", len(faltando))
    for k in faltando: print("  ", k[:70])
if extra:
    print("ERRO: vereditos sem par correspondente:", len(extra))
    for k in extra: print("  ", k[:70])
if faltando or extra:
    raise SystemExit(1)

validacoes = []
incertos_novos = {}
cont = {"mesmo": 0, "diferente": 0, "incerto": 0}
for c in cands:
    k = c['k']
    v = verd[k]
    cont[v] += 1
    if v in ('mesmo', 'diferente'):
        validacoes.append({"a": c['a'], "b": c['b'], "veredito": v})
    else:
        incertos_novos[k] = HOJE

print("cobertura OK:", len(cands), "pares |", cont)

# grava inbox de validacoes (certeza total)
os.makedirs(p('data/validacoes_inbox'), exist_ok=True)
with open(p('data/validacoes_inbox', f'auto_{HOJE}.json'), 'w', encoding='utf-8') as f:
    json.dump({"validacoes": validacoes}, f, ensure_ascii=False, indent=1)
print("inbox gravado:", len(validacoes), "validacoes (mesmo/diferente)")

# atualiza incertos (nao sobrescreve os existentes)
inc_path = p('data/similaridade_incertos.json')
incertos = json.load(open(inc_path, encoding='utf-8')) if os.path.exists(inc_path) else {}
antes = len(incertos)
for k, d in incertos_novos.items():
    incertos.setdefault(k, d)
with open(inc_path, 'w', encoding='utf-8') as f:
    json.dump(incertos, f, ensure_ascii=False, indent=1)
print(f"incertos: {antes} -> {len(incertos)} (+{len(incertos)-antes})")
