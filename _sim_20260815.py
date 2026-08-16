#!/usr/bin/env python3
"""Gera validacoes_inbox/auto_2026-08-15.json (pares CERTOS) e mescla os
pares INCERTOS em similaridade_incertos.json. Vereditos por indice vieram da
analise visual (subagentes) desta janela. a/b/k saem do proprio candidatos.
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")
HOJE = "2026-08-15"

VERDICTS = {
    0: "diferente", 1: "diferente", 2: "mesmo", 3: "mesmo", 4: "diferente",
    5: "incerto", 6: "mesmo", 7: "mesmo", 8: "mesmo", 9: "incerto",
    10: "diferente", 11: "mesmo", 12: "diferente", 13: "mesmo", 14: "mesmo",
    15: "mesmo", 16: "diferente", 17: "mesmo", 18: "diferente", 19: "diferente",
    20: "diferente", 21: "diferente", 22: "incerto", 23: "diferente", 24: "incerto",
    25: "incerto", 26: "mesmo", 27: "incerto", 28: "mesmo", 29: "mesmo",
    30: "mesmo", 31: "incerto", 32: "diferente", 33: "diferente", 34: "incerto",
    35: "diferente", 36: "diferente", 37: "mesmo", 38: "mesmo", 39: "incerto",
    40: "diferente", 41: "mesmo", 42: "mesmo", 43: "mesmo", 44: "mesmo",
    45: "mesmo", 46: "mesmo", 47: "diferente", 48: "mesmo", 49: "diferente",
    50: "diferente", 51: "incerto", 52: "incerto", 53: "diferente", 54: "diferente",
    55: "incerto", 56: "mesmo", 57: "diferente", 58: "diferente", 59: "mesmo",
    60: "mesmo", 61: "diferente", 62: "incerto", 63: "diferente", 64: "mesmo",
}


def salva(p, data):
    tmp = f"{p}.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    os.replace(tmp, p)


def main():
    cand = json.load(open(os.path.join(DATA, "similaridade_candidatos.json"), encoding="utf-8"))
    assert len(cand) == len(VERDICTS), (len(cand), len(VERDICTS))
    incertos = json.load(open(os.path.join(DATA, "similaridade_incertos.json"), encoding="utf-8"))

    validacoes = []
    n_inc = 0
    for i, par in enumerate(cand):
        v = VERDICTS[i]
        if v in ("mesmo", "diferente"):
            validacoes.append({"a": par["a"], "b": par["b"], "veredito": v})
        else:
            incertos[par["k"]] = HOJE
            n_inc += 1

    os.makedirs(os.path.join(DATA, "validacoes_inbox"), exist_ok=True)
    salva(os.path.join(DATA, "validacoes_inbox", f"auto_{HOJE}.json"),
          {"validacoes": validacoes})
    salva(os.path.join(DATA, "similaridade_incertos.json"), incertos)
    print(f"inbox: {len(validacoes)} pares certos "
          f"({sum(1 for x in validacoes if x['veredito']=='mesmo')} mesmo, "
          f"{sum(1 for x in validacoes if x['veredito']=='diferente')} diferente); "
          f"{n_inc} incertos mesclados (incertos total={len(incertos)})")


if __name__ == "__main__":
    main()
