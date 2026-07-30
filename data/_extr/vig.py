import json, datetime
a = json.load(open('data/actions.json'))
hoje = datetime.date.today().isoformat()
vig = [x for x in a if x['fim'] >= hoje]
pg = sum(len(x['paginas']) for x in vig)
print('encartes vigentes (fim>=hoje):', len(vig))
print('páginas embutidas (aprox):', pg)
top = sorted(vig, key=lambda x: -len(x['paginas']))[:10]
for x in top:
    print('  ', len(x['paginas']), 'pgs', x['id'], x['fim'])
