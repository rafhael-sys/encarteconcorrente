#!/usr/bin/env python3
"""Ingestão 28/07/2026 — janela da manhã.

Consome os produtos extraídos por visão desta rodada, monta ações/produtos/
canon com a MESMA canonicalização do pipeline (nrm_tokens/canon_add), esvazia
a fila e grava o resumo da notificação.

Aprovados nesta janela:
  atacadao_3b9105b675  Atacadão — Boa do Dia (Só Terça 28/07), web
  atacadao_806f2b524a  Atacadão — Super Fim de Mês (28 a 30/07), web
  atacadao_dc70699b7b  Atacadão — Especial Açougue (28 e 29/07), web
  story_supernordestaonatal_20260728  Super Nordestão — Cerveja Spaten (promo de story)

Descartados nesta janela (não entram):
  DbVLMNWGzLU  Mar Vermelho — MarZap: os 6 itens já estão no flyer DbJzQS-G14k (24-30/07)
  story_marvermelhoatacado_20260728  Mar Vermelho — mesmo MarZap (gêmea do carrossel/flyer)
  DbVEHMEm7BU  Mar Vermelho — institucional Dia do Agricultor (sem preços)
  story_miramarsupermercado_20260728  Miramar — reposição MIRA AQUI 22-30/07 (gêmea _20260722)
  story_cortefacil.atacarejo_20260728 Corte Fácil — reposição Festival dos Queijos (gêmea _20260727)
  story_redemaisrn_20260728  Rede Mais — Linguiça Frimesa já no DbCEgdfj_vF (21-28/07)
  story_redesupercop_20260728  Rede Supercop — frame de vídeo (sem produto/preço)
"""
import json
import os
import re
import shutil
import unicodedata

BASE = os.path.dirname(os.path.abspath(__file__))
def path(*p): return os.path.join(BASE, *p)

HOJE = "2026-07-28"
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

# ============================================================ Atacadão (web)
# ---- Boa do Dia (Só Terça 28/07) — 1 página, layout irregular
boa = [
    {"n": "Mamão Comum", "p": "3,49", "u": "kg", "x": 5, "y": 26, "w": 24, "h": 14},
    {"n": "Batata Lavada", "p": "4,99", "u": "kg", "x": 52, "y": 26, "w": 22, "h": 14},
    {"n": "Coxa de Frango Sadia Congelada Bandeja 1kg", "p": "11,49", "u": "un", "x": 7, "y": 45, "w": 22, "h": 14},
    {"n": "Hambúrguer Jundiaí Congelado Carne Bovina/Frango Caixeta 36x56g", "p": "19,90", "u": "un", "x": 51, "y": 46, "w": 25, "h": 13},
    {"n": "Macarrão Comum Lili Espaguete Fino Pacote 400g", "p": "1,89", "u": "un", "x": 6, "y": 64, "w": 17, "h": 16},
    {"n": "Lava Roupas Líquido Urca Bombona 5L", "p": "19,90", "u": "un", "x": 40, "y": 64, "w": 17, "h": 16},
    {"n": "Detergente Líquido Dragão Frasco 500ml", "p": "1,39", "u": "un", "x": 72, "y": 64, "w": 17, "h": 16},
]
posts.append({
    "shortcode": "atacadao_3b9105b675", "perfil": "atacadao.com.br",
    "banner": "Atacadão", "segmento": "atacarejo",
    "titulo": "Boa do Dia Atacadão (Só Terça 28/07)",
    "inicio": "2026-07-28", "fim": "2026-07-28", "fonte": "web",
    "link": "https://www.atacadao.com.br/loja/natal-sul",
    "pages": {"atacadao_3b9105b675_p1": boa},
})

# ---- Especial Açougue (28 e 29/07) — 1 página, grade 5x4 (preço por quilo)
acg = grid([
    ("Coxa de Frango Resfriada", "11,90", "kg"),
    ("Meio da Asa de Frango Resfriada", "17,50", "kg"),
    ("Asa de Frango Resfriada", "13,50", "kg"),
    ("Coxinha da Asa de Frango Resfriada", "17,50", "kg"),
    ("Frango Inteiro Resfriado", "10,50", "kg"),
    ("Sobrecoxa de Frango Resfriada", "11,90", "kg"),
    ("Carne Bovina Acém sem Osso Reserva Resfriada", "35,90", "kg"),
    ("Carne Bovina Bife de Patinho Reserva Resfriada", "39,90", "kg"),
    ("Carne Bovina de Sol Coxão Mole Resfriada", "43,90", "kg"),
    ("Carne Bovina Coxão Mole Reserva Resfriada", "39,90", "kg"),
    ("Carne Bovina Músculo Reserva Resfriada", "29,90", "kg"),
    ("Carne Bovina Acém com Osso Reserva Resfriada", "26,90", "kg"),
    ("Carne Suína Bisteca Fatiada Congelada", "13,90", "kg"),
    ("Carne Bovina Peito com Osso Reserva Resfriada", "26,50", "kg"),
    ("Carne Bovina Bisteca de Acém Reserva Resfriada", "26,50", "kg"),
    ("Bucho Bovino Reserva Resfriado", "18,90", "kg"),
    ("Carne Bovina Chambaril Dianteiro Reserva Resfriada", "27,90", "kg"),
    ("Carne Bovina Costela Ripa Reserva Resfriada", "22,90", "kg"),
    ("Fígado Bovino Reserva Resfriado", "12,80", "kg"),
    ("Carne Bovina com Osso Paleta Reserva Resfriada", "27,50", "kg"),
], xs=[4, 24, 44, 63, 82], ys=[(27, 5), (45, 5), (63, 5), (80, 5)], w=16, h=9)
posts.append({
    "shortcode": "atacadao_dc70699b7b", "perfil": "atacadao.com.br",
    "banner": "Atacadão", "segmento": "atacarejo",
    "titulo": "Especial Açougue Atacadão (28 e 29/07)",
    "inicio": "2026-07-28", "fim": "2026-07-29", "fonte": "web",
    "link": "https://www.atacadao.com.br/loja/natal-sul",
    "pages": {"atacadao_dc70699b7b_p1": acg},
})

# ---- Super Fim de Mês (28 a 30/07) — 5 páginas
# p1: HORTIFRÚTI + AÇOUGUE
fm_p1 = grid([
    ("Cebola Branca", "5,69", "kg"),
    ("Batata Lavada", "4,99", "kg"),
    ("Brócolis Japonês", "6,99", "un"),
    ("Mexerica Comum", "7,99", "kg"),
    ("Mamão Comum", "3,49", "kg"),
    ("Abacate", "3,89", "kg"),
    ("Maçã Nacional Gala", "5,69", "kg"),
    ("Melão Amarelo", "2,89", "kg"),
    ("Batata Doce", "3,99", "kg"),
    ("Ovo Branco Grande PVC Bandeja 20 unidades", "9,89", "un"),
], xs=[5, 25, 44, 63, 82], ys=[(37, 5), (60, 5)], w=15, h=13)
fm_p1 += grid([
    ("Carne Bovina Coxão Mole Friboi Porcionada Resfriada", "35,50", "kg"),
    ("Carne Bovina Cupim Porcionada Friboi Resfriada", "36,50", "kg"),
    ("Fígado Bovino Friboi Congelado", "12,80", "kg"),
    ("Carne Bovina Paleta Porcionada Friboi Resfriada", "27,90", "kg"),
    ("Carne Bovina Picanha Bordon Resfriada Fatiada", "46,50", "kg"),
], xs=[5, 25, 44, 63, 82], ys=[(86, 5)], w=15, h=9)

# p2: FRIOS & CONGELADOS (5 linhas x 3 colunas)
fm_p2 = grid([
    ("Peito de Frango Copacol Congelado", "9,99", "kg"),
    ("Frango à Passarinho Copacol Congelado Pacote 800g", "8,59", "un"),
    ("Coxa com Sobrecoxa de Frango Friato Congelada", "8,49", "kg"),
    ("Hambúrguer Faroeste Aurora Congelado Misto Caixeta 36x56g", "33,98", "un"),
    ("Salsicha Hot Dog Natto Resfriada Pacote 3kg", "23,50", "un"),
    ("Lanche de Frango Tony Resfriado", "13,90", "kg"),
    ("Margarina Claybom Resfriada com Sal Pote 250g", "2,49", "un"),
    ("Leite Longa Vida Natville Integral ou Desnatado TP 1L", "5,99", "un"),
    ("Margarina Primor 60% Lipídios com Sal Balde 3kg", "27,89", "un"),
    ("Açaí Ster Bom Congelado Mix Tradicional Pote 1L", "19,98", "un"),
    ("Polpa de Fruta Canaã Congelada Caju/Goiaba/Manga Unidade 100g", "0,69", "un"),
    ("Sorvete Bulnez Congelado Pote 1L", "11,98", "un"),
    ("Bebida Láctea Betânia Bat Gut Resfriado", "5,29", "un"),
    ("Cream Cheese Catupiry Resfriado Bisnaga 1,2kg", "49,90", "un"),
    ("Manteiga Itacolomy Resfriada com Sal Pote 500g", "24,90", "un"),
], xs=[2, 35, 68], ys=[(30, 3), (45, 3), (58, 3), (72, 3), (86, 3)], w=15, h=10)

# p3: MERCEARIA (4 linhas x 5 colunas)
fm_p3 = grid([
    ("Arroz Mariano Parboilizado Tipo 1 Pacote 1kg", "3,39", "un"),
    ("Azeite de Oliva Gomes da Costa Extra Virgem Vidro 500ml", "24,90", "un"),
    ("Farinha de Trigo Finna Tipo 1 Pacote 1kg", "3,69", "un"),
    ("Feijão Carioca Bulnez Tipo 1 Pacote 1kg", "8,99", "un"),
    ("Óleo de Soja Liza PET 900ml", "6,99", "un"),
    ("Biscoito Choco Biscuit Bauducco Pacote 80g", "6,89", "un"),
    ("Macarrão Comum Aliança Espaguete Pacote 400g", "1,95", "un"),
    ("Macarrão Comum Vitamassa Talharim Ninho Pacote 300g", "4,89", "un"),
    ("Bombom Neugebauer Amor Carioca Caixeta 200g", "9,49", "un"),
    ("Chocolate Granulado Mavalério Pacote 1,010kg", "16,99", "un"),
    ("Biscoito Recheado Oreo Embalagem Econômica Multipack 270g", "8,99", "un"),
    ("Ketchup Quero Tradicional/Picante PET 400g", "4,80", "un"),
    ("Maionese Hellmann's Sachê 200g", "4,79", "un"),
    ("Molho de Tomate Julieta Tradicional Sachê 310g", "0,99", "un"),
    ("Café Nordestino Vácuo/Almofada Pacote 250g", "11,98", "un"),
    ("Achocolatado em Pó 3 Corações Chocolatto Pacote 900g", "21,98", "un"),
    ("Batata Palha Gratícia Pacote 400g", "12,99", "un"),
    ("Aveia Yoki Flocos Finos/Flocos Caixeta 170g", "2,99", "un"),
    ("Amendoim Santa Helena Mendorato Pacote 60x24g", "29,40", "un"),
    ("Leite de Coco Sococo Tradicional TP 200ml", "5,49", "un"),
], xs=[4, 24, 44, 64, 84], ys=[(30, 5), (48, 5), (66, 5), (83, 5)], w=15, h=13)

# p4: BEBIDAS + AUTOMOTIVO & PET SHOP & BAZAR
fm_p4 = grid([
    ("Energético Red Bull Energy Drink Lata 250ml", "8,39", "un"),
    ("Água Mineral Petrópolis com Gás PET 500ml", "1,25", "un"),
    ("Refrigerante Coca-Cola e Kuat Pack 2x2L", "16,99", "un"),
    ("Refrigerante Coca-Cola Zero Açúcar PET 2L", "9,99", "un"),
    ("Refrigerante Refri Indaiá Mini PET 250ml", "1,19", "un"),
    ("Refrigerante Pepsi Cola PET 1L", "3,79", "un"),
    ("Isotônico Powerade PET 500ml", "4,99", "un"),
    ("Bebida Adoçada Guarafit Açaí e Guaraná Copo 290ml", "1,19", "un"),
    ("Cerveja Amstel Sleek Lata 350ml", "3,19", "un"),
    ("Cachaça Caranguejo Garrafa 980ml", "8,99", "un"),
    ("Vinho Casa Rodrigues Tinto Suave Garrafa 1L", "15,90", "un"),
    ("Vodka Smirnoff PET 1,75L", "44,90", "un"),
    ("Brandy Macieira Garrafa 700ml", "49,90", "un"),
    ("Campari Bitter Garrafa 998ml", "54,90", "un"),
    ("Tequila Jose Cuervo Silver Garrafa 750ml", "119,90", "un"),
], xs=[4, 24, 44, 64, 84], ys=[(35, 5), (55, 5), (75, 5)], w=15, h=13)
fm_p4 += grid([
    ("Guardanapo de Papel Malu 21cmx23cm Pacote 50 unidades", "1,05", "un"),
    ("Folha de Alumínio Wyda 30cm x 4m Rolo", "3,49", "un"),
    ("Pneu Sumitomo 185/65 R14 BC20 Unidade", "269,00", "un"),
    ("Saco para Lixo Embalixo Super Econômico 15L/30L Rolo 100/50 unidades", "8,90", "un"),
    ("Alimento para Cães Pedigree Raças Pequenas Sachê 100g", "2,69", "un"),
], xs=[4, 24, 44, 64, 84], ys=[(90, 5)], w=15, h=8)

# p5: HIGIENE PESSOAL & PERFUMARIA + LIMPEZA
fm_p5 = grid([
    ("Absorvente Noturno Always Seca com Abas Pacote 32 unidades", "19,90", "un"),
    ("Aparelho de Barbear Gillette Prestobarba 2 UltraGrip Blister 2 unidades", "5,79", "un"),
    ("Shampoo Pantene Frasco 400ml", "23,90", "un"),
    ("Desodorante em Creme Above Pote 50g", "3,49", "un"),
    ("Creme Dental Colgate Tripla Ação Menta Original/Hortelã Tubo 90g", "4,99", "un"),
    ("Fralda Descartável Huggies Rápida Absorção Pacote", "65,00", "un"),
    ("Kit Muito Mais Shampoo 1L + Condicionador 1L", "23,50", "un"),
    ("Papel Higiênico Personal Vip KM FDAQ 50m Pacote 20 rolos", "48,00", "un"),
    ("Sabonete Protex Unidade 85g", "2,89", "un"),
    ("Protetor Diário Delicacy Pacote 50 unidades", "6,59", "un"),
    ("Toalha Umedecida Piquitucho Pacote 60 unidades", "4,29", "un"),
    ("Enxaguante Bucal Colgate Plax Fresh Mint Frasco 500ml", "11,50", "un"),
    ("Tintura Imédia Excellence Kit", "29,90", "un"),
    ("Creme de Tratamento para Cabelo Elseve Pote 300g", "25,90", "un"),
    ("Sabonete Líquido Harrop Erva Doce/Lavanda Frasco 2L", "19,90", "un"),
], xs=[4, 24, 44, 64, 84], ys=[(26, 5), (43, 5), (60, 5)], w=15, h=13)
fm_p5 += grid([
    ("Amaciante para Roupas Concentrado Downy Frasco 500ml", "9,90", "un"),
    ("Detergente Líquido Ypê Neutro/Clear Bombona 5L", "18,90", "un"),
    ("Lava Roupas Líquido Omo Frasco 750ml", "10,90", "un"),
    ("Limpador Multiuso Brilux Limão/Tradicional Frasco 750ml", "4,19", "un"),
    ("Lava Roupas em Pó Omo Lavanderia Profissional Pacote 8kg", "79,90", "un"),
    ("Limpador Veja Perfumes Frasco 500ml", "3,99", "un"),
    ("Tira Manchas em Gel Vanish Tradicional/White Refil 1,2L", "20,90", "un"),
    ("Pastilha Adesiva Pato Lavanda/Tropical Caixeta 3 unidades", "7,90", "un"),
    ("Desodorizador Aerossol Bom Ar Lavanda/Cheirinho de Talco Frasco 432ml", "16,90", "un"),
    ("Inseticida Aerossol Raid Multi Insetos Eucalipto/Base Água Frasco 420ml", "14,90", "un"),
], xs=[4, 24, 44, 64, 84], ys=[(76, 5), (90, 5)], w=15, h=12)

posts.append({
    "shortcode": "atacadao_806f2b524a", "perfil": "atacadao.com.br",
    "banner": "Atacadão", "segmento": "atacarejo",
    "titulo": "Super Fim de Mês Atacadão (28 a 30/07)",
    "inicio": "2026-07-28", "fim": "2026-07-30", "fonte": "web",
    "link": "https://www.atacadao.com.br/loja/natal-sul",
    "pages": {"atacadao_806f2b524a_p1": fm_p1, "atacadao_806f2b524a_p2": fm_p2,
              "atacadao_806f2b524a_p3": fm_p3, "atacadao_806f2b524a_p4": fm_p4,
              "atacadao_806f2b524a_p5": fm_p5},
})

# ============================================================ Super Nordestão (story)
# Promo de story sem datas impressas (post de 27/07, coletado na janela de 28/07)
posts.append({
    "shortcode": "story_supernordestaonatal_20260728", "perfil": "supernordestaonatal",
    "banner": "Super Nordestão", "segmento": "varejo",
    "titulo": "Promoção Cerveja Spaten Super Nordestão",
    "inicio": "2026-07-27", "fim": "2026-07-28", "fonte": "story",
    "pages": {"story_supernordestaonatal_3950894964116750691": [
        {"n": "Cerveja Spaten Puro Malte Lata 350ml", "p": "3,99", "u": "un",
         "x": 5, "y": 3, "w": 90, "h": 72},
    ]},
})

# ================================================================ ingestão
actions = json.load(open(path("data/actions.json"), encoding="utf-8"))
products = json.load(open(path("data/products.json"), encoding="utf-8"))
canon = json.load(open(path("data/canon.json"), encoding="utf-8"))
fila = json.load(open(path("data/fila_novos.json"), encoding="utf-8"))
byshort = {p["shortcode"]: p for p in fila}

for f in ("data/actions.json", "data/products.json", "data/canon.json"):
    shutil.copy(path(f), path(f + ".bak-20260728"))

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
