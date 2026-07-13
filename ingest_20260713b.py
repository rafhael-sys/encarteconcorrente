#!/usr/bin/env python3
# Ingestao 13/07/2026 — LOTE B (vigentes): Rede Mais (feed) + Miramar (story).
#   Rede Mais "Copa RedeMAIS" (DaoUj8YjXJP)  feed   11-20/07  4 pág  83 prod
#   Miramar (story_...20260713)              story  13-21/07  4 frames de oferta 24 prod
# Só os frames de oferta do story do Miramar entram (f1/f2 eram dica pessoal,
# f4 duplicata). Extração manual na sessão do Claude Code.
import json, shutil, os, sys, unicodedata, re

BASE = os.path.dirname(os.path.abspath(__file__))
def path(*p): return os.path.join(BASE, *p)
HOJE = "2026-07-13"

NOISE = {"lata","lta","pct","pcte","pacote","pet","tb","gf","cada","un","und",
         "unid","unidade","sabores","sabor","fragrancias","fragrancia","tipos","tipo"}
def nrm_tokens(s):
    s = unicodedata.normalize("NFD", str(s).lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    return tuple(sorted(t for t in s.split() if t and t not in NOISE))

actions  = json.load(open(path("data/actions.json"),  encoding="utf-8"))
products = json.load(open(path("data/products.json"), encoding="utf-8"))
canon    = json.load(open(path("data/canon.json"),    encoding="utf-8"))
fila     = json.load(open(path("data/fila_novos.json"), encoding="utf-8"))
newprod  = json.load(open(path("data/_ingest_20260713b_produtos.json"), encoding="utf-8"))
byshort  = {p["shortcode"]: p for p in fila}

for f in ("data/actions.json","data/products.json","data/canon.json"):
    shutil.copy(path(f), path(f + ".bak-20260713b-ingest"))

by_key = {}
for g in canon:
    k = nrm_tokens(g["n"])
    if k not in by_key or len(g["m"]) > len(by_key[k]["m"]):
        by_key[k] = g

log = {"novos": [], "merges": 0}
def canon_add(name, unit, ref):
    k = nrm_tokens(name); g = by_key.get(k)
    if g is None:
        g = {"n": name, "u": unit, "m": [ref]}; canon.append(g); by_key[k] = g
        log["novos"].append(name)
    else:
        if ref not in g["m"]: g["m"].append(ref)
        log["merges"] += 1

# paginas=None -> usa as do fila; lista -> só essas (ex.: story só com frames de oferta)
ACOES = [
    {"sc":"DaoUj8YjXJP", "titulo":"Copa RedeMAIS (11 a 20/07)",
     "inicio":"2026-07-11", "fim":"2026-07-20", "paginas":None},
    {"sc":"story_miramarsupermercado_20260713", "titulo":"Ofertas Miramar — story (13 a 21/07)",
     "inicio":"2026-07-13", "fim":"2026-07-21",
     "paginas":["story_miramarsupermercado_3940279086463711431.jpg",
                "story_miramarsupermercado_3940328819063340780.jpg",
                "story_miramarsupermercado_3940328910440493102.jpg",
                "story_miramarsupermercado_3940328992573314087.jpg"]},
]
existing_ids = {a["id"] for a in actions}
total_prod = 0
for cfg in ACOES:
    sc = cfg["sc"]
    if sc not in byshort: sys.exit(f"ERRO: {sc} nao esta na fila")
    if sc in existing_ids: sys.exit(f"ERRO: acao {sc} ja existe")
    src = byshort[sc]
    paginas = cfg["paginas"] or src["paginas"]
    for pagjpg in paginas:
        key = os.path.splitext(pagjpg)[0]
        if key in products: sys.exit(f"ERRO: pagina {key} ja em products.json")
        items = newprod.get(key, [])
        products[key] = items
        total_prod += len(items)
        for idx, it in enumerate(items):
            canon_add(it["n"], it.get("u","un"), f"{key}#{idx}")
    actions.append({
        "id": sc, "perfil": src["perfil"], "titulo": cfg["titulo"],
        "banner": src["banner"], "segmento": src["segmento"],
        "inicio": cfg["inicio"], "fim": cfg["fim"],
        "carrossel": len(paginas) > 1, "shortcode": sc,
        "caption": src.get("caption",""), "paginas": paginas, "adicionado_em": HOJE,
        "fonte": src.get("fonte","feed"), "link": src.get("link",""),
    })

fila_rest = [p for p in fila if p["shortcode"] not in {c["sc"] for c in ACOES}]

json.dump(actions,  open(path("data/actions.json"), "w", encoding="utf-8"),  ensure_ascii=False, indent=1)
json.dump(products, open(path("data/products.json"),"w", encoding="utf-8"),  ensure_ascii=False, indent=1)
json.dump(canon,    open(path("data/canon.json"),   "w", encoding="utf-8"),  ensure_ascii=False, indent=1)
json.dump(fila_rest,open(path("data/fila_novos.json"),"w", encoding="utf-8"), ensure_ascii=False, indent=1)

print("OK — acoes:", len(actions), "| produtos ingeridos:", total_prod,
      "| canon:", len(canon), f"({len(log['novos'])} novos, {log['merges']} encaixes)")
print("Fila:", len(fila), "->", len(fila_rest))
