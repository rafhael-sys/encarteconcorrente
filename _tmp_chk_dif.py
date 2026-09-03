import json,os,re,unicodedata
def nrm_name(s):
    s=unicodedata.normalize("NFD",str(s).lower())
    return " ".join("".join(c for c in s if unicodedata.category(c)!="Mn").split())
dif=set()
for line in open('data/regras_similaridade.md',encoding='utf-8'):
    if line.startswith('- DIFERENTES:'):
        mm=re.findall(r'«([^»]*)»',line)
        if len(mm)==2: dif.add(frozenset((nrm_name(mm[0]),nrm_name(mm[1]))))
print('pares DIFERENTES carregados:',len(dif))
# checar se algum nome novo bate exatamente com um lado de par DIFERENTES
nd=json.load(open('_new_data_20260902.json'))
names=set()
for pk,lst in nd['products'].items():
    for p in lst: names.add(nrm_name(p['n']))
print('nomes novos unicos:',len(names))
hit=[fs for fs in dif if any(x in names for x in fs)]
print('pares DIFERENTES tocando algum nome novo:',len(hit))
for fs in hit[:15]:
    print('  ',list(fs))
