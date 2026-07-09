#!/usr/bin/env python3
# Ingestao da janela 09/07/2026.
# Aprovados: Queiroz Atacadao (Natal) e Queiroz Atacadao Joao Camara (Ofertaco 09-12/07),
# SuperFacil Atacado Joao Pessoa e SuperFacil Atacado RN (Feirao Hortifruti 09-11/07),
# Mar Vermelho Atacado hortifruti (09-10/07) e Mar Vermelho Festival Baby & Kids (09-13/07).
# Descartados: Atacadao web natal-sul 07-09 (dup de periodo ja existente),
# Mar Vermelho 03-09/07 (dup de mv_julho), sorteio Favorito Club, arte Baby&Kids
# sem precos e Oferta Surpresa Nordestao (produto oculto, sem preco visivel).
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
newprod  = json.load(open(path("data/_ingest_20260709_produtos.json"), encoding="utf-8"))
cap = {p["shortcode"]: p.get("caption","") for p in fila}

for f in ("data/actions.json","data/products.json","data/canon.json"):
    shutil.copy(path(f), path(f + ".bak-20260709-ingest"))

by_key = {}
for g in canon:
    k = nrm_tokens(g["n"])
    if k not in by_key or len(g["m"]) > len(by_key[k]["m"]):
        by_key[k] = g

def canon_add(name, unit, ref, log):
    k = nrm_tokens(name)
    g = by_key.get(k)
    if g is None:
        g = {"n": name, "u": unit, "m": [ref]}
        canon.append(g); by_key[k] = g
        log["novos"].append((name, ref))
    else:
        if ref not in g["m"]:
            g["m"].append(ref)
        log["merges"].append((name, g["n"], ref))

NOVAS = [
 {"id":"Dai5Aw-GzCL","perfil":"queirozatacadaonatal_",
  "titulo":"Ofertaço de Verdade (09 a 12/07)",
  "banner":"Queiroz Atacadão","segmento":"atacarejo",
  "inicio":"2026-07-09","fim":"2026-07-12","paginas":3},
 {"id":"Dai4vkok2fJ","perfil":"queirozatacadaojoaocamara",
  "titulo":"Ofertaço de Verdade (09 a 12/07)",
  "banner":"Queiroz Atacadão João Câmara","segmento":"atacarejo",
  "inicio":"2026-07-09","fim":"2026-07-12","paginas":3},
 {"id":"Dai-_doAeIN","perfil":"superfacilatacado",
  "titulo":"Feirão de Hortifrúti (09 a 11/07)",
  "banner":"SuperFácil Atacado João Pessoa","segmento":"atacarejo",
  "inicio":"2026-07-09","fim":"2026-07-11","paginas":2},
 {"id":"Dai9PfWgVcN","perfil":"superfacilatacado",
  "titulo":"Feirão de Hortifrúti (09 a 11/07)",
  "banner":"SuperFácil Atacado","segmento":"atacarejo",
  "inicio":"2026-07-09","fim":"2026-07-11","paginas":2},
 {"id":"DajLQkxm73t","perfil":"marvermelhoatacado",
  "titulo":"Hortifrúti (09 e 10/07)",
  "banner":"Mar Vermelho Atacado","segmento":"atacarejo",
  "inicio":"2026-07-09","fim":"2026-07-10","paginas":2},
 {"id":"DajY7cPG-wn","perfil":"marvermelhoatacado",
  "titulo":"Festival Baby & Kids (09 a 13/07)",
  "banner":"Mar Vermelho Atacado","segmento":"atacarejo",
  "inicio":"2026-07-09","fim":"2026-07-13","paginas":1},
]

existing_ids = {a["id"] for a in actions}
log = {"novos": [], "merges": []}

for a in NOVAS:
    if a["id"] in existing_ids:
        sys.exit("ERRO: acao %s ja existe" % a["id"])
    npag = a["paginas"]
    for i in range(1, npag+1):
        key = "%s_p%d" % (a["id"], i)
        if key in products:
            sys.exit("ERRO: pagina %s ja em products.json" % key)
        items = newprod.get(key, [])
        products[key] = items
        for idx, it in enumerate(items):
            canon_add(it["n"], it.get("u","un"), "%s#%d" % (key, idx), log)
    act = {
        "id": a["id"], "perfil": a["perfil"], "titulo": a["titulo"],
        "banner": a["banner"], "segmento": a["segmento"],
        "inicio": a["inicio"], "fim": a["fim"], "carrossel": npag > 1,
        "shortcode": a["id"], "caption": cap.get(a["id"], a["titulo"]),
        "paginas": ["%s_p%d.jpg" % (a["id"], i) for i in range(1, npag+1)],
        "adicionado_em": HOJE,
    }
    actions.append(act)

json.dump(actions,  open(path("data/actions.json"), "w", encoding="utf-8"),  ensure_ascii=False, indent=1)
json.dump(products, open(path("data/products.json"),"w", encoding="utf-8"),  ensure_ascii=False, indent=1)
json.dump(canon,    open(path("data/canon.json"),   "w", encoding="utf-8"),  ensure_ascii=False, indent=1)

print("OK — acoes:", len(actions), "| paginas produtos:", len(products), "| grupos canon:", len(canon))
print("Produtos novos ingeridos:", sum(len(newprod.get('%s_p%d'%(a['id'],i),[])) for a in NOVAS for i in range(1,a['paginas']+1)))
print("Grupos canonicos NOVOS:", len(log["novos"]), "| Encaixes em grupo existente:", len(log["merges"]))
