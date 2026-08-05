#!/usr/bin/env python3
"""Ingestao da janela de 2026-08-05.

Consome data/_extract/w0805_*.json (produtos por pagina, extraidos por visao).
Metadados vem de data/fila_novos.json. Mesmas regras do pipeline (ver 0804):
- Posts sem preco / teaser / educativo / B2B-comerciante -> DESCARTADOS
  (batch vazio ja cai fora por "sem pagina com produto").
- shortcode novo (feed/web/story) -> cria acao NOVA, com DEDUP por overlap:
  se existir acao de MESMO banner (e mesmo perfil, p/ banners multiunidade)
  cujo periodo SOBREPOE o do post novo e cujos produtos cobrem >= LIMIAR ->
  DEDUP. Posts da MESMA rodada NAO deduplicam entre si. Overrides KEEP/DISCARD.
- canon: canonicalizacao por nrm_tokens; NUNCA une pares DIFERENTES.

Casos desta janela:
- Mirassol mal-rotulado: o story coletado como 'story_miramarsupermercado_20260805'
  traz, nas imagens, a marca MIRASSOL ATACADO (erro de coleta). Atribuido ao
  banner/perfil corretos (override em STORY_META).
- story do Mar Vermelho repete o feed avulso + vinhos DA MESMA RODADA -> descartado.
- MV: carrossel de 6 cards avulsos (1 produto/pagina) e conteudo DISTINTO -> KEEP.

DRY_RUN por padrao. Rode 'python3 ingest_20260805.py commit' p/ gravar.
"""
import json
import os
import re
import shutil
import sys
import unicodedata

BASE = os.path.dirname(os.path.abspath(__file__))
HOJE = "2026-08-05"
LIMIAR = 0.6
DRY_RUN = not (len(sys.argv) > 1 and sys.argv[1] == "commit")

NOISE = {"lata", "lta", "pct", "pcte", "pacote", "pet", "tb", "gf", "cada", "un",
         "und", "unid", "unidade", "sabores", "sabor", "fragrancias",
         "fragrancia", "tipos", "tipo"}

# ---- Metadados dos posts FEED/WEB aprovados ----
# atacadao_*: fonte 'web' com inicio/fim confiaveis na fila -> so titulo aqui.
# Mar Vermelho (feed IG): periodo do que esta impresso na pagina / legenda.
FEED_META = {
    "Dbpxg74mygO": dict(inicio="2026-07-31", fim="2026-08-06",
                        titulo="Mês dos Pais — Ofertas avulsas", fonte="feed"),
    "DbpBQTSmyUs": dict(inicio="2026-08-05", fim="2026-08-30",
                        titulo="Festival de Vinhos", fonte="feed"),
    "atacadao_d539bc59f3": dict(titulo="Atacadão - Boa do Dia (05/08)"),
    "atacadao_f4e37f7117": dict(
        titulo="Atacadão - Super Ofertas (Terça a Quinta 04 a 06/08)"),
    "atacadao_28c555d715": dict(
        titulo="Atacadão - Açougue/Padaria/Frios (05 a 07/08)"),
    "atacadao_75d8349b61": dict(titulo="Atacadão - Hortifrúti (05 e 06/08)"),
}

# ---- Metadados das acoes de STORY novas (colecao do dia) ----
# banner/perfil/segmento opcionais: sobrepoem o que veio da fila.
STORY_META = {
    "story_miramarsupermercado_20260805": dict(
        inicio="2026-08-05", fim="2026-08-06",
        titulo="Mirassol Atacado — Quarta e Quinta dos Frios e Hortifruti (story)",
        banner="Mirassol Atacado", perfil="mirassolatacado", segmento="atacarejo"),
    "story_cortefacil.atacarejo_20260805": dict(
        inicio="2026-08-05", fim="2026-08-06",
        titulo="Corte Fácil — Ofertas Hortifruti (story)"),
    "story_redemaisrn_20260805": dict(
        inicio="2026-08-05", fim="2026-08-06",
        titulo="Rede Mais — Feirão de Hortifruti 26 Anos (story)"),
    "story_marvermelhoatacado_20260805": dict(
        inicio="2026-08-05", fim="2026-08-06",
        titulo="Mar Vermelho — vinhos e avulsos (story)"),
    "story_supernordestaonatal_20260805": dict(
        inicio="2026-08-05", fim="2026-08-05",
        titulo="Super Nordestão — story"),
}

# Descartes explicitos (alem dos batches vazios, que caem sozinhos)
DESCARTE = {
    "DbpsD_FgDKA": "teaser 'Oferta Surpresa do Dia' (produto borrado, só no app)",
    "Dbo_p6Sm4Au": "teaser institucional 'Festival de Vinhos' (sem preços)",
    "story_supernordestaonatal_20260805":
        "teaser 'Oferta Surpresa' (produto borrado, só no app)",
}

# Story do Mar Vermelho repete os 12 vinhos (DbpBQTSmyUs) + 6 avulsos
# (Dbpxg74mygO) do FEED da MESMA rodada -> descartada (mesma regra do 0804).
DISCARD_OVERRIDE = {"story_marvermelhoatacado_20260805"}
# MV: carrosseis avulsos de 1 produto/pagina sao conteudo DISTINTO (regra do dono)
# -> mantidos mesmo com overlap contra os encartes Mes dos Pais ja existentes.
KEEP_OVERRIDE = {"Dbpxg74mygO"}

# Banners compartilhados por unidades diferentes: dedup tambem casa por perfil.
BANNER_MULTIUNIDADE = {"Queiroz Atacadão", "Leva Mais Atacarejo"}


def path(*p):
    return os.path.join(BASE, *p)


def nrm_tokens(s):
    s = unicodedata.normalize("NFD", str(s).lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    return tuple(sorted(t for t in s.split() if t and t not in NOISE))


def nrm_name(s):
    s = unicodedata.normalize("NFD", str(s).lower())
    return " ".join("".join(c for c in s if unicodedata.category(c) != "Mn").split())


def overlaps(ai, af, bi, bf):
    if not (ai and af and bi and bf):
        return False
    return ai <= bf and bi <= af


# --- carrega extracao (w0805_*.json) ---
post_batch = {}       # shortcode -> {pagekey: [...]}
edir = path("data/_extract")
for fn in sorted(os.listdir(edir)):
    m = re.match(r"w0805_(.+)\.json$", fn)
    if not m:
        continue
    sc = m.group(1)
    d = json.load(open(os.path.join(edir, fn), encoding="utf-8"))
    post_batch[sc] = d

actions = json.load(open(path("data/actions.json"), encoding="utf-8"))
products = json.load(open(path("data/products.json"), encoding="utf-8"))
canon = json.load(open(path("data/canon.json"), encoding="utf-8"))
fila = json.load(open(path("data/fila_novos.json"), encoding="utf-8"))
byshort = {p["shortcode"]: p for p in fila}
byid = {a["id"]: a for a in actions}

# pares DIFERENTES (jamais unir)
diferentes = set()
rp = path("data/regras_similaridade.md")
if os.path.exists(rp):
    for line in open(rp, encoding="utf-8"):
        if line.startswith("- DIFERENTES:"):
            mm = re.findall(r"«([^»]*)»", line)
            if len(mm) == 2:
                diferentes.add(frozenset((nrm_name(mm[0]), nrm_name(mm[1]))))

by_key = {}
for g in canon:
    k = nrm_tokens(g["n"])
    if k not in by_key or len(g["m"]) > len(by_key[k]["m"]):
        by_key[k] = g

log = {"novos": 0, "merges": 0, "bloq_dif": 0}


def canon_add(name, unit, ref):
    k = nrm_tokens(name)
    g = by_key.get(k)
    if g is not None and frozenset((nrm_name(name), nrm_name(g["n"]))) in diferentes:
        g = None
        log["bloq_dif"] += 1
    if g is None:
        g = {"n": name, "u": unit, "m": [ref]}
        canon.append(g)
        by_key[nrm_tokens(name)] = g
        log["novos"] += 1
    else:
        if ref not in g["m"]:
            g["m"].append(ref)
        log["merges"] += 1


def twin_cover(banner, perfil, ini, fim, tokset):
    """Fracao de tokset coberta por acoes JA EXISTENTES de MESMO banner (e mesmo
    perfil, p/ banner multiunidade) com periodo sobreposto."""
    twin_toks, n_twins = set(), 0
    for a in actions:
        if a["banner"] != banner:
            continue
        if banner in BANNER_MULTIUNIDADE and a.get("perfil") != perfil:
            continue
        if not overlaps(a.get("inicio"), a.get("fim"), ini, fim):
            continue
        tot = 0
        for pg in a["paginas"]:
            for it in products.get(pg[:-4], []):
                twin_toks.add(nrm_tokens(it["n"]))
                tot += 1
        if tot:
            n_twins += 1
    if not tokset:
        return 0.0, n_twins
    inter = sum(1 for t in tokset if t in twin_toks)
    return inter / len(tokset), n_twins


def post_pages(sc):
    """Paginas (na ordem da fila) do post com >=1 produto extraido."""
    src = byshort.get(sc, {})
    out = []
    for pg in src.get("paginas", []):
        key = pg[:-4]
        items = post_batch.get(sc, {}).get(key) or []
        if items:
            out.append((key, items))
    return out


def eff_meta(sc, src):
    """Resolve metadados efetivos (com overrides de STORY/FEED_META)."""
    if sc.startswith("story_"):
        meta = STORY_META.get(sc, {})
        ini = meta.get("inicio", HOJE)
        fim = meta.get("fim", "2026-08-06")
    else:
        meta = FEED_META.get(sc, {})
        ini = meta.get("inicio") or src.get("inicio") or HOJE
        fim = meta.get("fim") or src.get("fim") or ini
    banner = meta.get("banner") or src.get("banner", "")
    perfil = meta.get("perfil") or src.get("perfil", "")
    segmento = meta.get("segmento") or src.get("segmento", "")
    return meta, ini, fim, banner, perfil, segmento


report = {"novos": [], "dedup": [], "discard": []}
plan_novos = []

order = sorted(byshort, key=lambda s: (s.startswith("story_"), s))

for sc in order:
    if sc in DESCARTE:
        report["discard"].append((sc, DESCARTE[sc]))
        continue
    pages = post_pages(sc)
    if not pages:
        report["discard"].append((sc, "sem página com produto/preço"))
        continue
    nprod = sum(len(v) for _, v in pages)
    src = byshort.get(sc, {})

    if sc in byid:
        report["discard"].append((sc, "id já existente (ver extend manual)"))
        continue

    meta, ini, fim, banner, perfil, segmento = eff_meta(sc, src)

    tokset = {nrm_tokens(it["n"]) for _, v in pages for it in v}
    frac, n_twins = twin_cover(banner, perfil, ini, fim, tokset)
    gatilho = n_twins > 0 and frac >= LIMIAR
    if sc in KEEP_OVERRIDE:
        gatilho = False
    if sc in DISCARD_OVERRIDE:
        gatilho = True

    if gatilho:
        report["dedup"].append((sc, banner, f"{ini}..{fim}", nprod,
                                round(frac, 2), n_twins))
        continue

    report["novos"].append((sc, banner, f"{ini}..{fim}", nprod,
                            round(frac, 2), n_twins))
    plan_novos.append((sc, pages, ini, fim, meta, banner, perfil, segmento))

# ---------- relatorio ----------
print("=" * 72)
print("DRY_RUN" if DRY_RUN else "COMMIT", "- ingest_20260805")
print("=" * 72)
print("\n[NOVAS acoes] (sc | banner | periodo | nprod | overlap | ntwins)")
for r in report["novos"]:
    print("  +", *r)
print("\n[DEDUP re-post descartado] (sc | banner | periodo | nprod | overlap | ntwins)")
for r in report["dedup"]:
    print("  x", *r)
print("\n[DISCARD] (sc | motivo)")
for r in report["discard"]:
    print("  -", *r)
print("\nTotais: novos=%d dedup=%d discard=%d" % (
    len(report["novos"]), len(report["dedup"]), len(report["discard"])))

if DRY_RUN:
    print("\n(dry-run: nada gravado. rode 'python3 ingest_20260805.py commit')")
    sys.exit(0)

# ================= COMMIT =================
for f in ("data/actions.json", "data/products.json", "data/canon.json"):
    shutil.copy(path(f), path(f + ".bak-20260805"))

total_prod = 0
banners_novos = {}

for sc, pages, ini, fim, meta, banner, perfil, segmento in plan_novos:
    src = byshort.get(sc, {})
    paginas = []
    for key, items in pages:
        if key in products:
            continue
        products[key] = items
        paginas.append(key + ".jpg")
        total_prod += len(items)
        for idx, it in enumerate(items):
            canon_add(it["n"], it.get("u", "un"), f"{key}#{idx}")
    if not paginas:
        continue
    if sc.startswith("story_"):
        dd = HOJE[8:10] + "/" + HOJE[5:7]
        titulo = meta.get("titulo") or f"Ofertas {banner} — story ({dd})"
        fonte = "story"
        link = ""
    else:
        titulo = meta.get("titulo", "")
        fonte = meta.get("fonte") or src.get("fonte") or "feed"
        link = src.get("link", "")
    actions.append({
        "id": sc,
        "perfil": perfil,
        "titulo": titulo,
        "banner": banner,
        "segmento": segmento,
        "inicio": ini,
        "fim": fim,
        "carrossel": len(paginas) > 1,
        "shortcode": sc,
        "caption": src.get("caption", ""),
        "paginas": paginas,
        "adicionado_em": HOJE,
        "fonte": fonte,
        "link": link,
    })
    byid[sc] = actions[-1]
    banners_novos[banner] = banners_novos.get(banner, 0) + 1

json.dump(actions, open(path("data/actions.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
json.dump(products, open(path("data/products.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
json.dump(canon, open(path("data/canon.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

print("\nGRAVADO. novas=%d | produtos_novos=%d | canon: %d novos, %d encaixes, %d bloq_dif" % (
    len(plan_novos), total_prod, log["novos"], log["merges"], log["bloq_dif"]))
print("Banners com novidade:", banners_novos)
