#!/usr/bin/env python3
"""Junta os sim_chunk_*.json em validacoes_inbox/auto_2026-08-03.json e
atualiza similaridade_incertos.json. Nao roda aplica_validacoes (feito depois).
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
HOJE = "2026-08-03"
edir = os.path.join(BASE, "data", "_extract")

cand = json.load(open(os.path.join(BASE, "data", "similaridade_candidatos.json"),
                     encoding="utf-8"))
kset = {c.get("k") for c in cand}

certos, incertos = [], []
seen_chunks = []
for start in range(0, 70, 10):
    fp = os.path.join(edir, f"sim_chunk_{start}.json")
    if not os.path.exists(fp):
        continue
    seen_chunks.append(start)
    d = json.load(open(fp, encoding="utf-8"))
    for v in d.get("certos", []):
        if v.get("veredito") in ("mesmo", "diferente") and v.get("a") and v.get("b"):
            certos.append({"a": v["a"], "b": v["b"], "veredito": v["veredito"]})
    for k in d.get("incertos", []):
        incertos.append(k)

print("chunks lidos:", seen_chunks)
print("certos:", len(certos), "| incertos:", len(incertos),
      "| total candidatos:", len(cand))

# validacoes_inbox
inbox_dir = os.path.join(BASE, "data", "validacoes_inbox")
os.makedirs(inbox_dir, exist_ok=True)
outp = os.path.join(inbox_dir, f"auto_{HOJE}.json")
json.dump({"validacoes": certos}, open(outp, "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("gravado", outp)

# similaridade_incertos (merge)
incp = os.path.join(BASE, "data", "similaridade_incertos.json")
try:
    inc = json.load(open(incp, encoding="utf-8"))
except (FileNotFoundError, json.JSONDecodeError):
    inc = {}
add = 0
for k in incertos:
    if k and k not in inc:
        add += 1
    if k:
        inc[k] = HOJE
json.dump(inc, open(incp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"similaridade_incertos: +{add} novos (total {len(inc)})")

mesmo = sum(1 for v in certos if v["veredito"] == "mesmo")
dif = sum(1 for v in certos if v["veredito"] == "diferente")
print(f"resumo: {mesmo} mesmo, {dif} diferente, {len(incertos)} incertos")
