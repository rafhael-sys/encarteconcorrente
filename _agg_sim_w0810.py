#!/usr/bin/env python3
"""Agrega vereditos de similaridade da janela 2026-08-10.

Mapeia cada veredito coletado (data/_simverd/collected.json) ao par original
(data/similaridade_candidatos.json) por assinatura normalizada e produz:
  - data/validacoes_inbox/auto_2026-08-10.json (pares mesmo/diferente, com
    a/b = nomes originais) — consumido por aplica_validacoes.py
  - data/similaridade_incertos.json (merge; pares incertos/sem match -> hoje)

Rode com 'commit' para gravar; sem argumento só mostra a conferência.
"""
import json
import os
import re
import sys
import unicodedata

BASE = os.path.dirname(os.path.abspath(__file__))
HOJE = "2026-08-10"
COMMIT = len(sys.argv) > 1 and sys.argv[1] == "commit"


def path(*p):
    return os.path.join(BASE, *p)


def nrm(s):
    s = unicodedata.normalize("NFD", str(s).lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return " ".join(re.sub(r"[^a-z0-9]+", " ", s).split())


def side_sig(s):
    return nrm(s)


cands = json.load(open(path("data/similaridade_candidatos.json"), encoding="utf-8"))
verds = json.load(open(path("data/_simverd/collected.json"), encoding="utf-8"))

# lookup por assinatura (frozenset dos dois lados normalizados)
vlook = {}
for v in verds:
    parts = [p for p in v["k"].split("||")]
    if len(parts) != 2:
        continue
    sig = frozenset(side_sig(p) for p in parts)
    vlook[sig] = v["veredito"]

auto = []
incertos_novos = {}
sem_match = []
cont = {"mesmo": 0, "diferente": 0, "incerto": 0, "sem_match": 0}

for c in cands:
    sig = frozenset((side_sig(c["a"]), side_sig(c["b"])))
    ver = vlook.get(sig)
    if ver is None:
        sem_match.append(c["k"])
        incertos_novos[c["k"]] = HOJE
        cont["sem_match"] += 1
        continue
    if ver in ("mesmo", "diferente"):
        auto.append({"a": c["a"], "b": c["b"], "veredito": ver})
        cont[ver] += 1
    else:
        incertos_novos[c["k"]] = HOJE
        cont["incerto"] += 1

print("candidatos:", len(cands), "| vereditos:", len(verds))
print("contagem:", cont)
print("auto (mesmo/diferente):", len(auto))
print("incertos novos:", len(incertos_novos))
if sem_match:
    print("SEM MATCH (viram incerto):")
    for k in sem_match:
        print("  -", k)

if not COMMIT:
    print("\n(conferência: nada gravado. rode com 'commit')")
    sys.exit(0)

# --- grava auto_2026-08-10.json ---
os.makedirs(path("data/validacoes_inbox"), exist_ok=True)
json.dump({"validacoes": auto},
          open(path("data/validacoes_inbox/auto_2026-08-10.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

# --- merge similaridade_incertos.json ---
inc_path = path("data/similaridade_incertos.json")
try:
    inc = json.load(open(inc_path, encoding="utf-8"))
except (FileNotFoundError, json.JSONDecodeError):
    inc = {}
antes = len(inc)
for k, d in incertos_novos.items():
    inc[k] = d
json.dump(inc, open(inc_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

print(f"\nGRAVADO. auto={len(auto)} | incertos: {antes} -> {len(inc)}")
