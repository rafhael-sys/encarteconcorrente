import json
acts = json.load(open('data/actions.json'))
print('=== last 6 actions (compact) ===')
for a in acts[-6:]:
    print(a.get('id'), '|', a.get('banner'), '|', a.get('inicio'), a.get('fim'), '| add:', a.get('adicionado_em'), '| fonte:', a.get('fonte'), '| sc:', a.get('shortcode'))
print()
print('=== web-sourced actions sample ===')
n=0
for a in acts:
    if a.get('fonte') == 'web':
        d = dict(a)
        d.pop('paginas', None)
        print(json.dumps(d, ensure_ascii=False))
        n += 1
        if n >= 3:
            break
print()
print('=== recent IG id vs shortcode ===')
n=0
for a in acts[-40:]:
    if a.get('shortcode'):
        print('id=', a.get('id'), ' sc=', a.get('shortcode'), ' perfil=', a.get('perfil'), ' add=', a.get('adicionado_em'))
        n += 1
        if n >= 12:
            break
print()
# which actions have adicionado_em
cnt = sum(1 for a in acts if a.get('adicionado_em'))
print('actions with adicionado_em:', cnt, '/', len(acts))
