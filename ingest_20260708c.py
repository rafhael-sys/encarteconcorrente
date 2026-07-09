#!/usr/bin/env python3
# Ingestao da janela 08/07/2026 (3a) — estreia dos banners de Joao Camara
# (Queiroz Atacadao Joao Camara e Leva Mais Atacarejo Joao Camara).
# Joao Camara e banner SEPARADO de Natal/Macau: nunca deduplica contra eles.
import json, shutil, os, sys, unicodedata, re

BASE = os.path.dirname(os.path.abspath(__file__))
def path(*p): return os.path.join(BASE, *p)

HOJE = "2026-07-08"

# ---------- normalizacao p/ canon ----------
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

# ---------- carga ----------
actions  = json.load(open(path("data/actions.json"),  encoding="utf-8"))
products = json.load(open(path("data/products.json"), encoding="utf-8"))
canon    = json.load(open(path("data/canon.json"),    encoding="utf-8"))
fila     = json.load(open(path("data/fila_novos.json"), encoding="utf-8"))
newprod  = json.load(open(path("data/_ingest_20260708c_produtos.json"), encoding="utf-8"))
cap = {p["shortcode"]: p.get("caption","") for p in fila}

# ---------- backups ----------
for f in ("data/actions.json","data/products.json","data/canon.json"):
    shutil.copy(path(f), path(f + ".bak-20260708c-ingest"))

# ---------- correcao: Dah4MbKst8_ ficou com banner sem o sufixo Joao Camara ----------
for a in actions:
    if a.get("id") == "Dah4MbKst8_" and a.get("perfil") == "levamaisjc":
        if a.get("banner") != "Leva Mais Atacarejo Joao Camara":
            a["banner"] = "Leva Mais Atacarejo João Câmara"

# ---------- indice canon por chave normalizada (maior grupo vence) ----------
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

# ---------- definicao das acoes novas ----------
NOVAS = [
 {"id":"DabRUA8jwaZ","perfil":"queirozatacadaojoaocamara",
  "titulo":"Copa de Ofertas (06 a 12/07)",
  "banner":"Queiroz Atacadão João Câmara","segmento":"atacarejo",
  "inicio":"2026-07-06","fim":"2026-07-12","paginas":3},
 {"id":"DaL_0i6FvJN","perfil":"levamaisjc",
  "titulo":"Seleção de Ofertas (30/06 a 09/07)",
  "banner":"Leva Mais Atacarejo João Câmara","segmento":"atacarejo",
  "inicio":"2026-06-30","fim":"2026-07-09","paginas":4},
 {"id":"DaVJbSjltiV","perfil":"levamaisjc",
  "titulo":"Leva Tudo & Leva Mais (03 a 05/07)",
  "banner":"Leva Mais Atacarejo João Câmara","segmento":"atacarejo",
  "inicio":"2026-07-03","fim":"2026-07-05","paginas":2},
 {"id":"DaIrAZzljbN","perfil":"levamaisjc",
  "titulo":"Fecha Mês com Economia (29 e 30/06)",
  "banner":"Leva Mais Atacarejo João Câmara","segmento":"atacarejo",
  "inicio":"2026-06-29","fim":"2026-06-30","paginas":2},
 {"id":"DaDQBrsg9vP","perfil":"levamaisjc",
  "titulo":"Ofertas do Açougue (26 a 28/06)",
  "banner":"Leva Mais Atacarejo João Câmara","segmento":"atacarejo",
  "inicio":"2026-06-26","fim":"2026-06-28","paginas":1},
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

# ---------- grava ----------
json.dump(actions,  open(path("data/actions.json"), "w", encoding="utf-8"),  ensure_ascii=False, indent=1)
json.dump(products, open(path("data/products.json"),"w", encoding="utf-8"),  ensure_ascii=False, indent=1)
json.dump(canon,    open(path("data/canon.json"),   "w", encoding="utf-8"),  ensure_ascii=False, indent=1)

print("OK — acoes:", len(actions), "| paginas produtos:", len(products), "| grupos canon:", len(canon))
print("Produtos novos ingeridos:", sum(len(newprod.get('%s_p%d'%(a['id'],i),[])) for a in NOVAS for i in range(1,a['paginas']+1)))
print("Grupos canonicos NOVOS:", len(log["novos"]), "| Encaixes em grupo existente:", len(log["merges"]))
