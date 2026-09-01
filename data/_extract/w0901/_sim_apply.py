#!/usr/bin/env python3
"""Grava vereditos de similaridade da janela 2026-09-01 e atualiza incertos.

Vereditos vindos da comparação visual (7 lotes); só certezas viram validação,
dúvidas vão para similaridade_incertos.json.
"""
import json

HOJE = "2026-09-01"

VERDICTS: dict[str, str] = {
    # lote 1
    "acucar cristal olho d'agua pacote com 1kg || acucar cristal olho d'agua triturado pacote com 1kg": "diferente",
    "batata pre-frita masterboi congelada pacote com 2kg || batata pre-frita rapmix congelada pacote com 2kg": "diferente",
    "molho para salada liza caseiro 234ml || molho para salada liza queijos 234ml": "diferente",
    "queijo mussarela molfino importado fatiado, peca ou pedaco || queijo mussarela tregar importado fatiado, peca ou pedaco": "diferente",
    "suco de uva galiotto 1l (tinto - integral) || suco de uva galiotto tinto integral vd 1l": "mesmo",
    "bisteca de pernil suino || carne bisteca de pernil suino": "mesmo",
    "lava roupas po ala sc 400g || lava-roupas em po ala 400g": "mesmo",
    "molho de tomate sadio 300g || molho tomate sadio sc 300g": "mesmo",
    "bebida lactea betania sabores bdj 540g || bebida lactea polpa betania sabores bandeja 540g": "mesmo",
    "lava roupas liq absoluto 3l fragrancias || lava roupas liq marilux 3l fragrancias": "diferente",
    # lote 2
    "sabonete palmolive naturals varias fragrancias unidade com 85g || sabonete palmolive naturals varios tipos unidade com 85g": "mesmo",
    "arroz parboilizado seu arroz tipo 1 1kg || arroz parboilizado urbano tipo 1 1kg": "diferente",
    "costela suina premium sadia congelada || costela suina sadia (congelada)": "incerto",
    "amaciante concentrado brilux diversos tb 500ml || amaciante concentrado downy (diversos) tb 500ml": "diferente",
    "capa de file bovina friboi resfriada kg || capa de file bovino friboi resfriada pedaco": "mesmo",
    "cerveja praya lager long neck 330ml || cerveja praya s/ gluten long neck 330ml": "mesmo",
    "bebida lactea uht nescau chocolate 180ml || bebida lactea uht nescau cx 180ml": "mesmo",
    "biscoito recheado bono/ negresco nestle varios sabores pacote com 90g || biscoito recheado bono/negresco nestle pacote com 90g": "mesmo",
    "file de peito de frango sadia congelado pct ou bd 1kg || filezinho de peito de frango sadia congelado bdj 1kg": "diferente",
    "aparelho de barbear bic flex 3 blister com 4 unidades || aparelho de barbear bic flex 3 blister com 4 unidades leve 4 pague 3": "mesmo",
    # lote 3
    "carne bovina costela em tira friboi congelada (preco por quilo na peca) || carne bovina cupim friboi congelada preco por quilo na peca": "diferente",
    "ovos brancos ou vermelhos grandes ou extras bandeja com 30 || ovos vermelhos grande ou extra bandeja com 30": "incerto",
    "ovos brancos grandes ou extras bandeja com 30 || ovos brancos ou vermelhos grandes ou extras bandeja com 30": "incerto",
    "agua mineral cristalina sem gas pet 500ml || agua mineral indaia sem gas pet 500ml": "diferente",
    "achoc po italac chocky 700g sachet || achocolatado em po italac chocky 700g sachet": "mesmo",
    "peito de frango ave nova ou super frango congelado kg || peito de frango super frango congelado kg": "incerto",
    "batata pre-frita masterboi congelada pacote 2kg || batata pre-frita natto congelada pacote com 2kg": "diferente",
    "arroz parboilizado mariano tipo 1 1kg || arroz parboilizado seu arroz tipo 1 1kg": "diferente",
    "polpa de fruta canaa congelada caju/goiaba/manga unidade 100g || polpa de fruta canaa congelada goiaba/ acerola/ manga unidade com 100g": "incerto",
    "bebida lactea uht nescau cx 180ml || bebida lactea uht nescau cx 180ml chocolate": "mesmo",
    # lote 4
    "linguica calabresa sadia kg || linguica calabresa saudali": "diferente",
    "shampoo clear varios tipos frasco 400ml || shampoo elseve varios tipos frasco com 400ml": "diferente",
    "linguica tipo calabresa aurora || linguica tipo calabresa suinco": "diferente",
    "pao de alho fabricacao propria pct 350g || pao de alho fabricacao propria tradicional pct 350g": "diferente",
    "filezinho de peito de frango aurora ou seara congelado bd 1kg || filezinho de peito de frango sadia congelado bdj 1kg": "diferente",
    "sobrecoxa de frango mauricea resfriada || sobrecoxa de frango resfriada": "mesmo",
    "abs semp livre ad 32un c/abas || absorvente sempre livre ad 32un c/abas": "mesmo",
    "inseticida aerosol baygon 360ml acao total || inseticida aerossol baygon 360ml acao total tradicional": "mesmo",
    "escova dental colgate pro alivio c/2 || escova dental colgate total c/2": "diferente",
    "absorvente sempre livre adapt suave c/ abas || absorvente sempre livre adapt suave c/ abas leve8 pague7": "mesmo",
    # lote 5
    "bebida lactea clan sc 900ml sabores || bebida lactea isis 900ml sabores": "diferente",
    "papel higienico caprice folha dupla leve 12 pague 11 || papel higienico clear luxo folha dupla 20m leve 12 pague 11": "diferente",
    "papel higienico nobel sublime folha dupla 20m 12 unidades || papel higienico sublime noble folha dupla 20m 12 unids": "mesmo",
    "queijo mussarela fatiado galbani 150g || queijo mussarela fatiado litoral 150g": "diferente",
    "batata fininhas bem brasil 1,5kg || batata pre-frita fininhas bem brasil 1,5kg": "mesmo",
    "agua mineral sterbom s/ gas 510ml || agua mineral sterbom sem gas pet com 510ml": "mesmo",
    "refrigerante antarctica guarana 2 litros || refrigerante kuat guarana 2 litros": "diferente",
    "acucar demerara petribu pacote com 1kg || acucar demerara uniao pacote com 1kg": "diferente",
    "arroz parboilizado blue soft tipo 1 1kg || arroz parboilizado safra tipo 1 1kg": "diferente",
    "cerveja eisenbahn pilsen lata 350ml || cerveja eisenbahn pilsen puro malte lata 350ml": "mesmo",
    # lote 6
    "absorvente sempre livre adapt c/8 suave || absorvente sempre livre adapt suave c/ abas": "mesmo",
    "lava roupa liquido omo 3l fragrancias || lava roupas liquido top clear 3l (fragrancias)": "diferente",
    "coxa e sobrecoxa de frango lar com dorsal || coxa e sobrecoxa de frango sem dorsal kg": "diferente",
    "arroz kika parboilizado tipo 1 pacote 1kg || arroz urbano parboilizado tipo 1 pacote com 1kg": "diferente",
    "cerveja praya lager long neck 330ml || cerveja praya lager puro malte long neck 330ml": "mesmo",
    "coxa com sobrecoxa de frango mauricea kg || coxa com sobrecoxa de frango resfriada kg": "incerto",
    "sabonete cremoso harrop 1l || sabonete p/ maos harrop 1l": "mesmo",
    "auroggets 275g sabores || auroggets aurora 275g sabores": "mesmo",
    "feijao carioca belo grao 1kg || feijao carioca kero 1kg": "diferente",
    "lava roupa em po ala 400g || lava roupas po ala sc 400g": "mesmo",
    # lote 7
    "carne bovina dianteira de sol || carne dianteira de sol": "mesmo",
    "queijo mussarela davaca fatiado, peca e pedaco || queijo mussarela natville fatiado, peca ou pedaco": "diferente",
    "file de peito de frango sadia congelado bandeja com 1kg || file de peito de frango sadia congelado iqf 1kg": "diferente",
    "farinha de trigo farina tradicional pacote 1kg || farinha de trigo finna tradicional tipo 1 pacote com 1kg": "diferente",
    "tira manchas em gel vanish multiuso/white refil 1,2l || tira-manchas em gel vanish tipos refil 1,2l": "mesmo",
}


def main() -> None:
    """Cruza vereditos com os candidatos e grava inbox + incertos."""
    cand = json.load(open('data/similaridade_candidatos.json'))
    por_k = {c['k']: c for c in cand}
    faltando = [k for k in por_k if k not in VERDICTS]
    sobrando = [k for k in VERDICTS if k not in por_k]
    print(f'pares sem veredito: {len(faltando)} {faltando[:3]}')
    print(f'vereditos sem par: {len(sobrando)} {sobrando[:3]}')

    validacoes = []
    incertos_novos = []
    for k, v in VERDICTS.items():
        if k not in por_k:
            continue
        c = por_k[k]
        if v == 'incerto':
            incertos_novos.append(k)
        else:
            validacoes.append({"a": c['a'], "b": c['b'], "veredito": v})

    with open('data/validacoes_inbox/auto_2026-09-01.json', 'w') as f:
        json.dump({"validacoes": validacoes}, f, ensure_ascii=False, indent=1)
    print(f'validacoes gravadas: {len(validacoes)}')

    inc = json.load(open('data/similaridade_incertos.json'))
    for k in incertos_novos:
        inc[k] = HOJE
    with open('data/similaridade_incertos.json', 'w') as f:
        json.dump(inc, f, ensure_ascii=False, indent=1)
    print(f'incertos adicionados: {len(incertos_novos)} | total incertos: {len(inc)}')


if __name__ == '__main__':
    main()
