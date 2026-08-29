#!/usr/bin/env python3
"""Constroi _new_data_20260829.json a partir dos extracts data/_extract/w0829_*.json.

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
HOJE = "2026-08-29"

NOISE = {"lata", "lta", "pct", "pcte", "pacote", "pet", "tb", "gf", "cada", "un",
         "und", "unid", "unidade", "sabores", "sabor", "fragrancias",
         "fragrancia", "tipos", "tipo", "kg"}

# Ordem deliberada: dentro de cada conjunto banner+periodo, o post mais
# completo entra primeiro para servir de referencia aos demais.
ORDEM = [
    "Dcio1BSm_4j",         # MV horti 27-28 (postado 27)
    "DclNqdpgI-T",         # MV horti 27-28 (postado 28)
    "Dcj7EyAmXsE",         # MV 28/08-03/09 flyer 55p — referencia
    "DcnkmFwjbty",         # MV 28/08-03/09 cards (dedup vs flyer)
    "Dclv3yTGZqr",         # MV 28/08-03/09 (descartado pelo extrator)
    "DcmgFJvmXeZ",         # MV fim de mes 29-31
    "DckFspjjtIZ",         # MV molhos 27-31
    "DcjpwyHAVYO",         # SuperFacil aniversario 28-31
    "DchCc7glbGU",         # Leva Mais JC Fecha Mes 27/08-02/09
    "Dci2ovkyiYB",         # Leva Mais JC Credito ELO 27/08-02/09
    "Dcllc5JgG1S",         # Leva Mais JC acougue 28-30
    "DcgEmudsbAQ",         # Leva Mais JC horti 26-27
    "DclNIdUlc90",         # Miramar Liquida Natal (descartado pelo extrator)
    "DcmDD8ATPAC",         # Favorito Pantene (postado 28) — referencia
    "Dcnl72jFvUv",         # Favorito Pantene repost (dedup vs anterior)
    "atacadao_ab174b8886",  # Atacadao web Boa do Dia 29
    "atacadao_529ee8d455",  # Atacadao web Fim de Mes 28-31
    "nosso_cd8b045379",    # Nosso web Final de Semana 28-30
]

DESCARTES_TRIAGEM = {
    "DcjffKvm7WW": "no-price (institucional alerta de golpe no WhatsApp)",
    "DcgXGj3FnXK": "b2b (Especial Food Service)",
    "DcmHNbbTrkR": "no-price (cupom de inscricao corrida Circuito Mira)",
}


def nrm_tokens(s: str) -> tuple:
    """Normaliza um nome em tokens ordenados sem ruido de embalagem."""
    s = unicodedata.normalize("NFD", str(s).lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    return tuple(sorted(t for t in s.split() if t and t not in NOISE))


def main() -> None:
    """Monta _new_data_20260829.json com dedup por conteudo."""
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
        fp = os.path.join(BASE, "data/_extract", f"w0829_{sc}.json")
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

        itens = []
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
    with open(os.path.join(BASE, "_new_data_20260829.json"), "w", encoding="utf-8") as f:
        json.dump(novo, f, ensure_ascii=False, indent=1)

    print("\n".join(resumo))
    n_prod = sum(len(v) for v in out_products.values())
    print(f"\n_new_data_20260829.json: {len(out_actions)} acoes, {n_prod} produtos, "
          f"{len(descartes)} descartes")


if __name__ == "__main__":
    main()
