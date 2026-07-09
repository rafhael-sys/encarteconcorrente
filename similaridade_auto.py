#!/usr/bin/env python3
"""Similaridade AUTOMÁTICA por foto: gera os pares candidatos que a análise
diária do Claude vai comparar VISUALMENTE (imagem do produto no encarte).

Fluxo: este script roda antes da análise e grava data/similaridade_candidatos.json
com até 10 pares (nome + imagem da página + posição do produto nela). O Claude
olha as duas fotos e só decide com certeza TOTAL:
  - certeza  -> escreve o veredito em data/validacoes_inbox/ (o
                aplica_validacoes.py une os grupos com toda a segurança)
  - dúvida   -> o par entra em data/similaridade_incertos.json e não é
                perguntado de novo
Pares já decididos (inclusive os validados manualmente no passado) nunca
voltam. Nenhuma fusão acontece aqui — só a preparação.
"""
import difflib
import json
import os
import re
import unicodedata

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, 'data')
PAGES = os.path.join(DATA, 'pages')
ARQUIVO = os.path.join(DATA, 'arquivo', 'pages')
MAX_PARES = 10

RUIDO = {'lata', 'lta', 'pct', 'pet', 'tb', 'gf', 'cada', 'un', 'sabores',
         'fragrancias', 'tipos', 'unidade', 'embalagem', 'congelada', 'congelado'}


def carrega(nome, default):
    try:
        with open(os.path.join(DATA, nome)) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def nrm(s):
    s = unicodedata.normalize('NFD', str(s).lower())
    return ' '.join(''.join(c for c in s if unicodedata.category(c) != 'Mn').split())


def chave_par(a, b):
    return ' || '.join(sorted([nrm(a), nrm(b)]))


def normtxt(s):
    return ' '.join(re.sub(r'[^a-z0-9,. ]+', ' ', nrm(s)).split())


def tokens(s):
    return {t for t in normtxt(s).split() if len(t) >= 3 and t not in RUIDO}


def tamanhos(s):
    return set(re.findall(r'\d+(?:[.,]\d+)?\s*(?:ml|kg|g|l|un)\b', normtxt(s)))


def main():
    canon = carrega('canon.json', [])
    products = carrega('products.json', {})
    actions = carrega('actions.json', [])
    decididos = set(carrega('similaridade_decisoes.json', {}))
    incertos = set(carrega('similaridade_incertos.json', {}))

    fname_de = {}
    for a in actions:
        if not a.get('id') or not isinstance(a.get('paginas'), list):
            continue
        for i, fn in enumerate(a['paginas']):
            pid = f"{a['id']}_p{i+1}" if not fn.startswith(a['id']) else fn.replace('.jpg', '')
            fname_de[pid] = fn

    def foto(c):
        """Primeira ocorrência do grupo com imagem existente: caminho + posição."""
        for ref in c.get('m', []):
            pid, _, idx = ref.partition('#')
            fn = fname_de.get(pid)
            if not fn:
                continue
            caminho = None
            for pasta in (PAGES, ARQUIVO):
                if os.path.exists(os.path.join(pasta, fn)):
                    caminho = os.path.join(os.path.relpath(pasta, BASE), fn)
                    break
            if not caminho:
                continue
            try:
                p = products[pid][int(idx)]
            except (KeyError, IndexError, ValueError):
                continue
            return {'imagem': caminho, 'nome_impresso': p.get('n', ''),
                    'regiao_pct': {'x': p.get('x'), 'y': p.get('y'),
                                   'w': p.get('w'), 'h': p.get('h')}}
        return None

    por_token = {}
    for i, c in enumerate(canon):
        for t in tokens(c['n']):
            por_token.setdefault(t, []).append(i)
    candidatos = set()
    for grupo in por_token.values():
        for x in range(len(grupo)):
            for y in range(x + 1, len(grupo)):
                candidatos.add((grupo[x], grupo[y]))

    pares = {}
    for i, j in candidatos:
        a, b = canon[i], canon[j]
        if len(tokens(a['n']) & tokens(b['n'])) < 2 or tamanhos(a['n']) != tamanhos(b['n']):
            continue
        k = chave_par(a['n'], b['n'])
        if k in decididos or k in incertos or k in pares:
            continue
        r = difflib.SequenceMatcher(None, normtxt(a['n']), normtxt(b['n'])).ratio()
        if r < 0.72:
            continue
        fa, fb = foto(a), foto(b)
        if not fa or not fb:
            continue  # sem foto dos dois lados não há avaliação visual
        pares[k] = {'k': k, 'a': a['n'], 'b': b['n'], 'foto_a': fa, 'foto_b': fb,
                    'r': round(r, 3)}

    lista = sorted(pares.values(), key=lambda p: -p['r'])[:MAX_PARES]
    tmp = os.path.join(DATA, 'similaridade_candidatos.json.tmp')
    with open(tmp, 'w') as f:
        json.dump(lista, f, ensure_ascii=False, indent=1)
    os.replace(tmp, os.path.join(DATA, 'similaridade_candidatos.json'))
    if lista:
        print(f'[info] similaridade: {len(lista)} par(es) para avaliação visual')


if __name__ == '__main__':
    main()
