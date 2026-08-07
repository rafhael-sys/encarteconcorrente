import json
d=json.load(open('data/actions.json'))
rows=[]
for a in d:
    fim=a.get('fim','')
    if fim>='2026-08-01':
        rows.append((a.get('banner',''),a.get('inicio',''),a.get('fim',''),a.get('id',''),a.get('fonte',''),len(a.get('paginas',[]))))
rows.sort()
for r in rows:
    print(f'{r[0]:45s} | {r[1]} -> {r[2]} | pg={r[5]:2d} | {r[4]:6s} | {r[3]}')
print('TOTAL recent:',len(rows))
