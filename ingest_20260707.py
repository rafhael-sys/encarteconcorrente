#!/usr/bin/env python3
# Ingestão da janela 07/07 — 2 ações novas (chocolate SuperFácil e achadinhas Favorito).
import json, shutil, sys, os

BASE = os.path.dirname(os.path.abspath(__file__))
def path(*p): return os.path.join(BASE, *p)

# backups
for f in ("data/actions.json", "data/products.json", "data/canon.json"):
    shutil.copy(path(f), path(f + ".bak-20260707-ingest"))

actions = json.load(open(path("data/actions.json"), encoding="utf-8"))
products = json.load(open(path("data/products.json"), encoding="utf-8"))
canon = json.load(open(path("data/canon.json"), encoding="utf-8"))

HOJE = "2026-07-07"

# ---- guarda: não duplicar ----
existing_ids = {a["id"] for a in actions}
for nid in ("DaflxIulaff", "DafjOXtDn-B"):
    if nid in existing_ids:
        sys.exit("ERRO: ação %s já existe" % nid)

# ---- captions (da fila) ----
cap_choc = ("🍫 Hoje é dia de celebrar quem deixa qualquer momento mais gostoso! 😍\n\n"
            "No Nordestão e no SuperFácil você encontra chocolates em oferta para adoçar o seu dia! "
            "Passe em uma de nossas lojas e aproveite! 💛\n\n#DiaMundialDoChocolate")
cap_fav = ("Hoje foi dia de fazer achadinhas no Favorito Varejo da Roberto Freire! 🤩✨ @favoritosuper \n\n"
           "As ofertas seguem válidas até o dia 30/06, então ainda dá tempo de aproveitar!\n\n"
           "E hoje também é dia de Terça do Cashback! 💸 Você recebe até 10% de volta no valor das suas compras. "
           "Ou seja, além de economizar com as ofertas, ainda ganha cashback para usar depois.\n\n"
           "Então não perde tempo! Corre pro Favorito e aproveita! 🛒💛")

# ---- produtos por página ----
prod_pages = {
    "DaflxIulaff_p1": [],
    "DaflxIulaff_p2": [{"n": "Bombom Sortido Nestlé Especialidades Caixa 220g", "p": "14,99", "u": "und", "x": 28, "y": 30, "w": 48, "h": 48}],
    "DaflxIulaff_p3": [{"n": "Chocolate Kit Kat ao Leite Sabores", "p": "3,49", "u": "und", "x": 30, "y": 28, "w": 42, "h": 46}],
    "DaflxIulaff_p4": [{"n": "Chocolate Recheio Crocante Garoto 90g", "p": "6,99", "u": "und", "x": 28, "y": 28, "w": 46, "h": 46}],
    "DaflxIulaff_p5": [{"n": "Chocolate ao Leite Alpino Pacote 80g", "p": "7,49", "u": "und", "x": 25, "y": 32, "w": 50, "h": 42}],
    "DaflxIulaff_p6": [{"n": "Bombom Sortido Garoto Caixa 220g", "p": "12,99", "u": "und", "x": 28, "y": 30, "w": 48, "h": 48}],

    "DafjOXtDn-B_p1": [{"n": "Leite em Pó Integral Aurora 750g", "p": "25,99", "u": "cada (de R$ 29,39)", "x": 13, "y": 5, "w": 33, "h": 33}],
    "DafjOXtDn-B_p2": [{"n": "Pizza Lebon 400g Sabores", "p": "13,89", "u": "cada (de R$ 15,90)", "x": 45, "y": 2, "w": 52, "h": 50}],
    "DafjOXtDn-B_p3": [{"n": "Filé de Peixe Tilápia Riviera 800g", "p": "36,99", "u": "cada (de R$ 41,99)", "x": 38, "y": 1, "w": 58, "h": 63}],
    "DafjOXtDn-B_p4": [{"n": "Detergente Líquido Brilux 500ml Fragrâncias", "p": "1,99", "u": "cada (de R$ 2,49)", "x": 24, "y": 37, "w": 44, "h": 37}],
    "DafjOXtDn-B_p5": [{"n": "Amaciante de Roupas Sonho Magic 2L (Leve 2L Pague 1,8L)", "p": "11,99", "u": "cada", "x": 28, "y": 47, "w": 33, "h": 40}],
    "DafjOXtDn-B_p6": [{"n": "Achocolatado em Pó Nescau 550g", "p": "15,99", "u": "cada", "x": 56, "y": 40, "w": 33, "h": 30}],
    "DafjOXtDn-B_p7": [
        {"n": "Carne Suína Paleta kg", "p": "13,99", "u": "kg (de R$ 18,99)", "x": 13, "y": 58, "w": 38, "h": 40},
        {"n": "Carne Bovina Peito com Osso kg", "p": "29,90", "u": "kg (de R$ 31,50)", "x": 60, "y": 56, "w": 33, "h": 38},
    ],
    "DafjOXtDn-B_p8": [{"n": "Queijo Coalho ou Manteiga Freezer kg", "p": "38,99", "u": "kg (de R$ 44,90)", "x": 18, "y": 4, "w": 52, "h": 53}],
    "DafjOXtDn-B_p9": [{"n": "Iogurte Batavo Pense Zero 1150g Sabores", "p": "16,99", "u": "cada (de R$ 18,99)", "x": 44, "y": 13, "w": 44, "h": 47}],
    "DafjOXtDn-B_p10": [{"n": "Leite Condensado Itambé Semidesnatado 395g", "p": "5,49", "u": "cada (de R$ 7,89)", "x": 11, "y": 40, "w": 36, "h": 35}],
    "DafjOXtDn-B_p11": [{"n": "Croissant Nutri 400g Frango ou Folhado Nutri 400g Calabresa ou Queijada Nutri 400g", "p": "15,90", "u": "cada (de R$ 19,90)", "x": 14, "y": 3, "w": 62, "h": 55}],
}
for k, v in prod_pages.items():
    if k in products:
        sys.exit("ERRO: página %s já em products.json" % k)
    products[k] = v

# ---- canon: (ref) -> grupo existente por nome exato, ou grupo novo ----
by_name = {g["n"]: g for g in canon}
def add_to_group(name, ref):
    g = by_name.get(name)
    if g is None:
        sys.exit("ERRO: grupo canônico não encontrado: %r" % name)
    if ref not in g["m"]:
        g["m"].append(ref)

def new_group(name, unit, ref):
    if name in by_name:
        sys.exit("ERRO: grupo novo já existe: %r" % name)
    g = {"n": name, "u": unit, "m": [ref]}
    canon.append(g); by_name[name] = g

# existentes
add_to_group("Bombom Especialidades Nestlé 220g", "DaflxIulaff_p2#0")
add_to_group("Bombom Garoto Sortido Caixa 220g", "DaflxIulaff_p6#0")
add_to_group("Leite em Pó Aurora Integral 750g", "DafjOXtDn-B_p1#0")
add_to_group("Pizza Lebon 400g Sabores", "DafjOXtDn-B_p2#0")
add_to_group("Filé de Tilápia Riviera 800g", "DafjOXtDn-B_p3#0")
add_to_group("Detergente Líquido Brilux 500ml", "DafjOXtDn-B_p4#0")
add_to_group("Amaciante de Roupas Sonho Leve 2L Pague 1,8L", "DafjOXtDn-B_p5#0")
add_to_group("Achocolatado em Pó Nescau 550g", "DafjOXtDn-B_p6#0")
add_to_group("Queijo de Manteiga ou Coalho Freezer KG ou Fatiado", "DafjOXtDn-B_p8#0")
add_to_group("Iog Batavo Pense Zero 1150g Sabores", "DafjOXtDn-B_p9#0")
add_to_group("Croissant Nutri 400g Frango ou Folhado Nutri 400g Calabresa ou Queijada Nutri 400g", "DafjOXtDn-B_p11#0")
# novos
new_group("Chocolate Kit Kat ao Leite Sabores", "un", "DaflxIulaff_p3#0")
new_group("Chocolate Garoto Recheado Crocante 90g", "un", "DaflxIulaff_p4#0")
new_group("Chocolate ao Leite Alpino 80g", "un", "DaflxIulaff_p5#0")
new_group("Carne Suína Paleta kg", "kg", "DafjOXtDn-B_p7#0")
new_group("Carne Bovina Peito com Osso kg", "kg", "DafjOXtDn-B_p7#1")
new_group("Leite Condensado Itambé Semidesnatado 395g", "un", "DafjOXtDn-B_p10#0")

# ---- ações ----
actions.append({
    "id": "DaflxIulaff", "perfil": "superfacilatacado", "titulo": "Dia do Chocolate",
    "banner": "SuperFácil Atacado", "segmento": "atacarejo",
    "inicio": "2026-07-07", "fim": "2026-07-07", "carrossel": True, "shortcode": "DaflxIulaff",
    "caption": cap_choc,
    "paginas": ["DaflxIulaff_p%d.jpg" % i for i in range(1, 7)],
    "adicionado_em": HOJE,
})
actions.append({
    "id": "DafjOXtDn-B", "perfil": "favoritosuper", "titulo": "Achadinhas Favorito Varejo (Roberto Freire)",
    "banner": "Favorito Super / Atacado Favorito", "segmento": "varejo",
    "inicio": "2026-06-30", "fim": "2026-07-01", "carrossel": True, "shortcode": "DafjOXtDn-B",
    "caption": cap_fav,
    "paginas": ["DafjOXtDn-B_p%d.jpg" % i for i in range(1, 12)],
    "adicionado_em": HOJE,
})

json.dump(actions, open(path("data/actions.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
json.dump(products, open(path("data/products.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
json.dump(canon, open(path("data/canon.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("OK — ações:", len(actions), "| páginas produtos:", len(products), "| grupos canon:", len(canon))
