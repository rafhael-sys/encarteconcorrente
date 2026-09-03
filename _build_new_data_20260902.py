#!/usr/bin/env python3
"""Monta _new_data_20260902.json (actions specs + products) a partir do
staging _win_extract_20260902.json e da fila. Classificacao/dedup ja decididos
nesta sessao."""
import json, os
BASE = os.path.dirname(os.path.abspath(__file__))
def path(*p): return os.path.join(BASE, *p)

extr = json.load(open(path('data/_win_extract_20260902.json'), encoding='utf-8'))
fila = json.load(open(path('data/fila_novos.json'), encoding='utf-8'))
byshort = {p['shortcode']: p for p in fila}

TITULOS = {
 'DcysAaUz8OS': 'Quarta e Quinta Verde Favorito (02 e 03/09)',
 'Dcy1n_MoCiY': 'Aniversário 21 anos Super Show — ofertas de prateleira (31/08 a 03/09)',
 'DcyhtTXlQ51': 'Aniversário Favorito — Atacado Ayrton Senna e Zona Norte',
 'DczXxIRjJMS': 'Feirão Hortifrúti Mar Vermelho (03 e 04/09)',
 'Dczlcd-jbOe': 'Festival da Limpeza Mar Vermelho (03 a 07/09)',
 'DcyU_ZalruW': 'Aniversário Premiado Nordestão (01 a 08/09)',
 'DcyV0E0jokB': 'Aniversário Premiado SuperFácil — RN (01 a 08/09)',
 'DczF092GcHt': 'Ofertaço de Aniversário Queiroz — Natal (03 a 07/09)',
 'DczFNcRGV6X': 'Ofertaço de Aniversário Queiroz — João Câmara (03 a 07/09)',
 'DczZxLKAN3M': 'Saldão de Aniversário Corte Fácil (03 a 07/09)',
 'DczT5FiGh4P': 'Feirão das Carnes Corte Fácil (03 e 04/09)',
 'DczV4YGoKGa': 'Encarte 7 de Setembro Supercop (03 a 08/09)',
 'DczVx_woI1K': 'Quinta Verde Supercop (03/09)',
 'atacadao_7abae5c0d2': 'Atacadão — Boa do Dia (03/09)',
 'atacadao_3a06d3cba9': 'Atacadão — Hortifrúti (02 e 03/09)',
}

DESCARTES = [
 {'shortcode':'Dcy0iXjzkUD','motivo':'teaser sem preço (contagem regressiva Sextou com Sabadão)'},
 {'shortcode':'DcyyUUex3Cv','motivo':'sorteio/institucional (vale-compras R$500)'},
 {'shortcode':'DcyKajQG5OJ','motivo':'teaser sem preço (É amanhã — Saldão)'},
 {'shortcode':'DcyXYq-jsBb','motivo':'fora do RN (SuperFácil João Pessoa/PB) — regra do perfil'},
 {'shortcode':'DcylQccTXa9','motivo':'arte institucional sem preços (Oferta dos Sonhos)'},
 {'shortcode':'Dczj1udjQA-','motivo':'capa/teaser sem preço (Festival da Limpeza)'},
]

actions = []
products = {}
for sid, info in extr.items():
    src = byshort.get(sid, {})
    ini, fim = info['validade']
    spec = {
        'id': sid,
        'perfil': src.get('perfil'),
        'titulo': TITULOS[sid],
        'banner': src.get('banner'),
        'segmento': src.get('segmento'),
        'inicio': ini,
        'fim': fim,
        'carrossel': src.get('carrossel', False),
        'paginas': list(src.get('paginas', [])),
    }
    if src.get('fonte'): spec['fonte'] = src['fonte']
    if src.get('link'): spec['link'] = src['link']
    actions.append(spec)
    for pk, lst in info['paginas'].items():
        products[pk] = lst

out = {'hoje': '2026-09-02', 'actions': actions, 'products': products, 'descartes': DESCARTES}
with open(path('_new_data_20260902.json'), 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print('acoes:', len(actions), '| paginas c/ produtos:', len(products),
      '| total produtos:', sum(len(v) for v in products.values()))
# sanity: paginas do spec batem com as chaves de products?
for spec in actions:
    for fn in spec['paginas']:
        pk = fn[:-4] if fn.endswith('.jpg') else fn
        if pk not in products:
            print('  AVISO pagina sem entrada em products:', pk)
