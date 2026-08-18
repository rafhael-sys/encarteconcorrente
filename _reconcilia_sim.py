"""Reconcilia os veredictos por foto (sim_part*.json) contra as decisoes humanas
existentes (que tem prioridade) e prepara inbox + incertos.

Modo: 'report' (padrao, nao grava) ou 'write' (grava inbox e incertos)."""
import glob
import json
import os
import sys
import unicodedata

HOJE = "2026-08-17"
MODE = sys.argv[1] if len(sys.argv) > 1 else "report"


def nrm(s):
    s = unicodedata.normalize("NFD", str(s).lower())
    return " ".join("".join(c for c in s if unicodedata.category(c) != "Mn").split())


def chave_par(a, b):
    return " || ".join(sorted([nrm(a), nrm(b)]))


cand = json.load(open("data/similaridade_candidatos.json"))
verd = {}
for f in sorted(glob.glob("data/_extract_win2_20260817/sim_part*.json")):
    for r in json.load(open(f)):
        verd[r["index"]] = r["veredito"]

decisoes = {}
if os.path.exists("data/similaridade_decisoes.json"):
    decisoes = json.load(open("data/similaridade_decisoes.json"))

validacoes = []
incertos_novos = {}
ja_resolvido = []
conflitos = []

for i, par in enumerate(cand):
    a, b, k = par["a"], par["b"], par["k"]
    v = verd.get(i, "incerto")
    key = chave_par(a, b)
    if key in decisoes:
        hv = decisoes[key]["veredito"]
        ja_resolvido.append((i, hv, v))
        if v in ("mesmo", "diferente") and v != hv:
            conflitos.append((i, a, b, "humano=" + hv, "foto=" + v))
        continue
    if v in ("mesmo", "diferente"):
        validacoes.append({"a": a, "b": b, "veredito": v})
    else:
        incertos_novos[k] = HOJE

print(f"candidatos: {len(cand)} | inbox(certos): {len(validacoes)} "
      f"| incertos: {len(incertos_novos)} | ja resolvidos: {len(ja_resolvido)}")
if ja_resolvido:
    print("ja resolvidos (idx, humano, foto):", ja_resolvido)
if conflitos:
    print("CONFLITOS (humano vence, foto ignorada):")
    for c in conflitos:
        print("  ", c)

if MODE == "write":
    os.makedirs("data/validacoes_inbox", exist_ok=True)
    with open("data/validacoes_inbox/auto_2026-08-17.json.tmp", "w", encoding="utf-8") as fh:
        json.dump({"validacoes": validacoes}, fh, ensure_ascii=False, indent=1)
    os.replace("data/validacoes_inbox/auto_2026-08-17.json.tmp",
               "data/validacoes_inbox/auto_2026-08-17.json")
    inc = {}
    if os.path.exists("data/similaridade_incertos.json"):
        inc = json.load(open("data/similaridade_incertos.json"))
    antes = len(inc)
    inc.update(incertos_novos)
    with open("data/similaridade_incertos.json.tmp", "w", encoding="utf-8") as fh:
        json.dump(inc, fh, ensure_ascii=False, indent=1)
    os.replace("data/similaridade_incertos.json.tmp", "data/similaridade_incertos.json")
    print(f"GRAVADO: inbox {len(validacoes)} validacoes; incertos {antes} -> {len(inc)}")
