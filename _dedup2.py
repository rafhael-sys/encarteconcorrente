import json

acts = {a['id']: a for a in json.load(open('data/actions.json'))}
prods = json.load(open('data/products.json'))


def dump(aid, filtro=None):
    a = acts.get(aid)
    if not a:
        print(f'  (acao {aid} nao existe)')
        return
    print(f'\n--- {aid} | {a.get("inicio")}->{a.get("fim")} | banner={a.get("banner")} ---')
    for pg in a.get('paginas', []):
        key = pg[:-4] if pg.endswith('.jpg') else pg
        for p in prods.get(key, []):
            if not isinstance(p, dict) or not p.get('n'):
                continue
            nome = p['n']
            if filtro and not any(f.lower() in nome.lower() for f in filtro):
                continue
            print(f"     {p.get('p','?'):>14}  {nome}")


print('=== MARZAP: precos na acao existente DbJzQS-G14k ===')
dump('DbJzQS-G14k', ['Sadia', 'DuBom', 'Betânia', 'Tambaú', 'Petrópolis', 'Brilhante'])

print('\n=== Miramar twins (22-30/07) ===')
for aid in ('story_miramarsupermercado_20260722', 'story_miramarsupermercado_20260723',
            'story_miramarsupermercado_20260727'):
    dump(aid)

print('\n=== CorteFacil twin 20260727 (23-28/07) ===')
dump('story_cortefacil.atacarejo_20260727')

print('\n=== Rede Mais periodo 21-28/07 (DbCEgdfj_vF etc.) ===')
for a in json.load(open('data/actions.json')):
    if a.get('banner') == 'Rede Mais' and not (a.get('fim','') < '2026-07-21' or a.get('inicio','') > '2026-07-28'):
        dump(a['id'])
