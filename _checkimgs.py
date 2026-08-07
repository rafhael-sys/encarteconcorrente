import json, os
fila = json.load(open('data/fila_novos.json'))
missing = []
present = 0
for p in fila:
    for pg in p['paginas']:
        fp = os.path.join('data/pages', pg)
        if os.path.exists(fp):
            present += 1
        else:
            missing.append(pg)
print('presentes:', present, 'faltando:', len(missing))
for m in missing:
    print('  FALTA', m)
