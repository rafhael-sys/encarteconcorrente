#!/usr/bin/env python3
"""Valida incertos contra os candidatos e atualiza similaridade_incertos.json."""
import json
import unicodedata


def nrm(s):
    s = unicodedata.normalize('NFD', str(s).lower())
    return ' '.join(''.join(c for c in s if unicodedata.category(c) != 'Mn').split())


def chave_par(a, b):
    return ' || '.join(sorted([nrm(a), nrm(b)]))


cand = json.load(open('data/similaridade_candidatos.json'))
kset = {p['k'] for p in cand}

incertos = [
    "detergente liquido limpol 500ml || detergente liquido limpol 500ml maca",
    "dueto/milho verde fugini sache 170g || milho verde fugini sache 170g",
    "cafe soluvel sao braz extra forte refil 40g || cafe soluvel sao braz familia/extraforte refil 40g",
    "coxa c/ sobrecoxa lar congelada kg || coxa e sobrecoxa congelada kg",
    "capa de file bovina friboi resfriada kg || capa de file bovino resfriada kg",
    "pao de forma center massas integral 400g || pao de forma center massas integral ou leite 400g",
]
print('--- checagem incertos ---')
for k in incertos:
    print('OK ' if k in kset else 'FALTA', k)

# valida que os certos correspondem a pares de candidatos
vals = json.load(open('data/validacoes_inbox/auto_2026-08-23.json'))['validacoes']
faltas = [v for v in vals if chave_par(v['a'], v['b']) not in kset]
print(f'--- certos: {len(vals)} vereditos; sem par candidato: {len(faltas)} ---')
for v in faltas:
    print('  SEM PAR:', v['a'], '||', v['b'])

# cobertura total
cobertos = {chave_par(v['a'], v['b']) for v in vals} | set(incertos)
faltando = kset - cobertos
print(f'--- cobertura: {len(cobertos & kset)}/{len(kset)} candidatos; nao cobertos: {len(faltando)} ---')
for k in faltando:
    print('  NAO COBERTO:', k)

# atualiza incertos json
inc = json.load(open('data/similaridade_incertos.json'))
add = 0
for k in incertos:
    if k in kset and k not in inc:
        inc[k] = '2026-08-23'
        add += 1
tmp = 'data/similaridade_incertos.json.tmp'
json.dump(inc, open(tmp, 'w'), ensure_ascii=False, indent=1)
import os
os.replace(tmp, 'data/similaridade_incertos.json')
print(f'incertos adicionados: {add}; total agora: {len(inc)}')
