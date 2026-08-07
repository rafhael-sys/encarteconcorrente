#!/usr/bin/env python3
"""Agrega os vereditos de similaridade por foto (sim0807_verd_*.json).

- mesmo/diferente (certeza total) -> data/validacoes_inbox/auto_2026-08-07.json
- incerto (ou par sem veredito)   -> data/similaridade_incertos.json {k: data}
Depois disso, o orquestrador roda aplica_validacoes.py e zera os candidatos.
"""
import json, os, glob

HOJE = "2026-08-07"
BASE = os.path.dirname(os.path.abspath(__file__))

cand = json.load(open(os.path.join(BASE, 'data/similaridade_candidatos.json')))
by_i = {i: c for i, c in enumerate(cand)}
by_k = {c['k']: c for c in cand}

verd = {}   # k -> veredito
for fp in sorted(glob.glob(os.path.join(BASE, 'data/_extract/sim0807_verd_*.json'))):
    try:
        rows = json.load(open(fp))
    except Exception as e:
        print('[aviso] verd ilegivel', os.path.basename(fp), e)
        continue
    for r in rows:
        k = r.get('k')
        v = r.get('veredito')
        if k is None:
            # fallback via indice
            c = by_i.get(r.get('i'))
            k = c['k'] if c else None
        if k is None:
            continue
        if v in ('mesmo', 'diferente', 'incerto'):
            verd[k] = v

validacoes = []
incertos_add = {}
faltando = []
for c in cand:
    k = c['k']
    v = verd.get(k)
    if v in ('mesmo', 'diferente'):
        validacoes.append({"a": c['a'], "b": c['b'], "veredito": v})
    elif v == 'incerto':
        incertos_add[k] = HOJE
    else:
        faltando.append(k)
        incertos_add[k] = HOJE   # sem veredito -> tratar como incerto (seguro)

# grava inbox (apenas se houver certezas)
os.makedirs(os.path.join(BASE, 'data/validacoes_inbox'), exist_ok=True)
inbox_path = os.path.join(BASE, 'data/validacoes_inbox/auto_2026-08-07.json')
if validacoes:
    json.dump({"validacoes": validacoes},
              open(inbox_path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# atualiza incertos (nao sobrescreve os antigos; adiciona os novos)
inc_path = os.path.join(BASE, 'data/similaridade_incertos.json')
incertos = json.load(open(inc_path)) if os.path.exists(inc_path) else {}
antes = len(incertos)
for k, d in incertos_add.items():
    incertos[k] = d
json.dump(incertos, open(inc_path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

n_mesmo = sum(1 for x in validacoes if x['veredito'] == 'mesmo')
n_dif = sum(1 for x in validacoes if x['veredito'] == 'diferente')
print(f"pares={len(cand)} | mesmo={n_mesmo} diferente={n_dif} incerto={len(incertos_add)} (sem_veredito={len(faltando)})")
print(f"incertos: {antes} -> {len(incertos)}")
print(f"inbox gravado: {'sim' if validacoes else 'NAO (0 certezas)'} ({inbox_path})")
if faltando:
    print("SEM VEREDITO (viraram incerto):")
    for k in faltando:
        print("  -", k)
