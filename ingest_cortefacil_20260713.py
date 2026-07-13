#!/usr/bin/env python3
# Corte Fácil Atacarejo — "Segunda é Feira" (13/07/2026), carrossel capa+ofertas.
# A API do Instagram RECUSA este perfil (web_profile_info devolve {"status":"ok"}
# vazio), então NÃO dá para coletar automaticamente. Extraído dos prints enviados
# pelo usuário. Sem arquivos de imagem: o build_painel embute os produtos mesmo
# sem a foto (só o visor do encarte fica sem imagem); os preços entram na Incidência.
import json, shutil, os, math, unicodedata, re

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
def grid(n, ncols=2, ytop=13, ybot=96):
    nrows = math.ceil(n/ncols); colw = 94/ncols; rowh = (ybot-ytop)/nrows
    return [(round(3+(i%ncols)*colw), round(ytop+(i//ncols)*rowh),
             round(colw-2), round(rowh-2)) for i in range(n)]

PAGINAS = {
 "cortefacil_segunda_20260713_p1": [
  ("Aveia Yoki Flocos Finos 170g","2,99","un"),
  ("Leite em Pó Integral Betânia 200g","6,69","un"),
  ("Café Almofada Marata 250g","11,89","un"),
  ("Bebida Láctea UHT Pirakids Chocolate 1L","7,99","un"),
 ],
 "cortefacil_segunda_20260713_p2": [
  ("Requeijão Cremoso Sertão Jucurutu Tradicional 400g","12,99","un"),
  ("Margarina Puro Sabor com Sal 500g","4,99","un"),
  ("Lasanha Aurora Congelada 600g","13,99","un"),
  ("Lanche de Frango Bom Todo","12,49","kg"),
 ],
}

actions  = json.load(open(path("data/actions.json")))
products = json.load(open(path("data/products.json")))
canon    = json.load(open(path("data/canon.json")))
for f in ("data/actions.json","data/products.json","data/canon.json"):
    shutil.copy(path(f), path(f + ".bak-cortefacil"))

by_key = {}
for g in canon:
    k = nrm_tokens(g["n"])
    if k not in by_key or len(g["m"]) > len(by_key[k]["m"]): by_key[k] = g
novos = merges = 0
def canon_add(name, unit, ref):
    global novos, merges
    k = nrm_tokens(name); g = by_key.get(k)
    if g is None:
        g = {"n":name,"u":unit,"m":[ref]}; canon.append(g); by_key[k]=g; novos+=1
    else:
        if ref not in g["m"]: g["m"].append(ref)
        merges += 1

SC = "cortefacil_segunda_20260713"
if SC in {a["id"] for a in actions}: raise SystemExit("já existe")
tot = 0
for key, items in PAGINAS.items():
    boxes = grid(len(items))
    products[key] = [{"n":n,"p":p,"u":u,"x":x,"y":y,"w":w,"h":h}
                     for (n,p,u),(x,y,w,h) in zip(items, boxes)]
    tot += len(items)
    for idx,(n,p,u) in enumerate(items): canon_add(n,u,f"{key}#{idx}")

actions.append({
    "id": SC, "perfil": "cortefacil.atacarejo", "titulo": "Segunda é Feira (13/07)",
    "banner": "Corte Fácil Atacarejo", "segmento": "atacarejo",
    "inicio": "2026-07-13", "fim": "2026-07-13", "carrossel": True, "shortcode": SC,
    "caption": "Segunda é dia de economia no Corte Fácil Atacarejo! Ofertas válidas 13/07.",
    "paginas": [f"{k}.jpg" for k in PAGINAS], "adicionado_em": HOJE, "fonte": "manual", "link": "",
})

json.dump(actions,  open(path("data/actions.json"),"w"),  ensure_ascii=False, indent=1)
json.dump(products, open(path("data/products.json"),"w"), ensure_ascii=False, indent=1)
json.dump(canon,    open(path("data/canon.json"),"w"),    ensure_ascii=False, indent=1)
print(f"OK — Corte Fácil: {tot} produtos | canon +{novos} novos, {merges} encaixes | ações={len(actions)}")
