#!/usr/bin/env python3
"""Ingestão 27/07/2026 — janela da manhã.

Consome os produtos extraídos por visão desta rodada, monta ações/produtos/
canon com a MESMA canonicalização do pipeline (nrm_tokens/canon_add), esvazia
a fila e grava o resumo da notificação.

Descartados nesta janela (não entram):
  DbS500BTcfH   Favorito  — teaser Terça do Cashback (sem produtos/preços)
  DbS3tJnFpNo   Nordestão — cashback Beleza e Limpeza (sem preços)
  DbSg6FeEnjQ   Nordestão — oferta surpresa (produto censurado, sem preço)
  story_miram.  Miramar   — reposição do encarte 22–30/07 (gêmea já tem produtos)
  DbSmTLvG_UK   Mar Verm. — idêntico ao DbJzQS-G14k (mesmo flyer 24–30/07)
  assai_168590  Assaí     — Especial do Comerciante (B2B revenda)
"""
import json
import os
import re
import shutil
import unicodedata

BASE = os.path.dirname(os.path.abspath(__file__))
def path(*p): return os.path.join(BASE, *p)

HOJE = "2026-07-27"
NOISE = {"lata", "lta", "pct", "pcte", "pacote", "pet", "tb", "gf", "cada", "un",
         "und", "unid", "unidade", "sabores", "sabor", "fragrancias",
         "fragrancia", "tipos", "tipo"}


def nrm_tokens(s):
    s = unicodedata.normalize("NFD", str(s).lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    return tuple(sorted(t for t in s.split() if t and t not in NOISE))


def grid(items, xs, ys, w, h):
    """items: lista de (name,price,unit) por célula em ordem de leitura.
    xs: x de cada coluna; ys: [(y,linha_len)] por linha. Gera dicts posicionados."""
    out = []
    i = 0
    for (y, n) in ys:
        for c in range(n):
            if i >= len(items):
                break
            name, price, unit = items[i]
            out.append({"n": name, "p": price, "u": unit,
                        "x": xs[c], "y": y, "w": w, "h": h})
            i += 1
    return out


posts = []

# ---------------------------------------------------------------- Mar Vermelho
# Festival de Doces e Biscoitos (27 a 31/07) — flyer único de 1 página
mv_fest = grid([
    ("Bolinho Vitarella Treloso Sabores 40g", "1,59", "un"),
    ("Biscoito Bauducco Choco Biscuit ao Leite 80g", "6,99", "un"),
    ("Biscoito Recheado Treloso Sabores 120g", "1,79", "un"),
    ("Biscoito Recheado Oreo Sabores 90g", "3,49", "un"),
    ("Biscoito Maria ou Maizena Vitarella Tradicional 350g", "5,69", "un"),
    ("Biscoito Cookies Nestlé Sabores 60g", "2,69", "un"),
    ("Biscoito Amanteigado Amidovil Sortidos 270g", "5,29", "un"),
    ("Biscoito Piraquê Leite Maltado ou Chocolate 80g", "3,49", "un"),
    ("Biscoito Sol Hits Sabores 80g", "1,99", "un"),
    ("Biscoito Wafer Bauducco Sabores 70g", "1,49", "un"),
    ("Biscoito Recheado Mini Oreo 35g", "2,99", "un"),
    ("Biscoito Richester Animados Zoo com Cobertura de Chocolate 40g", "2,69", "un"),
], xs=[2, 27, 51, 75], ys=[(43, 4), (61, 4), (79, 4)], w=22, h=15)
posts.append({
    "shortcode": "DbRvPfPm8_s", "perfil": "marvermelhoatacado",
    "banner": "Mar Vermelho Atacado", "segmento": "atacarejo",
    "titulo": "Festival de Doces e Biscoitos Mar Vermelho (27 a 31/07)",
    "inicio": "2026-07-27", "fim": "2026-07-31", "fonte": "feed",
    "pages": {"DbRvPfPm8_s_p1": mv_fest},
})

# Grandes Ofertas MarZap — cards avulsos (24 a 30/07), 6 páginas
posts.append({
    "shortcode": "DbStPdYG-Nd", "perfil": "marvermelhoatacado",
    "banner": "Mar Vermelho Atacado", "segmento": "atacarejo",
    "titulo": "Grandes Ofertas MarZap Mar Vermelho (24 a 30/07)",
    "inicio": "2026-07-24", "fim": "2026-07-30", "fonte": "feed",
    "pages": {
        "DbStPdYG-Nd_p1": [{"n": "Arroz Parboilizado Laguna Tipo 1 1kg", "p": "2,99", "u": "un", "x": 14, "y": 30, "w": 60, "h": 52}],
        "DbStPdYG-Nd_p2": [{"n": "Frango a Passarinho Super Frango Congelado 1kg", "p": "10,49", "u": "un", "x": 16, "y": 32, "w": 55, "h": 48}],
        "DbStPdYG-Nd_p3": [{"n": "Açúcar Alegre Triturado 1kg", "p": "2,59", "u": "un", "x": 16, "y": 32, "w": 58, "h": 50}],
        "DbStPdYG-Nd_p4": [{"n": "Salgadinho Pippo's São Braz Sabores 30g", "p": "1,49", "u": "un", "x": 12, "y": 32, "w": 60, "h": 50}],
        "DbStPdYG-Nd_p5": [{"n": "Cerveja Eisenbahn Pilsen Lata 350ml", "p": "3,49", "u": "un", "x": 20, "y": 32, "w": 45, "h": 50}],
        "DbStPdYG-Nd_p6": [{"n": "Sabonete Rexona Antibacterial Fragrâncias 84g", "p": "2,19", "u": "un", "x": 14, "y": 33, "w": 55, "h": 45}],
    },
})

# ---------------------------------------------------------------- Corte Fácil
cf_p1 = grid([
    ("Flocão de Milho Gratícia 500g", "1,39", "un"),
    ("Leite UHT Integral Elegê 1L", "5,99", "un"),
    ("Leite em Pó LeitBom Integral 700g", "27,99", "un"),
    ("Café em Pó Blend 53 Almofada 250g", "11,69", "un"),
], xs=[8, 52], ys=[(33, 2), (58, 2)], w=42, h=22)
cf_p2 = grid([
    ("Manteiga D'Nata com Sal Pote 500g", "17,99", "un"),
    ("Empanados de Frango Sadia Steak Congelado 100g", "1,89", "un"),
    ("Macarrão Parafuso Estrela 400g", "3,49", "un"),
    ("Batata Mazid Pré-frita Congelada Corte Tradicional 2kg", "19,99", "un"),
], xs=[8, 52], ys=[(33, 2), (58, 2)], w=42, h=22)
posts.append({
    "shortcode": "DbSvNbFFtpo", "perfil": "cortefacil.atacarejo",
    "banner": "Corte Fácil Atacarejo", "segmento": "atacarejo",
    "titulo": "Segunda é Feira Corte Fácil (27/07)",
    "inicio": "2026-07-27", "fim": "2026-07-27", "fonte": "feed",
    "pages": {"DbSvNbFFtpo_p1": cf_p1, "DbSvNbFFtpo_p2": cf_p2},
})

# ---------------------------------------------------------------- Assaí (web)
a_p1 = grid([
    ("Leite Longa Vida Integral ou Desnatado Natville TP 1L", "6,29", "un"),
    ("Leite em Pó Piracanjuba Integral 200g", "6,99", "un"),
    ("Leite Condensado Betânia TP 395g", "5,59", "un"),
    ("Feijão Preto Camil 1kg", "5,79", "un"),
    ("Óleo de Soja Liza PET 900ml", "6,75", "un"),
    ("Feijão Carioca Kumê 1kg", "6,99", "un"),
    ("Açúcar Cristal Alegre 1kg", "2,59", "un"),
    ("Farinha de Trigo Tipo 1 Farina 1kg", "2,99", "un"),
], xs=[2, 27, 51, 75], ys=[(28, 4), (40, 4)], w=22, h=11)
a_p1 += grid([
    ("Macarrão Spaghetti Bonsabor 400g", "1,95", "un"),
    ("Macarrão Instantâneo Turma da Mônica Nissin Sabores 85g", "1,89", "un"),
    ("Biscoito Cream Cracker Tostadinha Vitarella 350g", "3,99", "un"),
    ("Biscoito Chocolate ao Leite Choco Biscuit Nestlé 78g", "5,99", "un"),
    ("Biscoito Amanteigado Jucurutu 250g", "4,19", "un"),
], xs=[2, 21, 40, 59, 78], ys=[(55, 5)], w=18, h=12)
a_p1 += grid([
    ("Café Família ou Extraforte São Braz Almofada 250g", "10,99", "un"),
    ("Flocão de Milho Premium Dona Clara 500g", "1,39", "un"),
    ("Arroz Tipo 1 São Joaquim 1kg", "3,99", "un"),
    ("Fraldinha Bovina Resfriada a Vácuo Masterboi", "39,90", "kg"),
    ("Filé de Peito de Frango Congelado Super Frango Bandeja 1kg", "16,80", "un"),
    ("Coxas e Sobrecoxas de Frango com Porção Dorsal Congeladas Lar", "7,90", "kg"),
], xs=[2, 18, 34, 50, 66, 82], ys=[(76, 6)], w=15, h=13)

a_p2 = grid([
    ("Biscoito Salgado Original ou Integral Piraquê 138g", "4,89", "un"),
    ("Biscoito Salgado Hits Sol Sabores 80g", "2,15", "un"),
    ("Bala Fini Tubes Sabores 80g", "6,69", "un"),
    ("Chocolate Hershey's 102g", "5,69", "un"),
], xs=[3], ys=[(29, 1), (37, 1), (54, 1), (66, 1)], w=15, h=7)
a_p2 += grid([
    ("Farinha de Trigo do Padeiro Saco 25kg", "74,90", "un"),
    ("Cesta Básica Assaí Kit 1 com 11 Itens", "55,90", "un"),
    ("Margarina com Sal Sabor Manteiga 70% Lipídios Puro Sabor Balde 15kg", "139,90", "un"),
    ("Molho de Tomate Bonare Sabores Sachê 1,7kg", "13,90", "un"),
    ("Café Solúvel Clássico Santa Clara Sachê 40g", "4,59", "un"),
    ("Farinha Láctea Nestlé 210g", "7,99", "un"),
    ("Bebida Láctea Power Whey 3 Corações TP 250ml", "6,49", "un"),
    ("Aveia em Flocos Regulares ou Finos Yoki Caixeta 170g", "3,09", "un"),
    ("Azeite Extravirgem Fiorentini ou Manos Alba Vidro 500ml", "24,90", "un"),
    ("Azeitonas Verdes com Caroços Vale Fértil Vidro 500g Drenado", "16,90", "un"),
    ("Molho de Tomate Tradicional Pomodoro Sachê 300g", "1,49", "un"),
    ("Milho-Verde ou Dueto Bonare Lata 170g Drenado", "3,19", "un"),
    ("Catchup Tambaú Frasco 380g", "4,29", "un"),
    ("Maionese Hellmann's Sachê 200g", "4,99", "un"),
    ("Sardinha em Óleo ou ao Molho de Tomate 88 Lata 75g Drenado", "4,99", "un"),
    ("Atum Ralado Natural ou em Óleo Coqueiro Lata 120g Drenado", "7,99", "un"),
    ("Água Mineral sem Gás Ster Bom PET 510ml", "0,79", "un"),
    ("Bebida Energética Mormaii PET 2L", "9,90", "un"),
    ("Vodka Intencion Garrafa 900ml", "19,90", "un"),
    ("Whisky Escocês Black & White Garrafa 1L", "53,90", "un"),
], xs=[24, 46, 68, 88], ys=[(13, 4), (30, 4), (45, 4), (60, 4), (73, 4)], w=17, h=11)
a_p2 += grid([
    ("Cerveja Pilsen Itaipava Lata 350ml", "2,49", "un"),
    ("Refrigerante Original Pepsi PET 1L", "4,29", "un"),
    ("Bebida Mista Del Valle Frut Sabores PET 1,5L", "6,39", "un"),
    ("Vinho Nacional Quinta do Morgado Tipos Garrafa 750ml", "12,90", "un"),
    ("Cachaça Caranguejo Lata 350ml", "2,99", "un"),
], xs=[3, 27, 46, 65, 84], ys=[(88, 5)], w=15, h=9)

a_p3 = grid([
    ("Frango Congelado Friato", "10,50", "kg"),
    ("Bisteca Suína Congelada Frimesa", "17,99", "kg"),
    ("Filé de Merluza Congelado Vitalmar Pacote 500g", "23,90", "un"),
    ("Linguiça Suína Congelada Seara Pacote 5kg", "84,95", "un"),
    ("Steak de Frango Empanado Recheado com Presunto e Queijo Seara 110g", "3,99", "un"),
    ("Hambúrguer de Carne de Frango e Suína Tradicional Congelado Rezende 36x56g", "31,90", "un"),
    ("Linguiça Tipo Calabresa Defumada Seara 2,5kg", "63,90", "un"),
    ("Salsicha para Hot-Dog Congelada Bom Todo 3kg", "17,85", "un"),
    ("Leite Fermentado Bob Esponja Elegê Sabores Pack 480g", "6,69", "un"),
    ("Iogurte Líquido Sabor Morango Betânia PET 1,25kg", "13,99", "un"),
    ("Iogurte Natural Betânia Sabores Copo 170g", "3,29", "un"),
    ("Bebida Láctea Polpa Betânia Sabores Bandeja 540g", "4,99", "un"),
    ("Pizza Congelada Rezende Sabores Caixeta 460g", "11,99", "un"),
    ("Lasanha Congelada Perdigão Sabores Pacote 600g", "13,99", "un"),
    ("Açaí Natural ou com Morango Açaí Canaã Pote 1L", "19,90", "un"),
    ("Pão de Forma Tradicional Massas Nordestinas Pacote 400g", "4,99", "un"),
    ("Manteiga com Sal Sertão Jucurutu Pote 500g", "22,90", "un"),
    ("Requeijão Cremoso Tradicional ou Light Betânia Pote 200g", "7,39", "un"),
    ("Sorvete Cremosíssimo Sabores Kibon Pote 1,5L", "19,89", "un"),
    ("Batata Congelada Fininha para Air Fryer McCain 1,2kg", "23,90", "un"),
    ("Queijo Tipo Parmesão Ralado Vigor Pacote 50g", "5,29", "un"),
    ("Pão de Queijo Tradicional Gosto Mineiro Pacote 400g", "6,90", "un"),
    ("Massa de Ravioli Mezzani Sabores Pacote 400g", "10,69", "un"),
    ("Queijo Tipo Mussarela Italac", "38,90", "kg"),
], xs=[3, 25, 47, 69], ys=[(13, 4), (28, 4), (43, 4), (58, 4), (73, 4), (88, 4)], w=18, h=12)

a_p4 = grid([
    ("Lava-Roupas em Pó Sonho Fragrâncias Pacote 400g", "2,29", "un"),
    ("Lava-Roupas Líquido OMO Fragrâncias Galão 5L", "44,90", "un"),
    ("Sabão em Barra Neutro Minuano Pack 5x160g", "7,99", "un"),
    ("Amaciante de Roupas Magic Sonho Galão Leve 5L Pague 4,5L", "21,90", "un"),
    ("Água Sanitária Clorito Galão 5L", "8,89", "un"),
    ("Lava-Louças Limpol Fragrâncias Frasco 500ml", "1,99", "un"),
    ("Desinfetante Dragão Fragrâncias Galão 5L", "10,90", "un"),
    ("Limpador Multiuso Dragão Fragrâncias Frasco 500ml", "3,49", "un"),
    ("Esponja de Aço Bombril Pacote 45g", "1,39", "un"),
    ("Inseticida Aerossol Raid Tipos Frasco 420ml", "14,90", "un"),
    ("Papel Higiênico Folha Dupla Max Pure Leve 16 Pague 15 Rolos 30m", "18,49", "un"),
    ("Sabonete Líquido Botanicals Lux Fragrâncias Refil 200ml", "4,89", "un"),
    ("Absorvente com Abas Noite e Dia Sempre Livre Tipos Pacote 32 Unidades", "21,90", "un"),
    ("Lenços Umedecidos Piquitucho Pacote 48 Unidades", "4,29", "un"),
    ("Fralda Descartável Pants Protect&Sec Personal Baby Tamanhos", "19,90", "un"),
    ("Shampoo Clear Men Tipos Frasco Leve 400ml Pague 330ml", "20,50", "un"),
    ("Sabonete Lux Fragrâncias 85g", "1,79", "un"),
    ("Desodorante Aerossol Nivea Fragrâncias Frasco 200ml", "14,50", "un"),
    ("Creme Dental Tripla Limpeza Completa Sorriso Caixeta 140g", "4,45", "un"),
    ("Kit Coloração Casting Creme Gloss L'Oréal Paris Cores", "26,90", "un"),
    ("Conjunto de Potes Conect Plasútil Kit com 5 Unidades", "17,90", "un"),
    ("Filme de PVC Wyda Rolo 28cmx30m", "6,89", "un"),
    ("Alimento para Gatos Sabor Carne e Frango Cat Mix Domus Pacote 1kg", "9,90", "un"),
    ("Papel Sulfite A4 Chamex Pacote 500 Folhas", "24,90", "un"),
    ("Pneu Aro 15 185/65 XBRI Fastway", "249,90", "un"),
], xs=[3, 22, 41, 60, 79], ys=[(13, 5), (28, 5), (45, 5), (62, 5), (80, 5)], w=18, h=12)

posts.append({
    "shortcode": "assai_168587-572", "perfil": "assai.com.br",
    "banner": "Assaí Atacadista", "segmento": "atacarejo",
    "titulo": "Giro da Economia Assaí (27 a 30/07)",
    "inicio": "2026-07-27", "fim": "2026-07-30", "fonte": "web",
    "link": "https://www.assai.com.br/ofertas/rio-grande-do-norte/assai-natal",
    "pages": {"assai_168587-572_p1": a_p1, "assai_168587-572_p2": a_p2,
              "assai_168587-572_p3": a_p3, "assai_168587-572_p4": a_p4},
})

# ================================================================ ingestão
actions = json.load(open(path("data/actions.json"), encoding="utf-8"))
products = json.load(open(path("data/products.json"), encoding="utf-8"))
canon = json.load(open(path("data/canon.json"), encoding="utf-8"))
fila = json.load(open(path("data/fila_novos.json"), encoding="utf-8"))
byshort = {p["shortcode"]: p for p in fila}

for f in ("data/actions.json", "data/products.json", "data/canon.json"):
    shutil.copy(path(f), path(f + ".bak-20260727"))

by_key = {}
for g in canon:
    k = nrm_tokens(g["n"])
    if k not in by_key or len(g["m"]) > len(by_key[k]["m"]):
        by_key[k] = g

log = {"novos": 0, "merges": 0}


def canon_add(name, unit, ref):
    k = nrm_tokens(name)
    g = by_key.get(k)
    if g is None:
        g = {"n": name, "u": unit, "m": [ref]}
        canon.append(g)
        by_key[k] = g
        log["novos"] += 1
    else:
        if ref not in g["m"]:
            g["m"].append(ref)
        log["merges"] += 1


existing_ids = {a["id"] for a in actions}
kept, total_prod, banners_novos = [], 0, {}

for post in posts:
    sc = post["shortcode"]
    if sc in existing_ids:
        print(f"[skip] ação {sc} já existe")
        continue
    paginas = []
    for key, items in post["pages"].items():
        if key in products:
            print(f"[skip] página {key} já em products.json")
            continue
        products[key] = items
        paginas.append(key + ".jpg")
        total_prod += len(items)
        for idx, it in enumerate(items):
            canon_add(it["n"], it.get("u", "un"), f"{key}#{idx}")
    if not paginas:
        print(f"[skip] {sc} sem páginas com produto")
        continue
    src = byshort.get(sc, {})
    actions.append({
        "id": sc,
        "perfil": post.get("perfil", src.get("perfil", "")),
        "titulo": post.get("titulo", ""),
        "banner": post["banner"],
        "segmento": post.get("segmento", src.get("segmento", "")),
        "inicio": post["inicio"],
        "fim": post["fim"],
        "carrossel": len(paginas) > 1,
        "shortcode": sc,
        "caption": src.get("caption", ""),
        "paginas": paginas,
        "adicionado_em": HOJE,
        "fonte": post.get("fonte") or src.get("fonte") or "feed",
        "link": post.get("link", src.get("link", "")),
    })
    existing_ids.add(sc)
    kept.append(sc)
    banners_novos[post["banner"]] = banners_novos.get(post["banner"], 0) + 1

json.dump(actions, open(path("data/actions.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
json.dump(products, open(path("data/products.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
json.dump(canon, open(path("data/canon.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
json.dump([], open(path("data/fila_novos.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

print("OK — ações novas:", len(kept), "| produtos:", total_prod,
      "| canon:", len(canon), f"({log['novos']} novos, {log['merges']} encaixes)")
print("Banners:", banners_novos)
