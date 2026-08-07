import json, os

cands = json.load(open('data/similaridade_candidatos.json'))

verdict = {
 0:'mesmo',1:'mesmo',2:'mesmo',3:'mesmo',4:'mesmo',5:'mesmo',6:'mesmo',7:'mesmo',
 8:'diferente',9:'diferente',10:'diferente',11:'mesmo',12:'diferente',
 13:'mesmo',14:'mesmo',15:'mesmo',16:'mesmo',17:'mesmo',18:'diferente',19:'diferente',
 20:'diferente',21:'incerto',22:'mesmo',23:'incerto',24:'incerto',25:'diferente',
 26:'diferente',27:'diferente',28:'mesmo',29:'mesmo',30:'mesmo',31:'diferente',32:'diferente',
 33:'mesmo',34:'diferente',35:'mesmo',36:'diferente',37:'diferente',38:'diferente',
 39:'diferente',40:'diferente',41:'diferente',42:'mesmo',43:'diferente',44:'diferente',
 45:'diferente',46:'mesmo',47:'diferente',48:'mesmo',49:'mesmo',50:'diferente',51:'mesmo',
 52:'diferente',53:'diferente',54:'mesmo',55:'diferente',56:'diferente',57:'mesmo',58:'mesmo',
 59:'mesmo',60:'mesmo',61:'diferente',62:'diferente',63:'mesmo',64:'diferente',
}
assert len(verdict) == len(cands) == 65, (len(verdict), len(cands))

validacoes = []
incertos_novos = {}
for i, c in enumerate(cands):
    v = verdict[i]
    if v == 'incerto':
        incertos_novos[c['k']] = '2026-08-06'
    else:
        validacoes.append({'a': c['a'], 'b': c['b'], 'veredito': v})

os.makedirs('data/validacoes_inbox', exist_ok=True)
json.dump({'validacoes': validacoes},
          open('data/validacoes_inbox/auto_2026-08-06.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)

incertos = json.load(open('data/similaridade_incertos.json'))
before = len(incertos)
incertos.update(incertos_novos)
json.dump(incertos, open('data/similaridade_incertos.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)

mesmo = sum(1 for v in validacoes if v['veredito'] == 'mesmo')
dif = sum(1 for v in validacoes if v['veredito'] == 'diferente')
print("validacoes_inbox/auto_2026-08-06.json: %d validações (mesmo=%d, diferente=%d)" % (len(validacoes), mesmo, dif))
print("incertos: %d -> %d (novos=%d): %s" % (before, len(incertos), len(incertos_novos), list(incertos_novos)))
