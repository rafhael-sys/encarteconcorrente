import json
a = json.load(open('data/actions.json'))
for x in a:
    if x.get('adicionado_em'):
        print('=== exemplo com adicionado_em ===')
        print(json.dumps(x, ensure_ascii=False, indent=1)[:900])
        break
for x in a:
    if x.get('fonte') == 'web':
        print('=== exemplo fonte web ===')
        print(json.dumps(x, ensure_ascii=False, indent=1)[:900])
        break
for x in a:
    if x.get('fonte') == 'story':
        print('=== exemplo fonte story ===')
        print(json.dumps(x, ensure_ascii=False, indent=1)[:900])
        break
keys = set()
for x in a:
    keys |= set(x.keys())
print('=== campos usados ===')
print(sorted(keys))
