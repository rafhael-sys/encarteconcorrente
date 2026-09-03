import json
s=json.load(open('data/similaridade_candidatos.json'))
def blk(i):
    par=s[i]; fa=par['foto_a']; fb=par['foto_b']
    ra=fa['regiao_pct']; rb=fb['regiao_pct']
    return (f"[i={i}]\n"
            f"  A img: {fa['imagem']} | regiao x={ra['x']} y={ra['y']} w={ra['w']} h={ra['h']} | nome: {fa.get('nome_impresso','')}\n"
            f"  B img: {fb['imagem']} | regiao x={rb['x']} y={rb['y']} w={rb['w']} h={rb['h']} | nome: {fb.get('nome_impresso','')}")
ranges=[(0,11),(11,22),(22,33),(33,44),(44,55),(55,65)]
for (a,b) in ranges:
    print(f"===== BATCH {a}-{b-1} =====")
    for i in range(a,b):
        print(blk(i))
    print()
