#!/usr/bin/env python3
"""Ingestão 30/07/2026 (janela ~07h).

Consome os produtos extraídos por visão desta rodada
(data/_extracao_20260730.json), monta ações/produtos/canon com a MESMA
canonicalização do pipeline (nrm_tokens/canon_add), esvazia a fila e faz
backup dos JSONs.

Aprovados nesta janela (10 ações). Descartados por serem publicidade pura
(sem produto com preço): DbaG0rmm7M5 (Mar Vermelho teaser "Dias Imperdíveis"),
DbaPShCgDI6 (Super Nordestão Oferta Surpresa borrada) e
story_supernordestaonatal_20260730 (Oferta Surpresa borrada).
"""
import json
import os
import re
import shutil
import unicodedata

BASE = os.path.dirname(os.path.abspath(__file__))
def path(*p): return os.path.join(BASE, *p)

HOJE = "2026-07-30"
NOISE = {"lata", "lta", "pct", "pcte", "pacote", "pet", "tb", "gf", "cada", "un",
         "und", "unid", "unidade", "sabores", "sabor", "fragrancias",
         "fragrancia", "tipos", "tipo"}


def nrm_tokens(s):
    s = unicodedata.normalize("NFD", str(s).lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    return tuple(sorted(t for t in s.split() if t and t not in NOISE))


META = {
    "atacadao_8b88d3998a": {"perfil": "atacadao.com.br", "banner": "Atacadão",
        "segmento": "atacarejo", "titulo": "Boa do Dia Atacadão (30/07)",
        "inicio": "2026-07-30", "fim": "2026-07-30", "fonte": "web",
        "link": "https://www.atacadao.com.br/loja/natal-sul"},
    "atacadao_691784a937": {"perfil": "atacadao.com.br", "banner": "Atacadão",
        "segmento": "atacarejo", "titulo": "Hortifrúti Atacadão (30 e 31/07)",
        "inicio": "2026-07-30", "fim": "2026-07-31", "fonte": "web",
        "link": "https://www.atacadao.com.br/loja/natal-sul"},
    "assai_168726-572": {"perfil": "assai.com.br", "banner": "Assaí Atacadista",
        "segmento": "atacarejo", "titulo": "Ofertas Assaí (30 e 31/07)",
        "inicio": "2026-07-30", "fim": "2026-07-31", "fonte": "web",
        "link": "https://www.assai.com.br/ofertas/rio-grande-do-norte/assai-natal"},
    "assai_168730-572": {"perfil": "assai.com.br", "banner": "Assaí Atacadista",
        "segmento": "atacarejo", "titulo": "Ofertas App Meu Assaí (30/07 a 05/08)",
        "inicio": "2026-07-30", "fim": "2026-08-05", "fonte": "web",
        "link": "https://www.assai.com.br/ofertas/rio-grande-do-norte/assai-natal"},
    "DbaUwKpG4QN": {"perfil": "marvermelhoatacado", "banner": "Mar Vermelho Atacado",
        "segmento": "atacarejo", "titulo": "Ofertas MarZap Mar Vermelho (24 a 30/07)",
        "inicio": "2026-07-24", "fim": "2026-07-30", "fonte": "feed", "link": ""},
    "story_marvermelhoatacado_20260730": {"perfil": "marvermelhoatacado",
        "banner": "Mar Vermelho Atacado", "segmento": "atacarejo",
        "titulo": "Ofertas MarZap Mar Vermelho — story (24 a 30/07)",
        "inicio": "2026-07-24", "fim": "2026-07-30", "fonte": "story", "link": ""},
    "story_mirassolatacado_20260730": {"perfil": "mirassolatacado",
        "banner": "Mirassol Atacado", "segmento": "atacarejo",
        "titulo": "Ofertas Mirassol Atacado — story (30/07 a 01/08)",
        "inicio": "2026-07-30", "fim": "2026-08-01", "fonte": "story", "link": ""},
    "story_miramarsupermercado_20260730": {"perfil": "miramarsupermercado",
        "banner": "Miramar Supermercado", "segmento": "varejo",
        "titulo": "Ofertas do App Miramar — story (22 a 30/07)",
        "inicio": "2026-07-22", "fim": "2026-07-30", "fonte": "story", "link": ""},
    "story_redemaisrn_20260730": {"perfil": "redemaisrn", "banner": "Rede Mais",
        "segmento": "propria",
        "titulo": "Frango a Passarinho Jaguá Rede Mais — story (29 a 31/07)",
        "inicio": "2026-07-29", "fim": "2026-07-31", "fonte": "story", "link": ""},
    "story_cortefacil.atacarejo_20260730": {"perfil": "cortefacil.atacarejo",
        "banner": "Corte Fácil Atacarejo", "segmento": "atacarejo",
        "titulo": "Aniversário Corte Fácil — story (30/07 a 02/08)",
        "inicio": "2026-07-30", "fim": "2026-08-02", "fonte": "story", "link": ""},
}

extracao = json.load(open(path("data/_extracao_20260730.json"), encoding="utf-8"))
actions = json.load(open(path("data/actions.json"), encoding="utf-8"))
products = json.load(open(path("data/products.json"), encoding="utf-8"))
canon = json.load(open(path("data/canon.json"), encoding="utf-8"))
fila = json.load(open(path("data/fila_novos.json"), encoding="utf-8"))
byshort = {p["shortcode"]: p for p in fila}

# ordem das páginas por ação = ordem de inserção no arquivo de extração
ORDEM = {sc: list(pages.keys()) for sc, pages in extracao.items()}

for f in ("data/actions.json", "data/products.json", "data/canon.json"):
    shutil.copy(path(f), path(f + ".bak-20260730"))

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

for sc, meta in META.items():
    if sc in existing_ids:
        print(f"[skip] ação {sc} já existe")
        continue
    pages = extracao.get(sc, {})
    paginas = []
    for key in ORDEM[sc]:
        items = pages.get(key)
        if not items:
            continue
        if key in products:
            print(f"[skip] página {key} já em products.json")
            continue
        products[key] = items
        paginas.append(key + ".jpg")
        total_prod += len(items)
        for idx, it in enumerate(items):
            canon_add(it["n"], it.get("u", "un"), f"{key}#{idx}")
    if not paginas:
        print(f"[skip] {sc} sem páginas com produto")
        continue
    src = byshort.get(sc, {})
    actions.append({
        "id": sc,
        "perfil": meta.get("perfil", src.get("perfil", "")),
        "titulo": meta.get("titulo", ""),
        "banner": meta["banner"],
        "segmento": meta.get("segmento", src.get("segmento", "")),
        "inicio": meta["inicio"],
        "fim": meta["fim"],
        "carrossel": len(paginas) > 1,
        "shortcode": sc,
        "caption": src.get("caption", ""),
        "paginas": paginas,
        "adicionado_em": HOJE,
        "fonte": meta.get("fonte") or src.get("fonte") or "feed",
        "link": meta.get("link", src.get("link", "")),
    })
    existing_ids.add(sc)
    kept.append(sc)
    banners_novos[meta["banner"]] = banners_novos.get(meta["banner"], 0) + 1

json.dump(actions, open(path("data/actions.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
json.dump(products, open(path("data/products.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
json.dump(canon, open(path("data/canon.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
json.dump([], open(path("data/fila_novos.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

print("OK — ações novas:", len(kept), "| produtos:", total_prod,
      "| canon:", len(canon), f"({log['novos']} novos, {log['merges']} encaixes)")
print("Banners:", banners_novos)
