#!/usr/bin/env python3
# Ingestão da janela 08/07/2026.
import json, shutil, os, sys, unicodedata, re

BASE = os.path.dirname(os.path.abspath(__file__))
def path(*p): return os.path.join(BASE, *p)

HOJE = "2026-07-08"

# ---------- normalização p/ canon ----------
# Palavras de embalagem/ruído (a lista do CLAUDE.md + plurais/óbvios).
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
newprod  = json.load(open(path("data/_ingest_20260708_produtos.json"), encoding="utf-8"))
cap = {p["shortcode"]: p.get("caption","") for p in fila}

# ---------- backups ----------
for f in ("data/actions.json","data/products.json","data/canon.json"):
    shutil.copy(path(f), path(f + ".bak-20260708-ingest"))

# ---------- índice canon por chave normalizada (maior grupo vence) ----------
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

# ---------- definição das ações novas ----------
NOVAS = [
 {"id":"Dag1cX2DH80","perfil":"favoritosuper","titulo":"Ofertas de Copa — Torcida Favorito (Varejo)",
  "banner":"Favorito Super / Atacado Favorito","segmento":"varejo",
  "inicio":"2026-07-08","fim":"2026-07-14","paginas":4},
 {"id":"Dagn6LTDv1h","perfil":"favoritosuper","titulo":"Quarta e Quinta Verde (Hortifrúti)",
  "banner":"Favorito Super / Atacado Favorito","segmento":"varejo",
  "inicio":"2026-07-08","fim":"2026-07-09","paginas":1},
 {"id":"DagmaEAG6yg","perfil":"marvermelhoatacado","titulo":"Quarta da Padaria — MarZap",
  "banner":"Mar Vermelho Atacado","segmento":"atacarejo",
  "inicio":"2026-07-08","fim":"2026-07-08","paginas":1},
 {"id":"DagfUvTGOAj","perfil":"supernordestaonatal","titulo":"Hortifrúti Fresquinho",
  "banner":"Super Nordestão","segmento":"varejo",
  "inicio":"2026-07-08","fim":"2026-07-09","paginas":2},
 {"id":"atacadao_e3f033ee2a","perfil":"atacadao.com.br","titulo":"Boa do Dia",
  "banner":"Atacadão","segmento":"atacarejo",
  "inicio":"2026-07-08","fim":"2026-07-08","paginas":1,"fonte":"web",
  "link":"https://www.atacadao.com.br/loja/natal-sul"},
 {"id":"atacadao_c44a80f301","perfil":"atacadao.com.br","titulo":"Açougue / Padaria / Frios e Fatiados",
  "banner":"Atacadão","segmento":"atacarejo",
  "inicio":"2026-07-07","fim":"2026-07-09","paginas":1,"fonte":"web",
  "link":"https://www.atacadao.com.br/loja/natal-sul"},
 {"id":"atacadao_5b4604ae3d","perfil":"atacadao.com.br","titulo":"App Meu Atacadão",
  "banner":"Atacadão","segmento":"atacarejo",
  "inicio":"2026-07-07","fim":"2026-07-09","paginas":1,"fonte":"web",
  "link":"https://www.atacadao.com.br/loja/natal-sul"},
]

existing_ids = {a["id"] for a in actions}
log = {"novos": [], "merges": []}

for a in NOVAS:
    if a["id"] in existing_ids:
        sys.exit("ERRO: ação %s já existe" % a["id"])
    npag = a["paginas"]
    # produtos por página + canon
    for i in range(1, npag+1):
        key = "%s_p%d" % (a["id"], i)
        if key in products:
            sys.exit("ERRO: página %s já em products.json" % key)
        items = newprod.get(key, [])
        products[key] = items
        for idx, it in enumerate(items):
            canon_add(it["n"], it.get("u","un"), "%s#%d" % (key, idx), log)
    # objeto ação
    act = {
        "id": a["id"], "perfil": a["perfil"], "titulo": a["titulo"],
        "banner": a["banner"], "segmento": a["segmento"],
        "inicio": a["inicio"], "fim": a["fim"], "carrossel": npag > 1,
        "shortcode": a["id"], "caption": cap.get(a["id"], a["titulo"]),
        "paginas": ["%s_p%d.jpg" % (a["id"], i) for i in range(1, npag+1)],
        "adicionado_em": HOJE,
    }
    if a.get("fonte"):
        act["fonte"] = a["fonte"]; act["link"] = a["link"]
    actions.append(act)

# ---------- grava ----------
json.dump(actions,  open(path("data/actions.json"), "w", encoding="utf-8"),  ensure_ascii=False, indent=1)
json.dump(products, open(path("data/products.json"),"w", encoding="utf-8"),  ensure_ascii=False, indent=1)
json.dump(canon,    open(path("data/canon.json"),   "w", encoding="utf-8"),  ensure_ascii=False, indent=1)

print("OK — ações:", len(actions), "| páginas produtos:", len(products), "| grupos canon:", len(canon))
print("Produtos novos ingeridos:", sum(len(newprod.get('%s_p%d'%(a['id'],i),[])) for a in NOVAS for i in range(1,a['paginas']+1)))
print("Grupos canônicos NOVOS:", len(log["novos"]), "| Encaixes em grupo existente:", len(log["merges"]))
print("\n--- MERGES (produto novo -> grupo existente) ---")
for name, grp, ref in log["merges"]:
    print(f"  [{ref}] {name!r}\n        -> {grp!r}")
