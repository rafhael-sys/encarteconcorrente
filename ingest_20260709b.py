#!/usr/bin/env python3
# Ingestao da janela 09/07/2026 (2a rodada) — Nosso Atacarejo (fonte web).
# Aprovados: Nosso Atacarejo "Nossa Quarta & Quinta" (08-09/07, 1 pag) e
#            Nosso Atacarejo "Encarte do Mes" (30/06-13/07, 5 pags).
# Sem regra de perfil e sem duplicata (nenhuma acao Nosso Atacarejo existia).
import json, shutil, os, sys, unicodedata, re

BASE = os.path.dirname(os.path.abspath(__file__))
def path(*p): return os.path.join(BASE, *p)

HOJE = "2026-07-09"

NOISE = {
    "lata","lta","pct","pcte","pacote","pet","tb","gf","cada","un","und",
    "unid","unidade","sabores","sabor","fragrancias","fragrancia","tipos","tipo",
}
def nrm_tokens(s):
    s = unicodedata.normalize("NFD", str(s).lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    toks = [t for t in s.split() if t and t not in NOISE]
    return tuple(sorted(toks))

actions  = json.load(open(path("data/actions.json"),  encoding="utf-8"))
products = json.load(open(path("data/products.json"), encoding="utf-8"))
canon    = json.load(open(path("data/canon.json"),    encoding="utf-8"))
fila     = json.load(open(path("data/fila_novos.json"), encoding="utf-8"))
newprod  = json.load(open(path("data/_ingest_nosso_produtos.json"), encoding="utf-8"))
byshort  = {p["shortcode"]: p for p in fila}

for f in ("data/actions.json","data/products.json","data/canon.json"):
    shutil.copy(path(f), path(f + ".bak-20260709b-ingest"))

by_key = {}
for g in canon:
    k = nrm_tokens(g["n"])
    if k not in by_key or len(g["m"]) > len(by_key[k]["m"]):
        by_key[k] = g

log = {"novos": [], "merges": []}
def canon_add(name, unit, ref):
    k = nrm_tokens(name)
    g = by_key.get(k)
    if g is None:
        g = {"n": name, "u": unit, "m": [ref]}
        canon.append(g); by_key[k] = g
        log["novos"].append(name)
    else:
        if ref not in g["m"]:
            g["m"].append(ref)
        log["merges"].append((name, g["n"]))

NOVAS = ["nosso_ea3c7382a4", "nosso_385e7db048"]
existing_ids = {a["id"] for a in actions}

total_prod = 0
for sc in NOVAS:
    src = byshort[sc]
    if sc in existing_ids:
        sys.exit("ERRO: acao %s ja existe" % sc)
    paginas = src["paginas"]
    for i, pagjpg in enumerate(paginas, 1):
        key = "%s_p%d" % (sc, i)
        if key in products:
            sys.exit("ERRO: pagina %s ja em products.json" % key)
        items = newprod.get(key, [])
        products[key] = items
        total_prod += len(items)
        for idx, it in enumerate(items):
            canon_add(it["n"], it.get("u", "un"), "%s#%d" % (key, idx))
    act = {
        "id": sc, "perfil": src["perfil"], "titulo": src["caption"],
        "banner": src["banner"], "segmento": src["segmento"],
        "inicio": src["inicio"], "fim": src["fim"],
        "carrossel": src.get("carrossel", len(paginas) > 1),
        "shortcode": sc, "caption": src["caption"],
        "paginas": paginas, "adicionado_em": HOJE,
        "fonte": src["fonte"], "link": src["link"],
    }
    actions.append(act)

json.dump(actions,  open(path("data/actions.json"), "w", encoding="utf-8"),  ensure_ascii=False, indent=1)
json.dump(products, open(path("data/products.json"),"w", encoding="utf-8"),  ensure_ascii=False, indent=1)
json.dump(canon,    open(path("data/canon.json"),   "w", encoding="utf-8"),  ensure_ascii=False, indent=1)

print("OK — acoes:", len(actions), "| paginas produtos:", len(products), "| grupos canon:", len(canon))
print("Produtos novos ingeridos:", total_prod)
print("Grupos canonicos NOVOS:", len(log["novos"]), "| Encaixes em grupo existente:", len(log["merges"]))
print("--- MERGES (encaixe em grupo existente) ---")
for nome, grp in log["merges"]:
    print("  ", nome, "->", grp)
