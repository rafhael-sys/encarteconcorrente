import json
fila = json.load(open('data/fila_novos.json'))
actions = json.load(open('data/actions.json'))
byid = {a['id']: a for a in actions}
products = json.load(open('data/products.json'))
print("shortcode | status | exist_pg | fila_pg | fonte")
for p in fila:
    sc = p['shortcode']
    a = byid.get(sc)
    exist_pg = len(a['paginas']) if a else 0
    newframes = 0
    if a:
        for pg in p['paginas']:
            if pg not in a['paginas'] and pg[:-4] not in products:
                newframes += 1
    tag = "EXISTS nf=%d" % newframes if a else "NEW"
    print("%-46s | %-14s | e=%2d | f=%2d | %s" % (sc[:46], tag, exist_pg, len(p['paginas']), p.get('fonte', 'feed')))
