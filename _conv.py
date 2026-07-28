import json

acts = {a['id']: a for a in json.load(open('data/actions.json'))}
prods = json.load(open('data/products.json'))

for aid in ('story_supernordestaonatal_20260727', 'story_redemaisrn_20260727',
            'story_miramarsupermercado_20260727'):
    a = acts[aid]
    print(f'\n{aid}: {len(a["paginas"])} paginas')
    for pg in a['paginas']:
        key = pg[:-4] if pg.endswith('.jpg') else pg
        n = len(prods.get(key, []))
        print(f'   {pg}  -> {n} prod  (key em products? {key in prods})')
