#!/usr/bin/env python3
"""Constroi _new_data_20260826.json a partir dos extracts data/_extract/w0826_*.json.

Aplica a dedup POR CONTEUDO (memoria mv-favorito-feed-subset-flyer-descartar):
uma acao nova e descartada somente se TODOS os seus produtos ja existirem
(mesmo nome normalizado + mesmo preco) em acoes do MESMO banner e MESMO
periodo (inicio/fim identicos) — considerando as ja gravadas em actions.json
e as aceitas antes dela nesta mesma janela. Caso contrario, entra inteira.
"""
import json
import os
import re
import unicodedata

BASE = os.path.dirname(os.path.abspath(__file__))
HOJE = "2026-08-26"

NOISE = {"lata", "lta", "pct", "pcte", "pacote", "pet", "tb", "gf", "cada", "un",
         "und", "unid", "unidade", "sabores", "sabor", "fragrancias",
         "fragrancia", "tipos", "tipo", "kg"}

# Ordem deliberada: dentro de cada conjunto banner+periodo, o post mais
# completo entra primeiro para servir de referencia aos demais.
ORDEM = [
    "Dcer4JtmkZc",        # Corte Facil 26-27
    "DcexImUiR5Z",        # Rede Mais 26-27
    "DceqP_AD7K_",        # Super Show encarte 26-30
    "DcexMkQD_T-",        # Super Show feirao 26-27
    "Dceorq6PTmZ",        # Super Show oferta do dia 26
    "Dcejr8koAaM",        # Santo Antonio 26-27
    "Dce_ap2DZ_4",        # MV 25-26 (10p) — referencia do conjunto
    "DcdoOjznOfd",        # MV 25-26 (9p)
    "Dcf2NUmGjba",        # MV 21-27 A
    "Dce4amSjTVJ",        # MV 21-27 B
    "Dcdsribkffa",        # MV 21-27 C
    "DcexXAaGWOy",        # MV padaria 26
    "DcfF83bjdr6",        # MV molhos 26-31
    "Dcf4AGjGfHi",        # Favorito QQVerde 26-27 A
    "DcezCgAzRe9",        # Favorito QQVerde 26-27 B
    "Dce0nvomi3K",        # Favorito Parnamirim/Macaiba 26/08-01/09
    "Dce0l1xGoOG",        # Favorito Varejo PN/AS 26/08-01/09
    "DcdpYpLnGIz",        # Favorito Varejo 19-25 (dedup vs existentes)
    "assai_170410-572",   # Assai web 26-27
    "atacadao_26a3b9e7c8",  # Atacadao web 26
]

DESCARTES_TRIAGEM = {
    "DcedmaxMZ-y": "no-price (teaser Corta Preco)",
    "Dcd9nGYDtM4": "no-price (arte de comentarios aniversario)",
    "DceJYRcOezL": "no-price (institucional Dia do Feirante)",
    "DcelGoEGfei": "no-price (teaser Fecha Mes Supercop)",
    "Dcdo7aXnLUh": "no-price (institucional Dia do Feirante MV)",
    "DcdtIuWmJxy": "no-price (teaser Faltam 2 Dias MV)",
    "Dcf0Qlfm5Lf": "no-price (teaser aniversario Queiroz)",
    "DceNGwOm5jl": "no-price (teaser recorrente QQVerde, hash igual a 3 posts antigos)",
    "DcfEWNEj1Zn": "no-price (arte recorrente Molhos, hash igual a DbHadmtm6ZV)",
    "DceOH5bmvJk": "b2b (Alo Comerciante / televendas)",
}


def nrm_tokens(s: str) -> tuple:
    """Normaliza um nome em tokens ordenados sem ruido de embalagem."""
    s = unicodedata.normalize("NFD", str(s).lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    return tuple(sorted(t for t in s.split() if t and t not in NOISE))


def main() -> None:
    """Monta _new_data_20260826.json com dedup por conteudo."""
    actions = json.load(open(os.path.join(BASE, "data/actions.json"), encoding="utf-8"))
    products = json.load(open(os.path.join(BASE, "data/products.json"), encoding="utf-8"))
    fila = json.load(open(os.path.join(BASE, "data/fila_novos.json"), encoding="utf-8"))
    byshort = {p["shortcode"]: p for p in fila}

    # indice (banner, inicio, fim) -> conjunto de (tokens, preco) ja capturados
    grupo: dict = {}
    for a in actions:
        key = (a["banner"], a.get("inicio"), a.get("fim"))
        s = grupo.setdefault(key, set())
        for pg in a.get("paginas", []):
            pid = pg[:-4] if pg.endswith(".jpg") else pg
            for it in products.get(pid, []):
                s.add((nrm_tokens(it["n"]), str(it.get("p", ""))))

    out_actions = []
    out_products: dict = {}
    descartes = dict(DESCARTES_TRIAGEM)
    resumo = []

    for sc in ORDEM:
        fp = os.path.join(BASE, "data/_extract", f"w0826_{sc}.json")
        if not os.path.exists(fp):
            print(f"[FALTA] extract ausente: {fp}")
            continue
        ext = json.load(open(fp, encoding="utf-8"))
        if ext.get("discard"):
            descartes[sc] = ext.get("discard_reason", "descartado pelo extrator")
            resumo.append(f"[descarte-extrator] {sc}: {descartes[sc]}")
            continue
        src = byshort.get(sc, {})
        banner = src.get("banner", "")
        inicio = src.get("inicio") or ext.get("inicio")
        fim = src.get("fim") or ext.get("fim")
        key = (banner, inicio, fim)
        vistos = grupo.setdefault(key, set())

        itens = []           # (pid_novo, item)
        novos = 0
        total = 0
        for pid, lista in ext.get("pages", {}).items():
            for it in lista:
                total += 1
                assin = (nrm_tokens(it["n"]), str(it.get("p", "")))
                if assin not in vistos:
                    novos += 1
                itens.append(assin)
        if total > 0 and novos == 0:
            descartes[sc] = (f"dedup-conteudo: 0 produto novo vs acoes {banner} "
                             f"{inicio}..{fim}")
            resumo.append(f"[descarte-dedup] {sc}: {total} produtos, todos ja capturados")
            continue
        if total == 0:
            descartes[sc] = "no-price (extrator nao achou produto com preco)"
            resumo.append(f"[descarte-vazio] {sc}")
            continue

        for assin in itens:
            vistos.add(assin)
        spec = {
            "id": sc,
            "titulo": ext.get("titulo") or src.get("caption", "")[:60],
            "banner": banner,
            "segmento": src.get("segmento", ""),
            "inicio": inicio,
            "fim": fim,
        }
        if src.get("fonte"):
            spec["fonte"] = src["fonte"]
        if src.get("link"):
            spec["link"] = src["link"]
        out_actions.append(spec)
        for pid, lista in ext.get("pages", {}).items():
            out_products[pid] = lista
        resumo.append(f"[ok] {sc}: {total} produtos ({novos} ineditos no periodo) "
                      f"{inicio}..{fim} — {spec['titulo']}")

    novo = {"actions": out_actions, "products": out_products, "descartes": descartes}
    with open(os.path.join(BASE, "_new_data_20260826.json"), "w", encoding="utf-8") as f:
        json.dump(novo, f, ensure_ascii=False, indent=1)

    print("\n".join(resumo))
    n_prod = sum(len(v) for v in out_products.values())
    print(f"\n_new_data_20260826.json: {len(out_actions)} acoes, {n_prod} produtos, "
          f"{len(descartes)} descartes")


if __name__ == "__main__":
    main()
