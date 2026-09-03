#!/usr/bin/env python3
"""Agrega vereditos de similaridade da janela 2026-09-02.

Le _sim_decisoes_20260902.json = {"<indice>": "mesmo|diferente|incerto"} (todos
os 65 pares) e o data/similaridade_candidatos.json. Gera:
  - data/validacoes_inbox/auto_2026-09-02.json  (mesmo/diferente, com a/b)
  - data/similaridade_incertos.json  (merge; incertos -> {k: "2026-09-02"})
Nao mexe no canon (isso e do aplica_validacoes.py). Nao esvazia candidatos aqui.
"""
import json, os
BASE=os.path.dirname(os.path.abspath(__file__))
def p(*a): return os.path.join(BASE,*a)
HOJE="2026-09-02"

cands=json.load(open(p('data/similaridade_candidatos.json'),encoding='utf-8'))
dec=json.load(open(p('_sim_decisoes_20260902.json'),encoding='utf-8'))
dec={int(k):v for k,v in dec.items()}

# sanity: cobrir todos os indices
faltando=[i for i in range(len(cands)) if i not in dec]
if faltando:
    print('AVISO: indices sem decisao (tratados como incerto):',faltando)

validacoes=[]
incertos_novos={}
cont={'mesmo':0,'diferente':0,'incerto':0}
for i,par in enumerate(cands):
    d=dec.get(i,'incerto')
    if d in ('mesmo','diferente'):
        validacoes.append({'a':par['a'],'b':par['b'],'veredito':d})
        cont[d]+=1
    else:
        incertos_novos[par['k']]=HOJE
        cont['incerto']+=1

os.makedirs(p('data/validacoes_inbox'),exist_ok=True)
with open(p('data/validacoes_inbox/auto_2026-09-02.json'),'w',encoding='utf-8') as f:
    json.dump({'validacoes':validacoes},f,ensure_ascii=False,indent=1)

# merge incertos existentes
try:
    incertos=json.load(open(p('data/similaridade_incertos.json'),encoding='utf-8'))
    if not isinstance(incertos,dict): incertos={}
except (FileNotFoundError,json.JSONDecodeError):
    incertos={}
antes=len(incertos)
incertos.update(incertos_novos)
tmp=p('data/similaridade_incertos.json')+'.tmp'
with open(tmp,'w',encoding='utf-8') as f:
    json.dump(incertos,f,ensure_ascii=False,indent=1)
os.replace(tmp,p('data/similaridade_incertos.json'))

print(f"validacoes: mesmo={cont['mesmo']} diferente={cont['diferente']} | incertos novos={cont['incerto']}")
print(f"incertos.json: {antes} -> {len(incertos)}")
print("gravado: data/validacoes_inbox/auto_2026-09-02.json e similaridade_incertos.json")
