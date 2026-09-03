import json
c=json.load(open('data/canon.json'))
multi=[g for g in c if len(g.get('m',[]))>=3]
print('grupos com >=3 membros:',len(multi))
for g in multi[:3]:
    print(json.dumps(g, ensure_ascii=False, indent=1)[:500])
    print('---')
# tambem verificar formato dos membros
print('exemplo membros:', c[-1]['m'])
