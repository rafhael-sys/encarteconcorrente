import json, re, unicodedata, os
NOISE = {"lata","lta","pct","pcte","pacote","pet","tb","gf","cada","un","und",
         "unid","unidade","sabores","sabor","fragrancias","fragrancia","tipos","tipo"}
def toks(s):
    s = unicodedata.normalize("NFD", str(s).lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    return tuple(sorted(t for t in s.split() if t and t not in NOISE))

acts = json.load(open('data/actions.json'))
prods = json.load(open('data/products.json'))
byid = {a['id']: a for a in acts}

def act_tokens(aid):
    a = byid[aid]; out=set()
    for pg in a['paginas']:
        for it in prods.get(pg[:-4], []):
            out.add(toks(it['n']))
    return out

# same-unit existing flyers
parn_mac = act_tokens('Db6v0lXmrJl')   # PARN/MAC 61
pn_as    = act_tokens('Db6vyruGkKY')   # PN/AS 138
horti    = act_tokens('Db6v1SEmu0_')   # horti 20

def load_ext(sc):
    d = json.load(open(f'data/_extract/w0812_{sc}.json'))
    items=[]
    for k,v in d['pages'].items():
        for it in v: items.append(it)
    return d, items

for sc, sameunit_name, sameunit in [
    ('Db82gnbnc9K','PARN/MAC(Db6v0lXmrJl 61)', parn_mac),
    ('Db8VDKjFfxX','PN/AS(Db6vyruGkKY 138)', pn_as),
    ('Db8Lfvwjlg7','RF/AS/PC -> compare vs PN/AS', pn_as),
]:
    if not os.path.exists(f'data/_extract/w0812_{sc}.json'):
        print(sc, 'NO EXTRACT YET'); continue
    d, items = load_ext(sc)
    myt = [toks(it['n']) for it in items]
    myset = set(myt)
    def frac(twin):
        if not myset: return 0.0
        return sum(1 for t in myset if t in twin)/len(myset)
    in_same = [it['n'] for it,t in zip(items,myt) if t in sameunit]
    not_same = [it['n'] for it,t in zip(items,myt) if t not in sameunit]
    union_all = parn_mac|pn_as|horti
    print('='*60)
    print(sc, '| nprod', len(items), '| titulo', d['titulo'])
    print('  frac vs same-unit', sameunit_name, '=', round(frac(sameunit),2))
    print('  frac vs UNION(all favorito twins) =', round(frac(union_all),2))
    print('  produtos NÃO no same-unit flyer:', not_same)
