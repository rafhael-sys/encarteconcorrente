import json

a = json.load(open('data/actions.json'))
p = json.load(open('data/products.json'))
c = json.load(open('data/canon.json'))
print('actions:', len(a), '| products pages:', len(p), '| canon groups:', len(c))

ids = {'Dbk9GgejsLQ', 'Dbl4RwAPqNM', 'DblC6rhHFVu', 'DblKIIvFiHi', 'DblX_2MG-pU',
       'Dblzn2jm0Yg', 'DbmF-NwFrro', 'DbmHocUjRRD', 'DbmIO3PH4Pd', 'DbmKoN8A8_R',
       'atacadao_6ce160eb0f', 'story_atacarejo_santoantonio.ofc_20260803',
       'story_cortefacil.atacarejo_20260803', 'story_favoritosuper_20260803',
       'story_marvermelhoatacado_20260803', 'story_miramarsupermercado_20260803',
       'story_mirassolatacado_20260803', 'story_queirozatacadaojoaocamara_20260803',
       'story_queirozatacadaonatal__20260803', 'story_redesuper.show_20260803',
       'story_supernordestaonatal_20260803'}
novos = [x for x in a if x['id'] in ids]
print('novas de hoje encontradas:', len(novos))
prob = 0
for x in novos:
    if x.get('adicionado_em') != '2026-08-03':
        print('  [!] adicionado_em errado:', x['id'], x.get('adicionado_em')); prob += 1
    for pg in x['paginas']:
        k = pg[:-4]
        if k not in p or not p[k]:
            print('  [!] pagina sem produto:', x['id'], pg); prob += 1
print('problemas:', prob)

# membros de canon dos grupos recém-criados apontam para produtos existentes?
prodkeys = set(p.keys())
badref = 0
for g in c:
    for m in g['m']:
        pid, _, idx = m.rpartition('#')
        if pid in prodkeys:
            try:
                if int(idx) >= len(p[pid]):
                    badref += 1
            except ValueError:
                badref += 1
print('refs canon com idx fora de faixa (em paginas presentes):', badref)
print('OK')
