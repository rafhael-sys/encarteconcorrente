#!/usr/bin/env python3
"""Agrega os vereditos de similaridade da janela 2026-08-17 (9 lotes de subagentes).

- mesmo/diferente -> data/validacoes_inbox/auto_2026-08-17.json
- incerto         -> data/similaridade_incertos.json (chave k -> data)
- similaridade_candidatos.json -> []
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
HOJE = "2026-08-17"


def path(*p):
    return os.path.join(BASE, *p)


# Vereditos ecoados pelos subagentes (k = chave exata do candidato)
RESULTADOS = [
    # 0-6
    {"k": "petisco para gatos dreamies carne 40g || petisco para gatos friskies carne 40g", "veredito": "diferente"},
    {"k": "carne bovina coxao mole friboi || carne bovina coxao mole kg", "veredito": "incerto"},
    {"k": "margarina puro sabor 1kg || margarina puro sabor 1kg (com sal)", "veredito": "mesmo"},
    {"k": "hamburguer bovino friboi 56g || hamburguer friboi 56g", "veredito": "mesmo"},
    {"k": "oleo de soja liza 900ml || oleo de soja vitaliv 900ml", "veredito": "diferente"},
    {"k": "linguica calabresa imperio kg || linguica calabresa perdigao", "veredito": "diferente"},
    {"k": "lavanda johnsons baby 200ml || lavanda johnsons baby infantil 200ml", "veredito": "mesmo"},
    # 7-13
    {"k": "file de peito de frango lar congelado bandeja com 1kg || file de peito de frango lar congelado iqf 1kg", "veredito": "incerto"},
    {"k": "papel higienico floral folha dupla 12x20m (neutro) || papel higienico floral folha dupla 20m c/12", "veredito": "mesmo"},
    {"k": "refrigerante coca-cola e kuat || refrigerante coca-cola zero", "veredito": "diferente"},
    {"k": "chambaril bovino resfriado masterboi || lagarto bovino resfriado masterboi", "veredito": "diferente"},
    {"k": "requeijao cremoso catupiry tradicional ou light pt 200g || requeijao cremoso nestle tradicional/light pt 200g", "veredito": "diferente"},
    {"k": "detergente limpol 500ml fragrancias || detergente liquido alice 500ml fragrancias", "veredito": "diferente"},
    {"k": "maionese hellmann's doy pack 400g || maionese hellmann's sache 400g", "veredito": "mesmo"},
    # 14-20
    {"k": "file de peito de frango lar congelado bandeja com 1kg || filezinho de frango lar congelado bandeja 1kg", "veredito": "diferente"},
    {"k": "mac estrela semola estrela parafuso 400g || macarrao semola estrela parafuso 400g", "veredito": "mesmo"},
    {"k": "maca nacional gala || maca nacional gala quilo", "veredito": "mesmo"},
    {"k": "arroz parboilizado pop pct 1kg || arroz parboilizado tipo 2 pop pacote 1kg", "veredito": "mesmo"},
    {"k": "cafe santa clara extra forte 250g || cafe sao braz extra forte 250g", "veredito": "diferente"},
    {"k": "uva verde sem semente selecao mimo bandeja 500g || uva vermelha sem semente seleta bandeja 500g", "veredito": "diferente"},
    {"k": "pernil suino com osso kg || pernil suino com osso reserva kg", "veredito": "mesmo"},
    # 21-27
    {"k": "filezinho de frango aurora 1kg || filezinho de frango aurora congelado 1kg", "veredito": "mesmo"},
    {"k": "salgadinho cheetos bola 33g/35g/40g || salgadinho cheetos sabores 33g, 35g ou 40g", "veredito": "incerto"},
    {"k": "vinho casillero del diablo 750ml sabores || vinho chileno casillero diablo 750ml sabores", "veredito": "mesmo"},
    {"k": "fr desc pampers pants mega m c/30 || fralda descartavel pampers pants mega m c/30", "veredito": "mesmo"},
    {"k": "carne bovina posta gorda com osso kg || carne bovina posta gorda kg", "veredito": "incerto"},
    {"k": "coxas e sobrecoxas de frango aurora congeladas kg || coxas e sobrecoxas de frango congeladas friato kg", "veredito": "diferente"},
    {"k": "coracao de frango resfriado || coracao de frango resfriado mauricea", "veredito": "mesmo"},
    # 28-34
    {"k": "detergente liquido limpol 500ml || detergente liquido minuano 500ml", "veredito": "diferente"},
    {"k": "filezinho sassami de frango sadia congelado pct ou bd 1kg || filezinho sassami de frango seara congelado bandeja 1kg", "veredito": "diferente"},
    {"k": "linguica de frango aurora || linguica de frango sadia", "veredito": "diferente"},
    {"k": "ovos bra. grande almeida c/30 || ovos brancos grande almeida bdj/30", "veredito": "mesmo"},
    {"k": "azeite de oliva extra virgem la rambla vd 500ml || azeite de oliva extra virgem monini vd 500ml", "veredito": "diferente"},
    {"k": "arroz branco sao joaquim 1kg || arroz sao joaquim 1kg", "veredito": "mesmo"},
    {"k": "jerked beef dianteiro || jerked beef dianteiro friboi", "veredito": "mesmo"},
    # 35-41
    {"k": "flocao de milho marata 500g || flocao de milho sao braz 500g", "veredito": "diferente"},
    {"k": "azeite de oliva extra virgem palermo 500ml || azeite de oliva extra virgem sacciali vidro 500ml", "veredito": "diferente"},
    {"k": "requeijao cremoso catupiry tradicional ou light pt 200g || requeijao cremoso danone tradicional ou light 200g", "veredito": "diferente"},
    {"k": "peito frango kg || peito frango kg cong", "veredito": "incerto"},
    {"k": "lava roupas po ala 400g fragrancias || lava roupas po brilux pct 400g fragrancias", "veredito": "diferente"},
    {"k": "cafe em po santa clara classico pct 250g || cafe santa clara classico 250g", "veredito": "mesmo"},
    {"k": "agua sanitaria clorito 1l || agua sanitaria olimpo 1l", "veredito": "diferente"},
    # 42-48
    {"k": "lava roupas liquido tanlux 3l || lava roupas liquido urca 3l", "veredito": "diferente"},
    {"k": "maca gala kg || maca-gala", "veredito": "mesmo"},
    {"k": "absorvente lady suave com abas pacote com 32 unidades || absorvente noturno sym suave com abas pacote com 8 unidades", "veredito": "diferente"},
    {"k": "maca royal gala || maca royal kg", "veredito": "mesmo"},
    {"k": "lava loucas limpol 500ml || lava loucas liquido limpol 500ml", "veredito": "mesmo"},
    {"k": "cerveja heineken long neck 330ml || heineken long neck 330ml", "veredito": "mesmo"},
    {"k": "morango 200g || morango bdj 200g", "veredito": "mesmo"},
    # 49-55
    {"k": "arroz parboilizado emocoes 1kg || arroz parboilizado ou branco emocoes 1kg", "veredito": "mesmo"},
    {"k": "absorvente sempre livre conforto noturno leve + pague - suave com abas/seca com abas pacote com 32 unidades || absorvente sempre livre conforto noturno seca com abas pacote com 32 unidades", "veredito": "mesmo"},
    {"k": "carne bovina bife de patinho/patinho sem osso reserva resfriada || carne bovina patinho sem osso reserva resfriada", "veredito": "mesmo"},
    {"k": "coxa e sobrecoxa de frango lar com dorsal congelada kg || coxas e sobrecoxas de frango com dorso congeladas guibon", "veredito": "diferente"},
    {"k": "linguica de frango congelada bom todo sabores 600g || linguica de frango congelada top grill bom todo sabores pacote 600g", "veredito": "mesmo"},
    {"k": "leite uht natville integral ou desnatado cx 1 litro || leite uht ninho nestle integral ou semidesnatado cx 1 litro", "veredito": "diferente"},
    {"k": "lava roupas em po omo lavagem perfeita caixa ou bag 400g || lava roupas em po omo lavagem perfeita pacote com 400g", "veredito": "mesmo"},
    # 56-64
    {"k": "papel higienico neve folha dupla 30 metros pct leve 12 pague 11 || papel higienico noble folha dupla 20m leve 12 pague 11", "veredito": "diferente"},
    {"k": "coxa e sobrecoxa de frango lar com dorsal congelada kg || coxas e sobrecoxas de frango guibon com dorsal congelado", "veredito": "diferente"},
    {"k": "aparelho de barbear gillette prestobarba 2 2 unidades || aparelho de barbear gillette prestobarba 2 ultragrip blister 2 unidades", "veredito": "mesmo"},
    {"k": "absorvente sempre livre adapt suave c/ abas leve8 pague7 || absorvente sempre livre suave com abas leve 16 pague 14", "veredito": "diferente"},
    {"k": "leite condensado ccgl semidesnatado 395g || leite condensado semidesnatado italac 395g", "veredito": "diferente"},
    {"k": "requeijao tirolez resfriado tradicional 400g || requeijao tirolez resfriado tradicional/light pote com 400g", "veredito": "mesmo"},
    {"k": "pao de queijo tradicional aurora pacote 400g || pao de queijo tradicional forno de minas pacote 400g", "veredito": "diferente"},
    {"k": "pao de alho bom todo congelado 400g || pao de alho bom todo congelado 400g tradicional", "veredito": "mesmo"},
    {"k": "biscoito maria/maizena estrela 307g || biscoito maria/maizena estrela tradicional 307g", "veredito": "mesmo"},
]


def salva(p, data):
    tmp = f"{p}.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    os.replace(tmp, p)


def main():
    cand = json.load(open(path("data/similaridade_candidatos.json"), encoding="utf-8"))
    ab = {c["k"]: (c["a"], c["b"]) for c in cand}
    cand_keys = set(ab)

    verd = {r["k"]: r["veredito"] for r in RESULTADOS}

    # checagens de integridade
    faltando = cand_keys - set(verd)
    sobrando = set(verd) - cand_keys
    if faltando:
        print("[ERRO] candidatos sem veredito:", len(faltando))
        for k in faltando:
            print("   ", k)
    if sobrando:
        print("[ERRO] vereditos sem candidato (k nao casou):", len(sobrando))
        for k in sobrando:
            print("   ", k)
    if len(verd) != len(RESULTADOS):
        print("[ERRO] chaves duplicadas em RESULTADOS")
    if faltando or sobrando:
        print("Abortado: corrija antes de gravar.")
        return

    validacoes = []
    incertos_novos = []
    for k, v in verd.items():
        a, b = ab[k]
        if v in ("mesmo", "diferente"):
            validacoes.append({"a": a, "b": b, "veredito": v})
        elif v == "incerto":
            incertos_novos.append(k)

    nm = sum(1 for x in validacoes if x["veredito"] == "mesmo")
    nd = sum(1 for x in validacoes if x["veredito"] == "diferente")
    print(f"validacoes: {nm} mesmo, {nd} diferente | incertos: {len(incertos_novos)}")

    # 1) grava inbox
    os.makedirs(path("data/validacoes_inbox"), exist_ok=True)
    salva(path("data/validacoes_inbox/auto_2026-08-17.json"), {"validacoes": validacoes})

    # 2) incertos (nao reavaliar)
    inc = json.load(open(path("data/similaridade_incertos.json"), encoding="utf-8"))
    add = 0
    for k in incertos_novos:
        if k not in inc:
            inc[k] = HOJE
            add += 1
    salva(path("data/similaridade_incertos.json"), inc)
    print(f"incertos gravados (novos): {add} | total: {len(inc)}")

    # 3) esvazia candidatos
    salva(path("data/similaridade_candidatos.json"), [])
    print("similaridade_candidatos.json -> []")


if __name__ == "__main__":
    main()
