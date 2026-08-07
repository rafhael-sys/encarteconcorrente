import json, os
cands = json.load(open('data/similaridade_candidatos.json'))
incertos = json.load(open('data/similaridade_incertos.json'))
print("total candidatos:", len(cands))
missing = set()
already_incerto = 0
for i, c in enumerate(cands):
    for side in ('foto_a', 'foto_b'):
        img = c[side]['imagem']
        if not os.path.exists(img):
            missing.add(img)
    if c['k'] in incertos:
        already_incerto += 1
print("imagens faltando:", len(missing))
for m in list(missing)[:30]:
    print("   MISSING", m)
print("pares já em incertos (existente):", already_incerto)
print()
print("=== lista (idx | r | a  ||  b) ===")
for i, c in enumerate(cands):
    print("%2d | r=%.3f | %s  ||  %s" % (i, c.get('r', 0), c['a'][:42], c['b'][:42]))
