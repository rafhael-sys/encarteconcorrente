#!/usr/bin/env python3
"""Sanidade dos extratos da janela 2026-09-01 antes do merge."""
import json
import os
import re
import unicodedata

EXTRACT_DIR = "data/_extract/w0901"
APROVADOS = [
    "DcriSVWj4E7", "DcuHEEEjwZ3", "Dcme_Z9oExB", "DchVYErkj0q", "DchUObMFh_Z",
    "DcrpGk-DHcf", "Dcj6tF0DFu4", "DcgFBmZyiMg", "DchWYETIFog", "DcrzdcCoFfE",
    "DcmaaO7Gsqe", "DchGt8zEk2h", "DchDGXIErij", "DcmanVTH2KW", "DchDJhvnxZQ",
    "assai_170665-572", "assai_170679-572", "assai_170719-572",
    "atacadao_0b70eb111e", "atacadao_0e7895a02b", "atacadao_aba86d1eb4",
    "atacadao_53752fa680",
]
PRECO_RE = re.compile(r"^\d{1,4},\d{2}$")


def nrm(s: str) -> str:
    """Minúsculas, sem acento."""
    s = unicodedata.normalize("NFD", str(s).lower())
    return " ".join("".join(c for c in s if unicodedata.category(c) != "Mn").split())


def main() -> None:
    """Valida formato dos extratos e mede sobreposição do teaser descartado."""
    fila = json.load(open("data/fila_novos.json"))
    por_sc = {p["shortcode"]: p for p in fila}
    total = 0
    problemas = 0
    for sc in APROVADOS:
        path = os.path.join(EXTRACT_DIR, f"{sc}.json")
        if not os.path.exists(path):
            print(f"[FALTA] {path}")
            problemas += 1
            continue
        e = json.load(open(path))
        post = por_sc[sc]
        esperadas = {p.rsplit(".", 1)[0] for p in post["paginas"]}
        tem = set(e.get("paginas", {}).keys())
        if esperadas - tem:
            print(f"[{sc}] páginas faltando no extract: {sorted(esperadas - tem)}")
            problemas += 1
        n = 0
        for pg, itens in e.get("paginas", {}).items():
            for it in itens:
                n += 1
                if not PRECO_RE.match(str(it.get("p", ""))):
                    print(f"[{sc}/{pg}] preço estranho: {it.get('n')!r} -> {it.get('p')!r}")
                    problemas += 1
                for campo in ("x", "y", "w", "h"):
                    v = it.get(campo)
                    if not isinstance(v, (int, float)) or v < 0 or v > 100:
                        print(f"[{sc}/{pg}] bbox estranha em {it.get('n')!r}: {campo}={v!r}")
                        problemas += 1
        total += n
        print(f"[ok] {sc}: {n} produtos")

    # sobreposição teaser Dcg0OQ-IDtC vs encarte DchWYETIFog (mesmo período)
    teaser = json.load(open(os.path.join(EXTRACT_DIR, "Dcg0OQ-IDtC.json")))
    flyer = json.load(open(os.path.join(EXTRACT_DIR, "DchWYETIFog.json")))
    nomes_flyer = {nrm(i["n"]) for pg in flyer["paginas"].values() for i in pg}
    precos_flyer = {(nrm(i["n"]), i["p"]) for pg in flyer["paginas"].values() for i in pg}
    dentro = fora = 0
    for pg in teaser["paginas"].values():
        for i in pg:
            if nrm(i["n"]) in nomes_flyer or (nrm(i["n"]), i["p"]) in precos_flyer:
                dentro += 1
            else:
                fora += 1
                print(f"[teaser fora do encarte] {i['n']} {i['p']}")
    print(f"\nteaser Dcg0OQ-IDtC: {dentro} itens já no encarte, {fora} fora")
    print(f"\nTOTAL produtos aprovados: {total} | problemas: {problemas}")


if __name__ == "__main__":
    main()
