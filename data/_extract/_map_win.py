import json, os
BASE=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
fila=json.load(open(os.path.join(BASE,'data/fila_novos.json')))
actions=json.load(open(os.path.join(BASE,'data/actions.json')))
byid={a['id']:a for a in actions}
products=json.load(open(os.path.join(BASE,'data/products.json')))
print("shortcode | in_actions? | existing pg | fila pg | fonte")
for p in fila:
    sc=p['shortcode']
    a=byid.get(sc)
    exist_pg = len(a['paginas']) if a else 0
    # new frames = fila pages not already in existing action & not in products
    newframes=0
    if a:
        for pg in p['paginas']:
            if pg not in a['paginas'] and pg[:-4] not in products:
                newframes+=1
    tag = f"EXISTS(newframes={newframes})" if a else "NEW"
    print(f"{sc[:48]:48s} | {tag:22s} | exist={exist_pg:2d} | fila={len(p['paginas']):2d} | {p.get('fonte','feed')}")
