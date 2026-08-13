import json, glob, os
fila = json.load(open('data/fila_novos.json'))
byshort = {p['shortcode']: p for p in fila}
fields = {'n', 'p', 'u', 'x', 'y', 'w', 'h'}
problems = []
total_keep = total_prod = 0
for sc, src in byshort.items():
    f = f'data/_extract/w0812_{sc}.json'
    if not os.path.exists(f):
        problems.append(f'{sc}: MISSING FILE'); continue
    try:
        d = json.load(open(f))
    except Exception as e:
        problems.append(f'{sc}: JSON ERR {e}'); continue
    if d.get('shortcode') != sc:
        problems.append(f'{sc}: shortcode mismatch -> {d.get("shortcode")}')
    valid_pages = {p[:-4] for p in src['paginas']}
    if d.get('discard'):
        if d.get('pages'):
            problems.append(f'{sc}: discard but pages not empty')
        continue
    n = 0
    for pk, items in (d.get('pages') or {}).items():
        if pk not in valid_pages:
            problems.append(f'{sc}: page key {pk} not in post pages')
        for it in items:
            n += 1
            miss = fields - set(it.keys())
            if miss:
                problems.append(f'{sc}/{pk}: item missing {miss}: {it.get("n")}')
            p = str(it.get('p', ''))
            if not any(ch.isdigit() for ch in p):
                problems.append(f'{sc}/{pk}: price no digit: {it.get("n")} -> {p!r}')
    total_keep += 1
    total_prod += n
    print(f'{sc:22} KEEP  npag={len(d.get("pages") or {})} nprod={n}  {d.get("inicio")}..{d.get("fim")}  | {d.get("titulo")}')
print('\nDISCARDS:')
for sc, src in byshort.items():
    d = json.load(open(f'data/_extract/w0812_{sc}.json'))
    if d.get('discard'):
        print(f'  {sc:22} {d.get("discard_reason")}')
print(f'\nKEEP posts={total_keep}  total products={total_prod}')
print('\nPROBLEMS:' if problems else '\nNo structural problems.')
for p in problems:
    print('  !', p)
