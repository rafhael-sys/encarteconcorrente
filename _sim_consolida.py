#!/usr/bin/env python3
"""Consolida os vereditos de similaridade por foto desta janela (28/07).

Vereditos por ÍNDICE (posição na lista de candidatos), retornados pelos
subagentes que processaram fatias contíguas em ordem. Gera:
  - data/validacoes_inbox/auto_2026-07-28.json  (pares mesmo/diferente)
  - atualiza data/similaridade_incertos.json    (pares incertos -> 2026-07-28)
"""
import json
import os

HOJE = "2026-07-28"

# 65 vereditos por índice (0..64):
#   0-30  mesmo | 31 diferente (Toalhas Mili C/48 vs C/96)
#   32-61 mesmo | 62 incerto (Ração Pedigree 900g) | 63 mesmo
#   64 diferente (Coxinha da Asa Lar vs Seara)
verdict_by_index = (['mesmo'] * 31) + ['diferente'] + (['mesmo'] * 30) + ['incerto', 'mesmo', 'diferente']

cand = json.load(open('data/similaridade_candidatos.json'))
assert len(cand) == len(verdict_by_index), (len(cand), len(verdict_by_index))

validacoes = []
incertos_novos = {}
cont = {'mesmo': 0, 'diferente': 0, 'incerto': 0}

print('=== conferência dos pares NÃO-mesmo ===')
for i, p in enumerate(cand):
    v = verdict_by_index[i]
    cont[v] += 1
    if v == 'mesmo':
        validacoes.append({'a': p['a'], 'b': p['b'], 'veredito': 'mesmo'})
    elif v == 'diferente':
        validacoes.append({'a': p['a'], 'b': p['b'], 'veredito': 'diferente'})
        print(f'  [{i}] DIFERENTE: «{p["a"]}»  ×  «{p["b"]}»')
    else:
        incertos_novos[p['k']] = HOJE
        print(f'  [{i}] INCERTO:   «{p["a"]}»  ×  «{p["b"]}»')

os.makedirs('data/validacoes_inbox', exist_ok=True)
with open('data/validacoes_inbox/auto_2026-07-28.json', 'w', encoding='utf-8') as f:
    json.dump({'validacoes': validacoes}, f, ensure_ascii=False, indent=1)

inc = json.load(open('data/similaridade_incertos.json'))
antes = len(inc)
inc.update(incertos_novos)
with open('data/similaridade_incertos.json', 'w', encoding='utf-8') as f:
    json.dump(inc, f, ensure_ascii=False, indent=1)

print('\nvereditos:', cont)
print('validacoes no inbox:', len(validacoes), '| incertos:', antes, '->', len(inc))
