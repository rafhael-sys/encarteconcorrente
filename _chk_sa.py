import json, unicodedata, difflib
def nrm(s):
    s = unicodedata.normalize('NFD', str(s).lower())
    return ' '.join(''.join(c for c in s if unicodedata.category(c) != 'Mn').split())
acts = {a['id']: a for a in json.load(open('data/actions.json'))}
prods = json.load(open('data/products.json'))
a = acts['Db4BsEcoMR0']
existing = []
for p in a['paginas']:
    for x in prods.get(p[:-4], []):
        existing.append((x['n'], x['p']))
enorm = {nrm(n) for n, _ in existing}
new_items = [
 ('Flocao de Milho Rei de Ouro 500g','1,19'),('Macarrao Espaguete Gostoso 400g','2,19'),
 ('Feijao Preto Kume 1kg','5,49'),('Arroz Parboilizado Blue Soft 1kg','3,09'),
 ('Linguica de Frango Lar 700g','9,49'),('Queijo Mussarela Processado Caico','29,90'),
 ('Linguica Calabresa Sadia','20,98'),('Peito de Frango Coopavel','9,98'),
 ('Whisky ou Licor Jack Daniels 1L','129,90'),('Whisky Red Label 1L','78,90'),
 ('Cerveja Devassa Puro Malte Lata 350ml','2,69'),('Cerveja Itaipava Lata 350ml','2,49'),
 ('Lava Roupas em Po Ala 400g','2,69'),('Agua Sanitaria Dragao 1L','2,29'),
 ('Kit Shampoo Condicionador Pantene','29,99'),('Desodorante Dove Aerosol 150ml','14,99'),
]
print('Total existing products in Db4BsEcoMR0:', len(existing))
for n, p in new_items:
    hit = nrm(n) in enorm
    close = difflib.get_close_matches(nrm(n), list(enorm), n=1, cutoff=0.55)
    print(('OK ' if hit else '?? ') + f'{n} ({p}) exato={hit} parecido={close}')
print('=== beverage/limpeza no encarte existente ===')
for n, pp in existing:
    ln = n.lower()
    if any(w in ln for w in ['whisky','jack','red label','devassa','itaipava','ala','dragao','pantene','dove','sanit','shampoo','condic']):
        print('  ', n, '=', pp)
