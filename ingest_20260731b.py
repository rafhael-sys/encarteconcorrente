#!/usr/bin/env python3
"""Ingestao da janela da noite 31/07/2026 (segundo lote do dia).

Consome data/_visao_parts/*.json (um por post; marvermelho vem em __a/__b e e
mesclado por shortcode). Metadados (banner/perfil/segmento/caption/fonte/link)
vem de data/fila_novos.json. Regras desta rodada:
- verdict != process  -> descartado.
- shortcode ja em actions.json:
    * id de STORY -> ESTENDE a acao (anexa paginas novas, produtos, canon;
      atualiza fim se um frame novo mostrar data posterior).
    * senao -> pula (ja existe).
- shortcode novo:
    * story_* -> cria acao NOVA (stories nunca sao deduplicadas).
    * feed/web -> cria acao NOVA, mas com DEDUP por sobreposicao: se existir acao
      de MESMO banner e MESMO periodo (inicio+fim) cujos produtos ja cobrem
      >=60% dos produtos do post novo, e re-post -> DEDUP (nao cria).
      DISCARD_OVERRIDE/KEEP_OVERRIDE forcam manualmente.
- canon: canonicalizacao por nrm_tokens (igual ao pipeline); NUNCA une pares
  marcados DIFERENTES em regras_similaridade.md.

DRY_RUN por padrao (so relata). Rode 'python3 ingest_20260731b.py commit' p/ gravar.
"""
import json
import os
import re
import shutil
import sys
import unicodedata

BASE = os.path.dirname(os.path.abspath(__file__))
HOJE = "2026-07-31"
DRY_RUN = not (len(sys.argv) > 1 and sys.argv[1] == "commit")

NOISE = {"lata", "lta", "pct", "pcte", "pacote", "pet", "tb", "gf", "cada", "un",
         "und", "unid", "unidade", "sabores", "sabor", "fragrancias",
         "fragrancia", "tipos", "tipo"}

# Overrides manuais (apos revisar o dry-run):
# DbddlEFHJVK = Favoritaço Varejo 29/07-04/08: carrossel multi-produto cujos 7
# itens ja estao TODOS nas gemeas de mesmo banner+periodo (re-post confirmado
# item a item). Overlap por token deu 0.57 (abaixo do gatilho) so por diferenca
# de escrita; forco o descarte.
DISCARD_OVERRIDE = {"DbddlEFHJVK"}   # shortcodes a descartar como dedup
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

# carrega e mescla parts por shortcode
parts = {}
for fn in sorted(os.listdir(path("data/_visao_parts"))):
    if not fn.endswith(".json"):
        continue
    d = json.load(open(path("data/_visao_parts", fn), encoding="utf-8"))
    sc = d["shortcode"]
    if sc in parts:
        parts[sc].setdefault("pages", {}).update(d.get("pages", {}))
        for campo in ("inicio", "fim"):
            if not parts[sc].get(campo) and d.get(campo):
                parts[sc][campo] = d[campo]
        if d.get("verdict") == "process":
            parts[sc]["verdict"] = "process"
    else:
        parts[sc] = d

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


def pages_ordenadas(sc, pages):
    """Ordena as chaves de pages pela ordem original da fila."""
    src = byshort.get(sc, {})
    ordem = [pg[:-4] for pg in src.get("paginas", []) if pg[:-4] in pages]
    for k in pages:
        if k not in ordem:
            ordem.append(k)
    return ordem


report = {"novos": [], "extends": [], "dedup": [], "discard": [], "skip": []}
plan_novos, plan_extends = [], []

for sc, part in sorted(parts.items()):
    if part.get("verdict") != "process":
        report["discard"].append((sc, part.get("discard_reason", "discard")))
        continue
    pages = {k: v for k, v in part.get("pages", {}).items() if v}
    if not pages:
        report["discard"].append((sc, "sem paginas com produto"))
        continue
    nprod = sum(len(v) for v in pages.values())
    src = byshort.get(sc, {})
    banner = src.get("banner", "")

    if sc in byid:
        if not sc.startswith("story_"):
            report["skip"].append((sc, "id ja existe (nao-story)"))
            continue
        ex = byid[sc]
        ja = set(p[:-4] for p in ex["paginas"])
        novas = [k for k in pages_ordenadas(sc, pages)
                 if k not in ja and k not in products]
        if not novas:
            report["skip"].append((sc, "story sem paginas realmente novas"))
            continue
        nnp = sum(len(pages[k]) for k in novas)
        report["extends"].append((sc, banner, len(novas), nnp, part.get("fim")))
        plan_extends.append((sc, ex, pages, novas, part))
        continue

    ini, fim = part.get("inicio"), part.get("fim")
    tset = {nrm_tokens(it["n"]) for v in pages.values() for it in v}
    twinset, n_twins = twin_names(banner, ini, fim)
    inter = [t for t in tset if t in twinset]
    frac = (len(inter) / len(tset)) if tset else 0
    gatilho = (not sc.startswith("story_")) and n_twins > 0 and frac >= 0.6
    if sc in KEEP_OVERRIDE:
        gatilho = False
    if sc in DISCARD_OVERRIDE:
        gatilho = True
    if gatilho:
        report["dedup"].append((sc, banner, ini, fim, nprod, round(frac, 2), n_twins))
    else:
        report["novos"].append((sc, banner, ini, fim, nprod, round(frac, 2), n_twins))
        plan_novos.append((sc, part, pages))

print("=" * 70)
print("DRY_RUN" if DRY_RUN else "COMMIT", "- ingest_20260731b")
print("=" * 70)
print("\n[NOVAS acoes] (sc | banner | inicio | fim | nprod | overlap | ntwins)")
for r in report["novos"]:
    print("  +", *r)
print("\n[DEDUP re-post descartado] (sc | banner | inicio | fim | nprod | overlap | ntwins)")
for r in report["dedup"]:
    print("  x", *r)
print("\n[EXTENDS story] (sc | banner | npag_novas | nprod_novos | fim_part)")
for r in report["extends"]:
    print("  ~", *r)
print("\n[DISCARD verdict] (sc | motivo)")
for r in report["discard"]:
    print("  -", *r)
print("\n[SKIP]", report["skip"])
print("\nTotais: novos=%d dedup=%d extends=%d discard=%d skip=%d" % (
    len(report["novos"]), len(report["dedup"]), len(report["extends"]),
    len(report["discard"]), len(report["skip"])))

if DRY_RUN:
    print("\n(dry-run: nada gravado. rode 'python3 ingest_20260731b.py commit')")
    sys.exit(0)

# ================= COMMIT =================
for f in ("data/actions.json", "data/products.json", "data/canon.json"):
    shutil.copy(path(f), path(f + ".bak-20260731b"))

total_prod = 0
banners_novos = {}

# 1) NOVAS acoes
for sc, part, pages in plan_novos:
    src = byshort.get(sc, {})
    banner = src.get("banner", "")
    ordem = pages_ordenadas(sc, pages)
    paginas = []
    for key in ordem:
        items = pages.get(key)
        if not items or key in products:
            continue
        products[key] = items
        paginas.append(key + ".jpg")
        total_prod += len(items)
        for idx, it in enumerate(items):
            canon_add(it["n"], it.get("u", "un"), f"{key}#{idx}")
    if not paginas:
        continue
    ini = part.get("inicio") or src.get("inicio") or part.get("fim") or HOJE
    fim = part.get("fim") or src.get("fim") or ini
    actions.append({
        "id": sc,
        "perfil": src.get("perfil", ""),
        "titulo": part.get("titulo", ""),
        "banner": banner,
        "segmento": src.get("segmento", ""),
        "inicio": ini,
        "fim": fim,
        "carrossel": len(paginas) > 1,
        "shortcode": sc,
        "caption": src.get("caption", ""),
        "paginas": paginas,
        "adicionado_em": HOJE,
        "fonte": src.get("fonte") or "feed",
        "link": src.get("link", ""),
    })
    byid[sc] = actions[-1]
    banners_novos[banner] = banners_novos.get(banner, 0) + 1

# 2) EXTENDS de story
extends_prod = 0
for sc, ex, pages, novas, part in plan_extends:
    add_pag = []
    for key in novas:
        items = pages.get(key)
        if not items or key in products:
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
    # NAO altera o periodo (inicio/fim) da acao: frames sao produtos avulsos com
    # validade propria; o periodo da story do dia foi definido na 1a rodada.
    banners_novos[ex["banner"]] = banners_novos.get(ex["banner"], 0)

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
