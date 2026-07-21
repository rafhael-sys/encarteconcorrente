#!/usr/bin/env python3
"""Ingestão 20/07/2026 — janela noturna (feed + story Miramar).

Consome os resultados de extração por visão (scratchpad/results/*.json),
monta ações/produtos/canon com a MESMA canonicalização do pipeline
(nrm_tokens/canon_add). Descartes e duplicatas simplesmente não entram.
"""
import glob
import json
import os
import re
import shutil
import unicodedata

BASE = os.path.dirname(os.path.abspath(__file__))


def path(*p: str) -> str:
    return os.path.join(BASE, *p)


HOJE = "2026-07-20"
RESULTS_DIR = path("scratchpad/results")

NOISE = {"lata", "lta", "pct", "pcte", "pacote", "pet", "tb", "gf", "cada", "un",
         "und", "unid", "unidade", "sabores", "sabor", "fragrancias",
         "fragrancia", "tipos", "tipo"}

# título humano curto por ação (mesmo estilo das ações existentes)
TITULOS = {
    "DbCLX_Sih7U": "Mais Pet RedeMAIS (21 a 26/07)",
    "DbCEgdfj_vF": "Encarte RedeMAIS (21 a 28/07)",
    "DbB9tWHj8M1": "Ofertas Estouradas Super Show (21 a 27/07)",
    "DbCFGcJG65o": "Grandes Ofertas MarZap (21 e 22/07)",
    "DbCC1H3lmYN": "Terça da Carne Supercop (21/07)",
    "story_miramarsupermercado_20260720": "Ofertas Miramar — story (13 a 21/07)",
    "DbCSdsOm-Mv": "Festival de Pescados Mar Vermelho (21 a 25/07)",
    "DbBkKB7hNXL": "Black Princess 600ml — Leve 2 Pague 1 (20 a 25/07)",
    "DbBU33XG07y": "Grandes Ofertas MarZap (17 a 23/07)",
}


def nrm_tokens(s: str) -> tuple:
    """Normaliza um nome de produto em um conjunto ordenado de tokens."""
    s = unicodedata.normalize("NFD", str(s).lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    return tuple(sorted(t for t in s.split() if t and t not in NOISE))


def norm_preco(p: str) -> str:
    """Padroniza o preço ao convênio do acervo: sem prefixo 'R$'."""
    t = str(p or "").strip()
    t = re.sub(r"^r\$\s*", "", t, flags=re.I).strip()
    return t


actions = json.load(open(path("data/actions.json"), encoding="utf-8"))
products = json.load(open(path("data/products.json"), encoding="utf-8"))
canon = json.load(open(path("data/canon.json"), encoding="utf-8"))
fila = json.load(open(path("data/fila_novos.json"), encoding="utf-8"))
byshort = {p["shortcode"]: p for p in fila}

for f in ("data/actions.json", "data/products.json", "data/canon.json"):
    shutil.copy(path(f), path(f + ".bak-20260720-ingest"))

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
    # ordena as páginas pela ordem original do post (só as que têm produto)
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
