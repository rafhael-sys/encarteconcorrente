#!/usr/bin/env python3
"""Agrega os lotes de similaridade w0829_sim_*.json.

Gera data/validacoes_inbox/auto_2026-08-29.json (pares com certeza total) e
acrescenta os incertos a data/similaridade_incertos.json (chave k -> data),
para nao serem reavaliados.
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
HOJE = "2026-08-29"
LOTES = ["w0829_sim_00_12.json", "w0829_sim_13_25.json", "w0829_sim_26_38.json",
         "w0829_sim_39_51.json", "w0829_sim_52_64.json"]


def main() -> None:
    """Junta vereditos dos lotes e grava inbox + incertos."""
    validacoes = []
    incertos_novos = []
    vistos_k = set()
    for nome in LOTES:
        fp = os.path.join(BASE, "data/_extract", nome)
        if not os.path.exists(fp):
            print(f"[FALTA] {fp}")
            continue
        lote = json.load(open(fp, encoding="utf-8"))
        for c in lote.get("certos", []):
            v = c.get("veredito")
            if v not in ("mesmo", "diferente") or c.get("k") in vistos_k:
                continue
            vistos_k.add(c.get("k"))
            validacoes.append({"a": c["a"], "b": c["b"], "veredito": v})
        for i in lote.get("incertos", []):
            if i.get("k") and i["k"] not in vistos_k:
                vistos_k.add(i["k"])
                incertos_novos.append(i["k"])

    inbox_dir = os.path.join(BASE, "data/validacoes_inbox")
    os.makedirs(inbox_dir, exist_ok=True)
    out_inbox = os.path.join(inbox_dir, f"auto_{HOJE}.json")
    with open(out_inbox, "w", encoding="utf-8") as f:
        json.dump({"validacoes": validacoes}, f, ensure_ascii=False, indent=1)

    inc_path = os.path.join(BASE, "data/similaridade_incertos.json")
    incertos = {}
    if os.path.exists(inc_path):
        incertos = json.load(open(inc_path, encoding="utf-8"))
    for k in incertos_novos:
        incertos.setdefault(k, HOJE)
    tmp = f"{inc_path}.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(incertos, f, ensure_ascii=False, indent=1)
    os.replace(tmp, inc_path)

    n_m = sum(1 for v in validacoes if v["veredito"] == "mesmo")
    n_d = sum(1 for v in validacoes if v["veredito"] == "diferente")
    print(f"inbox: {len(validacoes)} validacoes ({n_m} mesmo, {n_d} diferente) "
          f"-> {out_inbox}")
    print(f"incertos: +{len(incertos_novos)} novos (total {len(incertos)})")


if __name__ == "__main__":
    main()
