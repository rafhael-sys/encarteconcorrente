import json
d=json.load(open('data/_win_extract_20260902.json'))
total=0
for sc,info in d.items():
    n=sum(len(v) for v in info['paginas'].values())
    total+=n
    print(f"{sc:20s} paginas={len(info['paginas'])} produtos={n} validade={info['validade']}")
print('TOTAL ACOES:',len(d),'TOTAL PRODUTOS:',total)
