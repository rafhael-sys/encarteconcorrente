import json
a=json.load(open('data/actions.json'))
p=json.load(open('data/products.json'))
c=json.load(open('data/canon.json'))
print('actions:',len(a),'| products keys:',len(p),'| canon:',len(c))
novos=['DcysAaUz8OS','Dcy1n_MoCiY','DcyhtTXlQ51','DczXxIRjJMS','Dczlcd-jbOe','DcyU_ZalruW','DcyV0E0jokB','DczF092GcHt','DczFNcRGV6X','DczZxLKAN3M','DczT5FiGh4P','DczV4YGoKGa','DczVx_woI1K','atacadao_7abae5c0d2','atacadao_3a06d3cba9']
byid={x['id']:x for x in a}
missing=[s for s in novos if s not in byid]
print('acoes novas presentes:',len(novos)-len(missing),'/',len(novos),'| faltando:',missing)
# checar adicionado_em e fim
for s in novos:
    ac=byid[s]
    prod=sum(len(p.get(fn[:-4] if fn.endswith('.jpg') else fn,[])) for fn in ac['paginas'])
    print(f"  {s:20s} {ac['inicio']}->{ac['fim']} add={ac.get('adicionado_em')} prods={prod} '{ac['titulo'][:45]}'")
# integridade canon: refs apontam para produtos existentes?
bad=0
for g in c:
    for m in g['m']:
        pk,idx=m.rsplit('#',1)
        if pk in p and int(idx)<len(p[pk]):
            pass
        else:
            bad+=1
print('refs canon quebradas (total no banco):',bad)
