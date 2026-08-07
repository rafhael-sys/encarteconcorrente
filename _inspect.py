import json

d = json.load(open('data/actions.json'))
print("=== acao fonte:web ===")
for a in d:
    if a.get('fonte') == 'web':
        obj = dict(a)
        obj.pop('caption', None)
        print(json.dumps(obj, ensure_ascii=False))
        break
print("=== acao com adicionado_em ===")
for a in d:
    if 'adicionado_em' in a:
        obj = dict(a)
        obj.pop('caption', None)
        print(json.dumps(obj, ensure_ascii=False))
        break

print("=== canon estrutura ===")
c = json.load(open('data/canon.json'))
print('tipo', type(c).__name__)
if isinstance(c, dict):
    ks = list(c.keys())
    print('num chaves top', len(ks), 'exemplos', ks[:5])
    k0 = ks[0]
    print('exemplo', repr(k0), '->', json.dumps(c[k0], ensure_ascii=False)[:400])
elif isinstance(c, list):
    print('len', len(c), 'ex0', json.dumps(c[0], ensure_ascii=False)[:500])
