import json
actions = json.load(open('data/actions.json'))
a = next(x for x in actions if x['id'] == 'DbjcA11jxwm')
print("id:", a['id'])
print("titulo:", a['titulo'])
print("periodo:", a['inicio'], '->', a['fim'])
print("paginas:", a['paginas'])
print("caption:", (a.get('caption') or '')[:300])
