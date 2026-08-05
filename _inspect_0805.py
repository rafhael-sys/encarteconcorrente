"""Inspeção da janela 2026-08-05: valida extrações e mostra gêmeas."""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))


def p(*a):
    return os.path.join(BASE, *a)


SCS = [
    "Dbpxg74mygO", "DbpBQTSmyUs", "Dbo_p6Sm4Au", "DbohF-IsL02",
    "atacadao_d539bc59f3", "atacadao_f4e37f7117", "atacadao_28c555d715",
    "atacadao_75d8349b61", "story_miramarsupermercado",
    "story_supernordestaonatal", "story_redemaisrn",
    "story_cortefacil.atacarejo", "story_marvermelhoatacado",
]

print("=== Extrações w0805 ===")
for sc in SCS:
    fn = p("data/_extract", f"w0805_{sc}.json")
    if not os.path.exists(fn):
        print(f"  FALTA: {sc}")
        continue
    d = json.load(open(fn, encoding="utf-8"))
    tot = sum(len(v) for v in d.values())
    npg = sum(1 for v in d.values() if v)
    print(f"  {sc}: {tot} produtos em {npg}/{len(d)} páginas com preço")

prod = json.load(open(p("data/products.json"), encoding="utf-8"))
act = {a["id"]: a for a in json.load(open(p("data/actions.json"), encoding="utf-8"))}


def show(aid):
    a = act.get(aid)
    if not a:
        print(f"  {aid}: NAO EXISTE")
        return
    names = []
    for pg in a["paginas"]:
        for it in prod.get(pg[:-4], []):
            names.append(f"{it['n']}={it.get('p')}")
    print(f"=== {aid} | {a['titulo']} | {a['inicio']}..{a['fim']} | {len(names)} prod")
    for n in names:
        print("   -", n)


print()
for aid in ["Dbolj3xn03X", "Dbosa-HATU9"]:
    show(aid)

print()
a = act.get("story_mirassolatacado_20260804")
if a:
    tot = sum(len(prod.get(pg[:-4], [])) for pg in a["paginas"])
    print(f"story_mirassolatacado_20260804 | {a['inicio']}..{a['fim']} | "
          f"{tot} produtos | {len(a['paginas'])} páginas")
