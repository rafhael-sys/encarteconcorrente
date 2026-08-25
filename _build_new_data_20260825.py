#!/usr/bin/env python3
"""Monta _new_data_20260825.json a partir dos extracts w0825_* desta janela."""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
FILES = ["w0825_DccKp1lFs6R.json", "w0825_Dcb-bnuIKl9.json", "w0825_DcbLfHnnPcz.json",
         "w0825_assai.json", "w0825_atacadao.json"]

DESCARTES = [
    {"id": "DcdL-7XFqk5", "motivo": "Nordestão Oferta Surpresa do app: produto borrado, sem preço (regra fixa)"},
    {"id": "DcbBhMhT2lL", "motivo": "Favorito Terça do Cashback: teaser institucional sem produto/preço"},
    {"id": "Dcbutrbk0Os", "motivo": "Queiroz JC Dia Q: teaser sem preço (27-28/08)"},
    {"id": "Dcbuf42FEiJ", "motivo": "Queiroz Natal Dia Q: teaser sem preço (27-28/08)"},
    {"id": "DcbNFRaFWDl", "motivo": "Leva Mais Macau: ofertas do televendas (Telemais) — B2B/televendas"},
    {"id": "DcbNmR-Fs15", "motivo": "Leva Mais JC: ofertas do televendas (Telemais) — B2B/televendas"},
    {"id": "DcbGtPFFpLp", "motivo": "SuperFácil Vale do Sol: arte institucional (checklist), sem produto/preço"},
    {"id": "DcbGsAgFmRg", "motivo": "SuperFácil Atacado: arte institucional (checklist), sem produto/preço"},
]


def main() -> None:
    """Une os extracts em um único _new_data com actions, products e descartes."""
    actions, products = [], {}
    for fname in FILES:
        with open(os.path.join(BASE, "data", "_extract", fname), encoding="utf-8") as f:
            d = json.load(f)
        blocos = d["acoes"] if "acoes" in d else [d]
        for b in blocos:
            a = dict(b["action"])
            pags = sorted(b["products"].keys(), key=lambda s: int(s.rsplit("_p", 1)[1]))
            a["paginas"] = [p + ".jpg" for p in pags]
            actions.append(a)
            for pid, lst in b["products"].items():
                products[pid] = lst

    out = {"actions": actions, "products": products, "descartes": DESCARTES}
    dest = os.path.join(BASE, "_new_data_20260825.json")
    with open(dest, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)

    n_prod = sum(len(v) for v in products.values())
    print(f"{len(actions)} acoes, {len(products)} paginas, {n_prod} produtos, "
          f"{len(DESCARTES)} descartes")
    for a in actions:
        print(" ", a["id"], "|", a["banner"], "|", a["inicio"], "->", a["fim"], "|",
              len(a["paginas"]), "pags")


if __name__ == "__main__":
    main()
