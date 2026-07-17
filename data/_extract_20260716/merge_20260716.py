#!/usr/bin/env python3
"""Ingestão da janela de 2026-07-16: cria ações novas, produtos e atualiza canon."""
import json
import os
import shutil
import unicodedata

BASE = '/Users/teste/encarteconcorrente'
DATA = os.path.join(BASE, 'data')
EXT = os.path.join(DATA, '_extract_20260716')
HOJE = '2026-07-16'


def load(name):
    with open(os.path.join(DATA, name)) as f:
        return json.load(f)


def save(name, obj):
    with open(os.path.join(DATA, name), 'w') as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)


def nrm(s):
    s = unicodedata.normalize('NFD', str(s).lower())
    return ' '.join(''.join(c for c in s if unicodedata.category(c) != 'Mn').split())


NOISE = {'lata', 'lta', 'pct', 'pet', 'tb', 'gf', 'gfa', 'cada', 'un', 'und', 'unid', 'unids',
         'sabores', 'sabor', 'fragrancias', 'fragrancia', 'tipos', 'varios', 'varias', 'com',
         'embalagem', 'pacote', 'pote', 'pt', 'frasco', 'garrafa', 'caixa', 'caixeta', 'cx',
         'sc', 'sch', 'pc', 'tp', 'vd', 'bdj', 'bandeja', 'unidade', 'unidades', 'kg', 'quilo',
         'preco', 'por', 'no', 'na', 'de', 'da', 'do', 'e', 'a', 'o'}


def chave(nome):
    toks = [t for t in nrm(nome).replace('-', ' ').replace('/', ' ').replace('(', ' ').replace(')', ' ').replace(',', ' ').replace('.', ' ').split() if t]
    return ' '.join(sorted(toks))


def chave_sem_ruido(nome):
    toks = [t for t in nrm(nome).replace('-', ' ').replace('/', ' ').replace('(', ' ').replace(')', ' ').replace(',', ' ').replace('.', ' ').split() if t and t not in NOISE]
    return ' '.join(sorted(toks))


def chave_par(a, b):
    return ' || '.join(sorted([nrm(a), nrm(b)]))


# ---------- carrega estado ----------
actions = load('actions.json')
products = load('products.json')
canon = load('canon.json')
fila = load('fila_novos.json')
fila_by_id = {p['shortcode']: p for p in fila}

decisoes = {}
if os.path.exists(os.path.join(DATA, 'similaridade_decisoes.json')):
    decisoes = load('similaridade_decisoes.json')
proibidos = set()
try:
    for k, v in decisoes.items():
        ver = v.get('veredito') if isinstance(v, dict) else v
        if str(ver).lower().startswith('dif'):
            proibidos.add(k)
except AttributeError:
    pass

# backups
for f in ('actions.json', 'products.json', 'canon.json'):
    shutil.copy2(os.path.join(DATA, f), os.path.join(DATA, f + '.bak-20260716-ingest'))

# ---------- extrações ----------
ext = {}
for fn in os.listdir(EXT):
    if fn.startswith('batch_') and fn.endswith('.json'):
        with open(os.path.join(EXT, fn)) as f:
            d = json.load(f)
        if fn == 'batch_sim.json':
            continue
        ext.update(d)

# páginas B2B Food Service (excluídas das ações e produtos)
FOOD_SERVICE = {
    'story_queirozatacadaojoaocamara_3942542752298588806.jpg',
    'story_queirozatacadaojoaocamara_3942543054582103666.jpg',
    'story_queirozatacadaojoaocamara_3942543362100064519.jpg',
    'story_queirozatacadaonatal__3942542898370105637.jpg',
    'story_queirozatacadaonatal__3942543191283529347.jpg',
    'story_queirozatacadaonatal__3942543457084899690.jpg',
}

# ---------- definição das ações novas ----------
NOVAS = [
    # feed
    dict(id='Da3xU6Pgddj', titulo='Rasga Preço RedeMAIS (17 a 20/07)', inicio='2026-07-17', fim='2026-07-20', fonte='feed'),
    dict(id='Da3lKDpGCzy', titulo='Show de Selos — Fim de Semana Nordestão (17 a 19/07)', inicio='2026-07-17', fim='2026-07-19', fonte='feed'),
    dict(id='Da3qd46D-ci', titulo='FDS Show (17 e 18/07)', inicio='2026-07-17', fim='2026-07-18', fonte='feed'),
    dict(id='Da3oQHIAOZf', titulo='Final de Semana Especial Santo Antônio (17 a 19/07)', inicio='2026-07-17', fim='2026-07-19', fonte='feed'),
    dict(id='Da3xsJWm_5R', titulo='Grandes Ofertas MarZap (17 a 23/07)', inicio='2026-07-17', fim='2026-07-23', fonte='feed'),
    dict(id='Da3dB1YFhmV', titulo='Mega Ofertas da Semana Leva Mais João Câmara (17 a 19/07)', inicio='2026-07-17', fim='2026-07-19', fonte='feed'),
    dict(id='Da3i3x9lVi9', titulo='Mega Ofertas da Semana Leva Mais Macau (17 a 19/07)', inicio='2026-07-17', fim='2026-07-19', fonte='feed'),
    dict(id='Da24AiZjppk', titulo='Ofertas da Loja — Favorito Varejo Ayrton Senna (até 21/07)', inicio='2026-07-16', fim='2026-07-21', fonte='feed'),
    # web
    dict(id='assai_168093-572', titulo='4ª & 5ª Feirassaí (15 e 16/07)', inicio='2026-07-15', fim='2026-07-16', fonte='web'),
    dict(id='assai_168129-572', titulo='Especial App Meu Assaí (16 a 22/07)', inicio='2026-07-16', fim='2026-07-22', fonte='web'),
    dict(id='atacadao_7a463baaca', titulo='Fim de Semana Parceirão (17 a 20/07)', inicio='2026-07-17', fim='2026-07-20', fonte='web'),
    dict(id='atacadao_b5c18c21b4', titulo='Especial Açougue, Frios e Padaria (17 a 20/07)', inicio='2026-07-17', fim='2026-07-20', fonte='web'),
    dict(id='atacadao_091b5dd3f3', titulo='Sexta Arrasadora (17/07)', inicio='2026-07-17', fim='2026-07-17', fonte='web'),
    # stories
    dict(id='story_miramarsupermercado_20260716', titulo='Ofertas Miramar — story', inicio='2026-07-10', fim='2026-07-21', fonte='story'),
    dict(id='story_atacarejo_santoantonio.ofc_20260716', titulo='Ofertas Santo Antônio — story', inicio='2026-07-17', fim='2026-07-19', fonte='story'),
    dict(id='story_redesuper.show_20260716', titulo='Ofertas Rede Super Show — story', inicio='2026-07-15', fim='2026-07-18', fonte='story'),
    dict(id='story_redemaisrn_20260716', titulo='Ofertas Rede Mais — story', inicio='2026-07-14', fim='2026-07-19', fonte='story'),
    dict(id='story_levamaismacau_20260716', titulo='Ofertas Leva Mais Macau — story', inicio='2026-07-16', fim='2026-07-17', fonte='story'),
    dict(id='story_favoritosuper_20260716', titulo='Ofertas Favorito — story', inicio='2026-07-08', fim='2026-07-21', fonte='story'),
    dict(id='story_levamaisjc_20260716', titulo='Ofertas Leva Mais João Câmara — story', inicio='2026-07-17', fim='2026-07-19', fonte='story'),
    dict(id='story_redesupercop_20260716', titulo='Ofertas Rede Supercop — story', inicio='2026-07-15', fim='2026-07-20', fonte='story'),
    dict(id='story_queirozatacadaojoaocamara_20260716', titulo='Ofertas Queiroz João Câmara — story', inicio='2026-07-16', fim='2026-07-17', fonte='story'),
    dict(id='story_supernordestaonatal_20260716', titulo='Ofertas Super Nordestão — story', inicio='2026-07-15', fim='2026-07-19', fonte='story'),
    dict(id='story_mirassolatacado_20260716', titulo='Ofertas Mirassol Atacado — story', inicio='2026-07-14', fim='2026-07-27', fonte='story'),
    dict(id='story_marvermelhoatacado_20260716', titulo='Ofertas Mar Vermelho — story', inicio='2026-07-10', fim='2026-08-09', fonte='story'),
    dict(id='story_queirozatacadaonatal__20260716', titulo='Ofertas Queiroz Natal — story', inicio='2026-07-16', fim='2026-07-31', fonte='story'),
]

ids_existentes = {a['id'] for a in actions}
novas_acoes = 0
for spec in NOVAS:
    post = fila_by_id[spec['id']]
    if spec['id'] in ids_existentes:
        print('JÁ EXISTE, pulando:', spec['id'])
        continue
    paginas = [p for p in post['paginas'] if p not in FOOD_SERVICE]
    acao = {
        'id': spec['id'],
        'perfil': post['perfil'],
        'titulo': spec['titulo'],
        'banner': post['banner'],
        'segmento': post['segmento'],
        'inicio': spec['inicio'],
        'fim': spec['fim'],
        'carrossel': len(paginas) > 1,
        'shortcode': post['shortcode'],
        'caption': post.get('caption', ''),
        'adicionado_em': HOJE,
        'paginas': paginas,
        'fonte': spec['fonte'],
    }
    if post.get('fonte') == 'web' and post.get('link'):
        acao['link'] = post['link']
    actions.append(acao)
    novas_acoes += 1

# ---------- products.json ----------
paginas_validas = set()
for spec in NOVAS:
    post = fila_by_id[spec['id']]
    for p in post['paginas']:
        if p not in FOOD_SERVICE:
            paginas_validas.add(p[:-4])

novos_produtos = 0
paginas_com_produto = 0
for pageid, dados in ext.items():
    if pageid not in paginas_validas:
        continue
    prods = dados.get('products') or []
    if not prods:
        continue
    lista = []
    for it in prods:
        lista.append({'n': it['n'], 'p': it['p'], 'u': it.get('u', 'un'),
                      'x': it['x'], 'y': it['y'], 'w': it['w'], 'h': it['h']})
    products[pageid] = lista
    novos_produtos += len(lista)
    paginas_com_produto += 1

# ---------- canon.json ----------
idx_exata = {}
idx_ruido = {}
for g in canon:
    idx_exata.setdefault(chave(g['n']), g)
    idx_ruido.setdefault(chave_sem_ruido(g['n']), g)

grupos_novos = 0
membros_add = 0
for pageid, dados in sorted(ext.items()):
    if pageid not in paginas_validas:
        continue
    prods = dados.get('products') or []
    for i, it in enumerate(prods):
        ref = f'{pageid}#{i}'
        nome = it['n']
        g = idx_exata.get(chave(nome))
        if g is None:
            cand = idx_ruido.get(chave_sem_ruido(nome))
            if cand is not None and chave_par(nome, cand['n']) not in proibidos:
                g = cand
        if g is not None:
            if ref not in g['m']:
                g['m'].append(ref)
                membros_add += 1
        else:
            novo = {'n': nome, 'u': it.get('u', 'un'), 'm': [ref]}
            canon.append(novo)
            idx_exata[chave(nome)] = novo
            idx_ruido.setdefault(chave_sem_ruido(nome), novo)
            grupos_novos += 1

# ---------- grava ----------
save('actions.json', actions)
save('products.json', products)
save('canon.json', canon)
save('fila_novos.json', [])

print(f'ações novas: {novas_acoes} (total {len(actions)})')
print(f'páginas com produto: {paginas_com_produto}; produtos novos: {novos_produtos} (total {sum(len(v) for v in products.values())})')
print(f'canon: {grupos_novos} grupos novos, {membros_add} incidências em grupos existentes (total {len(canon)})')
