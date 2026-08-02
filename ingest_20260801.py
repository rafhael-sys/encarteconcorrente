#!/usr/bin/env python3
"""Ingestao da janela de 2026-08-01.

Consome data/_extract/batch_*.json (produtos por pagina, extraidos por visao).
Metadados vem de data/fila_novos.json. Regras (iguais ao pipeline):
- Posts sem preco / teaser / educativo / evento  -> DESCARTADOS (nao entram aqui).
- shortcode de STORY ja em actions.json -> ESTENDE (anexa frames novos + produtos
  + canon; NAO altera o periodo da acao).
- shortcode novo:
    * story_* -> cria acao NOVA (stories nunca sao deduplicadas).
    * feed/web -> cria acao NOVA, com DEDUP por sobreposicao de tokens: se existir
      acao de MESMO banner e MESMO periodo cujos produtos ja cobrem >=60% dos
      produtos do post novo -> DEDUP (nao cria). Overrides manuais abaixo.
- canon: canonicalizacao por nrm_tokens (igual ao pipeline); NUNCA une pares
  marcados DIFERENTES em regras_similaridade.md.

DRY_RUN por padrao. Rode 'python3 ingest_20260801.py commit' p/ gravar.
"""
import json
import os
import re
import shutil
import sys
import unicodedata

BASE = os.path.dirname(os.path.abspath(__file__))
HOJE = "2026-08-01"
DRY_RUN = not (len(sys.argv) > 1 and sys.argv[1] == "commit")

NOISE = {"lata", "lta", "pct", "pcte", "pacote", "pet", "tb", "gf", "cada", "un",
         "und", "unid", "unidade", "sabores", "sabor", "fragrancias",
         "fragrancia", "tipos", "tipo"}

# Metadados dos posts feed/web aprovados (periodo preferido do que esta IMPRESSO)
FEED_META = {
    "Dbf1Wp7nNbC": dict(inicio="2026-07-29", fim="2026-08-04",
                        titulo="Favoritaço Varejo — Ponta Negra e Ayrton Senna", fonte="feed"),
    "DbfxIcslfQa": dict(inicio="2026-07-31", fim="2026-08-01",
                        titulo="Sextou com Sabadão", fonte="feed"),
    "Dbg-eZ4G2qd": dict(inicio="2026-07-31", fim="2026-08-06",
                        titulo="Mês dos Pais", fonte="feed"),
    "Dbg3xa7n-_E": dict(inicio="2026-08-01", fim="2026-08-03",
                        titulo="Ofertas de Fim de Semana", fonte="feed"),
    "DbgSKH-Go8R": dict(inicio="2026-07-31", fim="2026-08-02",
                        titulo="Colheita de Ofertas", fonte="feed"),
    "atacadao_505d274908": dict(inicio="2026-08-01", fim="2026-08-02",
                                titulo="Sábado Parceirão", fonte="web"),
}

# Periodo das acoes de STORY novas (colecao do dia)
STORY_NEW = {
    "story_favoritosuper_20260801": dict(inicio="2026-08-01", fim="2026-08-04"),
    "story_queirozatacadaojoaocamara_20260801": dict(inicio="2026-08-01", fim="2026-08-02"),
    "story_queirozatacadaonatal__20260801": dict(inicio="2026-08-01", fim="2026-08-02"),
    "story_atacarejo_santoantonio.ofc_20260801": dict(inicio="2026-08-01", fim="2026-08-10"),
    "story_redesuper.show_20260801": dict(inicio="2026-08-01", fim="2026-08-02"),
}

# Posts descartados na triagem (teaser/educativo/evento/sem preco)
DESCARTE = {
    "DbgPuqtDbvz": "teaser Sextou com Sabadão (sem preços)",
    "DbgQxSvz2im": "evento Food Truck Nissin (sem preços)",
    "Dbfmmt1lUSf": "teaser 'só até hoje' (sem preços)",
    "DbfymFlgZ3i": "carrossel educativo de cortes de carne (sem preços)",
}

DISCARD_OVERRIDE = set()   # shortcodes a descartar como dedup (apos revisar dry-run)
KEEP_OVERRIDE = set()      # shortcodes a manter mesmo com gatilho de dedup


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


# --- carrega extracao (batch_*.json) ---
extract = {}
edir = path("data/_extract")
for fn in sorted(os.listdir(edir)):
    if re.match(r"batch_\d+\.json$", fn):
        d = json.load(open(os.path.join(edir, fn), encoding="utf-8"))
        for k, v in d.items():
            extract[k] = v

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
            m = re.findall(r"«([^»]*)»", line)
            if len(m) == 2:
                diferentes.add(frozenset((nrm_name(m[0]), nrm_name(m[1]))))

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


def twin_names(banner, ini, fim):
    nomes, n_twins = set(), 0
    for a in actions:
        if a["banner"] == banner and a.get("inicio") == ini and a.get("fim") == fim:
            tot = 0
            for pg in a["paginas"]:
                for it in products.get(pg[:-4], []):
                    nomes.add(nrm_tokens(it["n"]))
                    tot += 1
            if tot:
                n_twins += 1
    return nomes, n_twins


def post_pages(sc):
    """Paginas (na ordem da fila) do post com >=1 produto extraido."""
    src = byshort.get(sc, {})
    out = []
    for pg in src.get("paginas", []):
        key = pg[:-4]
        items = extract.get(key) or []
        if items:
            out.append((key, items))
    return out


report = {"novos": [], "extends": [], "dedup": [], "discard": []}
plan_novos, plan_extends = [], []

for sc in byshort:
    if sc in DESCARTE:
        report["discard"].append((sc, DESCARTE[sc]))
        continue
    pages = post_pages(sc)
    if not pages:
        report["discard"].append((sc, "sem página com produto/preço"))
        continue
    nprod = sum(len(v) for _, v in pages)
    src = byshort.get(sc, {})
    banner = src.get("banner", "")

    if sc in byid:  # story ja existente -> extend
        ex = byid[sc]
        ja = set(p[:-4] for p in ex["paginas"])
        novas = [(k, v) for k, v in pages if k not in ja and k not in products]
        if not novas:
            report["discard"].append((sc, "story sem frames realmente novos"))
            continue
        nnp = sum(len(v) for _, v in novas)
        report["extends"].append((sc, banner, len(novas), nnp))
        plan_extends.append((sc, ex, novas))
        continue

    if sc.startswith("story_"):  # story nova
        report["novos"].append((sc, banner, "story", nprod))
        plan_novos.append((sc, pages))
        continue

    # feed/web novo -> dedup por overlap
    meta = FEED_META.get(sc, {})
    ini, fim = meta.get("inicio"), meta.get("fim")
    tset = {nrm_tokens(it["n"]) for _, v in pages for it in v}
    twinset, n_twins = twin_names(banner, ini, fim)
    inter = [t for t in tset if t in twinset]
    frac = (len(inter) / len(tset)) if tset else 0
    gatilho = n_twins > 0 and frac >= 0.6
    if sc in KEEP_OVERRIDE:
        gatilho = False
    if sc in DISCARD_OVERRIDE:
        gatilho = True
    if gatilho:
        report["dedup"].append((sc, banner, ini, fim, nprod, round(frac, 2), n_twins))
    else:
        report["novos"].append((sc, banner, f"{ini}..{fim}", nprod, round(frac, 2), n_twins))
        plan_novos.append((sc, pages))

print("=" * 70)
print("DRY_RUN" if DRY_RUN else "COMMIT", "- ingest_20260801")
print("=" * 70)
print("\n[NOVAS acoes]")
for r in report["novos"]:
    print("  +", *r)
print("\n[DEDUP re-post descartado] (sc | banner | ini | fim | nprod | overlap | ntwins)")
for r in report["dedup"]:
    print("  x", *r)
print("\n[EXTENDS story] (sc | banner | npag_novas | nprod_novos)")
for r in report["extends"]:
    print("  ~", *r)
print("\n[DISCARD] (sc | motivo)")
for r in report["discard"]:
    print("  -", *r)
print("\nTotais: novos=%d dedup=%d extends=%d discard=%d" % (
    len(report["novos"]), len(report["dedup"]),
    len(report["extends"]), len(report["discard"])))

if DRY_RUN:
    print("\n(dry-run: nada gravado. rode 'python3 ingest_20260801.py commit')")
    sys.exit(0)

# ================= COMMIT =================
for f in ("data/actions.json", "data/products.json", "data/canon.json"):
    shutil.copy(path(f), path(f + ".bak-20260801"))

total_prod = 0
banners_novos = {}

# 1) NOVAS acoes (feed/web/story)
for sc, pages in plan_novos:
    src = byshort.get(sc, {})
    banner = src.get("banner", "")
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
        meta = STORY_NEW.get(sc, {})
        ini = meta.get("inicio", HOJE)
        fim = meta.get("fim", HOJE)
        dd = HOJE[8:10] + "/" + HOJE[5:7]
        titulo = f"Ofertas {banner} — story ({dd})"
        fonte = "story"
        link = ""
    else:
        meta = FEED_META.get(sc, {})
        ini = meta.get("inicio") or src.get("inicio") or HOJE
        fim = meta.get("fim") or src.get("fim") or ini
        titulo = meta.get("titulo", "")
        fonte = meta.get("fonte") or src.get("fonte") or "feed"
        link = src.get("link", "")
    actions.append({
        "id": sc,
        "perfil": src.get("perfil", ""),
        "titulo": titulo,
        "banner": banner,
        "segmento": src.get("segmento", ""),
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

# 2) EXTENDS de story
extends_prod = 0
for sc, ex, novas in plan_extends:
    add_pag = []
    for key, items in novas:
        if key in products:
            continue
        products[key] = items
        add_pag.append(key + ".jpg")
        extends_prod += len(items)
        total_prod += len(items)
        for idx, it in enumerate(items):
            canon_add(it["n"], it.get("u", "un"), f"{key}#{idx}")
    if not add_pag:
        continue
    ex["paginas"] = ex["paginas"] + add_pag
    ex["carrossel"] = len(ex["paginas"]) > 1
    # NAO altera o periodo (inicio/fim) da acao de story.

json.dump(actions, open(path("data/actions.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
json.dump(products, open(path("data/products.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
json.dump(canon, open(path("data/canon.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

print("\nGRAVADO. novos=%d extends=%d | produtos_novos=%d (extends=%d) | canon: %d novos, %d encaixes, %d bloq_dif" % (
    len(plan_novos), len(plan_extends), total_prod, extends_prod,
    log["novos"], log["merges"], log["bloq_dif"]))
print("Banners com novidade:", banners_novos)
