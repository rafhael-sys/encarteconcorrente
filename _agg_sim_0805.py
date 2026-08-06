#!/usr/bin/env python3
"""Agrega os vereditos de similaridade (data/_extract/sim_verdicts.json) em:
- data/validacoes_inbox/auto_2026-08-05.json (pares de CERTEZA: mesmo/diferente)
- data/similaridade_incertos.json (pares 'duvida' ou nao avaliados -> {k: data})
Cada candidato cai em exatamente um bucket.
"""
import json

HOJE = "2026-08-05"
verd = json.load(open("data/_extract/sim_verdicts.json", encoding="utf-8"))
cands = json.load(open("data/similaridade_candidatos.json", encoding="utf-8"))
cand_keys = {c["k"] for c in cands}
by_k = {v["k"]: v for v in verd}

faltando = cand_keys - set(by_k)
extra = set(by_k) - cand_keys
print("candidatos:", len(cand_keys), "| vereditos:", len(verd),
      "| nao avaliados:", len(faltando), "| chaves fora dos candidatos:", len(extra))
for k in list(extra)[:10]:
    print("   EXTRA(k nao bate):", k)

validacoes = []
duvida_keys = []
for c in cands:
    k = c["k"]
    v = by_k.get(k)
    if v is None or v.get("veredito") == "duvida":
        duvida_keys.append(k)
    else:
        validacoes.append({"a": v["a"], "b": v["b"], "veredito": v["veredito"]})

n_mesmo = sum(1 for v in validacoes if v["veredito"] == "mesmo")
n_dif = sum(1 for v in validacoes if v["veredito"] == "diferente")
print("validacoes(certeza)=%d (mesmo=%d, diferente=%d) | duvida=%d" % (
    len(validacoes), n_mesmo, n_dif, len(duvida_keys)))

json.dump({"validacoes": validacoes},
          open("data/validacoes_inbox/auto_2026-08-05.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

inc = json.load(open("data/similaridade_incertos.json", encoding="utf-8"))
add = sum(1 for k in duvida_keys if k not in inc)
for k in duvida_keys:
    inc[k] = HOJE
json.dump(inc, open("data/similaridade_incertos.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("incertos: +%d novos (total=%d)" % (add, len(inc)))
print("OK: auto_2026-08-05.json gravado")
