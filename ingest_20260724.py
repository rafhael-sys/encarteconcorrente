#!/usr/bin/env python3
"""Ingestão 24/07/2026 — janela diária (feed + web).

Consome scratchpad/results/*.json (extração por visão) e monta ações/produtos/
canon com a MESMA canonicalização do pipeline (nrm_tokens/canon_add).
Descartes e duplicatas simplesmente não entram (não têm arquivo em results).
"""
import glob
import json
import os
import re
import shutil
import unicodedata

BASE = os.path.dirname(os.path.abspath(__file__))


def path(*p: str) -> str:
    """Monta caminho absoluto a partir da raiz do projeto."""
    return os.path.join(BASE, *p)


HOJE = "2026-07-24"
RESULTS_DIR = path("scratchpad/results")

NOISE = {"lata", "lta", "pct", "pcte", "pacote", "pet", "tb", "gf", "cada", "un",
         "und", "unid", "unidade", "sabores", "sabor", "fragrancias",
         "fragrancia", "tipos", "tipo"}

TITULOS = {
    "DbLZADgnFd7": "Favoritaço Varejo Ponta Negra/Ayrton Senna (22 a 28/07)",
    "DbMYQHYm-2W": "Churrasco Fim de Semana Mar Vermelho (25 a 27/07)",
    "DbLoDwGm6-q": "Grandes Ofertas MarZap Mar Vermelho (24 a 30/07)",
    "DbLF2M6m1JI": "Feirão Hortifruti Mar Vermelho (23 e 24/07)",
    "DbLI4hFlYyU": "Encarte Novo Leva Mais Macau (23/07 a 03/08)",
    "DbLJHpcFQfr": "Mega Oferta Leva Mais Macau (24 a 26/07)",
    "DbK5ZcKsN9K": "Ofertas Bom Todo Corte Fácil (24 a 26/07)",
    "assai_168485-572": "Encarte Fim de Semana Assaí Natal (24 a 26/07)",
    "atacadao_a64652d191": "Fim de Semana Atacadão Natal Sul (24 a 27/07)",
    "nosso_2e4ea67427": "Nosso Final de Semana (24 a 26/07)",
}


def nrm_tokens(s: str) -> tuple:
    """Normaliza nome para tokens ordenados sem acento/ruído de embalagem."""
    s = unicodedata.normalize("NFD", str(s).lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    return tuple(sorted(t for t in s.split() if t and t not in NOISE))


def norm_preco(p: str) -> str:
    """Remove prefixo R$ e usa vírgula como separador decimal."""
    t = str(p or "").strip()
    t = re.sub(r"^r\$\s*", "", t, flags=re.I).strip()
    if re.fullmatch(r"\d+\.\d{2}", t):
        t = t.replace(".", ",")
    return t


actions = json.load(open(path("data/actions.json"), encoding="utf-8"))
products = json.load(open(path("data/products.json"), encoding="utf-8"))
canon = json.load(open(path("data/canon.json"), encoding="utf-8"))
fila = json.load(open(path("data/fila_novos.json"), encoding="utf-8"))
byshort = {p["shortcode"]: p for p in fila}

for f in ("data/actions.json", "data/products.json", "data/canon.json"):
    shutil.copy(path(f), path(f + ".bak-20260724-ingest"))

by_key: dict = {}
for g in canon:
    k = nrm_tokens(g["n"])
    if k not in by_key or len(g["m"]) > len(by_key[k]["m"]):
        by_key[k] = g

log = {"novos": 0, "merges": 0}


def canon_add(name: str, unit: str, ref: str) -> None:
    """Encaixa a ocorrência num grupo canônico existente ou cria um novo."""
    k = nrm_tokens(name)
    g = by_key.get(k)
    if g is None:
        g = {"n": name, "u": unit, "m": [ref]}
        canon.append(g)
        by_key[k] = g
        log["novos"] += 1
    else:
        if ref not in g["m"]:
            g["m"].append(ref)
        log["merges"] += 1


existing_ids = {a["id"] for a in actions}
kept, total_prod = [], 0
banners_novos: dict = {}

for arq in sorted(glob.glob(os.path.join(RESULTS_DIR, "*.json"))):
    doc = json.load(open(arq, encoding="utf-8"))
    if doc.get("decision") != "keep":
        continue
    sc = doc["shortcode"]
    if sc in existing_ids:
        print(f"[skip] ação {sc} já existe")
        continue
    src = byshort.get(sc, {})
    pages_res = doc.get("pages", {}) or {}
    ordem = [p.replace(".jpg", "") for p in src.get("paginas", [])]
    chaves = [k for k in ordem if k in pages_res] or list(pages_res.keys())

    paginas = []
    for key in chaves:
        itens = []
        for it in pages_res[key]:
            p = norm_preco(it.get("p"))
            if not p:
                continue
            itens.append({"n": it["n"], "p": p, "u": it.get("u", "un"),
                          "x": it["x"], "y": it["y"], "w": it["w"], "h": it["h"]})
        if not itens:
            continue
        if key in products:
            print(f"[skip] página {key} já em products.json")
            continue
        products[key] = itens
        paginas.append(key + ".jpg")
        total_prod += len(itens)
        for idx, it in enumerate(itens):
            canon_add(it["n"], it.get("u", "un"), f"{key}#{idx}")
    if not paginas:
        print(f"[skip] {sc} sem páginas com produto")
        continue

    banner = src.get("banner", "")
    fonte = src.get("fonte") or "feed"
    actions.append({
        "id": sc,
        "perfil": src.get("perfil", ""),
        "titulo": TITULOS.get(sc, ""),
        "banner": banner,
        "segmento": src.get("segmento", ""),
        "inicio": doc["inicio"],
        "fim": doc["fim"],
        "carrossel": len(paginas) > 1,
        "shortcode": sc,
        "caption": src.get("caption", ""),
        "paginas": paginas,
        "adicionado_em": HOJE,
        "fonte": fonte,
        "link": src.get("link", ""),
    })
    existing_ids.add(sc)
    kept.append(sc)
    banners_novos[banner] = banners_novos.get(banner, 0) + 1

json.dump(actions, open(path("data/actions.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
json.dump(products, open(path("data/products.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
json.dump(canon, open(path("data/canon.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

print("OK — ações novas:", len(kept), "| produtos:", total_prod,
      "| canon:", len(canon), f"({log['novos']} novos, {log['merges']} encaixes)")
print("Banners:", banners_novos)
print("IDs:", kept)
