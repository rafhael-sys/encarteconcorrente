#!/usr/bin/env python3
"""Ingestao 31/07/2026.

Consome os produtos extraidos por visao desta rodada
(data/_visao_parts/<shortcode>.json, um arquivo por post), monta
acoes/produtos/canon com a MESMA canonicalizacao do pipeline
(nrm_tokens/canon_add) e faz backup dos JSONs. NAO esvazia a fila
(a limpeza da fila e feita a parte, depois de conferir todos os itens).

Regras desta rodada:
- Ingere todo part com verdict=="process" e pages nao-vazio, EXCETO os
  shortcodes em DISCARD_OVERRIDE (deduplicacoes decididas manualmente).
- Pula shortcodes que ja existem em actions.json (id repetido).
"""
import json
import os
import re
import shutil
import unicodedata

BASE = os.path.dirname(os.path.abspath(__file__))


def path(*p):
    return os.path.join(BASE, *p)


HOJE = "2026-07-31"
NOISE = {"lata", "lta", "pct", "pcte", "pacote", "pet", "tb", "gf", "cada", "un",
         "und", "unid", "unidade", "sabores", "sabor", "fragrancias",
         "fragrancia", "tipos", "tipo"}

# Deduplicacoes manuais (post novo que repete oferta da MESMA loja+periodo,
# cuja gemea ja tem produtos extraidos):
#  - DbahOogswAe: Hortifruti Leva Mais Joao Camara 29-31/07 == DbX5nyDsy4y
#    (Feirao de Frutas e Verduras Leva Mais JC ate 31/07, 13 prod).
DISCARD_OVERRIDE = {"DbahOogswAe"}

# Correcoes pontuais de metadados por shortcode (opcional).
META_OVERRIDE = {}


def nrm_tokens(s):
    s = unicodedata.normalize("NFD", str(s).lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    return tuple(sorted(t for t in s.split() if t and t not in NOISE))


actions = json.load(open(path("data/actions.json"), encoding="utf-8"))
products = json.load(open(path("data/products.json"), encoding="utf-8"))
canon = json.load(open(path("data/canon.json"), encoding="utf-8"))
fila = json.load(open(path("data/fila_novos.json"), encoding="utf-8"))
byshort = {p["shortcode"]: p for p in fila}

# carrega os parts de visao
parts = {}
for fn in sorted(os.listdir(path("data/_visao_parts"))):
    if not fn.endswith(".json"):
        continue
    d = json.load(open(path("data/_visao_parts", fn), encoding="utf-8"))
    parts[d["shortcode"]] = d

for f in ("data/actions.json", "data/products.json", "data/canon.json"):
    shutil.copy(path(f), path(f + ".bak-20260731"))

by_key = {}
for g in canon:
    k = nrm_tokens(g["n"])
    if k not in by_key or len(g["m"]) > len(by_key[k]["m"]):
        by_key[k] = g

log = {"novos": 0, "merges": 0}


def canon_add(name, unit, ref):
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
kept, total_prod, banners_novos = [], 0, {}
descartados = []

for sc, part in parts.items():
    if part.get("verdict") != "process":
        descartados.append((sc, part.get("discard_reason", "discard")))
        continue
    if sc in DISCARD_OVERRIDE:
        descartados.append((sc, "dedup manual (gemea ja tem produtos)"))
        continue
    if sc in existing_ids:
        print(f"[skip] acao {sc} ja existe")
        continue
    src = byshort.get(sc, {})
    over = META_OVERRIDE.get(sc, {})
    pages_part = part.get("pages", {})
    if not pages_part:
        descartados.append((sc, "sem paginas com produto"))
        continue
    # ordena paginas pela ordem original da fila quando disponivel
    ordem = [pg[:-4] for pg in src.get("paginas", []) if pg[:-4] in pages_part]
    for k in pages_part:
        if k not in ordem:
            ordem.append(k)
    paginas = []
    for key in ordem:
        items = pages_part.get(key)
        if not items:
            continue
        if key in products:
            print(f"[skip] pagina {key} ja em products.json")
            continue
        products[key] = items
        paginas.append(key + ".jpg")
        total_prod += len(items)
        for idx, it in enumerate(items):
            canon_add(it["n"], it.get("u", "un"), f"{key}#{idx}")
    if not paginas:
        descartados.append((sc, "paginas ja em products.json"))
        continue
    banner = over.get("banner", src.get("banner", ""))
    actions.append({
        "id": sc,
        "perfil": over.get("perfil", src.get("perfil", "")),
        "titulo": over.get("titulo", part.get("titulo", "")),
        "banner": banner,
        "segmento": over.get("segmento", src.get("segmento", "")),
        "inicio": over.get("inicio", part.get("inicio") or part.get("fim") or HOJE),
        "fim": over.get("fim", part.get("fim") or part.get("inicio") or HOJE),
        "carrossel": len(paginas) > 1,
        "shortcode": sc,
        "caption": src.get("caption", ""),
        "paginas": paginas,
        "adicionado_em": HOJE,
        "fonte": over.get("fonte") or src.get("fonte") or "feed",
        "link": over.get("link", src.get("link", "")),
    })
    existing_ids.add(sc)
    kept.append(sc)
    banners_novos[banner] = banners_novos.get(banner, 0) + 1

json.dump(actions, open(path("data/actions.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
json.dump(products, open(path("data/products.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
json.dump(canon, open(path("data/canon.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

print("OK — acoes novas:", len(kept), "| produtos:", total_prod,
      "| canon:", len(canon), f"({log['novos']} novos, {log['merges']} encaixes)")
print("Banners:", banners_novos)
print("Descartados/dedup:", descartados)
