#!/usr/bin/env python3
"""Ingestão 29/07/2026 — janela da tarde (2ª rodada do dia).

Consome data/_extr/_ALL.json (extração por visão desta janela), monta
ações/produtos/canon com a MESMA canonicalização do pipeline (nrm_tokens/
canon_add), faz merge das STORIES cujo id já existe (anexa frames novos à
ação do dia) e esvazia a fila. Backup dos JSONs antes de gravar.

Descartes desta janela:
  - DbY71_aTj0X  (Favorito, teaser "falta pouco", sem preço)
  - DbYbtIgFhdW  (Santo Antônio, "algumas ofertas do rasga preço" = subconjunto
                  do encarte Rasga Preço já registrado DbWwLXUFve3, mesma loja/período)
  - DbZHInKkZD1  (SuperFácil João Pessoa/PB — regra do perfil: só RN)
  - story_levamaismacau_20260729 / story_levamaisjc_20260729 (frames vazios, 0 produto)
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


# --- Ações NOVAS desta janela (feed aprovados + stories de id inédito) ---
NOVOS = {
    "DbYYx07judi": {"banner": "Rede Super Show", "segmento": "varejo",
        "titulo": "Fecha Mês Rede Super Show (29/07 a 01/08)",
        "inicio": "2026-07-29", "fim": "2026-08-01", "fonte": "feed"},
    "DbY0w1mFW_g": {"banner": "Rede Super Show", "segmento": "varejo",
        "titulo": "Fecha Mês Rede Super Show — carrossel (29/07 a 01/08)",
        "inicio": "2026-07-29", "fim": "2026-08-01", "fonte": "feed"},
    "DbYse9aFAr9": {"banner": "Rede Super Show", "segmento": "varejo",
        "titulo": "Fecha Mês Rede Super Show — ofertas (29/07 a 01/08)",
        "inicio": "2026-07-29", "fim": "2026-08-01", "fonte": "feed"},
    "DbYj6vunJbL": {"banner": "Favorito Super / Atacado Favorito", "segmento": "varejo",
        "titulo": "Quarta e Quinta Verde Favorito — hortifrúti (29 e 30/07)",
        "inicio": "2026-07-29", "fim": "2026-07-30", "fonte": "feed"},
    "DbYWhRTlR2X": {"banner": "Favorito Super / Atacado Favorito", "segmento": "varejo",
        "titulo": "Quarta e Quinta Verde Favorito — hortifrúti II (29 e 30/07)",
        "inicio": "2026-07-29", "fim": "2026-07-30", "fonte": "feed"},
    "DbY90YsoIlp": {"banner": "Queiroz Atacadão", "segmento": "atacarejo",
        "titulo": "Operação Fecha Mês Queiroz Natal (30/07 a 02/08)",
        "inicio": "2026-07-30", "fim": "2026-08-02", "fonte": "feed"},
    "DbZEmcnkcKw": {"banner": "SuperFácil Atacado", "segmento": "atacarejo",
        "titulo": "Ofertas Fim de Mês SuperFácil RN (30/07 a 02/08)",
        "inicio": "2026-07-30", "fim": "2026-08-02", "fonte": "feed"},
    "DbZP9aVm_MX": {"banner": "Mar Vermelho Atacado", "segmento": "atacarejo",
        "titulo": "Hortifrúti Mar Vermelho (30 e 31/07)",
        "inicio": "2026-07-30", "fim": "2026-07-31", "fonte": "feed"},
    "DbZdrvom9TF": {"banner": "Mar Vermelho Atacado", "segmento": "atacarejo",
        "titulo": "Dias Imperdíveis Mar Vermelho (30 e 31/07)",
        "inicio": "2026-07-30", "fim": "2026-07-31", "fonte": "feed"},
    "DbZOjy2FYs7": {"banner": "Leva Mais Atacarejo", "segmento": "atacarejo",
        "titulo": "Operação Fecha Mês Leva Mais Macau (30/07 a 02/08)",
        "inicio": "2026-07-30", "fim": "2026-08-02", "fonte": "feed"},
    "DbZDJeumHPP": {"banner": "Super Nordestão", "segmento": "varejo",
        "titulo": "Fecha Mês Nordestão (30/07 a 02/08)",
        "inicio": "2026-07-30", "fim": "2026-08-02", "fonte": "feed"},
    "DbY9f5tGTKV": {"banner": "Queiroz Atacadão", "segmento": "atacarejo",
        "titulo": "Operação Fecha Mês Queiroz João Câmara (30/07 a 02/08)",
        "inicio": "2026-07-30", "fim": "2026-08-02", "fonte": "feed"},
    "DbZOhmFlkho": {"banner": "Leva Mais Atacarejo João Câmara", "segmento": "atacarejo",
        "titulo": "Operação Fecha Mês Leva Mais João Câmara (30/07 a 02/08)",
        "inicio": "2026-07-30", "fim": "2026-08-02", "fonte": "feed"},
    "DbX5nyDsy4y": {"banner": "Leva Mais Atacarejo João Câmara", "segmento": "atacarejo",
        "titulo": "Feirão de Frutas e Verduras Leva Mais João Câmara (até 31/07)",
        "inicio": "2026-07-29", "fim": "2026-07-31", "fonte": "feed"},
    "DbZOReaFiMp": {"banner": "Rede Supercop", "segmento": "varejo",
        "titulo": "Quinta Verde Supercop (30/07)",
        "inicio": "2026-07-30", "fim": "2026-07-30", "fonte": "feed"},
    "DbZPq9PDV7g": {"banner": "Corte Fácil Atacarejo", "segmento": "atacarejo",
        "titulo": "Mistério dos Prêmios Corte Fácil (30/07 a 02/08)",
        "inicio": "2026-07-30", "fim": "2026-08-02", "fonte": "feed"},
    "DbZIzTBDz1j": {"banner": "Corte Fácil Atacarejo", "segmento": "atacarejo",
        "titulo": "Feirão das Carnes Corte Fácil (30 e 31/07)",
        "inicio": "2026-07-30", "fim": "2026-07-31", "fonte": "feed"},
    # --- stories de id inédito ---
    "story_atacarejo_santoantonio.ofc_20260729": {"banner": "Atacarejo Santo Antônio",
        "segmento": "atacarejo", "titulo": "Ofertas Santo Antônio — story (29 e 30/07)",
        "inicio": "2026-07-29", "fim": "2026-07-30", "fonte": "story"},
    "story_queirozatacadaonatal__20260729": {"banner": "Queiroz Atacadão",
        "segmento": "atacarejo", "titulo": "Fecha Mês Queiroz Natal — story (até 02/08)",
        "inicio": "2026-07-29", "fim": "2026-08-02", "fonte": "story"},
    "story_mirassolatacado_20260729": {"banner": "Mirassol Atacado",
        "segmento": "atacarejo", "titulo": "Ofertas Mirassol Atacado — story",
        "inicio": "2026-07-29", "fim": "2026-08-02", "fonte": "story"},
    "story_redesupercop_20260729": {"banner": "Rede Supercop",
        "segmento": "varejo", "titulo": "Quinta Verde Supercop — story (30/07)",
        "inicio": "2026-07-30", "fim": "2026-07-30", "fonte": "story"},
    "story_supernordestaonatal_20260729": {"banner": "Super Nordestão",
        "segmento": "varejo", "titulo": "Ofertas Super Nordestão — story",
        "inicio": "2026-07-29", "fim": "2026-07-31", "fonte": "story"},
    "story_queirozatacadaojoaocamara_20260729": {"banner": "Queiroz Atacadão",
        "segmento": "atacarejo", "titulo": "Ofertas Queiroz João Câmara — story (29 a 31/07)",
        "inicio": "2026-07-29", "fim": "2026-07-31", "fonte": "story"},
    "story_redesuper.show_20260729": {"banner": "Rede Super Show",
        "segmento": "varejo", "titulo": "Fecha Mês Rede Super Show — story (29/07 a 01/08)",
        "inicio": "2026-07-29", "fim": "2026-08-01", "fonte": "story"},
}

# --- Stories cujo id JÁ existe hoje: anexa frames novos à ação existente ---
MERGES = [
    "story_miramarsupermercado_20260729",
    "story_marvermelhoatacado_20260729",
    "story_cortefacil.atacarejo_20260729",
    "story_favoritosuper_20260729",
    "story_redemaisrn_20260729",
]

DESCARTES = {"DbY71_aTj0X", "DbYbtIgFhdW", "DbZHInKkZD1",
             "story_levamaismacau_20260729", "story_levamaisjc_20260729"}

extr = json.load(open(path("data/_extr/_ALL.json"), encoding="utf-8"))
actions = json.load(open(path("data/actions.json"), encoding="utf-8"))
products = json.load(open(path("data/products.json"), encoding="utf-8"))
canon = json.load(open(path("data/canon.json"), encoding="utf-8"))
fila = json.load(open(path("data/fila_novos.json"), encoding="utf-8"))
byshort = {p["shortcode"]: p for p in fila}
byid = {a["id"]: a for a in actions}

for f in ("data/actions.json", "data/products.json", "data/canon.json"):
    shutil.copy(path(f), path(f + ".bak-20260729b"))

by_key = {}
for g in canon:
    k = nrm_tokens(g["n"])
    if k not in by_key or len(g["m"]) > len(by_key[k]["m"]):
        by_key[k] = g

log = {"novos_canon": 0, "merges_canon": 0}


def canon_add(name, unit, ref):
    k = nrm_tokens(name)
    g = by_key.get(k)
    if g is None:
        g = {"n": name, "u": unit, "m": [ref]}
        canon.append(g)
        by_key[k] = g
        log["novos_canon"] += 1
    else:
        if ref not in g["m"]:
            g["m"].append(ref)
        log["merges_canon"] += 1


def paginas_ordenadas(sc):
    """Ordem = ordem original das páginas na fila, filtrando as que têm produto."""
    pages = extr[sc].get("paginas", {})
    ordem_fila = [f.replace(".jpg", "") for f in byshort.get(sc, {}).get("paginas", [])]
    keys = [k for k in ordem_fila if k in pages and pages[k]]
    # inclui eventuais chaves fora da lista da fila (defensivo)
    for k in pages:
        if pages[k] and k not in keys:
            keys.append(k)
    return keys


def adiciona_paginas(sc):
    """Grava as páginas de sc em products/canon. Devolve (lista de .jpg, nprod)."""
    paginas, nprod = [], 0
    for key in paginas_ordenadas(sc):
        if key in products:
            print(f"[skip] página {key} já em products.json")
            continue
        items = extr[sc]["paginas"][key]
        products[key] = items
        paginas.append(key + ".jpg")
        nprod += len(items)
        for idx, it in enumerate(items):
            canon_add(it["n"], it.get("u", "un"), f"{key}#{idx}")
    return paginas, nprod


existing_ids = {a["id"] for a in actions}
kept, merged, total_prod = [], [], 0
banners = {}

# 1) Ações NOVAS
for sc, meta in NOVOS.items():
    if sc in existing_ids:
        print(f"[skip] {sc} já existe em actions (esperava novo)")
        continue
    if extr.get(sc, {}).get("classificacao") != "encarte":
        print(f"[skip] {sc} não é encarte na extração")
        continue
    paginas, nprod = adiciona_paginas(sc)
    if not paginas:
        print(f"[skip] {sc} sem página com produto")
        continue
    src = byshort.get(sc, {})
    actions.append({
        "id": sc,
        "perfil": src.get("perfil", ""),
        "titulo": meta["titulo"],
        "banner": meta["banner"],
        "segmento": meta["segmento"],
        "inicio": meta["inicio"],
        "fim": meta["fim"],
        "carrossel": len(paginas) > 1,
        "shortcode": sc,
        "caption": src.get("caption", ""),
        "paginas": paginas,
        "adicionado_em": HOJE,
        "fonte": meta["fonte"],
        "link": src.get("link", ""),
    })
    existing_ids.add(sc)
    kept.append(sc)
    total_prod += nprod
    banners[meta["banner"]] = banners.get(meta["banner"], 0) + 1

# 2) MERGES em stories já existentes hoje
for sc in MERGES:
    a = byid.get(sc)
    if a is None:
        print(f"[aviso] merge {sc}: ação não existe — pulando")
        continue
    if extr.get(sc, {}).get("classificacao") != "encarte":
        print(f"[skip] merge {sc} não é encarte")
        continue
    paginas, nprod = adiciona_paginas(sc)
    if not paginas:
        print(f"[skip] merge {sc} sem página nova com produto")
        continue
    a["paginas"].extend(paginas)
    a["carrossel"] = len(a["paginas"]) > 1
    a["adicionado_em"] = HOJE  # mantém a tag "Novo" acesa nesta janela
    merged.append((sc, len(paginas), nprod))
    total_prod += nprod
    banners[a["banner"]] = banners.get(a["banner"], 0) + 1

# 3) grava
json.dump(actions, open(path("data/actions.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
json.dump(products, open(path("data/products.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
json.dump(canon, open(path("data/canon.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
json.dump([], open(path("data/fila_novos.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

print("OK")
print("  ações novas:", len(kept))
print("  stories merge:", [(m[0], f"+{m[1]}pg/{m[2]}prod") for m in merged])
print("  descartados:", sorted(DESCARTES))
print("  produtos adicionados:", total_prod)
print("  canon:", len(canon), f"({log['novos_canon']} novos, {log['merges_canon']} encaixes)")
print("  banners:", banners)
