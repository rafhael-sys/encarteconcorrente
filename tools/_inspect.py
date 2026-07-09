import json
p = json.load(open('data/products.json'))
# find a page with products
for k, v in p.items():
    if v:
        print('PAGE KEY:', k, 'count:', len(v))
        print(json.dumps(v[0], ensure_ascii=False, indent=1))
        print('--- second ---')
        if len(v) > 1:
            print(json.dumps(v[1], ensure_ascii=False, indent=1))
        break
# show a web page product
for k, v in p.items():
    if k.startswith('atacadao_c192') and v:
        print('=== WEB PAGE', k, 'count', len(v))
        print(json.dumps(v[0], ensure_ascii=False, indent=1))
        break
# canon "m" reference format explanation: it's pageid#index into products list
print('\nCANON m ref = <pageid>#<index in that page product list>')
