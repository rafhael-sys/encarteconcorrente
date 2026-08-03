#!/usr/bin/env python3
"""Gera os vereditos de similaridade da janela 2026-08-03.

Regra CERTEZA TOTAL:
- 'mesmo'    -> só formatação/abreviação/typo de marca+tamanho+variante idênticos.
- 'diferente'-> marca, produto, contagem ou tamanho claramente distintos no nome.
- incerto    -> variante nuance, rótulo "ou", marca presente só em um, dúvida de tamanho.

Escreve data/validacoes_inbox/auto_2026-08-03.json (mesmo/diferente) e ACRESCENTA
as chaves incertas em data/similaridade_incertos.json.
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
HOJE = "2026-08-03"

# índice do par (na ordem de similaridade_candidatos.json) -> veredito
VERDICT = {
    0: "mesmo",       # Chocolatto/Chocolato 700g 3 Corações (typo)
    1: "mesmo",       # Papel Toalha Leve Mais c/02 vs c/2
    2: "mesmo",       # Saco Lixo Felitá Clean para/P/
    3: "mesmo",       # Azeitona(s) Verde(s) Vale Fertil 100g Doypack
    4: "incerto",     # Clear Fresh 18un vs 18un NT (sufixo NT)
    5: "incerto",     # Colgate 180g MPA vs sem MPA
    6: "diferente",   # Azeite Palermo x Allegro
    7: "diferente",   # Adoçante Magro Fit x Fruto (linhas distintas)
    8: "mesmo",       # Farelo Aveia Vitalin Whey 160g / Sch
    9: "mesmo",       # Ração Cão Tutti Canis Select 10,1kg (Cão / para Cão)
    10: "mesmo",      # Mop Plast/Plástico Noviça Fit 10L
    11: "mesmo",      # Pastilha Ades Pro/Adesiva Pato 3un
    12: "mesmo",      # Capa de Filé Cong/Congelada kg
    13: "mesmo",      # Charque Ponta (de) Agulha Jerked Beef Litoral
    14: "mesmo",      # Bebida Láctea Nescau / UHT Nescau 180ml
    15: "diferente",  # Azeite Gallo x Allegro
    16: "incerto",    # Faroeste Burger vs Aurora (marca só em um)
    17: "diferente",  # Mini Coxinha x Mini Kibe
    18: "mesmo",      # Wafer Prot/Proteína Bendu 40g
    19: "diferente",  # Lava-Roupas Omo x +eKonômico
    20: "mesmo",      # Capa de Filé Congelada/Cong kg
    21: "diferente",  # Azeite Fioz x Allegro
    22: "incerto",    # Leite Cond Natville vs Natville ou Betânia
    23: "mesmo",      # Goiabada Tambaú 500g / (Poly)
    24: "incerto",    # Ovos Grandes/Extras vs Grandes Almeida
    25: "incerto",    # Mistura Meu Bom vs Meu Bom LeitBom (marca só em um)
    26: "mesmo",      # Bisc Rech/Biscoito Recheado Sucrilhos 85g Morango
    27: "mesmo",      # Filezinho (de Frango) Grelhado Natto 700g Temperado
    28: "diferente",  # Açúcar Cristal x Triturado Ecoaçúcar
    29: "mesmo",      # Farinha Trigo (Tipo 1) Farina 1kg
    30: "diferente",  # Lava Roupas Marilux x Limpamil
    31: "mesmo",      # Feijão Carioca Precioso (Tipo 1) 1kg
    32: "mesmo",      # Açúcar Magro Light 400g / 400g Light
    33: "diferente",  # Flocão São Braz x São Ouro
    34: "incerto",    # Guaraná Antarctica Tradicional vs Tradicional ou Zero
    35: "diferente",  # Papel Higiênico Sublime 4 unids x 12 unidades
    36: "mesmo",      # Chocolatto 3 Corações x Caramelo 560g (regra humana MESMO)
    37: "mesmo",      # Milho Pipoca Micro-ondas Yoki 100g / Pacote com 100g
    38: "mesmo",      # Ovo(s) Granja Almeida bandeja c/30 / com 30
    39: "mesmo",      # Biscoito/Bolacha Cream Cracker Vitarella Tostadinha 350g
    40: "mesmo",      # Hambúrguer Rezende (Caixeta) 36x56g
    41: "incerto",    # Açúcar Ecoçúcar (tipo não especificado) vs Trit
    42: "mesmo",      # Linguiça Frango Lar Cong./Congelada Grossa 1kg
    43: "diferente",  # Pizza Rezende x Seara
    44: "diferente",  # Leite Cond Natville x Damare
    45: "diferente",  # Massa Grano Duro La Molisana x Antico Molino
    46: "diferente",  # Papel Higiênico Paloma x Deluxe
    47: "diferente",  # Azeite Cocineiro x Allegro
    48: "mesmo",      # Wafer / Wafer Recheado Marilan 70g
    49: "diferente",  # Arroz Mariano x Tio Manoel
    50: "diferente",  # Molho Tomate Fugini x Quero
    51: "incerto",    # Filezinho Seara de Peito vs Sassami (corte)
    52: "incerto",    # Always Noturno Fluxo Intenso vs Suave ou Seca
    53: "incerto",    # Leite Cond Betânia vs Natville ou Betânia
    54: "mesmo",      # Filezinho Frango Aurora 1kg / Bandeja 1kg
    55: "diferente",  # Papel Higiênico Nobel Sublime x Deluxe
    56: "mesmo",      # Bebida Power Whey 3 Corações 250ml TP/Sabores
    57: "incerto",    # Arroz Urbano Tipo 1 vs não especificado
    58: "mesmo",      # Vinho Pictor Cabernet Sauvignon (abreviações)
    59: "mesmo",      # Supra Soy sem Lactose 300g (Leite Alimento / Alimento Lata)
    60: "incerto",    # Galinha Q'Delícia vs Galinha Pequena Q Delícia
    61: "diferente",  # Biscoito Cream Cracker Lícia x Marilan
    62: "mesmo",      # Peito Frango Congelado Bom Todo 1kg (abreviações)
    63: "incerto",    # Café Pilão Torrado vs Vácuo 250g (embalagem)
    64: "mesmo",      # Costela Ponta de Agulha (Bovina) kg
}

cand = json.load(open(os.path.join(BASE, "data", "similaridade_candidatos.json"), encoding="utf-8"))
assert len(cand) == len(VERDICT), f"pares={len(cand)} vereditos={len(VERDICT)}"

validacoes = []
incertos_novos = {}
for i, par in enumerate(cand):
    v = VERDICT[i]
    if v == "incerto":
        incertos_novos[par["k"]] = HOJE
    else:
        validacoes.append({"a": par["a"], "b": par["b"], "veredito": v})

# 1) validacoes_inbox
inbox_dir = os.path.join(BASE, "data", "validacoes_inbox")
os.makedirs(inbox_dir, exist_ok=True)
out = os.path.join(inbox_dir, "auto_2026-08-03.json")
json.dump({"validacoes": validacoes}, open(out, "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

# 2) acrescenta incertos (sem sobrescrever os existentes)
inc_path = os.path.join(BASE, "data", "similaridade_incertos.json")
incertos = json.load(open(inc_path, encoding="utf-8"))
antes = len(incertos)
incertos.update(incertos_novos)
json.dump(incertos, open(inc_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

n_m = sum(1 for x in validacoes if x["veredito"] == "mesmo")
n_d = sum(1 for x in validacoes if x["veredito"] == "diferente")
print(f"validacoes_inbox: {out}")
print(f"  mesmo={n_m} diferente={n_d} | incertos novos={len(incertos_novos)} "
      f"(incertos {antes} -> {len(incertos)})")
