import json
p = json.load(open('data/products.json'))
print('=== products.json tipo:', type(p).__name__)
if isinstance(p, dict):
    ks = list(p.keys())
    print('num chaves:', len(ks))
    print('exemplo chave:', ks[0])
    print(json.dumps({ks[0]: p[ks[0]]}, ensure_ascii=False, indent=1)[:1200])

c = json.load(open('data/canon.json'))
print('=== canon.json tipo:', type(c).__name__)
if isinstance(c, dict):
    ks = list(c.keys())
    print('num chaves:', len(ks))
    print('exemplo:', json.dumps({ks[0]: c[ks[0]]}, ensure_ascii=False, indent=1)[:800])
elif isinstance(c, list):
    print('num itens:', len(c))
    print('exemplo:', json.dumps(c[0], ensure_ascii=False, indent=1)[:800])
