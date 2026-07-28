import json

prods = json.load(open('data/products.json'))
print('products.json tipo:', type(prods).__name__)
if isinstance(prods, dict):
    ks = list(prods.keys())
    print('total chaves (paginas):', len(ks))
    print('exemplo de chave:', ks[0])
    print('exemplo de valor:')
    print(json.dumps(prods[ks[0]], ensure_ascii=False, indent=1)[:1200])
print()

canon = json.load(open('data/canon.json'))
print('canon.json tipo:', type(canon).__name__)
if isinstance(canon, dict):
    ks = list(canon.keys())
    print('total grupos:', len(ks))
    print('exemplo chave:', repr(ks[0]))
    print('exemplo valor:')
    print(json.dumps(canon[ks[0]], ensure_ascii=False, indent=1)[:1000])
elif isinstance(canon, list):
    print('total:', len(canon))
    print(json.dumps(canon[0], ensure_ascii=False, indent=1)[:1000])
