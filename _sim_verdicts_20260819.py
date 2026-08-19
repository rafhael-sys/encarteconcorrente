#!/usr/bin/env python3
"""Compila os veredictos de similaridade por foto da janela 2026-08-19.

Regra: veredito so entra no auto file com CERTEZA TOTAL. Pares ja decididos
(qualquer origem) em similaridade_decisoes.json NAO sao sobrescritos
(prioridade da validacao existente). Duvidas -> similaridade_incertos.json.
"""
import json
import os
import unicodedata

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")
HOJE = "2026-08-19"


def nrm(s: str) -> str:
    """Normaliza para comparacao (igual ao aplica_validacoes.py)."""
    s = unicodedata.normalize("NFD", str(s).lower())
    return " ".join("".join(c for c in s if unicodedata.category(c) != "Mn").split())


def chave_par(a: str, b: str) -> str:
    """Chave normalizada e ordenada de um par."""
    return " || ".join(sorted([nrm(a), nrm(b)]))


# index -> veredito. Default 'mesmo'; excecoes abaixo.
EXC = {28: "incerto", 30: "diferente"}

cand = json.load(open(os.path.join(DATA, "similaridade_candidatos.json"), encoding="utf-8"))
decisoes = json.load(open(os.path.join(DATA, "similaridade_decisoes.json"), encoding="utf-8"))
incertos = json.load(open(os.path.join(DATA, "similaridade_incertos.json"), encoding="utf-8"))

validacoes = []
add_incertos = 0
skip_existente = 0
for i, par in enumerate(cand):
    ver = EXC.get(i, "mesmo")
    a, b, k = par["a"], par["b"], par["k"]
    if ver == "incerto":
        incertos[k] = HOJE
        add_incertos += 1
        continue
    ch = chave_par(a, b)
    if ch in decisoes and decisoes[ch].get("veredito") != ver:
        # decisao existente diverge -> respeita a existente, nao sobrescreve
        skip_existente += 1
        continue
    validacoes.append({"a": a, "b": b, "veredito": ver})

os.makedirs(os.path.join(DATA, "validacoes_inbox"), exist_ok=True)
auto_path = os.path.join(DATA, "validacoes_inbox", f"auto_{HOJE}.json")
tmp = auto_path + ".tmp"
with open(tmp, "w", encoding="utf-8") as f:
    json.dump({"validacoes": validacoes}, f, ensure_ascii=False, indent=1)
os.replace(tmp, auto_path)

tmp = os.path.join(DATA, "similaridade_incertos.json") + ".tmp"
with open(tmp, "w", encoding="utf-8") as f:
    json.dump(incertos, f, ensure_ascii=False, indent=1)
os.replace(tmp, os.path.join(DATA, "similaridade_incertos.json"))

n_mesmo = sum(1 for v in validacoes if v["veredito"] == "mesmo")
n_dif = sum(1 for v in validacoes if v["veredito"] == "diferente")
print(f"auto file: {len(validacoes)} validacoes ({n_mesmo} mesmo, {n_dif} diferente); "
      f"+{add_incertos} incertos; {skip_existente} puladas (decisao existente diverge)")
