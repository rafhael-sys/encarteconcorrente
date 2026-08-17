#!/usr/bin/env python3
"""Ingestao da janela de 2026-08-17 (analise diaria do Claude).

Adiciona as 5 acoes NOVAS decididas por leitura das imagens (classificacao/dedup
ja feita). Descartes desta janela NAO entram:
  - DcI7xKizpn4  (teaser "Terca do Cashback" Favorito, sem precos)
  - DcGVZfdlvNK  (teaser "Dia Q do Comerciante" Queiroz, B2B, sem precos)
  - DcBdtS9oKTe  (teaser "Faltam 3 dias / Dia Q do Comerciante", B2B, sem precos)
  - Db-6EH4m6tx  (encarte B2B "Alo Comerciante" Queiroz, revenda + expirado)

canon: canonicalizacao por nrm_tokens (mesma logica de ingest_20260815.py);
NUNCA une pares marcados DIFERENTES em regras_similaridade.md.

DRY_RUN por padrao. Rode 'python3 ingest_20260817.py commit' p/ gravar.
"""
import json
import os
import re
import shutil
import sys
import unicodedata

BASE = os.path.dirname(os.path.abspath(__file__))
HOJE = "2026-08-17"
DRY_RUN = not (len(sys.argv) > 1 and sys.argv[1] == "commit")

NOISE = {"lata", "lta", "pct", "pcte", "pacote", "pet", "tb", "gf", "cada", "un",
         "und", "unid", "unidade", "sabores", "sabor", "fragrancias",
         "fragrancia", "tipos", "tipo"}


def path(*p):
    return os.path.join(BASE, *p)


def nrm_tokens(s):
    s = unicodedata.normalize("NFD", str(s).lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    return tuple(sorted(t for t in s.split() if t and t not in NOISE))


def nrm_name(s):
    s = unicodedata.normalize("NFD", str(s).lower())
    return " ".join("".join(c for c in s if unicodedata.category(c) != "Mn").split())


def salva(p, data):
    tmp = f"{p}.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    os.replace(tmp, p)


# --- Produtos extraidos das imagens (pagekey = arquivo sem .jpg) ---
# Fonte: leitura das paginas nesta janela. "&amp;" ja normalizado p/ "&".
EXTRACTS_JSON = r"""
{
 "DcI-a4pnMgp": [
  {"key": "DcI-a4pnMgp_p1", "produtos": [{"n": "Desinfetante Becker Lavanda 3L", "p": "9,99", "u": "de R$ 10,99", "x": 27, "y": 2, "w": 47, "h": 70}]},
  {"key": "DcI-a4pnMgp_p2", "produtos": [{"n": "Desodorante Aerosol Nivea 150ml", "p": "12,99", "u": "de R$ 14,99", "x": 18, "y": 48, "w": 53, "h": 51}]},
  {"key": "DcI-a4pnMgp_p3", "produtos": [{"n": "Água Sanitária Olimpo 1L", "p": "1,99", "u": "de R$ 2,29", "x": 18, "y": 3, "w": 42, "h": 59}]},
  {"key": "DcI-a4pnMgp_p4", "produtos": [{"n": "Papel Higiênico Deluxe Cotton Folha Dupla 20m 12 rolos", "p": "13,99", "u": "leve 12 pague 11", "x": 44, "y": 5, "w": 18, "h": 35}]},
  {"key": "DcI-a4pnMgp_p5", "produtos": [{"n": "Azeite de Oliva Extra Virgem Condesa Antunes 500ml", "p": "27,99", "u": "de R$ 42,99", "x": 30, "y": 18, "w": 27, "h": 47}]}
 ],
 "DcGgGp8nJi7": [
  {"key": "DcGgGp8nJi7_p1", "produtos": [{"n": "Filé de Tilápia Lar 700g", "p": "36,99", "u": "preço exclusivo cliente clube, de R$ 45,90", "x": 57, "y": 13, "w": 42, "h": 53}]},
  {"key": "DcGgGp8nJi7_p2", "produtos": [{"n": "Frango a Passarinho Lar IQF 1kg", "p": "11,99", "u": "cada, de R$ 13,99", "x": 50, "y": 18, "w": 49, "h": 45}]},
  {"key": "DcGgGp8nJi7_p3", "produtos": [{"n": "Filé de Peito de Frango Lar IQF 1kg", "p": "18,99", "u": "cada, de R$ 24,99", "x": 57, "y": 26, "w": 42, "h": 36}]},
  {"key": "DcGgGp8nJi7_p4", "produtos": [{"n": "Linguiça de Frango Aurora 700g", "p": "11,99", "u": "cada, de R$ 26,90", "x": 17, "y": 4, "w": 38, "h": 61}]},
  {"key": "DcGgGp8nJi7_p5", "produtos": [{"n": "Batata Palito Congelada Uai 2kg", "p": "21,99", "u": "cada, de R$ 26,99", "x": 5, "y": 2, "w": 48, "h": 65}]}
 ],
 "DcGfTsRHFEL": [
  {"key": "DcGfTsRHFEL_p1", "produtos": [{"n": "Goma de Mandioca Hidratada Kumê 1kg", "p": "4,59", "u": "cada", "x": 34, "y": 24, "w": 61, "h": 68}]},
  {"key": "DcGfTsRHFEL_p2", "produtos": [{"n": "Sabonete Even Suave 85g", "p": "1,79", "u": "cada", "x": 1, "y": 17, "w": 72, "h": 76}]},
  {"key": "DcGfTsRHFEL_p3", "produtos": [{"n": "Papel Higiênico Floral Folha Dupla Neutro 12 rolos 20m", "p": "10,90", "u": "cada", "x": 5, "y": 47, "w": 47, "h": 46}]},
  {"key": "DcGfTsRHFEL_p4", "produtos": [{"n": "Flocão de Milho Dona Clara 500g", "p": "1,39", "u": "cada", "x": 58, "y": 22, "w": 34, "h": 32}]},
  {"key": "DcGfTsRHFEL_p5", "produtos": [{"n": "Macarrão Parafuso Estrela Sêmola 400g", "p": "3,99", "u": "cada", "x": 12, "y": 55, "w": 27, "h": 28}]},
  {"key": "DcGfTsRHFEL_p6", "produtos": [{"n": "Maionese Hellmann's Sachê 200g", "p": "5,49", "u": "cada", "x": 20, "y": 45, "w": 34, "h": 38}]}
 ],
 "DcHTjscoAO2": [
  {"key": "DcHTjscoAO2_p1", "produtos": [
    {"n": "Carne Bovina Coxão Mole kg", "p": "38,90", "u": "kg", "x": 11, "y": 45, "w": 18, "h": 22},
    {"n": "Carne Bovina Capa de Filé kg", "p": "29,98", "u": "kg", "x": 30, "y": 45, "w": 18, "h": 22},
    {"n": "Carne Suína Carré kg", "p": "12,49", "u": "kg", "x": 50, "y": 45, "w": 18, "h": 22},
    {"n": "Pernil Suíno Congelado kg", "p": "11,98", "u": "kg", "x": 70, "y": 45, "w": 18, "h": 22},
    {"n": "Filé de Peito de Frango Congelado kg", "p": "13,85", "u": "kg", "x": 11, "y": 68, "w": 18, "h": 17},
    {"n": "Peito de Frango Congelado kg", "p": "8,90", "u": "kg", "x": 30, "y": 68, "w": 18, "h": 17},
    {"n": "Coxa e Sobrecoxa de Frango com Dorsal kg", "p": "6,90", "u": "kg", "x": 50, "y": 68, "w": 18, "h": 17},
    {"n": "Coxa e Sobrecoxa de Frango sem Dorsal kg", "p": "7,98", "u": "kg", "x": 70, "y": 68, "w": 18, "h": 17}
  ]},
  {"key": "DcHTjscoAO2_p2", "produtos": [
    {"n": "Leite em Pó Ninho 750g Integral ou Instantâneo", "p": "29,99", "u": "", "x": 5, "y": 6, "w": 17, "h": 26},
    {"n": "Molho de Tomate Tradicional Quero Sachê 240g", "p": "1,45", "u": "", "x": 24, "y": 6, "w": 17, "h": 26},
    {"n": "Batata Palha Gratícia 400g Culinária", "p": "13,99", "u": "", "x": 43, "y": 6, "w": 17, "h": 26},
    {"n": "Cerveja Pilsen Itaipava Lata 350ml", "p": "2,54", "u": "", "x": 62, "y": 6, "w": 17, "h": 26},
    {"n": "Cerveja Budweiser Lata 350ml", "p": "3,59", "u": "", "x": 81, "y": 6, "w": 17, "h": 26},
    {"n": "Refrigerante Pepsi Cola 1L Tradicional", "p": "4,18", "u": "", "x": 5, "y": 33, "w": 17, "h": 22},
    {"n": "Whisky Escocês Black & White 1L", "p": "57,98", "u": "", "x": 24, "y": 33, "w": 17, "h": 22},
    {"n": "Sabonete em Barra Sensus 80g", "p": "1,38", "u": "", "x": 43, "y": 33, "w": 17, "h": 22},
    {"n": "Creme Dental Colgate MPA Menta Refrescante 90g", "p": "4,35", "u": "", "x": 62, "y": 33, "w": 17, "h": 22},
    {"n": "Absorvente Naturalmente Max com 10un com Abas", "p": "5,28", "u": "", "x": 81, "y": 33, "w": 17, "h": 22},
    {"n": "Ração Úmida Sachê Whiskas 85g Sabores", "p": "2,19", "u": "", "x": 5, "y": 58, "w": 17, "h": 24},
    {"n": "Ração Úmida Sachê Champ e Kitekat Sabores", "p": "1,85", "u": "", "x": 24, "y": 58, "w": 17, "h": 24},
    {"n": "Amaciante Downy 500ml Fragrâncias", "p": "8,79", "u": "", "x": 43, "y": 58, "w": 17, "h": 24},
    {"n": "Água Sanitária Dragão 1L", "p": "1,85", "u": "", "x": 62, "y": 58, "w": 17, "h": 24},
    {"n": "Inseticida Aerosol Baygon 360ml Ação Total Tradicional", "p": "11,99", "u": "", "x": 81, "y": 58, "w": 17, "h": 24}
  ]},
  {"key": "DcHTjscoAO2_p3", "produtos": [
    {"n": "Maçã Nacional kg", "p": "7,00", "u": "kg", "x": 24, "y": 3, "w": 17, "h": 17},
    {"n": "Goma Hidratada Caicó 1kg", "p": "3,59", "u": "", "x": 43, "y": 3, "w": 17, "h": 17},
    {"n": "Alho a Granel kg", "p": "17,00", "u": "kg", "x": 62, "y": 3, "w": 17, "h": 17},
    {"n": "Copo Nadir Americano 190ml", "p": "1,05", "u": "", "x": 5, "y": 24, "w": 17, "h": 18},
    {"n": "Papel Toalha Mili 2un Folha Dupla", "p": "4,98", "u": "", "x": 24, "y": 24, "w": 17, "h": 18},
    {"n": "Bolacha Jucurutu Manteiga do Sertão 250g", "p": "5,19", "u": "", "x": 43, "y": 24, "w": 17, "h": 18},
    {"n": "Pão de Forma Center Massas 400g", "p": "4,98", "u": "", "x": 62, "y": 24, "w": 17, "h": 18},
    {"n": "Frango Bom Todo com Miúdos kg", "p": "8,78", "u": "kg", "x": 81, "y": 24, "w": 17, "h": 18},
    {"n": "Galinha Pequena Q Delícia Congelada kg", "p": "5,39", "u": "kg", "x": 5, "y": 45, "w": 17, "h": 18},
    {"n": "Filé de Peito de Frango Levo Alimentos 1kg", "p": "15,98", "u": "", "x": 24, "y": 45, "w": 17, "h": 18},
    {"n": "Steak de Frango Seara 100g", "p": "1,19", "u": "", "x": 43, "y": 45, "w": 17, "h": 18},
    {"n": "Salsicha Hot Dog Avivar kg", "p": "5,49", "u": "kg", "x": 62, "y": 45, "w": 17, "h": 18},
    {"n": "Margarina Puro Sabor 3kg", "p": "26,98", "u": "", "x": 81, "y": 45, "w": 17, "h": 18},
    {"n": "Queijo Ralado Pampulha 50g", "p": "3,79", "u": "", "x": 5, "y": 66, "w": 17, "h": 18},
    {"n": "Queijo Mussarela Freezer Peça ou Pedaço kg", "p": "37,98", "u": "kg", "x": 24, "y": 66, "w": 17, "h": 18},
    {"n": "Arroz Parboilizado Branco Fazenda 1kg", "p": "3,19", "u": "", "x": 43, "y": 66, "w": 17, "h": 18},
    {"n": "Feijão Carioca Precioso 1kg", "p": "6,78", "u": "", "x": 62, "y": 66, "w": 17, "h": 18},
    {"n": "Leite Condensado CCGL Semidesnatado 395g", "p": "5,25", "u": "", "x": 81, "y": 66, "w": 17, "h": 18}
  ]}
 ],
 "DcHg2p1mnjy": [
  {"key": "DcHg2p1mnjy_p1", "produtos": []},
  {"key": "DcHg2p1mnjy_p2", "produtos": [
    {"n": "Arroz Parboilizado Caçarola 1kg", "p": "3,48", "u": "", "x": 2, "y": 5, "w": 15, "h": 17},
    {"n": "Feijão Carioca Precioso ou Belo Grão 1kg", "p": "6,98", "u": "", "x": 18, "y": 5, "w": 15, "h": 17},
    {"n": "Macarrão Espaguete Fino Vitarella 400g", "p": "2,29", "u": "", "x": 34, "y": 5, "w": 14, "h": 17},
    {"n": "Café Torrado São Braz Almofada Extra Forte 250g", "p": "11,98", "u": "", "x": 49, "y": 5, "w": 15, "h": 17},
    {"n": "Farinha de Trigo Finna s/ Fermento 1kg", "p": "3,68", "u": "", "x": 65, "y": 5, "w": 14, "h": 17},
    {"n": "Flocão de Milho Fortemilho 400g", "p": "0,98", "u": "", "x": 82, "y": 5, "w": 15, "h": 17},
    {"n": "Limpa Pisos Azulim 1L Citrus ou Lavanda", "p": "7,49", "u": "no app 6,99", "x": 7, "y": 27, "w": 9, "h": 11},
    {"n": "Água Sanitária Dragão 5L", "p": "12,49", "u": "no app 11,79", "x": 16, "y": 27, "w": 9, "h": 11},
    {"n": "Whisky Old Parr 12 Anos 1L", "p": "119,98", "u": "no app 116,90", "x": 25, "y": 27, "w": 9, "h": 11},
    {"n": "Bebida Láctea UHT Pirakids Chocolate 200ml", "p": "1,49", "u": "no app 1,25", "x": 34, "y": 27, "w": 9, "h": 11},
    {"n": "Creme de Leite CCGL Tradicional 200g", "p": "2,79", "u": "no app 2,38", "x": 43, "y": 27, "w": 9, "h": 11},
    {"n": "Requeijão Clan Light ou Tradicional 200g", "p": "7,38", "u": "no app 6,89", "x": 52, "y": 27, "w": 9, "h": 11},
    {"n": "Queijo do Reino Ilda Lata ou Fracionado", "p": "79,98", "u": "kg, no app 76,98", "x": 61, "y": 27, "w": 9, "h": 11},
    {"n": "Queijo Bom Todo Congelado 1kg", "p": "15,48", "u": "no app 14,28", "x": 70, "y": 27, "w": 9, "h": 11},
    {"n": "Carne Bovina Peito ou Acém com Osso", "p": "28,90", "u": "kg, no app 27,48", "x": 79, "y": 27, "w": 9, "h": 11},
    {"n": "Pernil Suíno Congelado", "p": "13,98", "u": "kg, no app 11,98", "x": 88, "y": 27, "w": 9, "h": 11},
    {"n": "Carne Bovina Capa de Filé Congelada", "p": "33,98", "u": "kg", "x": 7, "y": 40, "w": 11, "h": 9},
    {"n": "Carne Bovina Coxão Duro Peça", "p": "36,48", "u": "kg", "x": 18, "y": 40, "w": 11, "h": 9},
    {"n": "Coração Bovino Congelado", "p": "14,98", "u": "kg", "x": 29, "y": 40, "w": 11, "h": 9},
    {"n": "Carne de Sol Coxão Mole", "p": "44,98", "u": "kg", "x": 40, "y": 40, "w": 11, "h": 9},
    {"n": "Costela Bovina Janela ou Minga Congelada", "p": "24,98", "u": "kg", "x": 52, "y": 40, "w": 11, "h": 9},
    {"n": "Costela Suína c/ Pele Jucurutu", "p": "24,98", "u": "kg", "x": 64, "y": 40, "w": 11, "h": 9},
    {"n": "Frango Jaguá Congelado c/ Miúdos", "p": "9,98", "u": "kg", "x": 76, "y": 40, "w": 11, "h": 9},
    {"n": "Coxa e Sobrecoxa de Frango c/ Dorsal", "p": "7,28", "u": "kg", "x": 88, "y": 40, "w": 11, "h": 9},
    {"n": "Coxa de Frango Bom Todo Resfriada", "p": "10,98", "u": "kg", "x": 7, "y": 50, "w": 11, "h": 9},
    {"n": "Peito de Frango Congelado", "p": "9,48", "u": "kg", "x": 18, "y": 50, "w": 11, "h": 9},
    {"n": "Galinha Pequena Q Delícia Congelada", "p": "5,78", "u": "kg", "x": 29, "y": 50, "w": 11, "h": 9},
    {"n": "Linguiça Suína Churrasco Aurora", "p": "16,98", "u": "kg", "x": 40, "y": 50, "w": 11, "h": 9},
    {"n": "Batata Frita Easychef Tradicional Congelada 2kg", "p": "18,98", "u": "", "x": 52, "y": 50, "w": 11, "h": 9},
    {"n": "Filé de Peito de Frango Sadia 1kg", "p": "18,78", "u": "", "x": 64, "y": 50, "w": 11, "h": 9},
    {"n": "Frango à Passarinho Bom Todo IQF Temperado 1kg", "p": "11,68", "u": "", "x": 76, "y": 50, "w": 11, "h": 9},
    {"n": "Linguiça de Frango Bom Todo Congelada", "p": "12,78", "u": "kg", "x": 88, "y": 50, "w": 11, "h": 9},
    {"n": "Requeijão Jucurutu Tradicional 400g", "p": "12,99", "u": "", "x": 7, "y": 60, "w": 11, "h": 9},
    {"n": "Batata Palito Bom Todo Pré-Frita Temperada 1kg", "p": "11,58", "u": "", "x": 18, "y": 60, "w": 11, "h": 9},
    {"n": "Steak de Frango Seara 100g", "p": "1,28", "u": "", "x": 29, "y": 60, "w": 11, "h": 9},
    {"n": "Morango Inteiro Easychef Congelado 1,01kg", "p": "11,78", "u": "", "x": 40, "y": 60, "w": 11, "h": 9},
    {"n": "Polpa de Fruta Canaã 1kg (Abacaxi/Caju/Goiaba/Manga/Tangerina)", "p": "6,99", "u": "", "x": 52, "y": 60, "w": 11, "h": 9},
    {"n": "Salsicha Hot Dog Bom Todo", "p": "6,68", "u": "kg", "x": 64, "y": 60, "w": 11, "h": 9},
    {"n": "Presunto de Peru Perdigão/Sadia Peça, Pedaço ou Fatiado", "p": "27,98", "u": "kg", "x": 76, "y": 60, "w": 11, "h": 9},
    {"n": "Queijo Petit Suisse Nestlé Sabores 320g", "p": "9,98", "u": "", "x": 88, "y": 60, "w": 11, "h": 9},
    {"n": "Queijo Mussarela Freezer Peça ou Pedaço", "p": "36,98", "u": "kg", "x": 7, "y": 69, "w": 11, "h": 9},
    {"n": "Iogurte Nestlé Chambinho, Chamyto ou Ninho 100g", "p": "3,49", "u": "", "x": 18, "y": 69, "w": 11, "h": 9},
    {"n": "Bebida Láctea Isis Sachê Sabores 900g", "p": "4,98", "u": "", "x": 29, "y": 69, "w": 11, "h": 9},
    {"n": "Iogurte Isis Parcialmente Desnatado Sabores 170g", "p": "2,99", "u": "", "x": 40, "y": 69, "w": 11, "h": 9},
    {"n": "Iogurte Integral Clan Geleia de Morango 130g", "p": "3,68", "u": "", "x": 52, "y": 69, "w": 11, "h": 9},
    {"n": "Iogurte de Polpa Clan Sabores 540g", "p": "4,89", "u": "", "x": 64, "y": 69, "w": 11, "h": 9},
    {"n": "Margarina Delícia 500g", "p": "5,89", "u": "", "x": 76, "y": 69, "w": 11, "h": 9},
    {"n": "Manteiga Itacolomy 500g", "p": "25,98", "u": "", "x": 88, "y": 69, "w": 11, "h": 9},
    {"n": "Limpeza Perfumada Casa Perfume 1V 1L PG 900ml Fragrâncias", "p": "9,89", "u": "no cartão 9,19", "x": 40, "y": 83, "w": 10, "h": 11},
    {"n": "Kit Vida Macia Lava Roupas + Amaciante 1L Glicerina", "p": "28,29", "u": "no cartão 25,99", "x": 53, "y": 83, "w": 10, "h": 11},
    {"n": "Essência Limpeza Concentrada Coala 120ml Fragrâncias", "p": "11,19", "u": "no cartão 9,98", "x": 63, "y": 83, "w": 10, "h": 11},
    {"n": "Difusor de Ambientes Varetas Coala 100ml Fragrâncias", "p": "13,98", "u": "no cartão 13,19", "x": 76, "y": 83, "w": 10, "h": 11},
    {"n": "Odorizante de Ambientes Spray Coala 260ml Fragrâncias", "p": "26,98", "u": "no cartão 25,29", "x": 88, "y": 83, "w": 10, "h": 11}
  ]},
  {"key": "DcHg2p1mnjy_p3", "produtos": [
    {"n": "Leite Condensado CCGL Semidesnatado 395g", "p": "5,28", "u": "", "x": 7, "y": 4, "w": 11, "h": 8},
    {"n": "Achocolatado em Pó Powerlate Sachê 700g", "p": "10,98", "u": "", "x": 18, "y": 4, "w": 11, "h": 8},
    {"n": "Azeite Extra Virgem Conde Benalua 500ml", "p": "28,98", "u": "", "x": 29, "y": 4, "w": 11, "h": 8},
    {"n": "Bebida Láctea Betânia Chocolate Kids 200ml", "p": "1,45", "u": "", "x": 40, "y": 4, "w": 11, "h": 8},
    {"n": "Biscoito Cream Cracker Vitarella Tostatinha 350g", "p": "4,68", "u": "", "x": 52, "y": 4, "w": 11, "h": 8},
    {"n": "Biscoito Coberto Choco Biscuit Bauducco Sabores 80g", "p": "6,98", "u": "", "x": 64, "y": 4, "w": 11, "h": 8},
    {"n": "Biscoito Cookies Vitarella Gotas Chocolate Branco 80g", "p": "3,98", "u": "", "x": 76, "y": 4, "w": 11, "h": 8},
    {"n": "Caixa de Bombom Garoto 220g", "p": "9,98", "u": "", "x": 88, "y": 4, "w": 11, "h": 8},
    {"n": "Café Solúvel Santa Clara Clássico/Extra Forte Refil 40g", "p": "5,68", "u": "", "x": 7, "y": 13, "w": 11, "h": 9},
    {"n": "Chocolate em Barra Garoto Sabores 80g", "p": "6,98", "u": "", "x": 18, "y": 13, "w": 11, "h": 9},
    {"n": "Biscoito Recheado Mini Oreo Baunilha 35g", "p": "2,98", "u": "", "x": 29, "y": 13, "w": 11, "h": 9},
    {"n": "Biscoito Maizena Marilan 300g", "p": "4,88", "u": "", "x": 40, "y": 13, "w": 11, "h": 9},
    {"n": "Batata Frita Reizinho Cebola/Salsa 40g", "p": "3,28", "u": "", "x": 52, "y": 13, "w": 11, "h": 9},
    {"n": "Adoçante Líquido Assugrin Diet 100ml", "p": "3,48", "u": "", "x": 64, "y": 13, "w": 11, "h": 9},
    {"n": "Barra de Proteína Integralmedica Cookies/Cream 45g", "p": "8,99", "u": "", "x": 76, "y": 13, "w": 11, "h": 9},
    {"n": "Aveia em Flocos Allnutri Finos/Tradicional 170g", "p": "3,48", "u": "", "x": 88, "y": 13, "w": 11, "h": 9},
    {"n": "Azeitona Sadio Fatiadas Pouch 100g", "p": "5,88", "u": "", "x": 7, "y": 22, "w": 11, "h": 9},
    {"n": "Amido de Milho Kimimo 200g", "p": "3,28", "u": "", "x": 18, "y": 22, "w": 11, "h": 9},
    {"n": "Dueto Predilecta Pouch 170g", "p": "2,98", "u": "", "x": 30, "y": 22, "w": 12, "h": 9},
    {"n": "Farinha Láctea Italac Sachê 180g", "p": "4,98", "u": "", "x": 44, "y": 22, "w": 12, "h": 9},
    {"n": "Biscoito Recheado Amori Sabores 125g", "p": "2,29", "u": "", "x": 58, "y": 22, "w": 11, "h": 9},
    {"n": "Bala de Gelatina Fini Sabores 60g", "p": "6,99", "u": "", "x": 72, "y": 22, "w": 11, "h": 9},
    {"n": "Marshmallow Fini Sabores 70/60g", "p": "6,99", "u": "", "x": 86, "y": 22, "w": 11, "h": 9},
    {"n": "Cerveja Amstel Ultra s/ Glúten Lata 350ml", "p": "4,18", "u": "", "x": 7, "y": 33, "w": 11, "h": 9},
    {"n": "Cerveja Pilsen Itaipava Lata 350ml", "p": "2,49", "u": "", "x": 18, "y": 33, "w": 11, "h": 9},
    {"n": "Cerveja Praya s/ Glúten Long Neck 330ml", "p": "6,28", "u": "", "x": 29, "y": 33, "w": 11, "h": 9},
    {"n": "Cerveja Devassa Tropical Lata 350ml", "p": "2,68", "u": "", "x": 40, "y": 33, "w": 11, "h": 9},
    {"n": "Refresco em Pó Frisco Sabores 18g", "p": "0,75", "u": "", "x": 52, "y": 33, "w": 11, "h": 9},
    {"n": "Cachaça Extrema Ouro ou Prata 500ml", "p": "20,98", "u": "", "x": 64, "y": 33, "w": 11, "h": 9},
    {"n": "Vodka Natasha Tri Destilada 900ml", "p": "17,98", "u": "", "x": 76, "y": 33, "w": 11, "h": 9},
    {"n": "Água Mineral Crystal c/ Gás 500ml", "p": "2,09", "u": "", "x": 7, "y": 44, "w": 11, "h": 9},
    {"n": "Refrigerante Sprite, Fanta Laranja ou Uva 2L", "p": "8,79", "u": "", "x": 18, "y": 44, "w": 11, "h": 9},
    {"n": "Bebida Isotônica Powerade Sabores 500ml", "p": "5,49", "u": "", "x": 29, "y": 44, "w": 11, "h": 9},
    {"n": "Refresco Adoçado Del Valle Sabores 1,5L", "p": "6,49", "u": "", "x": 40, "y": 44, "w": 11, "h": 9},
    {"n": "Bebida Energética Baly Sabores Lata 473ml", "p": "6,18", "u": "", "x": 52, "y": 44, "w": 11, "h": 9},
    {"n": "Vinho Colonial/Nacional Sabores 750ml", "p": "12,98", "u": "", "x": 64, "y": 44, "w": 11, "h": 9},
    {"n": "Pão Doce de Coco Queiroz", "p": "12,98", "u": "kg", "x": 82, "y": 34, "w": 9, "h": 9},
    {"n": "Bolacha Santo Antônio Amanteigada Torrada ou Amanteigada 250g", "p": "3,98", "u": "", "x": 91, "y": 34, "w": 9, "h": 9},
    {"n": "Biscoito Água & Sal 3 de Maio 300g", "p": "3,99", "u": "", "x": 82, "y": 45, "w": 9, "h": 9},
    {"n": "Pão de Forma 400g / Bisnaguinha Center Massas 300g", "p": "5,29", "u": "", "x": 91, "y": 45, "w": 9, "h": 9},
    {"n": "Amaciante Concentrado Downy Fragrâncias 1L", "p": "18,29", "u": "", "x": 7, "y": 57, "w": 9, "h": 9},
    {"n": "Inseticida Aerosol Baygon Fragrâncias 380ml", "p": "13,59", "u": "", "x": 16, "y": 57, "w": 9, "h": 9},
    {"n": "Água Sanitária Marilux 5L", "p": "11,19", "u": "", "x": 25, "y": 57, "w": 9, "h": 9},
    {"n": "Saco para Lixo Diva 15L ou 30L", "p": "15,99", "u": "", "x": 34, "y": 57, "w": 9, "h": 9},
    {"n": "Lava Roupas em Pó Concentrado Tixan Ypê Fragrâncias 1,3kg", "p": "15,99", "u": "", "x": 43, "y": 57, "w": 9, "h": 9},
    {"n": "Sabão em Barra Absoluto Glicerinado Sun 169g", "p": "6,29", "u": "", "x": 52, "y": 57, "w": 9, "h": 9},
    {"n": "Esponja Lã de Aço Bombril 45g", "p": "1,59", "u": "", "x": 61, "y": 57, "w": 9, "h": 9},
    {"n": "Lava Roupas Líquido Uau 1L PG 800ml / 1,7L Fragrâncias", "p": "13,89", "u": "", "x": 70, "y": 57, "w": 9, "h": 9},
    {"n": "Limpador Perfumado Uau 1L PG 800ml Fragrâncias", "p": "9,19", "u": "", "x": 79, "y": 57, "w": 9, "h": 9},
    {"n": "Amaciante Concentrado Bombril Mon Bijou Fragrâncias 500ml", "p": "9,29", "u": "", "x": 88, "y": 57, "w": 9, "h": 9},
    {"n": "Desodorante Antitranspirante Aerosol Rexona Clinical Fragrâncias", "p": "17,98", "u": "", "x": 7, "y": 72, "w": 9, "h": 9},
    {"n": "Fralda Cremer Shortinho Jumbo", "p": "24,78", "u": "", "x": 16, "y": 72, "w": 9, "h": 9},
    {"n": "Creme Dental Colgate Total 12 Original Mint 22g", "p": "15,98", "u": "", "x": 25, "y": 72, "w": 9, "h": 9},
    {"n": "Fio Dental Johnson & Johnson Reach Essencial 100m", "p": "13,78", "u": "", "x": 34, "y": 72, "w": 9, "h": 9},
    {"n": "Sabonete Palmolive Fragrâncias 150g", "p": "3,68", "u": "", "x": 43, "y": 72, "w": 9, "h": 9},
    {"n": "Papel Higiênico Velud Moviment Unissex Folha Dupla 4un 30m", "p": "26,48", "u": "", "x": 52, "y": 72, "w": 9, "h": 9},
    {"n": "Roupa Íntima Bigfral Sempre Livre Adapt Suave c/16", "p": "7,68", "u": "", "x": 61, "y": 72, "w": 9, "h": 9},
    {"n": "Shampoo Anticaspa Palmolive Clássico 350ml", "p": "15,98", "u": "", "x": 70, "y": 72, "w": 9, "h": 9},
    {"n": "Body Splash Carmed Fragrâncias 200ml", "p": "37,48", "u": "", "x": 79, "y": 72, "w": 9, "h": 9},
    {"n": "Body Splash Exopure Secret Fragrâncias 200ml", "p": "24,98", "u": "", "x": 88, "y": 72, "w": 9, "h": 9},
    {"n": "Shampoo 2em1 Baruel Baby 210ml", "p": "12,98", "u": "", "x": 7, "y": 86, "w": 8, "h": 9},
    {"n": "Papel Toalha Mili Folha Dupla 2un", "p": "5,98", "u": "", "x": 15, "y": 86, "w": 8, "h": 9},
    {"n": "Acendedor Recarregável Bic Handy Azul", "p": "17,98", "u": "", "x": 23, "y": 86, "w": 8, "h": 9},
    {"n": "Papel A4 Suzano Report 500 folhas", "p": "27,98", "u": "", "x": 31, "y": 86, "w": 8, "h": 9},
    {"n": "Pote Mix Color Tramontina 2L 3 Cores", "p": "24,98", "u": "", "x": 39, "y": 86, "w": 8, "h": 9},
    {"n": "Caneca Disney Plastfil Mickey 380ml", "p": "9,98", "u": "", "x": 47, "y": 86, "w": 8, "h": 9},
    {"n": "Tapete Higiênico Mili Pet 7un", "p": "13,19", "u": "", "x": 55, "y": 86, "w": 8, "h": 9},
    {"n": "Ração Bono Cat Sabores 500g", "p": "4,89", "u": "", "x": 63, "y": 86, "w": 8, "h": 9},
    {"n": "Ração Dogfort Adulto Sabores 900g", "p": "7,99", "u": "", "x": 71, "y": 86, "w": 8, "h": 9},
    {"n": "Ração Tutti Canis Adulto Select 10,1kg", "p": "57,98", "u": "", "x": 79, "y": 86, "w": 8, "h": 9},
    {"n": "Ração Úmida Sachê Champ ou Kitekat Sabores 70/85g", "p": "1,65", "u": "leve 5 pague 4 (de 1,98 un)", "x": 88, "y": 86, "w": 9, "h": 9}
  ]}
 ]
}
"""

EXTRACTS = json.loads(EXTRACTS_JSON)
PRODUCTS = {}
for _sc, _pgs in EXTRACTS.items():
    for _pg in _pgs:
        PRODUCTS[_pg["key"]] = _pg["produtos"]

# --- Acoes NOVAS (metadados) ---
NEW_ACTIONS = [
    {"id": "DcI-a4pnMgp", "titulo": "Favoritaço Gôndola — Varejo Ponta Negra e Ayrton Senna (12 a 18/08)",
     "banner": "Favorito Super / Atacado Favorito", "segmento": "varejo",
     "inicio": "2026-08-12", "fim": "2026-08-18"},
    {"id": "DcGgGp8nJi7", "titulo": "Favoritaço Gôndola — Varejo Ponta Negra e Ayrton Senna (12 a 18/08)",
     "banner": "Favorito Super / Atacado Favorito", "segmento": "varejo",
     "inicio": "2026-08-12", "fim": "2026-08-18"},
    {"id": "DcGfTsRHFEL", "titulo": "Favoritaço Gôndola — Parnamirim e Macaíba (12 a 18/08)",
     "banner": "Favorito Super / Atacado Favorito", "segmento": "varejo",
     "inicio": "2026-08-12", "fim": "2026-08-18"},
    {"id": "DcHTjscoAO2", "titulo": "Dia Q do Comerciante — Queiroz Atacadão (17 e 18/08)",
     "banner": "Queiroz Atacadão", "segmento": "atacarejo",
     "inicio": "2026-08-17", "fim": "2026-08-18"},
    {"id": "DcHg2p1mnjy", "titulo": "Encarte Semanal Queiroz Atacadão (17 a 26/08)",
     "banner": "Queiroz Atacadão", "segmento": "atacarejo",
     "inicio": "2026-08-17", "fim": "2026-08-26"},
]


def main():
    actions = json.load(open(path("data/actions.json"), encoding="utf-8"))
    products = json.load(open(path("data/products.json"), encoding="utf-8"))
    canon = json.load(open(path("data/canon.json"), encoding="utf-8"))
    fila = json.load(open(path("data/fila_novos.json"), encoding="utf-8"))
    byshort = {p["shortcode"]: p for p in fila}
    byid = {a["id"]: a for a in actions}

    # pares DIFERENTES (jamais unir)
    diferentes = set()
    rp = path("data/regras_similaridade.md")
    if os.path.exists(rp):
        for line in open(rp, encoding="utf-8"):
            if line.startswith("- DIFERENTES:"):
                mm = re.findall(r"«([^»]*)»", line)
                if len(mm) == 2:
                    diferentes.add(frozenset((nrm_name(mm[0]), nrm_name(mm[1]))))

    by_key = {}
    for g in canon:
        k = nrm_tokens(g["n"])
        if k not in by_key or len(g["m"]) > len(by_key[k]["m"]):
            by_key[k] = g

    log = {"novos_canon": 0, "merges_canon": 0, "bloq_dif": 0}

    def canon_add(name, unit, ref):
        k = nrm_tokens(name)
        g = by_key.get(k)
        if g is not None and frozenset((nrm_name(name), nrm_name(g["n"]))) in diferentes:
            g = None
            log["bloq_dif"] += 1
        if g is None:
            g = {"n": name, "u": unit, "m": [ref]}
            canon.append(g)
            by_key[nrm_tokens(name)] = g
            log["novos_canon"] += 1
        else:
            if ref not in g["m"]:
                g["m"].append(ref)
            log["merges_canon"] += 1

    n_act = n_prod = 0
    for spec in NEW_ACTIONS:
        sid = spec["id"]
        if sid in byid:
            print(f"[pula] acao ja existe: {sid}")
            continue
        src = byshort.get(sid)
        if not src:
            print(f"[aviso] shortcode ausente na fila: {sid}")
            continue
        act = {
            "id": sid,
            "perfil": src.get("perfil"),
            "titulo": spec["titulo"],
            "banner": spec["banner"],
            "segmento": spec["segmento"],
            "inicio": spec["inicio"],
            "fim": spec["fim"],
            "carrossel": src.get("carrossel", False),
            "shortcode": sid,
            "caption": src.get("caption", ""),
            "adicionado_em": HOJE,
            "paginas": list(src.get("paginas", [])),
        }
        if src.get("fonte"):
            act["fonte"] = src["fonte"]
        if src.get("link"):
            act["link"] = src["link"]
        actions.append(act)
        byid[sid] = act
        n_act += 1
        for fname in src.get("paginas", []):
            pid = fname[:-4] if fname.endswith(".jpg") else fname
            lista = PRODUCTS.get(pid, [])
            products[pid] = lista
            for i, p in enumerate(lista):
                n_prod += 1
                canon_add(p["n"], p.get("u", "un"), f"{pid}#{i}")

    print(f"{'DRY-RUN' if DRY_RUN else 'COMMIT'}: {n_act} acoes novas, {n_prod} produtos, "
          f"canon: {log['novos_canon']} grupos novos, {log['merges_canon']} merges, "
          f"{log['bloq_dif']} bloqueios DIFERENTES")

    if DRY_RUN:
        return
    stamp = HOJE.replace("-", "")
    for nome in ("actions.json", "products.json", "canon.json"):
        pth = path("data", nome)
        if os.path.exists(pth):
            shutil.copy2(pth, f"{pth}.bak-{stamp}-ingest")
    salva(path("data/actions.json"), actions)
    salva(path("data/products.json"), products)
    salva(path("data/canon.json"), canon)
    print("gravado.")


if __name__ == "__main__":
    main()
