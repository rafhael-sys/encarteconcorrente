#!/usr/bin/env python3
"""Agrega os veredictos de similaridade da janela e prepara os arquivos.

- verdicts_*.json -> validacoes_inbox/auto_2026-07-27.json (só mesmo/diferente)
- pares 'incerto' -> data/similaridade_incertos.json (chave k -> data)
"""
import glob
import json
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def p(*x):
    return os.path.join(BASE, *x)


HOJE = "2026-07-27"
cand = json.load(open(p("data/similaridade_candidatos.json"), encoding="utf-8"))
por_k = {c["k"]: c for c in cand}

verdicts = []
for f in sorted(glob.glob(p("scratchpad/sim_ev/verdicts_*.json"))):
    d = json.load(open(f, encoding="utf-8"))
    verdicts.extend(d.get("verdicts", []))

vistos = set()
validacoes = []
incertos = json.load(open(p("data/similaridade_incertos.json"), encoding="utf-8"))
n_mesmo = n_dif = n_inc = 0
for v in verdicts:
    k = v.get("k")
    if k in vistos:
        continue
    vistos.add(k)
    ver = v.get("veredito")
    a = v.get("a") or (por_k.get(k, {}).get("a"))
    b = v.get("b") or (por_k.get(k, {}).get("b"))
    if ver == "mesmo":
        validacoes.append({"a": a, "b": b, "veredito": "mesmo"})
        n_mesmo += 1
    elif ver == "diferente":
        validacoes.append({"a": a, "b": b, "veredito": "diferente"})
        n_dif += 1
    else:
        if k:
            incertos[k] = HOJE
        n_inc += 1

# pares sem veredito (subagente falhou) -> incerto por segurança
for k in por_k:
    if k not in vistos:
        incertos[k] = HOJE
        n_inc += 1

os.makedirs(p("data/validacoes_inbox"), exist_ok=True)
json.dump({"validacoes": validacoes},
          open(p("data/validacoes_inbox/auto_2026-07-27.json"), "w",
               encoding="utf-8"), ensure_ascii=False, indent=1)
json.dump(incertos, open(p("data/similaridade_incertos.json"), "w",
                         encoding="utf-8"), ensure_ascii=False, indent=1)

print("veredictos recebidos:", len(verdicts))
print("auto validacoes: mesmo=%d diferente=%d | incertos+=%d (total incertos=%d)"
      % (n_mesmo, n_dif, n_inc, len(incertos)))
