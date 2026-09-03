import json,os
s=json.load(open('data/similaridade_candidatos.json'))
miss=0
for i,par in enumerate(s):
    fa=par['foto_a']['imagem']; fb=par['foto_b']['imagem']
    ea=os.path.exists(fa); eb=os.path.exists(fb)
    if not ea or not eb: miss+=1
    flag='' if (ea and eb) else '  <<FALTA'+('' if ea else ' A')+('' if eb else ' B')
    print(f"{i:2d} r={par.get('r')} | {par['a']}  ||  {par['b']}{flag}")
print('---- imagens faltando em', miss, 'pares')
