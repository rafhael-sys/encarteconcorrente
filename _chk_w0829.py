#!/usr/bin/env python3
"""Checagens pré-extração da janela 2026-08-29."""
import json
import os

d = json.load(open('data/_extract/w0826_sim_00_12.json'))
print(json.dumps(d if isinstance(d, dict) else d[:2], ensure_ascii=False, indent=1)[:1200])

print('---incertos---')
if os.path.exists('data/similaridade_incertos.json'):
    inc = json.load(open('data/similaridade_incertos.json'))
    print('incertos existentes:', len(inc))
else:
    print('sem arquivo de incertos')

print('---paginas da fila existem?---')
fila = json.load(open('data/fila_novos.json'))
falta = 0
for p in fila:
    for pg in p['paginas']:
        if not os.path.exists(f'data/pages/{pg}'):
            print('FALTA', pg)
            falta += 1
print('faltando:', falta)

print('---extracts antigos com shortcodes de hoje?---')
scs = set()
for p in fila:
    scs.add(p['shortcode'])
for f in os.listdir('data/_extract'):
    for sc in scs:
        if sc in f:
            print('CONFLITO:', f)

print('---candidatos: imagens existem?---')
cand = json.load(open('data/similaridade_candidatos.json'))
miss = 0
for c in cand:
    for lado in ('foto_a', 'foto_b'):
        img = c[lado]['imagem']
        if not os.path.exists(img):
            miss += 1
            print('IMG FALTA:', img)
print('imgs faltando:', miss, '| pares:', len(cand))
