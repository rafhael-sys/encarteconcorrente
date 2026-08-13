import json, re, unicodedata
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

def act_items(aid):
    a = byid[aid]; out=[]
    for pg in a['paginas']:
        for it in prods.get(pg[:-4], []):
            out.append(it)
    return out

horti_items = act_items('Db6v1SEmu0_')
horti_tok = {toks(it['n']): it for it in horti_items}
print('Db6v1SEmu0_ (horti flyer 12-13) produtos:')
for it in horti_items:
    print('   ', it['n'], '=', it['p'], it.get('u',''))

d = json.load(open('data/_extract/w0812_Db8TupgnB93.json'))
print('\nDb8TupgnB93 (5 fruits) — match vs horti flyer:')
for k, v in d['pages'].items():
    for it in v:
        t = toks(it['n'])
        status = 'IN flyer' if t in horti_tok else 'NOT in flyer'
        extra = f" (flyer: {horti_tok[t]['p']})" if t in horti_tok else ''
        print(f'   {it["n"]:40} = {it["p"]:8} -> {status}{extra}')
