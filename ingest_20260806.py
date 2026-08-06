#!/usr/bin/env python3
"""Ingestao da janela de 2026-08-06.

Consome data/_extract/w0806_*.json (produtos por pagina, extraidos por visao)
+ data/_extract/w0806_meta.json (datas/titulo/discard por shortcode).
Mesmas regras das janelas anteriores:
- Post sem preco / teaser / B2B / institucional -> DESCARTADO (meta:discard).
- shortcode novo (feed/web/story) -> cria acao NOVA, com DEDUP por overlap:
  acao existente de MESMO banner (e mesmo perfil p/ banner multiunidade) com
  periodo SOBREPOSTO e cobertura de tokens >= LIMIAR -> DEDUP. Posts da MESMA
  rodada NAO deduplicam entre si. Overrides KEEP/DISCARD.
- STORY cujo id JA existe em actions.json -> ESTENDE a acao (frames novos).
- canon: canonicalizacao por nrm_tokens; NUNCA une pares DIFERENTES.

DRY_RUN por padrao. Rode 'python3 ingest_20260806.py commit' p/ gravar.
"""
import json
import os
import re
import shutil
import sys
import unicodedata

BASE = os.path.dirname(os.path.abspath(__file__))
HOJE = "2026-08-06"
LIMIAR = 0.6
DRY_RUN = not (len(sys.argv) > 1 and sys.argv[1] == "commit")

NOISE = {"lata", "lta", "pct", "pcte", "pacote", "pet", "tb", "gf", "cada", "un",
         "und", "unid", "unidade", "sabores", "sabor", "fragrancias",
         "fragrancia", "tipos", "tipo"}

KEEP_OVERRIDE = set()      # forca manter mesmo com overlap alto
DISCARD_OVERRIDE = set()   # forca descartar
DESCARTE = {}              # shortcode -> motivo (descarte explicito)

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


# --- carrega extracao (w0806_*.json, exceto meta) ---
post_batch = {}       # shortcode -> {pagekey: [...]}
edir = path("data/_extract")
for fn in sorted(os.listdir(edir)):
    m = re.match(r"w0806_(.+)\.json$", fn)
    if not m:
        continue
    sc = m.group(1)
    if sc == "meta":
        continue
    try:
        d = json.load(open(os.path.join(edir, fn), encoding="utf-8"))
    except json.JSONDecodeError:
        print("[aviso] json invalido:", fn)
        continue
    if isinstance(d, dict):
        post_batch[sc] = d

META = json.load(open(path("data/_extract/w0806_meta.json"), encoding="utf-8"))

actions = json.load(open(path("data/actions.json"), encoding="utf-8"))
products = json.load(open(path("data/products.json"), encoding="utf-8"))
canon = json.load(open(path("data/canon.json"), encoding="utf-8"))
fila = json.load(open(path("data/fila_novos.json"), encoding="utf-8"))
byshort = {p["shortcode"]: p for p in fila}
byid = {a["id"]: a for a in actions}

# pares DIFERENTES (jamais unir) — le regras_similaridade.md
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


def twin_cover(banner, perfil, ini, fim, tokset, ignore_id=None):
    twin_toks, n_twins = set(), 0
    for a in actions:
        if a.get("id") == ignore_id:
            continue
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
    m = META.get(sc, {})
    ini = m.get("inicio") or src.get("inicio") or HOJE
    fim = m.get("fim") or src.get("fim") or ini
    banner = m.get("banner") or src.get("banner", "")
    perfil = m.get("perfil") or src.get("perfil", "")
    segmento = m.get("segmento") or src.get("segmento", "")
    return m, ini, fim, banner, perfil, segmento


def eff_id(sc):
    return META.get(sc, {}).get("id_override") or sc


report = {"novos": [], "dedup": [], "discard": [], "extend": []}
plan_novos = []
plan_extend = []

order = sorted(byshort, key=lambda s: (s.startswith("story_"), s))

for sc in order:
    if sc in DESCARTE:
        report["discard"].append((sc, DESCARTE[sc]))
        continue
    if META.get(sc, {}).get("discard"):
        report["discard"].append((sc, "meta:discard " + META[sc].get("reason", "")))
        continue
    pages = post_pages(sc)
    if not pages:
        report["discard"].append((sc, "sem página com produto/preço"))
        continue
    nprod = sum(len(v) for _, v in pages)
    src = byshort.get(sc, {})
    meta, ini, fim, banner, perfil, segmento = eff_meta(sc, src)

    eid = eff_id(sc)
    if eid in byid:
        a = byid[eid]
        novos_frames = [(k, v) for k, v in pages
                        if k not in products and (k + ".jpg") not in a["paginas"]]
        if novos_frames:
            plan_extend.append((sc, a, novos_frames))
            report["extend"].append((sc, a["banner"],
                                     sum(len(v) for _, v in novos_frames),
                                     len(novos_frames)))
        else:
            report["discard"].append((sc, "id existente sem frames novos"))
        continue

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
print("DRY_RUN" if DRY_RUN else "COMMIT", "- ingest_20260806")
print("=" * 72)
print("\n[NOVAS acoes] (sc | banner | periodo | nprod | overlap | ntwins)")
for r in report["novos"]:
    print("  +", *r)
print("\n[EXTEND story] (sc | banner | nprod_novos | nframes_novos)")
for r in report["extend"]:
    print("  ^", *r)
print("\n[DEDUP re-post descartado] (sc | banner | periodo | nprod | overlap | ntwins)")
for r in report["dedup"]:
    print("  x", *r)
print("\n[DISCARD] (sc | motivo)")
for r in report["discard"]:
    print("  -", *r)
print("\nTotais: novos=%d extend=%d dedup=%d discard=%d" % (
    len(report["novos"]), len(report["extend"]),
    len(report["dedup"]), len(report["discard"])))

if DRY_RUN:
    print("\n(dry-run: nada gravado. rode 'python3 ingest_20260806.py commit')")
    sys.exit(0)

# ================= COMMIT =================
for f in ("data/actions.json", "data/products.json", "data/canon.json"):
    shutil.copy(path(f), path(f + ".bak-20260806"))

total_prod = 0
banners_novos = {}

# --- EXTEND stories existentes ---
for sc, a, novos_frames in plan_extend:
    for key, items in novos_frames:
        if key in products:
            continue
        products[key] = items
        a["paginas"].append(key + ".jpg")
        total_prod += len(items)
        for idx, it in enumerate(items):
            canon_add(it["n"], it.get("u", "un"), f"{key}#{idx}")
    a["carrossel"] = len(a["paginas"]) > 1

# --- NOVAS acoes ---
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
    eid = eff_id(sc)
    actions.append({
        "id": eid,
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
    byid[eid] = actions[-1]
    banners_novos[banner] = banners_novos.get(banner, 0) + 1

json.dump(actions, open(path("data/actions.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
json.dump(products, open(path("data/products.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
json.dump(canon, open(path("data/canon.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

print("\nGRAVADO. novas=%d | extend=%d | produtos_novos=%d | canon: %d novos, %d encaixes, %d bloq_dif" % (
    len(plan_novos), len(plan_extend), total_prod,
    log["novos"], log["merges"], log["bloq_dif"]))
print("Banners com novidade:", banners_novos)
