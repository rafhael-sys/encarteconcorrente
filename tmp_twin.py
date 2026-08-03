import json
a = json.load(open('data/actions.json'))
prods = json.load(open('data/products.json'))
for tid in ['Dbb00bzH3Vq', 'DbfeXfaG_eu', 'DbiDJGXm1xc']:
    act = next(x for x in a if x['id'] == tid)
    print(f"\n===== {tid}  {act['inicio']}->{act['fim']}  paginas={act['paginas']}")
    print("caption:", (act.get('caption') or '')[:200])
    for pg in act['paginas']:
        k = pg[:-4]
        pl = prods.get(k, [])
        print(f"  -- {k}: {len(pl)} produtos")
        for it in pl:
            print(f"       {it.get('n')} | {it.get('p')} {it.get('u','')}")
