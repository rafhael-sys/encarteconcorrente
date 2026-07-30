import json, glob, os
d = '/Users/teste/encarteconcorrente/data/_extr'
fila = json.load(open('/Users/teste/encarteconcorrente/data/fila_novos.json'))
order = [p['shortcode'] for p in fila]
meta = {p['shortcode']: p for p in fila}
res = {}
for sc in order:
    fp = os.path.join(d, sc + '.json')
    if not os.path.exists(fp):
        print('!!FALTA', sc); continue
    res[sc] = json.load(open(fp))

print('=== RESUMO POR POST ===')
for sc in order:
    r = res.get(sc, {})
    pags = r.get('paginas', {})
    nprod = sum(len(v) for v in pags.values())
    per = r.get('periodo_impresso', {})
    m = meta[sc]
    print('{:36s} [{}] {:22s} class={:9s} per={}..{} pgs={} prod={} {}'.format(
        sc, m.get('fonte') or 'feed', m['banner'][:22], r.get('classificacao','?'),
        per.get('inicio'), per.get('fim'), len(pags), nprod,
        ('DESC:'+str(r.get('motivo',''))[:40]) if r.get('classificacao')=='descartar' else ''))

json.dump(res, open(os.path.join(d, '_ALL.json'), 'w'), ensure_ascii=False)
print('\nsalvo _ALL.json')
