#!/usr/bin/env python3
"""Gera o próximo lote de pares para avaliação visual de similaridade.

Regenera a fila a partir do canon ATUAL (refletindo uniões já feitas), filtra
pelos mesmos critérios do similaridade_auto.py e grava os N mais parecidos em
data/similaridade_candidatos.json.

Uso: python3 gera_lote.py [N] [r_minimo]
"""
from __future__ import annotations

import difflib
import json
import os
import sys

sys.path.insert(0, '/Users/teste/encarteconcorrente')
import similaridade_auto as sa  # noqa: E402


def foto(c: dict, fname_de: dict, prods: dict) -> dict | None:
    """Primeira ocorrência do grupo com imagem existente: caminho + posição."""
    for ref in c.get('m', []):
        pid, _, idx = ref.partition('#')
        fn = fname_de.get(pid)
        if not fn:
            continue
        caminho = None
        for pasta in (sa.PAGES, sa.ARQUIVO):
            if os.path.exists(os.path.join(pasta, fn)):
                caminho = os.path.join(os.path.relpath(pasta, sa.BASE), fn)
                break
        if not caminho:
            continue
        try:
            p = prods[pid][int(idx)]
        except (KeyError, IndexError, ValueError):
            continue
        return {'imagem': caminho, 'nome_impresso': p.get('n', ''),
                'regiao_pct': {'x': p.get('x'), 'y': p.get('y'),
                               'w': p.get('w'), 'h': p.get('h')}}
    return None


def main() -> None:
    """Monta e grava o próximo lote de candidatos."""
    n_lote = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    r_min = float(sys.argv[2]) if len(sys.argv) > 2 else 0.88

    canon = sa.carrega('canon.json', [])
    acts = sa.carrega('actions.json', [])
    prods = sa.carrega('products.json', {})
    decididos = set(sa.carrega('similaridade_decisoes.json', {}))
    incertos = set(sa.carrega('similaridade_incertos.json', {}))

    fname_de: dict[str, str] = {}
    for a in acts:
        for fn in a.get('paginas', []) or []:
            fname_de[fn.replace('.jpg', '')] = fn

    por_token: dict[str, list[int]] = {}
    for i, c in enumerate(canon):
        for t in sa.tokens(c['n']):
            por_token.setdefault(t, []).append(i)
    candidatos = set()
    for grupo in por_token.values():
        for x in range(len(grupo)):
            for y in range(x + 1, len(grupo)):
                candidatos.add((grupo[x], grupo[y]))

    pares: dict[str, dict] = {}
    for i, j in candidatos:
        a, b = canon[i], canon[j]
        if len(sa.tokens(a['n']) & sa.tokens(b['n'])) < 2:
            continue
        if sa.tamanhos(a['n']) != sa.tamanhos(b['n']):
            continue
        k = sa.chave_par(a['n'], b['n'])
        if k in decididos or k in incertos or k in pares:
            continue
        r = difflib.SequenceMatcher(None, sa.normtxt(a['n']), sa.normtxt(b['n'])).ratio()
        if r < r_min:
            continue
        fa, fb = foto(a, fname_de, prods), foto(b, fname_de, prods)
        if not fa or not fb:
            continue
        pares[k] = {'k': k, 'a': a['n'], 'b': b['n'],
                    'foto_a': fa, 'foto_b': fb, 'r': round(r, 3)}

    lista = sorted(pares.values(), key=lambda p: -p['r'])
    lote = lista[:n_lote]
    destino = os.path.join(sa.DATA, 'similaridade_candidatos.json')
    with open(destino, 'w') as f:
        json.dump(lote, f, ensure_ascii=False, indent=1)

    restante = len(lista) - len(lote)
    faixa = f"{lote[-1]['r']} a {lote[0]['r']}" if lote else '-'
    print(f'fila r>={r_min}: {len(lista)} pares | lote gravado: {len(lote)} (r {faixa}) '
          f'| restam depois deste: {restante}')


if __name__ == '__main__':
    main()
