#!/usr/bin/env python3
"""Grava vereditos de similaridade da janela 2026-08-25.

Vereditos decididos nesta sessao comparando as fotos dos pares (marca,
variante e tamanho). Pares com qualquer duvida vao para
similaridade_incertos.json e nao sao reavaliados.
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
HOJE = "2026-08-25"

# indice do par na lista -> veredito ("mesmo" | "diferente" | "incerto")
VEREDITOS = {
    0: "diferente",   # Papel hig. Noble x Rose (marcas)
    1: "mesmo",       # Chococandy Dori 500g = Chococandy 500g (mesma embalagem Dori)
    2: "diferente",   # Rose 20m x Sublime 30m (marca e metragem)
    3: "diferente",   # Oleo composto Maria x Olivia (marcas, lado a lado no mesmo encarte)
    4: "diferente",   # Papel hig. Personal x Rose (marcas)
    5: "diferente",   # Bala gelatina Dori x Fini (marcas)
    6: "mesmo",       # Taboleiro Torrada Amanteigada = Amanteigada (mesma embalagem)
    7: "diferente",   # Papel hig. Caprice x Rose (marcas)
    8: "mesmo",       # Cafe Sao Braz Extra Forte refil = sache 40g (mesmo pouch)
    9: "mesmo",       # Taboleiro Manteiga da Terra = Amanteigada (mesma embalagem)
    10: "diferente",  # Patinho x Picanha Masterboi (cortes)
    11: "mesmo",      # Piquitucho c/60 = Piquitucho Premium c/60 (mesma embalagem amarela)
    12: "diferente",  # Rosquinhas 3 de Maio x Galo (marcas)
    13: "diferente",  # Rosquinhas Galo x Vitarella (marcas)
    14: "mesmo",      # Powerlate Sao Braz 700g = Powerlate SCH 700g (SCH = sache)
    15: "incerto",    # Cream Cracker Marilan x Marilan Nordeste (linhas distintas?)
    16: "diferente",  # Vassoura Novica Facil x Original (modelos distintos)
    17: "diferente",  # Uva Melodia x Vitoria (cultivares)
    18: "incerto",    # Aveia Quaker guarda-chuva x sabor unico
    19: "mesmo",      # Choc Barra Hersheys = Chocolate Barra Hershey's (abreviacao)
    20: "mesmo",      # Cafe Santa Clara Classico Almofada 250g (formatacao)
    21: "mesmo",      # Mini Tangerinas Pick & Nicky (cumbuca = embalagem)
    22: "mesmo",      # Manteiga Itacolomy 500g = (C/ Sal): pote vermelho com sal nas duas
    23: "mesmo",      # Batata Lays = Batata Frita Lays 30g
    24: "mesmo",      # Frango passarinho Cox/Sobrecox Lar 700g (abreviacao)
    25: "diferente",  # Vinagre Leto x Palmeiron (marcas)
    26: "diferente",  # Acem x Paleta Masterboi (cortes)
    27: "mesmo",      # Cafeteira Ramos N2 (formatacao)
    28: "mesmo",      # Pernil suino com osso (formatacao)
    29: "mesmo",      # Organizador Ovos/Clear Fresh 18U NT (mesma foto; "Brinox" era vizinho)
    30: "diferente",  # Aguardente 51 tradicional (transparente) x 51 Ouro (dourada)
    31: "mesmo",      # Aveia Allnutri (ordem de palavras)
    32: "mesmo",      # Cha de Fora Resf = Resfriado (abreviacao)
    33: "incerto",    # Wafer Bauducco Brigadeiro x Chocolate/Brigadeiro (guarda-chuva)
    34: "diferente",  # Coxinha da asa Jagua x Mauricea (marcas)
    35: "mesmo",      # Peito frango c/ osso Mauricea (logo Mauricea nos dois encartes)
    36: "mesmo",      # Coxinha da asa Mauricea (logo Mauricea nos dois encartes)
    37: "diferente",  # Picanha australiana Nordestao 132,99 x fatiada MV 38,99
    38: "diferente",  # Manteiga Itacolomy x Itambe (marcas)
    39: "mesmo",      # Coxa/sobrecoxa Bom Todo bd 1kg (formatacao)
    40: "diferente",  # Desodorante Francis x Rexona (marcas)
    41: "diferente",  # Barriga x Bisteca suina Reserva (cortes)
    42: "diferente",  # Cachaca Caranguejo Limao x Ouro (variantes)
    43: "diferente",  # Leite desnatado Leitbom x Molico (marcas)
    44: "mesmo",      # Batata palha Graticia = Graticia Culinaria (mesmo saco azul)
    45: "mesmo",      # Costela (bovina) ponta de agulha (formatacao)
    46: "incerto",    # Polpa Serido listas de sabores diferentes
    47: "diferente",  # Amaciante Comfort x Fofo (marcas)
    48: "mesmo",      # Galinha pequena (Q')Delicia — mesma loja, mesmo produto Qdelicia
    49: "diferente",  # Coxinha da asa Lar x Mauricea (marcas)
    50: "incerto",    # Coxa c/ sobrecoxa cong sem marca x Lar (foto B sem marca visivel)
    51: "incerto",    # File envelopado: foto antiga Lar x nova Ave Nova (placa generica)
    52: "diferente",  # Leite UHT Elege x Italac (marcas)
    53: "diferente",  # Condicionador Monange x Seda (marcas)
    54: "mesmo",      # Taboleiro "Manteiga do Sertao" = mesma torrada amanteigada (erro do encarte)
    55: "diferente",  # Amaciante Downy x Brilux (marcas)
    56: "mesmo",      # Papel toalha Mili F/D = Folha Dupla (abreviacao)
    57: "mesmo",      # Whisky (escoces) Black & White 1L
    58: "diferente",  # File merluza x panga Pescados da Cruz (especies)
    59: "diferente",  # Sadia Filezinho Sassami x File de Peito (SKUs distintos nas fotos)
    60: "mesmo",      # Glade 360ml ("20% desc" = ruido promocional)
    61: "mesmo",      # Coxa c/ sobrecoxa Bom Todo 1kg bandeja (formatacao)
    62: "diferente",  # Coxa c/ sobrecoxa congelada x resfriada (estados)
    63: "mesmo",      # Filezinho Lar 1kg ("congelado" e atributo inerente)
    64: "diferente",  # Farinha Finna com fermento x sem fermento
}


def main() -> None:
    """Gera validacoes_inbox/auto e atualiza similaridade_incertos."""
    cand_path = os.path.join(BASE, "data", "similaridade_candidatos.json")
    pares = json.load(open(cand_path, encoding="utf-8"))
    assert len(pares) == 65, f"esperava 65 pares, achei {len(pares)}"

    validacoes, incertos_novos = [], {}
    for i, par in enumerate(pares):
        v = VEREDITOS[i]
        if v == "incerto":
            incertos_novos[par["k"]] = HOJE
        else:
            validacoes.append({"a": par["a"], "b": par["b"], "veredito": v})

    inbox_dir = os.path.join(BASE, "data", "validacoes_inbox")
    os.makedirs(inbox_dir, exist_ok=True)
    out = os.path.join(inbox_dir, f"auto_{HOJE}.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump({"validacoes": validacoes}, f, ensure_ascii=False, indent=1)

    inc_path = os.path.join(BASE, "data", "similaridade_incertos.json")
    incertos = json.load(open(inc_path, encoding="utf-8")) if os.path.exists(inc_path) else {}
    incertos.update(incertos_novos)
    with open(inc_path, "w", encoding="utf-8") as f:
        json.dump(incertos, f, ensure_ascii=False, indent=1)

    n_m = sum(1 for v in VEREDITOS.values() if v == "mesmo")
    n_d = sum(1 for v in VEREDITOS.values() if v == "diferente")
    print(f"gravado: {len(validacoes)} validacoes ({n_m} mesmo, {n_d} diferente), "
          f"{len(incertos_novos)} incertos novos (total {len(incertos)})")


if __name__ == "__main__":
    main()
