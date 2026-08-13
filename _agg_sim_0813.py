#!/usr/bin/env python3
"""Agrega os vereditos de similaridade por foto da janela 2026-08-13.

Casa cada veredito (data/_tmp_verd_0813.json) ao candidato correspondente em
data/similaridade_candidatos.json pela chave 'k' (independente da ordem das
duas metades). Gera:
  - data/validacoes_inbox/auto_2026-08-13.json  (mesmo/diferente, certeza total)
  - atualiza data/similaridade_incertos.json     (incertos, para nao reavaliar)
Nao toca em canon (isso e feito por aplica_validacoes.py depois).
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
HOJE = "2026-08-13"


def path(*p):
    return os.path.join(BASE, *p)


def sortkey(k):
    parts = [" ".join(h.split()) for h in k.split("||")]
    return " || ".join(sorted(parts))


cand = json.load(open(path("data/similaridade_candidatos.json"), encoding="utf-8"))
verd = json.load(open(path("data/_tmp_verd_0813.json"), encoding="utf-8"))

cand_by = {}
for c in cand:
    cand_by[sortkey(c["k"])] = c

validacoes = []
incertos_novos = {}
nao_casou = []
usados = set()

for v in verd:
    sk = sortkey(v["k"])
    c = cand_by.get(sk)
    if c is None:
        nao_casou.append(v["k"])
        continue
    usados.add(sk)
    ver = v["veredito"]
    if ver in ("mesmo", "diferente"):
        validacoes.append({"a": c["a"], "b": c["b"], "veredito": ver})
    elif ver == "incerto":
        incertos_novos[c["k"]] = HOJE

# candidatos sem veredito (nao deveria acontecer)
sem_verd = [c["k"] for c in cand if sortkey(c["k"]) not in usados]

print("candidatos:", len(cand), "| vereditos:", len(verd))
print("validacoes (mesmo/diferente):", len(validacoes))
print("  mesmo:", sum(1 for x in validacoes if x["veredito"] == "mesmo"),
      "| diferente:", sum(1 for x in validacoes if x["veredito"] == "diferente"))
print("incertos novos:", len(incertos_novos))
if nao_casou:
    print("!! vereditos SEM candidato:", nao_casou)
if sem_verd:
    print("!! candidatos SEM veredito:", sem_verd)

if nao_casou or sem_verd:
    print("\nABORTANDO: divergencia de casamento — nada gravado.")
    raise SystemExit(1)

# grava auto_2026-08-13.json
os.makedirs(path("data/validacoes_inbox"), exist_ok=True)
json.dump({"validacoes": validacoes},
          open(path("data/validacoes_inbox/auto_%s.json" % HOJE), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

# funde incertos
inc_path = path("data/similaridade_incertos.json")
try:
    incertos = json.load(open(inc_path, encoding="utf-8"))
except (FileNotFoundError, json.JSONDecodeError):
    incertos = {}
antes = len(incertos)
incertos.update(incertos_novos)
json.dump(incertos, open(inc_path, "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("incertos: %d -> %d" % (antes, len(incertos)))
print("OK gravado auto_%s.json + incertos atualizados." % HOJE)
