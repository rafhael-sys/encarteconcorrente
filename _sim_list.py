import json, os

cand = json.load(open('data/similaridade_candidatos.json'))
print("total pares:", len(cand))
miss = 0
for i, c in enumerate(cand):
    fa = c['foto_a']['imagem']
    fb = c['foto_b']['imagem']
    for f in (fa, fb):
        if not os.path.exists(f):
            print("  FALTA IMG:", f)
            miss += 1
print("imgs faltando:", miss)
# dump compact list to a file for subagent chunking
out = []
for i, c in enumerate(cand):
    out.append({
        "i": i,
        "k": c["k"],
        "a": c["a"],
        "b": c["b"],
        "ra": c["foto_a"],
        "rb": c["foto_b"],
        "r": c.get("r"),
    })
json.dump(out, open('data/_extract/sim0807_pairs.json', 'w'), ensure_ascii=False, indent=1)
print("gravado data/_extract/sim0807_pairs.json")
