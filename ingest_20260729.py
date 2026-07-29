#!/usr/bin/env python3
"""Ingestão 29/07/2026.

Consome os produtos extraídos por visão desta rodada (data/_extracao_20260729.json),
monta ações/produtos/canon com a MESMA canonicalização do pipeline
(nrm_tokens/canon_add), esvazia a fila e faz backup dos JSONs.

Aprovados nesta janela (13 ações). Descartados por serem publicidade pura
(sem preço): DbXx7ZjE4rw (Super Nordestão Oferta Surpresa), DbXq7UVE9Jq
(Rede Supercop teaser), story_supernordestaonatal_20260729,
story_redesupercop_20260729.
"""
import json
import os
import re
import shutil
import unicodedata

BASE = os.path.dirname(os.path.abspath(__file__))
def path(*p): return os.path.join(BASE, *p)

HOJE = "2026-07-29"
NOISE = {"lata", "lta", "pct", "pcte", "pacote", "pet", "tb", "gf", "cada", "un",
         "und", "unid", "unidade", "sabores", "sabor", "fragrancias",
         "fragrancia", "tipos", "tipo"}


def nrm_tokens(s):
    s = unicodedata.normalize("NFD", str(s).lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    return tuple(sorted(t for t in s.split() if t and t not in NOISE))


# metadados por ação (banner/segmento/perfil exatos, iguais aos já existentes)
META = {
    "DbWeEsxvm8V": {"perfil": "redesuper.show", "banner": "Rede Super Show",
        "segmento": "varejo", "titulo": "Lasanha Aurora Rede Super Show (28/07 a 02/08)",
        "inicio": "2026-07-28", "fim": "2026-08-02", "fonte": "feed", "link": ""},
    "DbXv-RZm15J": {"perfil": "marvermelhoatacado", "banner": "Mar Vermelho Atacado",
        "segmento": "atacarejo", "titulo": "Ofertas MarZap Mar Vermelho (24 a 30/07)",
        "inicio": "2026-07-24", "fim": "2026-07-30", "fonte": "feed", "link": ""},
    "DbXo5Tcm_KX": {"perfil": "marvermelhoatacado", "banner": "Mar Vermelho Atacado",
        "segmento": "atacarejo", "titulo": "Lasanha Aurora Mar Vermelho (29 e 30/07)",
        "inicio": "2026-07-29", "fim": "2026-07-30", "fonte": "feed", "link": ""},
    "assai_168663-572": {"perfil": "assai.com.br", "banner": "Assaí Atacadista",
        "segmento": "atacarejo", "titulo": "Ofertas do Dia Assaí (29/07)",
        "inicio": "2026-07-29", "fim": "2026-07-29", "fonte": "web",
        "link": "https://www.assai.com.br/ofertas/rio-grande-do-norte/assai-natal"},
    "assai_168666-572": {"perfil": "assai.com.br", "banner": "Assaí Atacadista",
        "segmento": "atacarejo", "titulo": "Hortifrúti e Açougue Assaí (29 e 30/07)",
        "inicio": "2026-07-29", "fim": "2026-07-30", "fonte": "web",
        "link": "https://www.assai.com.br/ofertas/rio-grande-do-norte/assai-natal"},
    "atacadao_c8f4d76326": {"perfil": "atacadao.com.br", "banner": "Atacadão",
        "segmento": "atacarejo", "titulo": "Boa do Dia Atacadão (29/07)",
        "inicio": "2026-07-29", "fim": "2026-07-29", "fonte": "web",
        "link": "https://www.atacadao.com.br/loja/natal-sul"},
    "nosso_922f839791": {"perfil": "nossoatacarejo.com.br", "banner": "Nosso Atacarejo",
        "segmento": "atacarejo", "titulo": "Nossa Quarta & Quinta Nosso Atacarejo (29 e 30/07)",
        "inicio": "2026-07-29", "fim": "2026-07-30", "fonte": "web",
        "link": "https://www.nossoatacarejo.com.br/encarte/quarta-e-quinta-rn/5"},
    "story_marvermelhoatacado_20260729": {"perfil": "marvermelhoatacado",
        "banner": "Mar Vermelho Atacado", "segmento": "atacarejo",
        "titulo": "Ofertas MarZap Mar Vermelho — story (29 e 30/07)",
        "inicio": "2026-07-29", "fim": "2026-07-30", "fonte": "story", "link": ""},
    "story_favoritosuper_20260729": {"perfil": "favoritosuper",
        "banner": "Favorito Super / Atacado Favorito", "segmento": "varejo",
        "titulo": "Batalha de Preço Favorito — story (31/07 a 02/08)",
        "inicio": "2026-07-31", "fim": "2026-08-02", "fonte": "story", "link": ""},
    "story_redemaisrn_20260729": {"perfil": "redemaisrn", "banner": "Rede Mais",
        "segmento": "propria", "titulo": "Peito de Frango Real Rede Mais — story (29 a 31/07)",
        "inicio": "2026-07-29", "fim": "2026-07-31", "fonte": "story", "link": ""},
    "story_miramarsupermercado_20260729": {"perfil": "miramarsupermercado",
        "banner": "Miramar Supermercado", "segmento": "varejo",
        "titulo": "Ofertas do App Miramar — story (29 e 30/07)",
        "inicio": "2026-07-29", "fim": "2026-07-30", "fonte": "story", "link": ""},
    "story_cortefacil.atacarejo_20260729": {"perfil": "cortefacil.atacarejo",
        "banner": "Corte Fácil Atacarejo", "segmento": "atacarejo",
        "titulo": "Hortifrúti Corte Fácil — story (29 e 30/07)",
        "inicio": "2026-07-29", "fim": "2026-07-30", "fonte": "story", "link": ""},
}
# ordem das páginas por ação (os frames de story sem preço já ficaram fora da extração)
ORDEM = {
    "DbWeEsxvm8V": ["DbWeEsxvm8V_p1"],
    "DbXv-RZm15J": [f"DbXv-RZm15J_p{i}" for i in range(1, 7)],
    "DbXo5Tcm_KX": ["DbXo5Tcm_KX_p1"],
    "assai_168663-572": ["assai_168663-572_p1", "assai_168663-572_p2"],
    "assai_168666-572": ["assai_168666-572_p1", "assai_168666-572_p2"],
    "atacadao_c8f4d76326": ["atacadao_c8f4d76326_p1"],
    "nosso_922f839791": ["nosso_922f839791_p1"],
    "story_marvermelhoatacado_20260729": [
        "story_marvermelhoatacado_3951807996427443726",
        "story_marvermelhoatacado_3951838192874501955",
        "story_marvermelhoatacado_3951838459850328857",
        "story_marvermelhoatacado_3951838721105190852",
        "story_marvermelhoatacado_3951838981890243120",
        "story_marvermelhoatacado_3951839240813018973",
        "story_marvermelhoatacado_3951839501807715515"],
    "story_favoritosuper_20260729": [
        "story_favoritosuper_3951866564651755631",
        "story_favoritosuper_3951867118677392184",
        "story_favoritosuper_3951867517631150482",
        "story_favoritosuper_3951869153552161380",
        "story_favoritosuper_3951870383615646318"],
    "story_redemaisrn_20260729": ["story_redemaisrn_3951844016690212883"],
    "story_miramarsupermercado_20260729": [
        "story_miramarsupermercado_3951837220617138019",
        "story_miramarsupermercado_3951837329711689215",
        "story_miramarsupermercado_3951837420149322406"],
    "story_cortefacil.atacarejo_20260729": [
        "story_cortefacil.atacarejo_3951806287206268148",
        "story_cortefacil.atacarejo_3951806437722630425",
        "story_cortefacil.atacarejo_3951806577309056297"],
}

extracao = json.load(open(path("data/_extracao_20260729.json"), encoding="utf-8"))
actions = json.load(open(path("data/actions.json"), encoding="utf-8"))
products = json.load(open(path("data/products.json"), encoding="utf-8"))
canon = json.load(open(path("data/canon.json"), encoding="utf-8"))
fila = json.load(open(path("data/fila_novos.json"), encoding="utf-8"))
byshort = {p["shortcode"]: p for p in fila}

for f in ("data/actions.json", "data/products.json", "data/canon.json"):
    shutil.copy(path(f), path(f + ".bak-20260729"))

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
