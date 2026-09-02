#!/usr/bin/env python3
"""Consolida os vereditos de similaridade da janela 2026-09-02.

- simres_*.json -> validacoes_inbox/auto_2026-09-02.json (mesmo/diferente)
- pares com dúvida (incerto) ou rebaixados -> similaridade_incertos.json
- pares de "oferta dupla" (A ou B vs A) rebaixados para incerto por cautela.
"""
import json
import os
from collections import Counter

HOJE = "2026-09-02"

DOWNGRADE = {
    "oleo de soja concordia 900ml || oleo de soja concordia/liza 900ml",
    "linguica de churrasco ou frango aurora || linguica p/ churrasco de frango aurora",
}


def main() -> None:
    """Gera o inbox de validações e atualiza os incertos."""
    cands = json.load(open("data/similaridade_candidatos.json"))
    por_k = {c["k"]: c for c in cands}

    vals: list[dict] = []
    incertos_novos: dict[str, str] = {}
    vistos: set[str] = set()

    for f in sorted(os.listdir("data/_extract/w0902")):
        if not f.startswith("simres_"):
            continue
        d = json.load(open(f"data/_extract/w0902/{f}"))
        for r in d["resultados"]:
            k = r["k"]
            if k not in por_k:
                print(f"[aviso] k desconhecido: {k[:80]}")
                continue
            if k in vistos:
                continue
            vistos.add(k)
            v = "incerto" if k in DOWNGRADE else r["veredito"]
            c = por_k[k]
            if v in ("mesmo", "diferente"):
                vals.append({"a": c["a"], "b": c["b"], "veredito": v})
            else:
                incertos_novos[k] = HOJE

    faltantes = set(por_k) - vistos
    for k in faltantes:
        incertos_novos[k] = HOJE
    print(f"validacoes: {len(vals)} | incertos novos: {len(incertos_novos)} | "
          f"sem veredito: {len(faltantes)}")

    os.makedirs("data/validacoes_inbox", exist_ok=True)
    with open(f"data/validacoes_inbox/auto_{HOJE}.json", "w") as f:
        json.dump({"validacoes": vals}, f, ensure_ascii=False, indent=1)

    inc = json.load(open("data/similaridade_incertos.json"))
    inc.update(incertos_novos)
    with open("data/similaridade_incertos.json", "w") as f:
        json.dump(inc, f, ensure_ascii=False, indent=1)
    print(f"incertos total: {len(inc)}")
    print(Counter(v["veredito"] for v in vals))


if __name__ == "__main__":
    main()
