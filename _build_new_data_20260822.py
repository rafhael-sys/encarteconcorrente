#!/usr/bin/env python3
"""Monta _new_data.json da janela 2026-08-22 a partir da analise dos subagentes."""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))

acougue = [
    {"n": "Peito Serrado", "p": "27,99", "u": "kg", "x": 3, "y": 37, "w": 22, "h": 16},
    {"n": "Lombo Serrado", "p": "27,99", "u": "kg", "x": 26, "y": 37, "w": 22, "h": 16},
    {"n": "Carne Bovina Posta Gorda c/ Osso", "p": "28,98", "u": "kg", "x": 50, "y": 37, "w": 22, "h": 16},
    {"n": "Carne Dianteira de Sol", "p": "36,98", "u": "kg", "x": 74, "y": 37, "w": 22, "h": 16},
    {"n": "Carne Moída Dianteira", "p": "27,98", "u": "kg", "x": 6, "y": 56, "w": 26, "h": 18},
    {"n": "Alcatra Bovina Congelada", "p": "39,98", "u": "kg", "x": 38, "y": 56, "w": 26, "h": 18},
    {"n": "Costela Ponta de Agulha", "p": "21,98", "u": "kg", "x": 70, "y": 56, "w": 26, "h": 18},
    {"n": "Bisteca de Pernil Suíno", "p": "13,98", "u": "kg", "x": 6, "y": 76, "w": 26, "h": 18},
    {"n": "Carne Bovina Bisteca Paulista", "p": "32,98", "u": "kg", "x": 38, "y": 76, "w": 26, "h": 18},
    {"n": "Linguiça de Frango / Churrasco Avivar", "p": "12,98", "u": "kg", "x": 70, "y": 76, "w": 26, "h": 18},
]

products = {
    "DcTzuy9HB5H_p1": [{"n": "Café Santa Clara Extra Forte Almofada 250g", "p": "14,49", "u": "un", "x": 18, "y": 22, "w": 80, "h": 76}],
    "DcTzuy9HB5H_p2": [{"n": "Bebida Láctea Nescau Fator Crescer Chocolate 180ml", "p": "1,99", "u": "un", "x": 13, "y": 33, "w": 56, "h": 64}],
    "DcTzuy9HB5H_p3": [{"n": "Biscoito Rosquinha Mabel 300g Sabores", "p": "4,79", "u": "un", "x": 40, "y": 7, "w": 58, "h": 52}],
    "DcTzuy9HB5H_p4": [{"n": "Ovo Branco da Gema Grande C/30", "p": "15,89", "u": "un", "x": 50, "y": 7, "w": 45, "h": 55}],

    "DcTcpz_HDtc_p1": [{"n": "Detergente Líquido Limpol 500ml Maçã", "p": "2,19", "u": "un", "x": 8, "y": 42, "w": 52, "h": 56}],
    "DcTcpz_HDtc_p2": [{"n": "Lava Roupas Líquido eKonômico 3L", "p": "13,49", "u": "un", "x": 26, "y": 49, "w": 39, "h": 37}],
    "DcTcpz_HDtc_p3": [{"n": "Torrada Magic Toast Marilan 110g", "p": "6,99", "u": "un", "x": 25, "y": 41, "w": 45, "h": 45}],
    "DcTcpz_HDtc_p4": [{"n": "Panettone Parati Frutas 400g", "p": "27,99", "u": "un", "x": 33, "y": 48, "w": 60, "h": 52}],
    "DcTcpz_HDtc_p5": [{"n": "Pão de Leite Favorito 400g", "p": "4,99", "u": "un", "x": 26, "y": 51, "w": 43, "h": 43}],
    "DcTcpz_HDtc_p6": [{"n": "Tortilha Pitabread Integral 180g", "p": "8,49", "u": "un", "x": 30, "y": 50, "w": 45, "h": 47}],

    "DcUegoFm4kg_p1": [{"n": "Picanha Suína Excelência Temperada Congelada Linha Churrasco kg", "p": "26,89", "u": "kg", "x": 23, "y": 33, "w": 54, "h": 48}],
    "DcUegoFm4kg_p2": [{"n": "Lombo Suíno Aurora Congelado kg", "p": "17,90", "u": "kg (exceto Ceasa)", "x": 9, "y": 42, "w": 80, "h": 26}],
    "DcUegoFm4kg_p3": [{"n": "Filé de Peito de Frango Aurora Congelado Bandeja 1kg", "p": "16,99", "u": "cada", "x": 5, "y": 31, "w": 62, "h": 50}],
    "DcUegoFm4kg_p4": [{"n": "Linguiça de Frango ou Mista Churrasco Aurora Congelada kg", "p": "16,99", "u": "kg", "x": 17, "y": 31, "w": 72, "h": 44}],
    "DcUegoFm4kg_p5": [{"n": "Filezinho de Frango Aurora PC 1kg", "p": "15,79", "u": "cada", "x": 19, "y": 29, "w": 57, "h": 54}],
    "DcUegoFm4kg_p6": [{"n": "Pizza Sadia Sabores 460g", "p": "14,99", "u": "cada", "x": 9, "y": 27, "w": 80, "h": 54}],
    "DcUegoFm4kg_p7": [{"n": "Pão de Alho Baguete Zinho Recheado com Queijo Tradicional 300g", "p": "13,49", "u": "cada (exceto Ceasa)", "x": 9, "y": 38, "w": 63, "h": 40}],
    "DcUegoFm4kg_p8": [{"n": "Coxinhas de Frango Nossa Coxinha Congeladas PC 300g", "p": "11,99", "u": "cada (exceto Ceasa)", "x": 21, "y": 29, "w": 54, "h": 54}],
    "DcUegoFm4kg_p9": [{"n": "Steak de Frango Perdigão Dia a Dia 100g", "p": "1,65", "u": "cada", "x": 18, "y": 31, "w": 52, "h": 50}],
    "DcUegoFm4kg_p10": [{"n": "Açaí do Norte 5L", "p": "44,98", "u": "cada (exceto Ceasa)", "x": 21, "y": 34, "w": 54, "h": 46}],

    "DcTbxSBFm_J_p1": [
        {"n": "Açúcar Triturado Alegre 1kg", "p": "2,59", "u": "un", "x": 8, "y": 34, "w": 24, "h": 19},
        {"n": "Feijão Carioca DuBom 1kg", "p": "6,98", "u": "un", "x": 37, "y": 34, "w": 26, "h": 19},
        {"n": "Leite em Pó Integral Aurora 750g", "p": "25,89", "u": "un", "x": 69, "y": 34, "w": 24, "h": 19},
        {"n": "Macarrão Espaguete Bonsabor 400g", "p": "1,98", "u": "un", "x": 9, "y": 55, "w": 24, "h": 18},
        {"n": "Macarrão Parafuso Vitarella 400g", "p": "2,99", "u": "un", "x": 37, "y": 55, "w": 26, "h": 18},
        {"n": "Papel Higiênico Neutro Floral c/12 fd 20m", "p": "9,98", "u": "un", "x": 69, "y": 55, "w": 24, "h": 18},
        {"n": "Frango a Passarinho Jaguá IQF 1kg", "p": "10,98", "u": "pct", "x": 8, "y": 76, "w": 25, "h": 19},
        {"n": "Costela Bovina Ponta de Agulha", "p": "21,98", "u": "kg", "x": 42, "y": 76, "w": 23, "h": 19},
        {"n": "Bebida Láctea Morango Betânia BDJ 540g", "p": "2,99", "u": "un", "x": 69, "y": 76, "w": 25, "h": 19},
    ],
    "DcTbxSBFm_J_p2": [
        {"n": "Flocão de Milho Vitamilho 500g", "p": "1,19", "u": "un", "x": 8, "y": 3, "w": 25, "h": 22},
        {"n": "Café Santa Clara Clássico 250g", "p": "12,98", "u": "un", "x": 37, "y": 3, "w": 26, "h": 22},
        {"n": "Arroz Parboilizado Blue Soft 1kg", "p": "3,29", "u": "un", "x": 69, "y": 3, "w": 25, "h": 22},
        {"n": "Água Mineral Sterbom s/ Gás 510ml", "p": "0,89", "u": "un", "x": 9, "y": 30, "w": 24, "h": 22},
        {"n": "Cerveja Itaipava Pilsen 350ml", "p": "2,58", "u": "un", "x": 37, "y": 30, "w": 26, "h": 22},
        {"n": "Conhaque Dreher 900ml", "p": "19,98", "u": "un", "x": 69, "y": 30, "w": 24, "h": 22},
        {"n": "Amaciante Concentrado Downy 500ml Fragrâncias", "p": "9,98", "u": "un", "x": 8, "y": 57, "w": 25, "h": 22},
        {"n": "Coxa de Frango Friato pct 1kg", "p": "9,98", "u": "pct", "x": 37, "y": 57, "w": 26, "h": 22},
        {"n": "Filezinho Sassami Jaguá IQF 1kg", "p": "16,98", "u": "pct", "x": 69, "y": 57, "w": 25, "h": 22},
    ],

    "DcTTaSWMvlF_p1": [dict(p) for p in acougue],
    "DcTTPHGyNv__p1": [dict(p) for p in acougue],

    "DcUZGF4oEdu_p1": [
        {"n": "Papinha AllNutri 100g", "p": "5,99", "u": "un", "x": 3, "y": 39, "w": 18, "h": 14},
        {"n": "Farinha Láctea AllNutri 600g", "p": "14,99", "u": "un", "x": 27, "y": 39, "w": 17, "h": 14},
        {"n": "Achocolatado Trad/Levinho Toddynho 200ml", "p": "2,29", "u": "un", "x": 50, "y": 39, "w": 16, "h": 14},
        {"n": "Leite Fermentado Chamyto Trad Nestlé 450g", "p": "6,99", "u": "un", "x": 74, "y": 39, "w": 22, "h": 14},
        {"n": "Leite Integral Instantâneo Ninho 750g", "p": "32,99", "u": "un", "x": 5, "y": 57, "w": 18, "h": 14},
        {"n": "Leite em Pó Integral LeitBom 700g", "p": "25,99", "u": "un", "x": 27, "y": 57, "w": 18, "h": 14},
        {"n": "Leite em Pó Italac Integral 200g", "p": "6,99", "u": "un", "x": 51, "y": 57, "w": 17, "h": 14},
        {"n": "Leite em Pó Zero Lactose Itambé 300g", "p": "19,89", "u": "un", "x": 75, "y": 57, "w": 19, "h": 14},
        {"n": "Leite UHT Integral Zero Lactose Tampa Italac 1lt", "p": "7,99", "u": "un", "x": 3, "y": 75, "w": 19, "h": 14},
        {"n": "Alimento em Pó Sem Lactose Nature SupraSoy 300g", "p": "19,99", "u": "un", "x": 28, "y": 75, "w": 18, "h": 14},
        {"n": "Mingau Mucilon 600g Sabores", "p": "16,99", "u": "un", "x": 52, "y": 75, "w": 17, "h": 14},
        {"n": "Cremogema LV 180g e PG 130g Tradicional", "p": "4,49", "u": "un", "x": 75, "y": 75, "w": 20, "h": 14},
    ],
    "DcUZGF4oEdu_p2": [
        {"n": "Kit Condicionador Kids Salon Line 500ml", "p": "23,99", "u": "cada", "x": 3, "y": 40, "w": 22, "h": 14},
        {"n": "Gelatina Salon Line 550g", "p": "23,99", "u": "cada", "x": 28, "y": 42, "w": 18, "h": 13},
        {"n": "Kit Sabonete Líquido Bebê Granado", "p": "39,99", "u": "cada", "x": 50, "y": 40, "w": 20, "h": 14},
        {"n": "Sabonete Infantil Glicerina Ref Baruel Baby 210ml", "p": "7,99", "u": "cada", "x": 74, "y": 38, "w": 20, "h": 15},
        {"n": "Enxaguante Bucal Infantil Barbie Condor 250ml", "p": "19,99", "u": "cada", "x": 4, "y": 58, "w": 17, "h": 13},
        {"n": "Creme Dental Morango Tandy 50g Sabores", "p": "9,99", "u": "cada", "x": 27, "y": 60, "w": 18, "h": 11},
        {"n": "Creme Infantil P/ Assadura Turma da Xuxinha 45g", "p": "10,99", "u": "cada", "x": 50, "y": 58, "w": 18, "h": 13},
        {"n": "Talco Infantil Flora Neném 180g", "p": "9,99", "u": "cada", "x": 76, "y": 58, "w": 18, "h": 13},
        {"n": "Toalha Umedecida C/120un Premium Piquitucho", "p": "10,99", "u": "un", "x": 3, "y": 76, "w": 18, "h": 13},
        {"n": "Fralda Cremer Jumbo Shortinho", "p": "24,99", "u": "cada", "x": 27, "y": 74, "w": 18, "h": 15},
        {"n": "Fralda Natural Baby Premium Mega Baby", "p": "32,99", "u": "cada", "x": 50, "y": 76, "w": 18, "h": 13},
        {"n": "Amaciante Vida Macia 500ml", "p": "7,99", "u": "cada", "x": 76, "y": 74, "w": 18, "h": 15},
    ],

    "atacadao_57d87eb04f_p1": [
        {"n": "Goma de Mandioca Delícia Potiguar Pacote 1kg", "p": "4,79", "u": "un", "x": 5, "y": 34, "w": 30, "h": 22},
        {"n": "Laranja-pera", "p": "1,89", "u": "kg", "x": 52, "y": 34, "w": 28, "h": 18},
        {"n": "Frango Mauricéa Congelado", "p": "8,79", "u": "preço por quilo na peça", "x": 5, "y": 60, "w": 30, "h": 18},
        {"n": "Salsicha Hot Dog Perdigão Congelada Pacote 5kg", "p": "54,90", "u": "pacote 5kg (kg sai 10,98)", "x": 52, "y": 60, "w": 30, "h": 18},
        {"n": "Refrigerante Coca-Cola Zero Açúcar Pet 2L", "p": "9,98", "u": "un", "x": 7, "y": 80, "w": 26, "h": 18},
        {"n": "Cerveja Heineken Long Neck 330ml", "p": "5,99", "u": "un", "x": 52, "y": 80, "w": 26, "h": 18},
    ],

    "nosso_a2a99062a3_p1": [
        {"n": "Flocão Nordestino 500g", "p": "1,29", "u": "un", "x": 7, "y": 18, "w": 15, "h": 15},
        {"n": "Fécula de Mandioca Lopes 1Kg", "p": "4,78", "u": "un", "x": 22, "y": 19, "w": 14, "h": 14},
        {"n": "Café Kimimo 250g", "p": "11,88", "u": "un", "x": 36, "y": 19, "w": 14, "h": 14},
        {"n": "Óleo de Soja Coamo 900ml", "p": "7,28", "u": "un", "x": 50, "y": 17, "w": 14, "h": 16},
        {"n": "Margarina Puro Sabor com Sal 3kg", "p": "25,48", "u": "un", "x": 64, "y": 16, "w": 15, "h": 17},
        {"n": "Leite em Pó Betânia Integral 750g", "p": "24,98", "u": "un", "x": 79, "y": 17, "w": 16, "h": 16},
        {"n": "Carne Bovina Acém ou Paleta c/ Osso", "p": "27,68", "u": "kg", "x": 7, "y": 38, "w": 16, "h": 14},
        {"n": "Carne Bovina Patinho", "p": "39,48", "u": "kg", "x": 24, "y": 38, "w": 16, "h": 14},
        {"n": "Costela Suína", "p": "18,98", "u": "kg", "x": 42, "y": 38, "w": 15, "h": 14},
        {"n": "Coxa e Sobrecoxa Lar com Dorsal", "p": "7,68", "u": "kg", "x": 59, "y": 38, "w": 15, "h": 14},
        {"n": "Linguiça Suína Aurora", "p": "15,68", "u": "kg", "x": 77, "y": 38, "w": 16, "h": 14},
        {"n": "Bebida Láctea Italakinho 200ml", "p": "1,19", "u": "un", "x": 7, "y": 56, "w": 15, "h": 13},
        {"n": "Cerveja Lokal Pilsen 350ml", "p": "2,29", "u": "un", "x": 24, "y": 56, "w": 14, "h": 13},
        {"n": "Cerveja Michelob Lata 350ml", "p": "4,69", "u": "un", "x": 40, "y": 56, "w": 15, "h": 13},
        {"n": "Whisky Chivas Regal 12 Anos 1L", "p": "114,98", "u": "un", "x": 57, "y": 56, "w": 15, "h": 13},
        {"n": "Kuat Guaraná 2 Litros", "p": "7,38", "u": "un", "x": 78, "y": 56, "w": 16, "h": 13},
        {"n": "Tomate Cajá ou Longa Vida", "p": "2,98", "u": "kg", "x": 7, "y": 72, "w": 15, "h": 12},
        {"n": "Batata Inglesa", "p": "4,88", "u": "kg", "x": 24, "y": 72, "w": 14, "h": 12},
        {"n": "Abacate", "p": "4,88", "u": "un", "x": 40, "y": 72, "w": 15, "h": 12},
        {"n": "Goiaba", "p": "3,98", "u": "kg", "x": 57, "y": 72, "w": 13, "h": 12},
        {"n": "Ovos Vermelhos Grandes ou Extras Bandeja com 30", "p": "14,78", "u": "bandeja 30", "x": 72, "y": 72, "w": 23, "h": 12},
        {"n": "Creme Dental Oral-B 70g", "p": "3,68", "u": "un", "x": 7, "y": 85, "w": 14, "h": 13},
        {"n": "Água Sanitária Ypê 1L", "p": "2,29", "u": "un", "x": 24, "y": 85, "w": 14, "h": 13},
        {"n": "Amaciante Comfort 500ml + 400ml", "p": "8,98", "u": "un", "x": 40, "y": 85, "w": 15, "h": 13},
        {"n": "Ração Bomguy 10,1Kg", "p": "69,98", "u": "un", "x": 57, "y": 85, "w": 14, "h": 13},
        {"n": "Fralda Mili Love & Care Pants Jumbo", "p": "28,98", "u": "un", "x": 72, "y": 85, "w": 23, "h": 13},
    ],
}

actions = [
    {"id": "DcTzuy9HB5H", "titulo": "Favoritaço Gôndola — Parnamirim e Macaíba (19 a 25/08)",
     "banner": "Favorito Super / Atacado Favorito", "segmento": "varejo",
     "inicio": "2026-08-19", "fim": "2026-08-25"},
    {"id": "DcTcpz_HDtc", "titulo": "Favoritaço Gôndola — Ponta Negra e Ayrton Senna C (19 a 25/08)",
     "banner": "Favorito Super / Atacado Favorito", "segmento": "varejo",
     "inicio": "2026-08-19", "fim": "2026-08-25"},
    {"id": "DcUegoFm4kg", "titulo": "Ofertas de Fim de Semana Churrasco — Mar Vermelho (22 a 24/08)",
     "banner": "Mar Vermelho Atacado", "segmento": "atacarejo",
     "inicio": "2026-08-22", "fim": "2026-08-24"},
    {"id": "DcTbxSBFm_J", "titulo": "Mega Ofertas da Semana — Leva Mais João Câmara (21 a 23/08)",
     "banner": "Leva Mais Atacarejo João Câmara", "segmento": "atacarejo",
     "inicio": "2026-08-21", "fim": "2026-08-23"},
    {"id": "DcTTaSWMvlF", "titulo": "Ofertas do Açougue — Leva Mais João Câmara (21 a 23/08)",
     "banner": "Leva Mais Atacarejo João Câmara", "segmento": "atacarejo",
     "inicio": "2026-08-21", "fim": "2026-08-23"},
    {"id": "DcTTPHGyNv_", "titulo": "Ofertas do Açougue — Leva Mais Macau (21 a 23/08)",
     "banner": "Leva Mais Atacarejo", "segmento": "atacarejo",
     "inicio": "2026-08-21", "fim": "2026-08-23"},
    {"id": "DcUZGF4oEdu", "titulo": "Festival Baby e Kids — Atacarejo Santo Antônio (22 a 28/08)",
     "banner": "Atacarejo Santo Antônio", "segmento": "atacarejo",
     "inicio": "2026-08-22", "fim": "2026-08-28"},
    {"id": "atacadao_57d87eb04f", "titulo": "Atacadão — Boa do Dia (22/08)",
     "banner": "Atacadão", "segmento": "atacarejo",
     "inicio": "2026-08-22", "fim": "2026-08-22", "fonte": "web",
     "link": "https://www.atacadao.com.br/loja/natal-sul"},
    {"id": "nosso_a2a99062a3", "titulo": "Nosso Final de Semana — Nosso Atacarejo (21 a 23/08)",
     "banner": "Nosso Atacarejo", "segmento": "atacarejo",
     "inicio": "2026-08-21", "fim": "2026-08-23", "fonte": "web",
     "link": "https://www.nossoatacarejo.com.br/encarte/nosso-final-de-semana-rn/5"},
]

descartes = {
    "publicidade_teaser": [
        "DcTU8q6oLVG (Queiroz Atacadão JC — teaser de aniversário, sem preço)",
        "DcTVEaCoA2n (Queiroz Atacadão Natal — teaser de aniversário, sem preço)",
        "DcTaUaPlpza (Mirassol Atacado — evento Circuito Mira, sem preço)",
        "DcVdk4mFqNY (Super Nordestão — Oferta Surpresa do app, produto borrado sem preço)",
        "DcTNXFJTeBQ (Favorito — arte teaser Sexta da Carne, sem preço)",
        "DcTzkrczYAC (Favorito — arte teaser Sextou da Carne, sem preço)",
    ],
    "duplicata_mesma_loja_periodo": [
        "DcTuTwGmzZu (MV Ofertas da Semana 21-27/08 — 6 itens 100% ja em DcR5gSXm9zS)",
        "DcTMEi9Gw7L (MV Feirao Hortifruti 20-21/08 — 9 itens 100% ja em DcPUqm8GxMS)",
        "DcTXcbsm53X (MV Festival de Pescados 20-24/08 — 12 itens 100% ja em DcPiUQYGwmt)",
        "DcT9au2IBrZ (Santo Antonio novo encarte 20-26/08 — 20 itens 100% ja em DcPNkG_oKuA)",
    ],
}

new = {"actions": actions, "products": products, "descartes": descartes}
tmp = os.path.join(BASE, "_new_data.json.tmp")
with open(tmp, "w", encoding="utf-8") as f:
    json.dump(new, f, ensure_ascii=False, indent=1)
os.replace(tmp, os.path.join(BASE, "_new_data.json"))

nprod = sum(len(v) for v in products.values())
print(f"OK: {len(actions)} acoes, {nprod} produtos em {len(products)} paginas")
for a in actions:
    keys = [k for k in products if k.startswith(a["id"])]
    print(" -", a["id"], "->", sum(len(products[k]) for k in keys), "prod")
