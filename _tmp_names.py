import json
products=json.load(open('data/products.json'))
for key in ['DcriSVWj4E7_p1','DcmanVTH2KW_p1','Dcw2dlQGyRm_p1']:
    print('====',key)
    for pr in products.get(key,[])[:8]:
        print('  ',json.dumps(pr,ensure_ascii=False))
