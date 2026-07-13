#!/usr/bin/env python3
# Monta data/_ingest_20260713b_produtos.json — 2º lote de 13/07/2026:
# Rede Mais "Copa RedeMAIS" (feed, 4 pág, 11-20/07) + Miramar (story, 4 frames de
# oferta, 13-21/07). Extração manual na sessão do Claude Code.
import json, math, os
BASE = os.path.dirname(os.path.abspath(__file__))

def grid(n, ncols, ytop=13, ybot=96):
    nrows = math.ceil(n / ncols); colw = 94/ncols; rowh = (ybot-ytop)/nrows
    return [(round(3+ (i%ncols)*colw), round(ytop+(i//ncols)*rowh),
             round(colw-2), round(rowh-2)) for i in range(n)]

PAGES = {
 # ---------- Rede Mais — Copa RedeMAIS (feed) ----------
 "DaoUj8YjXJP_p1": (5, [
  ("Flocão de Milho Vitamilho 500g","1,39","un"),
  ("Bombom Garoto Sortido 220g","11,98","un"),
  ("Coxa com Sobrecoxa de Frango c/ Dorsal Jaguá","7,49","kg"),
  ("Salsicha Hot Dog Chuletão","5,99","kg"),
  ("Carré Suíno Frimesa","13,98","kg"),
  ("Café União Tradicional 250g","11,99","un"),
  ("Creme Culinário Damare 200g","1,69","un"),
  ("Leite em Pó CCGL Integral 800g","26,98","un"),
  ("Leite Condensado CCGL Semidesnatado 395g","5,79","un"),
  ("Arroz Parboilizado Blue Soft Tipo 1 1kg","3,49","un"),
  ("Açúcar Triturado Ecoçúcar 1kg","2,89","un"),
  ("Macarrão Espaguete Bonsabor 400g","1,99","un"),
  ("Queijo Mussarela Ipanema Fatiado 150g","7,99","un"),
  ("Margarina Claybom 500g","5,49","un"),
  ("Almôndegas Mista Chuletão 1kg","12,98","un"),
  ("Bisteca Suína Coopavel","14,98","kg"),
  ("Coxinha da Asa de Frango Jaguá","11,98","kg"),
  ("Bebida Láctea YoPRO 15g Proteínas 250ml","6,99","un"),
  ("Suco de Uva Casa da Serra Integral 1,5L","14,98","un"),
  ("Cerveja Devassa Lata 350ml","2,79","un"),
  ("Cerveja Heineken Lata 350ml","4,99","un"),
 ]),
 "DaoUj8YjXJP_p2": (4, [
  ("Feijão Preto DuBom Tipo 1 1kg","5,79","un"),
  ("Biscoito Cream Cracker Vitarella Tostadinha 350g","4,49","un"),
  ("Bebida Láctea Damare Kids Chocolate 200ml","1,09","un"),
  ("Achocolatado em Pó Chocky 200g","3,99","un"),
  ("Doce de Leite Cremoso Clan 380g","9,59","un"),
  ("Biscoito Recheado Toddy 100g","2,39","un"),
  ("Biscoito Recheado Treloso 120g","1,99","un"),
  ("Biscoito Wafer Vitarella 80g","1,59","un"),
  ("Sardinha Robinson Crusoe Óleo/Tomate 125g","5,49","un"),
  ("Azeite Extra Virgem La Española 500ml","27,98","un"),
  ("Macarrão Instantâneo Lámen Vitarella 74,3g","1,39","un"),
  ("Alho em Pasta Sadio Puro Alho 200g","5,89","un"),
  ("Kit Leto Tempero Completo Especial/Extrato de Alho/Vinagre 500ml","7,49","un"),
  ("Molho de Tomate Tambaú Tradicional 300g","1,99","un"),
  ("Azeitonas Verdes Tambaú Fatiada/sem Caroço 120g","6,99","un"),
  ("Catchup Tambaú Tradicional/Picante 830g","6,99","un"),
  ("Dueto Predilecta 170g","3,29","un"),
  ("Maionese Fugini Tradicional 180g","2,29","un"),
  ("Milho Verde Fugini 170g","3,39","un"),
 ]),
 "DaoUj8YjXJP_p3": (5, [
  ("Escova Dental Oral-B Indicator c/2","18,49","un"),
  ("Escova Dental Oral-B Ultra Macia Sensitive","19,98","un"),
  ("Creme Dental Even Flúor e Cálcio/Juá e Hortelã 50g","1,79","un"),
  ("Aparelho de Barbear BIC Comfort 3 Advance Leve 4 Pague 3","16,98","un"),
  ("Creme Dental Oral-B 4 em 1 70g","3,99","un"),
  ("Absorvente Intimus Proteção Seca/Suave com Abas c/16","6,59","un"),
  ("Fralda Descartável Personal Baby Total Protect Pants","27,98","un"),
  ("Máscara de Tratamento Corpo Dourado 1kg","11,49","un"),
  ("Sabonete Barra Even Suave 85g","1,99","un"),
  ("Amaciante Concentrado Brilux 500ml","7,99","un"),
  ("Detergente Líquido Tanlux 500ml","1,49","un"),
  ("Lava Roupas Líquido Tanlux 3L","13,49","un"),
  ("Água Sanitária Olimpo 1L","2,29","un"),
  ("Lava Roupas em Pó Sonho 400g","2,69","un"),
  ("Desodorante Aerosol Rexona 150ml","14,99","un"),
  ("Kit Seda Shampoo 300ml + Condicionador 190ml","16,49","un"),
  ("Shampoo Clear Anticaspa 200ml","19,98","un"),
  ("Lava Roupas Líquido Ala Refil Lavanda/Cuidado do Coco 700ml","7,49","un"),
  ("Sabonete Lux Botanicals 85g","2,49","un"),
  ("Lava Roupas em Pó Ala 800g","5,98","un"),
  ("Lava Roupas em Pó Omo Lavanda/Lavagem Perfeita 1,6kg","23,99","un"),
  ("Amido de Milho Maizena 200g","3,99","un"),
  ("Maionese Hellmann's Tradicional 200g","5,29","un"),
  ("Ketchup Hellmann's Tradicional Squeeze 380g","12,98","un"),
 ]),
 "DaoUj8YjXJP_p4": (5, [
  ("Bebida Láctea Clan Sachê 900g","4,99","un"),
  ("Requeijão Cremoso Clan Tradicional/Light 200g","7,49","un"),
  ("Bebida Láctea Isis Bandeja 540g","4,98","un"),
  ("Iogurte Isis Pro 15g Proteínas 180g","5,89","un"),
  ("Almôndegas Bovina Chuletão 1kg","19,98","un"),
  ("Linguiça de Frango Bom Todo","14,98","kg"),
  ("Carne Bovina Chã de Fora Resfriada","39,98","kg"),
  ("Coxa de Frango Lar IQF 1kg","12,99","un"),
  ("Auroggets de Frango Aurora 900g","19,98","un"),
  ("Empanado de Frango Sadia/Perdigão 100g","1,99","un"),
  ("Hambúrguer Misto Sadia 56g","1,19","un"),
  ("Batata Congelada BemBrasil Carinhas 400g","7,59","un"),
  ("Polpa de Frutas Seridó 400g","3,59","un"),
  ("Gatorade 500ml","6,59","un"),
  ("Refrigerante Guaraná Antarctica 2L","8,99","un"),
  ("Vinho Chileno Água Santa 750ml","19,98","un"),
  ("Bebida Mista Raykoff Limão/Red Fruits Long Neck 275ml","4,49","un"),
  ("Aguardente Pitú Lata 350ml","4,69","un"),
  ("Frisante Randon 750ml","19,98","un"),
 ]),
 # ---------- Miramar — story (só os frames que são oferta) ----------
 "story_miramarsupermercado_3940279086463711431": (2, [   # f3 — saúde (10-19/07)
  ("Aveia Áster Flocos Finos ou Grossos 400g","8,69","un"),
  ("Semente de Chia Áster 120g","11,99","un"),
  ("Cacau em Pó 100% Áster 180g","22,55","un"),
  ("Farinha de Linhaça Marrom Áster 180g","7,49","un"),
  ("Farinha de Linhaça Dourada Áster 180g","7,99","un"),
  ("Flocos de Milho para Cuscuz Livre D 500g","4,78","un"),
  ("Pasta de Amendoim Integral Natural ou Crunchy Livre D 400g","18,89","un"),
  ("Adoçante Stévia EX Svilli 90ml","10,98","un"),
 ]),
 "story_miramarsupermercado_3940328819063340780": (2, [   # f5
  ("Óleo de Soja ABC 900ml","7,29","un"),
  ("Carne Bovina Coxão Mole","38,99","kg"),
  ("Filé de Peito de Frango LAR 1kg","17,99","un"),
  ("Leite UHT Natville Integral ou Desnatado 1L","5,79","un"),
 ]),
 "story_miramarsupermercado_3940328910440493102": (2, [   # f6
  ("Fraldas Descartáveis Cremer Shortinho Jumbo","24,99","un"),
  ("Papel Higiênico Caprice Neutro Folha Dupla 12 Rolos","9,99","un"),
  ("Lava Roupas em Pó Ala Fragrâncias 400g","2,69","un"),
  ("Água Sanitária Clorito 1L","2,19","un"),
 ]),
 "story_miramarsupermercado_3940328992573314087": (2, [   # f7
  ("Carne Bovina Patinho","38,99","kg"),
  ("Salsicha Hot Dog Rara","6,49","kg"),
  ("Açúcar Dumel Triturado 1kg","3,29","un"),
  ("Batata Pré-frita EasyChef Congelada Tradicional 2kg","19,99","un"),
  ("Flocão de Milho Rei de Ouro 500g","1,29","un"),
  ("Arroz Parboilizado Emoções 1kg","4,39","un"),
  ("Farinha de Trigo Finna Tradicional 1kg","3,99","un"),
  ("Café São Braz Extraforte Almofada ou A Vácuo 250g","12,99","un"),
 ]),
}

out, tot = {}, 0
for key, (ncols, items) in PAGES.items():
    boxes = grid(len(items), ncols)
    out[key] = [{"n":n,"p":p,"u":u,"x":x,"y":y,"w":w,"h":h}
                for (n,p,u),(x,y,w,h) in zip(items, boxes)]
    tot += len(items)
json.dump(out, open(os.path.join(BASE,"data/_ingest_20260713b_produtos.json"),"w",
          encoding="utf-8"), ensure_ascii=False, indent=1)
print("produtos.json (lote b):", tot, "produtos em", len(out), "páginas")
