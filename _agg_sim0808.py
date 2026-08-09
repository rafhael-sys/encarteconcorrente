import json, glob, os, sys

HOJE = "2026-08-08"
cand = json.load(open('data/similaridade_candidatos.json'))
by_k = {p['k']: p for p in cand}

verd = {}   # k -> veredito
for f in sorted(glob.glob('data/_extract/sim0808_batch*.json')):
    d = json.load(open(f))
    for v in d.get('verdicts', []):
        k = v.get('k'); ver = v.get('veredito')
        if k in by_k and ver in ('mesmo', 'diferente', 'incerto'):
            verd[k] = ver

falta = [k for k in by_k if k not in verd]
mesmo = [k for k in verd if verd[k] == 'mesmo']
dif   = [k for k in verd if verd[k] == 'diferente']
inc   = [k for k in verd if verd[k] == 'incerto']
print("pares candidatos:", len(by_k))
print("com veredito:", len(verd), "| mesmo:", len(mesmo), "diferente:", len(dif), "incerto:", len(inc))
print("SEM veredito (tratados como incerto):", len(falta))
for k in falta:
    print("   falta:", k[:80])

if len(sys.argv) > 1 and sys.argv[1] == 'commit':
    # 1) auto validacoes (so certezas absolutas)
    vals = []
    for k in mesmo + dif:
        p = by_k[k]
        vals.append({"a": p['a'], "b": p['b'], "veredito": verd[k]})
    os.makedirs('data/validacoes_inbox', exist_ok=True)
    json.dump({"validacoes": vals}, open('data/validacoes_inbox/auto_2026-08-08.json', 'w'),
              ensure_ascii=False, indent=1)
    # 2) incertos: incerto + falta -> nao reavaliar
    incertos = json.load(open('data/similaridade_incertos.json'))
    for k in inc + falta:
        incertos[k] = HOJE
    tmp = 'data/similaridade_incertos.json.tmp'
    json.dump(incertos, open(tmp, 'w'), ensure_ascii=False, indent=1)
    os.replace(tmp, 'data/similaridade_incertos.json')
    # 3) esvazia candidatos
    json.dump([], open('data/similaridade_candidatos.json', 'w'), ensure_ascii=False, indent=1)
    print("\nGRAVADO: auto_2026-08-08.json com", len(vals), "validacoes (",
          len(mesmo), "mesmo,", len(dif), "diferente ) |",
          len(inc)+len(falta), "incertos registrados | candidatos esvaziados")
