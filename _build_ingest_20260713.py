#!/usr/bin/env python3
# Monta data/_ingest_20260713_produtos.json a partir dos produtos extraidos
# manualmente das 11 paginas dos 4 encartes do Atacadao coletados em 13/07/2026.
# (o claude CLI nao esta nesta maquina; a extracao foi feita na sessao do Claude Code)
import json, math, os
BASE = os.path.dirname(os.path.abspath(__file__))

def grid(n, ncols, ytop=13, ybot=96):
    nrows = math.ceil(n / ncols)
    colw = 94 / ncols
    rowh = (ybot - ytop) / nrows
    out = []
    for i in range(n):
        c, r = i % ncols, i // ncols
        out.append((round(3 + c*colw), round(ytop + r*rowh),
                    round(colw - 2), round(rowh - 2)))
    return out

# pageid -> (ncols, [ (nome, preco, unidade), ... ])  em ordem de leitura
PAGES = {
 "atacadao_c21038cd2b_p1": (3, [
  ("Tomate Italiano","2,79","kg"),
  ("Abacate","3,69","kg"),
  ("Coxa com Sobrecoxa de Frango Friato Congelada","8,39","kg"),
  ("Hambúrguer Jundiaí Congelado Carne Bovina/Frango 36x56g","19,90","un"),
  ("Óleo de Soja Soya 900ml","6,99","un"),
  ("Bombom Garoto Sortido 220g","11,99","un"),
  ("Ketchup Quero Tradicional 400g","4,99","un"),
 ]),
 "atacadao_3caae4f9fa_p1": (5, [
  ("Tomate Italiano","2,79","kg"),("Cenoura","6,59","kg"),("Cebola Branca","5,79","kg"),
  ("Pimentão Verde","3,89","kg"),("Melão Amarelo","2,59","kg"),
  ("Abacate","3,69","kg"),("Banana Pacovan","3,59","kg"),("Maçã Nacional Gala","5,89","kg"),
  ("Mexerica Comum","7,49","kg"),("Macaxeira","2,39","kg"),
  ("Carne Bovina Picanha Maturatta Congelada","89,00","kg"),
  ("Carne Bovina Coxão Mole Friboi Resfriada","41,90","kg"),
  ("Carne Bovina Cupim Friboi Congelada","33,99","kg"),
  ("Carne Bovina Costela em Tira Friboi Congelada","29,99","kg"),
  ("Coração Bovino Porcionado Friboi Congelado","15,90","kg"),
 ]),
 "atacadao_3caae4f9fa_p2": (3, [
  ("Frango Mauricéa Congelado","8,79","kg"),
  ("Margarina Deline Resfriada com Sal 500g","5,99","un"),
  ("Queijo Mussarela Jucurutu Resfriado","37,90","kg"),
  ("Salsicha Hot Dog Friato Congelada 5kg","29,90","un"),
  ("Lasanha Seara Congelada Bolonhesa 1kg","24,90","un"),
  ("Linguiça Defumada Seara Fininha 215g","6,99","un"),
  ("Batata Pré-Frita McCain Congelada 2kg","26,90","un"),
  ("Linguiça Tipo Calabresa Tony 2kg","39,90","un"),
  ("Mortadela Tony Frango sem Toucinho","7,59","kg"),
  ("Manteiga Tirolez Resfriada com Sal 200g","11,90","un"),
  ("Morango Nossa Fruta Congelado 1,02kg","16,90","un"),
  ("Requeijão Cremoso Tirolez Resfriado 1,5kg","42,90","un"),
  ("Iogurte Nestlé Resfriado 1,15kg","15,49","un"),
  ("Leite Fermentado Itambé Resfriado 480g","5,89","un"),
  ("Requeijão Sertão Jucurutu Resfriado 200g","6,90","un"),
 ]),
 "atacadao_3caae4f9fa_p3": (5, [
  ("Açúcar Cristal Olho D'Água Triturado 1kg","2,69","un"),
  ("Arroz Tio João Parboilizado Tipo 1 1kg","3,79","un"),
  ("Azeite de Oliva Andorinha Extra Virgem 500ml","26,90","un"),
  ("Farinha de Trigo Dona Benta Tipo 1 1kg","3,59","un"),
  ("Feijão Carioca Eu Kero Tipo 2 1kg","7,99","un"),
  ("Biscoito Jucurutu Tareco 270g","4,99","un"),
  ("Bolacha São Francisco Palito Manteiga 200g","3,29","un"),
  ("Leite em Pó Molico Desnatado 280g","18,80","un"),
  ("Chocolate Granulado Mavalério 1,010kg","18,99","un"),
  ("Farelo de Aveia Kodilar 500g","5,99","un"),
  ("Chocolate Neugebauer 80g","5,99","un"),
  ("Ketchup Heinz Tradicional 567g","13,90","un"),
  ("Ervilha e Milho Sófruta Dueto 170g","2,49","un"),
  ("Maionese Vigor 200g","2,69","un"),
  ("Café Puro Almofada 250g","12,48","un"),
  ("Café Solúvel Nescafé Dolca 40g","4,69","un"),
  ("Flocão de Milho Vitamilho 500g","1,49","un"),
  ("Extrato de Alho Folha Verde 500ml","2,29","un"),
  ("Pão de Forma Plusvita Integral 480g","9,90","un"),
  ("Batata Palha Amarelinha Extra Fina 400g","14,49","un"),
 ]),
 "atacadao_3caae4f9fa_p4": (3, [
  ("Refrigerante Guaraná Antarctica 1L","4,39","un"),
  ("Energético Baly 2L","12,90","un"),
  ("Água Mineral Bulnez sem Gás 510ml","0,78","un"),
  ("Refresco Líquido D+ 1L","4,49","un"),
  ("Suco de Uva OQ Integral Tinto 1,5L","15,90","un"),
  ("Isotônico Gatorade 500ml","4,99","un"),
  ("Refresco Líquido Kapo 200ml","2,19","un"),
  ("Bebida Adoçada Guarafit Açaí e Guaraná 290ml","1,29","un"),
  ("Cerveja Heineken Long Neck 330ml","6,29","un"),
  ("Cerveja Itaipava Lata 350ml","2,59","un"),
  ("Cerveja Spaten Puro Malte Lata 350ml","3,99","un"),
  ("Cachaça Samanaú Prata 500ml","21,90","un"),
  ("Cachaça São Paulo Original 1L","15,90","un"),
  ("Vinho Adega do Vale 750ml","9,90","un"),
  ("Whisky White Horse 1L","54,90","un"),
 ]),
 "atacadao_3caae4f9fa_p5": (5, [
  ("Desodorante Aerossol Axe 200ml","9,90","un"),
  ("Absorvente Always Super Proteção com Abas 8un","3,49","un"),
  ("Absorvente Sempre Livre Conforto Noturno com Abas 32un","21,90","un"),
  ("Antisséptico Bucal Listerine sem Álcool 500ml","16,99","un"),
  ("Body Splash Giovanna Baby 260ml","26,50","un"),
  ("Fralda-Calça Mamypoko Superproteção Jumbo","34,50","un"),
  ("Papel Higiênico Fofex Soft Folha Simples 30m 4 rolos","3,00","un"),
  ("Protetor Diário Carefree 80un","23,99","un"),
  ("Sabonete Francis 80g","1,69","un"),
  ("Creme de Tratamento Novex 1kg","21,90","un"),
  ("Lã de Aço Assolan 45g","1,09","un"),
  ("Amaciante Comfort Concentrado 1,5L","19,90","un"),
  ("Detergente Líquido Absoluto 2L","4,99","un"),
  ("Lava Roupas em Pó Brilhante 400g","3,69","un"),
  ("Lava Roupas Líquido Omo 1,4L","21,90","un"),
  ("Tira Manchas em Pó Vanish 400g","19,90","un"),
  ("Desinfetante Pato Germinex 750ml","16,90","un"),
  ("Limpador Multiuso Dragão 500ml","3,39","un"),
  ("Inseticida Mat Inset 360ml","12,90","un"),
  ("Repelente em Loção Off Kids 200ml","21,90","un"),
  ("Copo Americano Nadir Ref. 2010","1,19","un"),
  ("Alimento para Cães Champ Filhotes Frango 85g","1,99","un"),
  ("Folha de Alumínio Wyda 30cm x 4m","2,95","un"),
  ("Guardanapo TV Malu 14x14cm 160un","1,59","un"),
  ("Mop Compacto Brilhus 10L","69,90","un"),
 ]),
 "atacadao_3caae4f9fa_p6": (3, [
  ("Iogurte Natural Nestlé 170g","4,29","un"),
  ("Polpa de Fruta Brasfrut Congelada 100g","2,49","un"),
  ("Leite em Pó Itambé Zero Lactose 300g","18,30","un"),
  ("Milho de Pipoca para Micro-ondas Yoki 100g","4,29","un"),
  ("Crocantíssimo Pullman 40g","2,99","un"),
  ("Salgadinho Elma Chips Ruffles 68g","8,50","un"),
  ("Empanado de Frango Seara Chicken Supreme Congelado 300g","10,98","un"),
  ("Feijão Preto Kicaldo Tipo 1 1kg","7,59","un"),
  ("Flocão de Milho Novomilho 500g","1,34","un"),
  ("Macarrão Instantâneo Nissin Cup Noodles 69g","5,39","un"),
  ("Molho de Tomate Tambaú Pizza 300g","2,50","un"),
  ("Queijo Ralado Parmesão Président 50g","4,79","un"),
  ("Sabonete Johnson's Erva Doce 80g","2,69","un"),
 ]),
 "atacadao_cb8d108830_p1": (3, [
  ("Asa de Frango Resfriada","16,90","kg"),
  ("Coração de Frango Resfriado","38,90","kg"),
  ("Coxa e Sobrecoxa de Frango Resfriada","10,90","kg"),
  ("Filé de Peito de Frango Resfriado","19,59","kg"),
  ("Carne Bovina Peito com Osso Reserva Resfriada","24,99","kg"),
  ("Carne Bovina Chambaril Dianteiro Reserva Resfriada","25,99","kg"),
  ("Mocotó Bovino Reserva Resfriado","9,99","kg"),
  ("Carne Bovina Rabo Reserva Resfriada","26,99","kg"),
  ("Carne Bovina Acém sem Osso Reserva Resfriada","32,90","kg"),
  ("Carne Bovina de Sol Coxão Mole Resfriada","42,99","kg"),
  ("Carne Bovina Coxão Mole Reserva Resfriada","34,99","kg"),
  ("Carne Bovina Músculo Reserva Resfriada","29,99","kg"),
 ]),
 "atacadao_cb8d108830_p2": (5, [
  ("Jerked Beef Ponta de Agulha","44,99","kg"),
  ("Bacon Defumado Seara","36,90","kg"),
  ("Embutido de Lombo Fatiado Levíssimo Seara","29,90","kg"),
  ("Linguiça Tipo Calabresa Seara Resfriada","25,90","kg"),
  ("Queijo Mussarela Girolanda Fatiado","39,90","kg"),
  ("Pão Francês Pancristal","9,90","kg"),
  ("Pão de Hambúrguer Pancristal","23,50","kg"),
  ("Pão de Hot Dog Pancristal","18,90","kg"),
  ("Pão Placa Pancristal","22,50","kg"),
  ("Pão Recife Pancristal","19,90","kg"),
  ("Bolo Pancristal Chocolate","36,90","kg"),
  ("Bolo Pancristal Inglês","34,90","kg"),
  ("Bolo Pancristal Maracujá","35,90","kg"),
  ("Broa de Milho Pancristal","49,90","kg"),
  ("Brownie Pancristal","89,00","kg"),
 ]),
 "atacadao_56cb6e227b_p1": (5, [
  ("Linguiça Tipo Calabresa Tony 2kg","39,90","un"),
  ("Presunto Cozido Rezende Resfriado sem Capa de Gordura","21,90","kg"),
  ("Queijo Mussarela Jucurutu Resfriado","37,90","kg"),
  ("Queijo Cheddar Processado Vigor Resfriado Fatiado 2,24kg","114,90","un"),
  ("Manteiga Itacolomy Resfriada com Sal 200g","10,90","un"),
  ("Margarina Qualy Resfriada com Sal 1kg","16,90","un"),
  ("Requeijão Cremoso Tirolez Resfriado 200g","7,49","un"),
  ("Requeijão Tirolez Resfriado Tradicional 400g","14,90","un"),
  ("Cobertura Culinária R-Pizza Cheddar 1,2kg","15,90","un"),
  ("Cream Cheese Catupiry Resfriado 1,2kg","52,90","un"),
  ("Queijo Parmesão Faixa Azul Resfriado 195g","30,90","un"),
  ("Queijo Ralado Parmesão Président 50g","5,69","un"),
  ("Azeite de Oliva Andorinha Seleção 500ml","27,90","un"),
  ("Farinha de Trigo Tia Mara Tipo 1 1kg","2,95","un"),
  ("Catchup Sadio 830g","5,99","un"),
  ("Molho de Tomate Tambaú Pizza 1,7kg","10,90","un"),
  ("Milho Verde Quero 170g","3,49","un"),
  ("Maionese Ekma Minissachê 140x7g","19,90","un"),
  ("Ketchup Heinz Minissachê 144x7g","26,90","un"),
 ]),
 "atacadao_56cb6e227b_p2": (3, [
  ("Energético Red Bull Energy Drink 250ml","8,29","un"),
  ("Refrigerante Guaraná Antarctica 2,5L","7,99","un"),
  ("Isotônico Gatorade 500ml","4,99","un"),
  ("Refresco Líquido Kapo 200ml","2,19","un"),
  ("Água Mineral Indaiá com Gás 500ml","1,65","un"),
  ("Guardanapo TV Malu 14x14cm 160un","1,59","un"),
  ("Toalha de Papel Splash Interfolhas 1000 folhas","21,90","un"),
  ("Copo Descartável Cristalcopo 180ml 100un","4,99","un"),
  ("Embalagem para Pizza Ondunorte Oitavada 35cm 25un","26,90","un"),
 ]),
}

out = {}
tot = 0
for key, (ncols, items) in PAGES.items():
    boxes = grid(len(items), ncols)
    lst = []
    for (n, p, u), (x, y, w, h) in zip(items, boxes):
        lst.append({"n": n, "p": p, "u": u, "x": x, "y": y, "w": w, "h": h})
    out[key] = lst
    tot += len(lst)

json.dump(out, open(os.path.join(BASE, "data/_ingest_20260713_produtos.json"), "w",
          encoding="utf-8"), ensure_ascii=False, indent=1)
print("produtos.json escrito:", tot, "produtos em", len(out), "páginas")
