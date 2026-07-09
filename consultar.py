#!/usr/bin/env python3
"""Consulta o histórico de preços em data/encartes.db, em linguagem simples.

Uso:
  python3 consultar.py picanha            histórico de preço do produto
  python3 consultar.py "leite condensado" (aspas quando tiver espaço)
  python3 consultar.py --resumo           visão geral do banco
"""
import os
import re
import sqlite3
import sys
import unicodedata

BASE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(BASE, 'data', 'encartes.db')


def norm(s):
    s = unicodedata.normalize('NFD', str(s or '').lower())
    return ''.join(c for c in s if unicodedata.category(c) != 'Mn')


def fmt_preco(v):
    return f'R$ {v:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')


def fmt_dia(d):
    return f'{d[8:10]}/{d[5:7]}' if d and len(d) == 10 else (d or '?')


def resumo(con):
    a, p = (con.execute(f'SELECT COUNT(*) FROM {t}').fetchone()[0]
            for t in ('acoes', 'produtos'))
    ini, fim = con.execute('SELECT MIN(inicio), MAX(fim) FROM acoes').fetchone()
    print(f'Banco de preços: {p} produtos em {a} encartes, de {fmt_dia(ini)} a {fmt_dia(fim)}.')
    print('\nProdutos mais repetidos entre as redes:')
    for nome, n, banners in con.execute(
            "SELECT canon, COUNT(*), GROUP_CONCAT(DISTINCT banner) FROM precos "
            "WHERE canon IS NOT NULL GROUP BY canon ORDER BY COUNT(*) DESC LIMIT 10"):
        print(f'  {nome} — {n} aparições ({banners})')


def busca(con, termo):
    termos = norm(termo).split()
    linhas = con.execute(
        'SELECT canon, nome, preco, preco_texto, unidade, banner, inicio, fim '
        'FROM precos ORDER BY inicio DESC').fetchall()
    # procura no nome canônico E no nome impresso — 19% dos produtos têm
    # palavras que só existem num dos dois
    achadas = [ln for ln in linhas
               if all(t in norm(ln[0] or '') for t in termos)
               or all(t in norm(ln[1]) for t in termos)]
    if not achadas:
        print(f'Nenhum produto com "{termo}" no histórico.')
        return
    grupos = {}
    for ln in achadas:
        grupos.setdefault(ln[0] or ln[1], []).append(ln)
    for gnome, occ in sorted(grupos.items()):
        precos = [o[2] for o in occ if o[2]]
        cab = f'\n▶ {gnome} — {len(occ)} aparição(ões)'
        if precos:
            cab += f' · menor {fmt_preco(min(precos))} · maior {fmt_preco(max(precos))}'
        print(cab)
        for _, nome, preco, ptxt, uni, banner, ini, fim in occ:
            valor = fmt_preco(preco) if preco else (ptxt or '?')
            uni_s = f' ({uni.split(";")[0].strip()})' if uni else ''
            print(f'   {fmt_dia(ini)}–{fmt_dia(fim)}  {banner:<28} {valor}{uni_s}')


def main():
    if not os.path.exists(DB):
        sys.exit('banco ainda não existe — rode: python3 atualiza_banco.py')
    con = sqlite3.connect(DB)
    args = [a for a in sys.argv[1:] if a.strip()]
    if not args or args[0] == '--resumo':
        resumo(con)
    else:
        busca(con, ' '.join(args))
    con.close()


if __name__ == '__main__':
    main()
