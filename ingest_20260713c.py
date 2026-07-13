#!/usr/bin/env python3
"""Ingestão 13/07/2026 — LOTE C: janela noturna (feed + stories).

Consome os resultados de extração por visão (scratchpad/results/*.json),
monta ações/produtos/canon com a MESMA canonicalização do pipeline
(nrm_tokens/canon_add), esvazia a fila e grava o resumo da notificação.
"""
import glob
import json
import os
import re
import shutil
import sys
import unicodedata

BASE = os.path.dirname(os.path.abspath(__file__))
def path(*p: str) -> str:
    return os.path.join(BASE, *p)


HOJE = "2026-07-13"
RESULTS_DIR = sys.argv[1]

NOISE = {"lata", "lta", "pct", "pcte", "pacote", "pet", "tb", "gf", "cada", "un",
         "und", "unid", "unidade", "sabores", "sabor", "fragrancias",
         "fragrancia", "tipos", "tipo"}


def nrm_tokens(s: str) -> tuple:
    """Normaliza um nome de produto em um conjunto ordenado de tokens."""
    s = unicodedata.normalize("NFD", str(s).lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    return tuple(sorted(t for t in s.split() if t and t not in NOISE))


actions = json.load(open(path("data/actions.json"), encoding="utf-8"))
products = json.load(open(path("data/products.json"), encoding="utf-8"))
canon = json.load(open(path("data/canon.json"), encoding="utf-8"))
fila = json.load(open(path("data/fila_novos.json"), encoding="utf-8"))
byshort = {p["shortcode"]: p for p in fila}

for f in ("data/actions.json", "data/products.json", "data/canon.json"):
    shutil.copy(path(f), path(f + ".bak-20260713c-ingest"))

by_key: dict = {}
for g in canon:
    k = nrm_tokens(g["n"])
    if k not in by_key or len(g["m"]) > len(by_key[k]["m"]):
        by_key[k] = g

log = {"novos": 0, "merges": 0}


def canon_add(name: str, unit: str, ref: str) -> None:
    """Encaixa uma referência no grupo canônico existente ou cria um novo."""
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


def norm_products(items: list, is_arr: bool) -> list:
    """Converte itens (obj ou array) para o formato padrão e descarta sem preço."""
    out = []
    for it in items:
        if is_arr:
            name, price, size = it[0], it[1], it[2]
            x, y, w, h = it[3], it[4], it[5], it[6]
            if str(size).strip().lower() in ("kg",):
                n, u = name, "kg"
            else:
                n = f"{name} {size}".strip()
                u = "un"
            obj = {"n": n, "p": price, "u": u, "x": x, "y": y, "w": w, "h": h}
        else:
            obj = dict(it)
        if not str(obj.get("p", "")).strip():
            continue
        out.append(obj)
    return out


existing_ids = {a["id"] for a in actions}
kept, total_prod = [], 0
banners_novos: dict = {}

for arq in sorted(glob.glob(os.path.join(RESULTS_DIR, "*.json"))):
    doc = json.load(open(arq, encoding="utf-8"))
    if "posts" in doc:
        posts = doc["posts"]
        is_arr_default = doc.get("fmt") == "arr"
    else:
        posts = [doc]
        is_arr_default = doc.get("fmt") == "arr"
    for post in posts:
        if post.get("decision") != "keep":
            continue
        sc = post["shortcode"]
        if sc in existing_ids:
            print(f"[skip] ação {sc} já existe")
            continue
        is_arr = post.get("fmt", is_arr_default and "arr") == "arr"
        pages = post.get("pages", {})
        paginas = []
        for key, items in pages.items():
            norm = norm_products(items, is_arr)
            if not norm:
                continue
            if key in products:
                print(f"[skip] página {key} já em products.json")
                continue
            products[key] = norm
            paginas.append(key + ".jpg")
            total_prod += len(norm)
            for idx, it in enumerate(norm):
                canon_add(it["n"], it.get("u", "un"), f"{key}#{idx}")
        if not paginas:
            print(f"[skip] {sc} sem páginas com produto")
            continue
        src = byshort.get(sc, {})
        fonte = post.get("fonte") or src.get("fonte") or "feed"
        actions.append({
            "id": sc,
            "perfil": post.get("perfil", src.get("perfil", "")),
            "titulo": post.get("titulo", ""),
            "banner": post["banner"],
            "segmento": post.get("segmento", src.get("segmento", "")),
            "inicio": post["inicio"],
            "fim": post["fim"],
            "carrossel": len(paginas) > 1,
            "shortcode": sc,
            "caption": src.get("caption", ""),
            "paginas": paginas,
            "adicionado_em": HOJE,
            "fonte": fonte,
            "link": post.get("link", src.get("link", "")),
        })
        existing_ids.add(sc)
        kept.append(sc)
        banners_novos.setdefault(post["banner"], 0)
        banners_novos[post["banner"]] += 1

# esvazia toda a fila processada nesta janela (todos os 33 posts)
fila_rest: list = []

json.dump(actions, open(path("data/actions.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
json.dump(products, open(path("data/products.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
json.dump(canon, open(path("data/canon.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
json.dump(fila_rest, open(path("data/fila_novos.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

print("OK — ações novas:", len(kept), "| produtos:", total_prod,
      "| canon:", len(canon), f"({log['novos']} novos, {log['merges']} encaixes)")
print("Banners:", banners_novos)
