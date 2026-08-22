#!/usr/bin/env python3
"""Grava validacoes de similaridade da janela 2026-08-22 (inbox + incertos)."""
import json
import os
import unicodedata

cand = json.load(open('data/similaridade_candidatos.json'))
MESMO = {1, 2, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 18, 19, 20, 21, 22,
         24, 26, 27, 28, 32, 33, 34, 35, 38, 39, 40, 41, 45, 46, 47, 51, 55, 57,
         58, 61, 62, 63, 64}
DIFERENTE = {3, 17, 23, 29, 31, 36, 37, 43, 44, 48, 52, 53, 54, 59, 60}
INCERTO = {0, 25, 30, 42, 49, 50, 56}


def nrm(s):
    s = unicodedata.normalize('NFD', str(s).lower())
    return ' '.join(''.join(c for c in s if unicodedata.category(c) != 'Mn').split())


def salva(p, data):
    with open(p + '.tmp', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    os.replace(p + '.tmp', p)


certos = []
for i in sorted(MESMO):
    certos.append({'a': cand[i]['a'], 'b': cand[i]['b'], 'veredito': 'mesmo'})
for i in sorted(DIFERENTE):
    certos.append({'a': cand[i]['a'], 'b': cand[i]['b'], 'veredito': 'diferente'})
os.makedirs('data/validacoes_inbox', exist_ok=True)
salva('data/validacoes_inbox/auto_2026-08-22.json', {'validacoes': certos})
print('inbox: %d certos (%d mesmo, %d diferente)' % (len(certos), len(MESMO), len(DIFERENTE)))

inc = json.load(open('data/similaridade_incertos.json'))
add = 0
for i in sorted(INCERTO):
    k = cand[i]['k']
    if k not in inc:
        inc[k] = '2026-08-22'
        add += 1
salva('data/similaridade_incertos.json', inc)
print('incertos: +%d novos (total %d)' % (add, len(inc)))

canon = json.load(open('data/canon.json'))
name2grp = {}
for gi, g in enumerate(canon):
    name2grp.setdefault(nrm(g['n']), gi)
co = []
for i in sorted(DIFERENTE):
    ga = name2grp.get(nrm(cand[i]['a']))
    gb = name2grp.get(nrm(cand[i]['b']))
    if ga is not None and gb is not None and ga == gb:
        co.append((i, cand[i]['a'], cand[i]['b']))
print('pares DIFERENTE co-agrupados no canon:', co if co else 'nenhum')
