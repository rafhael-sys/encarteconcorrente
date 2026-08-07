import json, os
fila = json.load(open('data/fila_novos.json'))
missing = []
total = 0
for p in fila:
    for pg in p['paginas']:
        total += 1
        if not os.path.exists(os.path.join('data/pages', pg)):
            missing.append(pg)
print("total pages referenced:", total)
print("missing:", len(missing))
for m in missing[:50]:
    print("  MISSING", m)
