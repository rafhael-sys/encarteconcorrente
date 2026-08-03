#!/usr/bin/env python3
"""Monta data/_extract/batch_20260803.json com os produtos das páginas aprovadas.

Cada chave é o nome do arquivo da página SEM .jpg; o valor é a lista de produtos
com preço e posição (x,y,w,h em % da imagem). Extraído por visão em 2026-08-03.
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))


def p(n: str, price: str, u: str, x: float, y: float, w: float, h: float) -> dict:
    """Cria um produto no formato do banco."""
    return {"n": n, "p": price, "u": u, "x": x, "y": y, "w": w, "h": h}


batch: dict = {}

# ============ Mar Vermelho Atacado — carrossel avulso "Mês dos Pais" (DbkuzUBm7jk)
# Nomes alinhados aos grupos canônicos existentes (flyer Dbb00bzH3Vq) p/ mesclarem.
batch["DbkuzUBm7jk_p1"] = [p("Coxão Mole Bovino Resfriado Peça ou Pedaço", "35,88", "kg", 12, 45, 50, 38)]
batch["DbkuzUBm7jk_p2"] = [p("Leite em Pó Confiança Integral 200g", "5,69", "cada", 16, 34, 56, 50)]
batch["DbkuzUBm7jk_p3"] = [p("Óleo de Soja Siol PET 500ml", "4,99", "cada", 28, 32, 44, 55)]
batch["DbkuzUBm7jk_p4"] = [p("Hambúrguer Rezende Ave e Suíno 56g", "0,99", "cada", 14, 36, 58, 45)]
batch["DbkuzUBm7jk_p5"] = [p("Cerveja Heineken Long Neck 250ml", "4,59", "cada (exceto Ceasa)", 28, 30, 44, 55)]
batch["DbkuzUBm7jk_p6"] = [p("Papel Higiênico Sublime Folha Dupla 30m Leve 12 Pague 11", "15,99", "cada", 30, 30, 40, 52)]

# ============ Corte Fácil Atacarejo — "Segunda é Feira 03 AGO" (Dbj4uftmoWo)
batch["Dbj4uftmoWo_p1"] = [
    p("Café em Pó União Tradicional 250g", "10,99", "und", 8, 30, 38, 22),
    p("Leite em Pó Integral Itambé 200g", "7,49", "und", 50, 30, 42, 22),
    p("Aveia em Flocos ou Flocos Finos AllNutry 170g", "3,49", "und", 8, 53, 38, 22),
    p("Bebida Láctea UHT Nescau Prontinho 180ml", "1,89", "und", 50, 53, 42, 22),
]
batch["Dbj4uftmoWo_p2"] = [
    p("Azeite Extra Virgem Andorinha 250ml", "16,99", "und", 8, 30, 38, 22),
    p("Almôndega Fast Meat Bovina e Aves Congelada 1kg", "16,99", "und", 50, 30, 42, 22),
    p("Margarina Primor com Sal 500g", "5,49", "und", 8, 53, 38, 22),
    p("Morango Congelado Delta 1,02kg", "15,99", "und", 50, 53, 42, 22),
]

# ============ Assaí Atacadista — "Giro da Economia" (assai_169300-572), 4 páginas
batch["assai_169300-572_p1"] = [
    p("Leite Longa Vida Integral ou Desnatado Damare 1L", "5,59", "cada", 2, 21, 20, 15),
    p("Leite em Pó Integral Ninho Nestlé 750g", "28,90", "cada", 24, 21, 20, 15),
    p("Leite Condensado Betânia 395g", "5,49", "cada", 46, 21, 18, 15),
    p("Creme de Leite CCGL 200g", "2,79", "cada", 64, 21, 17, 15),
    p("Óleo de Soja Liza 900ml", "6,75", "cada", 2, 38, 20, 15),
    p("Feijão Carioca Kumê 1kg", "6,89", "cada", 24, 38, 20, 15),
    p("Açúcar Cristal ou Triturado Alegre 1kg", "2,55", "cada", 46, 38, 18, 15),
    p("Farinha de Trigo Tradicional Boa Sorte 1kg", "3,49", "cada", 64, 38, 17, 15),
    p("Macarrão Espaguete Gostoso Estrela 400g", "1,99", "cada", 2, 57, 18, 14),
    p("Macarrão Instantâneo Lámen Vitarella 74,3g", "1,19", "cada", 21, 57, 17, 14),
    p("Biscoito Cream Cracker Tostadinha Vitarella 350g", "3,99", "cada", 40, 57, 18, 14),
    p("Biscoito Recheado Treloso Vitarella 74g", "1,29", "cada", 60, 57, 16, 14),
    p("Biscoito Maria Tradicional Estrela 307g", "4,49", "cada", 80, 57, 18, 14),
    p("Café Extraforte Santa Clara Almofada ou a Vácuo 250g", "11,59", "cada", 2, 80, 15, 17),
    p("Flocão de Milho Nordestino 500g", "1,25", "cada", 18, 80, 15, 17),
    p("Arroz Parboilizado Tipo 2 POP 1kg", "3,19", "cada", 34, 80, 15, 17),
    p("Peito com Osso Bovino Resfriado Masterboi", "28,90", "quilo", 50, 80, 14, 17),
    p("Filé de Peito de Frango Congelado Seara IQF ZIP 1kg", "16,99", "cada", 65, 80, 15, 17),
    p("Coxas e Sobrecoxas de Frango com Porção Dorsal Congeladas Lar", "7,75", "quilo", 81, 80, 17, 17),
]
batch["assai_169300-572_p2"] = [
    # coluna app Meu Assaí (esquerda)
    p("Bala Fini Tubes 80g", "5,99", "no app Meu Assaí", 2, 24, 20, 9),
    p("Salgadinho Queijo Nachos Doritos 257g", "10,95", "no app Meu Assaí", 2, 36, 20, 9),
    p("Batata Palha Tradicional ou Extrafina Yoki 100g/105g", "7,99", "no app Meu Assaí", 2, 48, 20, 9),
    p("Amendoim Torrado e Salgado Sem Pele Grelhaditos Santa Helena 60g", "1,99", "no app Meu Assaí", 2, 62, 20, 9),
    # grade principal
    p("Farinha de Trigo para Panificação Suprema 25kg", "83,90", "cada", 24, 5, 18, 12),
    p("Cesta Básica Assaí NE Kit 11 itens", "55,90", "cada", 43, 5, 18, 12),
    p("Margarina Sabor Manteiga 60% Gordura Puro Sabor 3kg", "27,90", "cada", 62, 5, 18, 12),
    p("Molho de Tomate Tradicional Tarantella 1,02kg", "6,49", "cada", 81, 5, 17, 12),
    p("Café Solúvel Clássico ou Extraforte Santa Clara 40g", "3,89", "cada", 24, 22, 18, 12),
    p("Mistura para Bolo Apti 400g", "4,19", "cada", 43, 22, 18, 12),
    p("Bebida Láctea Power Whey 3 Corações 250ml", "5,99", "cada", 62, 22, 18, 12),
    p("Aveia em Flocos Regulares ou Finos Quaker 165g", "3,79", "cada", 81, 22, 17, 12),
    p("Azeite de Oliva Fiorentini ou Manosalbas 500ml", "25,90", "cada", 24, 38, 18, 12),
    p("Azeitonas Verdes com Caroços Vale Fértil 500g", "16,90", "cada", 43, 38, 18, 12),
    p("Molho de Tomate Tradicional Stella D'Oro 300g", "1,29", "cada", 62, 38, 18, 12),
    p("Dueto ou Milho-Verde Quero 170g", "3,29", "cada", 81, 38, 17, 12),
    p("Catchup Tambaú 380g", "4,29", "cada", 24, 54, 18, 12),
    p("Maionese Arisco 196g", "1,99", "cada", 43, 54, 18, 12),
    p("Sardinha Ralada em Óleo ou Molho de Tomate 88 80g/90g", "3,89", "cada", 62, 54, 18, 12),
    p("Atum em Pedaços ao Natural ou em Óleo 88 98g", "7,99", "cada", 81, 54, 17, 12),
    p("Água Mineral sem Gás San Valle 500ml", "0,69", "cada", 24, 70, 18, 12),
    p("Bebida Energética Baly 2L", "12,90", "cada", 43, 70, 18, 12),
    p("Vodka Nacional Smirnoff 1,75L", "49,89", "cada", 62, 70, 18, 12),
    p("Whisky Escocês Red Label Johnnie Walker 1L", "79,90", "cada", 81, 70, 17, 12),
    p("Cerveja Puro Malte Devassa 350ml", "2,59", "cada", 2, 86, 18, 13),
    p("Refrigerante de Caju Tradicional ou Zero Açúcares São Geraldo 1L", "5,99", "cada", 24, 86, 18, 13),
    p("Suco Misto Natural One 1,7L", "19,90", "cada", 43, 86, 18, 13),
    p("Vinho Chileno Concha y Toro 750ml", "24,90", "cada", 62, 86, 18, 13),
    p("Aguardente Pitú 965ml", "10,49", "cada", 81, 86, 17, 13),
]
batch["assai_169300-572_p3"] = [
    p("Peito de Frango com Osso Congelado Mauricéa", "12,75", "quilo", 4, 5, 20, 14),
    p("Bisteca Suína Congelada Sadia", "15,90", "quilo", 26, 5, 18, 14),
    p("Filé de Peixe Merluza Congelado Fish 800g", "27,90", "cada", 45, 5, 17, 14),
    p("Linguiça de Frango Congelada Top Grill Bom Todo 600g", "14,90", "cada", 63, 5, 18, 14),
    p("Steak de Frango Empanado Perdigão 100g", "1,69", "cada", 4, 22, 20, 14),
    p("Hambúrguer Misto Tradicional Texas Burger Seara 36x56g", "39,90", "cada", 26, 22, 18, 14),
    p("Linguiça Tipo Calabresa Defumada Seara 400g", "12,59", "cada", 45, 22, 17, 14),
    p("Salsicha para Hot-Dog Congelada Bom Todo 3kg", "17,90", "cada", 63, 22, 18, 14),
    p("Leite Fermentado Desnatado Baunilha Activia Danone 6x75g", "10,99", "cada", 4, 38, 20, 14),
    p("Iogurte Líquido Nestlé 1,15kg", "15,79", "cada", 26, 38, 18, 14),
    p("Iogurte Natural Betânia 170g", "3,29", "cada", 45, 38, 17, 14),
    p("Bebida Láctea Sabor Morango Betânia 680g", "6,49", "cada", 63, 38, 18, 14),
    p("Pizza Congelada Rezende 400g", "11,90", "cada", 4, 55, 20, 14),
    p("Lasanha Congelada Seara 600g", "14,45", "cada", 26, 55, 18, 14),
    p("Morangos Congelados Canaã 1,02kg", "13,90", "cada", 45, 55, 17, 14),
    p("Açaí Natural Fruta Nobre 5L", "49,90", "cada", 63, 55, 18, 14),
    p("Pão de Forma Center Massas 400g", "5,49", "cada", 4, 71, 20, 13),
    p("Manteiga com Sal Betânia 200g", "8,99", "cada", 26, 71, 18, 13),
    p("Requeijão Cremoso Tradicional ou Light Clan 200g", "6,99", "cada", 45, 71, 17, 13),
    p("Sorvete Tradicional Nestlé 1,5L", "18,90", "cada", 63, 71, 18, 13),
    p("Batata Congelada +Fininha McCain 1,5kg", "22,90", "cada", 2, 86, 18, 13),
    p("Queijo Tipo Parmesão Ralado Vigor 50g", "5,29", "cada", 22, 86, 16, 13),
    p("Pão de Queijo Tradicional Jeito de Minas 800g", "18,90", "cada", 40, 86, 17, 13),
    p("Massa para Pastel Industrial Massa Forte 500g", "5,79", "cada", 58, 86, 16, 13),
    p("Queijo Tipo Mussarela Italac Peça (preço do quilo)", "37,90", "quilo", 80, 86, 18, 13),
]
batch["assai_169300-572_p4"] = [
    p("Lava-Roupas em Pó Ala 1,6kg", "8,90", "cada", 2, 4, 18, 14),
    p("Lava-Roupas Líquido Perfume das Flores Bem-Te-Vi 5L", "19,90", "cada", 22, 4, 17, 14),
    p("Sabão em Barra Neutro Absoluto 5x160g", "5,49", "cada", 40, 4, 17, 14),
    p("Amaciante de Roupas Concentrado Downy 500ml", "9,90", "cada", 58, 4, 16, 14),
    p("Água Sanitária Clorito 2L", "2,89", "cada", 76, 4, 16, 14),
    p("Lava-Louças Ypê 500ml", "1,89", "cada", 2, 24, 18, 14),
    p("Desinfetante Perfumado Dragão 2L", "3,99", "cada", 22, 24, 17, 14),
    p("Limpador Multiúso Becker 500ml", "3,19", "cada", 40, 24, 17, 14),
    p("Esponja de Aço Assolan 45g", "1,19", "cada", 58, 24, 16, 14),
    p("Multi-Inseticida Aerossol SBP 450ml", "15,90", "cada", 76, 24, 16, 14),
    p("Papel Higiênico Folha Dupla Velud VIP 12 unidades 30m", "12,90", "cada", 2, 40, 18, 15),
    p("Papel-Toalha Malu 2 rolos 50 folhas", "3,59", "cada", 22, 40, 17, 15),
    p("Absorvente Noturno com Abas Sempre Livre 32 unidades", "21,90", "cada", 40, 40, 17, 15),
    p("Lenço Umedecido Piquitucho 120 unidades", "11,99", "cada", 58, 40, 16, 15),
    p("Fralda Descartável Hiper Cremer", "49,90", "cada", 76, 40, 16, 15),
    p("Kit Shampoo 300ml + Condicionador 190ml Seda", "15,50", "cada", 2, 58, 18, 14),
    p("Sabonete Antibacterial Rexona 84g", "1,99", "cada", 22, 58, 17, 14),
    p("Desodorante Aerossol Axe 200ml", "9,50", "cada", 40, 58, 17, 14),
    p("Creme Dental Dentes Brancos Fresh Sorriso 90g", "3,95", "cada", 58, 58, 16, 14),
    p("Enxaguante Bucal Listerine Cool Mint 500ml", "15,90", "cada", 76, 58, 16, 14),
    p("Caixa Térmica Bel Fix 19L", "42,90", "cada", 2, 75, 18, 16),
    p("Papel-Alumínio Bompack 30cm x 4m", "2,99", "cada", 22, 75, 17, 16),
    p("Alimento para Cães Classic Vittamax 10,1kg", "89,90", "cada", 40, 75, 17, 16),
    p("Frigideira Fun Brinox 22cm", "32,90", "cada", 58, 75, 16, 16),
    p("Pneu Aro 15 195/55 85V XBRI Fastway", "249,90", "cada", 76, 75, 16, 16),
]

# ============ Atacadão — "Festival Linha Pet" (atacadao_f632ad4559), preço = "por"
batch["atacadao_f632ad4559_p1"] = [
    p("Alimento para Cães Champ Carne e Cereal 18kg", "89,00", "cada (de 129,00)", 2, 16, 30, 11),
    p("Alimento para Cães Pedigree 2,7kg", "32,90", "cada (de 55,90)", 35, 16, 30, 11),
    p("Alimento para Cães Pedigree Nutrição Essencial Leite/Filhotes 900g", "11,90", "cada (de 19,90)", 67, 16, 31, 11),
    p("Alimento para Gatos KiteKat Mix de Carnes 10,1kg", "99,00", "cada (de 134,90)", 2, 28, 30, 11),
    p("Alimento para Gatos Whiskas Carne 10,1kg", "139,00", "cada (de 169,00)", 35, 28, 30, 11),
    p("Alimento para Cães Pedigree 100g", "2,49", "cada (de 3,49)", 67, 28, 31, 11),
    p("Alimento para Gatos Whiskas 85g", "2,29", "cada (de 3,29)", 2, 41, 30, 11),
    p("Petisco para Gatos Dreamies Carne 40g", "3,49", "cada (de 5,90)", 35, 41, 30, 11),
    p("Alimento para Cães Champ Filhotes Frango/Carne 85g", "1,99", "cada (de 2,69)", 67, 41, 31, 11),
    p("Alimento para Cães Adultos Dog Chow Raças Médias/Grandes/Pequenas 10,1kg", "99,00", "cada (de 139,00)", 2, 54, 30, 11),
    p("Alimento para Cães Bonzo Carne e Cereais 1kg", "15,90", "cada (de 21,90)", 35, 54, 30, 11),
    p("Alimento para Cães Filhotes Dog Chow Pequenos 10,1kg", "99,00", "cada (de 149,00)", 67, 54, 31, 11),
    p("Alimento para Gatos Gatsy Carne 2,7kg", "34,90", "cada (de 46,90)", 2, 67, 30, 11),
    p("Alimento para Gatos Friskies Frutos do Mar 10,1kg", "139,00", "cada (de 199,00)", 35, 67, 30, 11),
    p("Alimento para Gatos Friskies Carne 85g", "2,59", "cada (de 3,39)", 67, 67, 31, 11),
]
batch["atacadao_f632ad4559_p2"] = [
    p("Bifinho para Cães Doguitos Adulto 65g", "5,95", "cada (de 7,85)", 2, 13, 30, 10),
    p("Petisco para Cães Oral Dog Chow Médios e Grandes 200g", "14,90", "cada (de 21,90)", 35, 13, 30, 10),
    p("Alimento para Cães Dog Chow 2,5kg", "44,90", "cada (de 59,90)", 67, 13, 31, 10),
    p("Alimento para Cães Adultos Dog Chow Frango 100g", "2,59", "cada (de 3,49)", 2, 25, 30, 10),
    p("Alimento para Gatos Gatsy Carne 2,7kg", "34,90", "cada (de 46,90)", 35, 25, 30, 10),
    p("Alimento para Gatos Gatsy Carne 1kg", "14,90", "cada (de 23,90)", 67, 25, 31, 10),
    p("Bifinho para Cães Filezitos Pedigree Carne 60g", "4,49", "cada (de 5,90)", 2, 37, 30, 10),
    p("Biscoito para Cães Pedigree Biscrock Filhotes 300g", "13,49", "cada (de 19,90)", 35, 37, 30, 10),
    p("Pedigree Dentastix Raças Médias 180g", "15,90", "cada (de 23,90)", 67, 37, 31, 10),
    p("Alimento para Cães Pedigree Raças Pequenas 900g", "15,90", "cada (de 22,90)", 2, 50, 30, 10),
    p("Petiscos para Gatos Dreamies Carne/Salmão 80g", "8,49", "cada (de 10,90)", 35, 50, 30, 10),
    p("Arroz para Cães Au! Au! 5kg", "16,49", "cada (de 18,50)", 67, 50, 31, 10),
    p("Alimento para Cães Bomguy Multi Raça Pequena Carne 2kg", "30,90", "cada (de 36,90)", 2, 63, 30, 11),
    p("Alimento para Gatos Chanin 1kg", "15,90", "cada (de 19,90)", 50, 63, 30, 11),
]

# ============ Atacadão — "Semana Beleza & Cuidados" (atacadao_35f104b75e), preço = "por"
batch["atacadao_35f104b75e_p1"] = [
    p("Antisséptico Bucal Listerine 250ml", "13,50", "cada (de 17,50)", 2, 19, 30, 13),
    p("Creme para Pentear Hair Fly Ativador/Modelador Cachos 500ml", "14,90", "cada (de 18,90)", 35, 19, 30, 13),
    p("Hastes Flexíveis Nathy 75 unidades", "1,49", "cada (de 1,85)", 67, 19, 31, 13),
    p("Kit Shampoo + Condicionador Hair Fly 300ml", "15,90", "cada (de 18,90)", 2, 35, 30, 13),
    p("Sabonete Líquido Clean Level 500ml", "6,29", "cada (de 8,99)", 35, 35, 30, 13),
    p("Creme Dental Colgate Luminous White 70g", "9,90", "cada (de 12,90)", 67, 35, 31, 13),
    p("Disco de Algodão Nathy 50 unidades", "3,99", "cada (de 4,90)", 2, 52, 30, 13),
    p("Lenço Umedecido Neve Dermacare 48 unidades", "9,90", "cada (de 13,90)", 35, 52, 30, 13),
    p("Sabonete Bulnez 80g", "1,55", "cada (de 1,75)", 67, 52, 31, 13),
    p("Tintura Casting Gloss L'Oréal", "34,90", "cada (de 37,90)", 2, 68, 30, 13),
    p("Água Micelar L'Oréal 200ml", "22,90", "cada (de 26,90)", 35, 68, 30, 13),
    p("Aparelho de Barbear Bic Comfort 4 unidades", "14,90", "cada (de 17,90)", 67, 68, 31, 13),
]
batch["atacadao_35f104b75e_p2"] = [
    p("Absorvente Noturno Always Seca com Abas 32 unidades", "19,90", "cada (de 28,90)", 2, 17, 30, 13),
    p("Aparelho de Barbear Gillette Prestobarba 2 2 unidades", "5,79", "cada (de 6,90)", 35, 17, 30, 13),
    p("Creme Dental Even Flúor e Cálcio/Juá e Hortelã 70g", "1,89", "cada (de 2,19)", 67, 17, 31, 13),
    p("Desodorante Aerossol One Above 150ml", "5,99", "cada (de 7,70)", 2, 33, 30, 13),
    p("Desodorante em Creme Above 50g", "3,49", "cada (de 4,69)", 35, 33, 30, 13),
    p("Sabonete Flor de Ypê Suave 85g", "1,25", "cada (de 1,59)", 67, 33, 31, 13),
    p("Sabonete Líquido Lux Refil 200ml", "4,79", "cada (de 9,50)", 2, 50, 30, 13),
    p("Shampoo Seda 325ml", "9,90", "cada (de 11,98)", 35, 50, 30, 13),
    p("Kit Shampoo + Condicionador Niely", "18,90", "cada (de 22,90)", 67, 50, 31, 13),
    p("Hidratante Garnier 85g", "33,90", "cada (de 36,90)", 2, 67, 30, 13),
    p("Condicionador Novex Recarga de Queratina 80g", "13,90", "cada (de 17,90)", 35, 67, 30, 13),
    p("Gelatina Capilar Kolene Super Finalizadores Ultradefinição 500g", "23,90", "cada (de 26,90)", 67, 67, 31, 13),
]

os.makedirs(os.path.join(BASE, "data", "_extract"), exist_ok=True)
out = os.path.join(BASE, "data", "_extract", "batch_20260803.json")
json.dump(batch, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
tot = sum(len(v) for v in batch.values())
print(f"batch gravado: {out}")
print(f"páginas: {len(batch)} | produtos: {tot}")
for k, v in batch.items():
    print(f"  {k}: {len(v)}")
