#!/usr/bin/env python3
# Ingestao da janela 13/07/2026 — Atacadao (coleta web).
# 4 encartes aprovados (todos com precos impressos; validade da propria fonte web):
#   Boa do Dia (atacadao_c21038cd2b)            13/07        1 pag   7 prod
#   Fim de Semana Parceirao (atacadao_3caae4f9fa) 10-13/07   6 pag 103 prod
#   Acougue/Frios/Padaria (atacadao_cb8d108830) 10-13/07     2 pag  27 prod
#   Especial da Pizza (atacadao_56cb6e227b)     13-19/07     2 pag  28 prod
# Extracao feita na sessao do Claude Code (o claude CLI nao esta nesta maquina).
# Sem duplicata: nenhum destes shortcodes existe em actions.json.
import json, shutil, os, sys, unicodedata, re

BASE = os.path.dirname(os.path.abspath(__file__))
def path(*p): return os.path.join(BASE, *p)

HOJE = "2026-07-13"

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
newprod  = json.load(open(path("data/_ingest_20260713_produtos.json"), encoding="utf-8"))
byshort  = {p["shortcode"]: p for p in fila}

for f in ("data/actions.json","data/products.json","data/canon.json"):
    shutil.copy(path(f), path(f + ".bak-20260713-ingest"))

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

# titulo por acao; inicio/fim vem do proprio JSON da fonte web (validade_confiavel)
TITULOS = {
    "atacadao_c21038cd2b": "Boa do Dia — Só Segunda (13/07)",
    "atacadao_3caae4f9fa": "Fim de Semana Parceirão (10 a 13/07)",
    "atacadao_cb8d108830": "Especial Açougue, Frios e Padaria (10 a 13/07)",
    "atacadao_56cb6e227b": "Especial da Pizza (13 a 19/07)",
}
NOVAS = list(TITULOS.keys())
existing_ids = {a["id"] for a in actions}

total_prod = 0
for sc in NOVAS:
    if sc not in byshort:
        sys.exit("ERRO: shortcode %s nao esta na fila_novos.json" % sc)
    src = byshort[sc]
    if sc in existing_ids:
        sys.exit("ERRO: acao %s ja existe em actions.json" % sc)
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
        "id": sc, "perfil": src["perfil"], "titulo": TITULOS[sc],
        "banner": src["banner"], "segmento": src["segmento"],
        "inicio": src["inicio"], "fim": src["fim"],
        "carrossel": src.get("carrossel", len(paginas) > 1),
        "shortcode": sc, "caption": src.get("caption", ""),
        "paginas": paginas, "adicionado_em": HOJE,
        "fonte": src.get("fonte", "web"), "link": src.get("link", ""),
    }
    actions.append(act)

# remove da fila o que foi ingerido (higiene: nao reprocessar)
fila_rest = [p for p in fila if p["shortcode"] not in set(NOVAS)]

json.dump(actions,  open(path("data/actions.json"), "w", encoding="utf-8"),  ensure_ascii=False, indent=1)
json.dump(products, open(path("data/products.json"),"w", encoding="utf-8"),  ensure_ascii=False, indent=1)
json.dump(canon,    open(path("data/canon.json"),   "w", encoding="utf-8"),  ensure_ascii=False, indent=1)
json.dump(fila_rest,open(path("data/fila_novos.json"),"w", encoding="utf-8"), ensure_ascii=False, indent=1)

print("OK — acoes:", len(actions), "| paginas produtos:", len(products), "| grupos canon:", len(canon))
print("Produtos novos ingeridos:", total_prod)
print("Grupos canonicos NOVOS:", len(log["novos"]), "| Encaixes em grupo existente:", len(log["merges"]))
print("Fila: %d -> %d itens" % (len(fila), len(fila_rest)))
print("--- alguns MERGES (encaixe em grupo existente) ---")
for nome, grp in log["merges"][:15]:
    print("  ", nome, "->", grp)
