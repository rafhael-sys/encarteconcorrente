import json
import datetime

acts = json.load(open('data/actions.json'))
prods = json.load(open('data/products.json'))


def prods_da_acao(a):
    out = []
    for pg in a.get('paginas', []):
        key = pg[:-4] if pg.endswith('.jpg') else pg
        for p in prods.get(key, []):
            if isinstance(p, dict) and p.get('n'):
                out.append(p['n'])
    return out


def examinar(banner, ini, fim, rotulo):
    print(f'\n===== {rotulo} | banner={banner} | periodo {ini}->{fim} =====')
    achou = False
    for a in acts:
        if a.get('banner') != banner:
            continue
        # sobreposicao de periodo
        if a.get('fim', '') < ini or a.get('inicio', '') > fim:
            continue
        pn = prods_da_acao(a)
        print(f"  [{a['id']}] {a.get('inicio')}->{a.get('fim')} fonte={a.get('fonte','-')} nprod={len(pn)}")
        if pn:
            achou = True
            for n in pn:
                print('       -', n)
    if not achou:
        print('  (nenhuma acao sobreposta com produtos)')


# A: MV MARZAP 24-30/07
examinar('Mar Vermelho Atacado', '2026-07-24', '2026-07-30', 'A: MV MARZAP (carrossel DbVLMNWGzLU)')

# converter taken_at do super nordestao p/ data
ta = 1785152183
d = datetime.datetime.utcfromtimestamp(ta) - datetime.timedelta(hours=3)
print('\n>>> Super Nordestao taken_at ->', d.strftime('%Y-%m-%d %H:%M'), '(Natal)')
