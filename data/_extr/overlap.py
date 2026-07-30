import json, unicodedata, re
acts = json.load(open('data/actions.json'))
prods = json.load(open('data/products.json'))
allc = json.load(open('data/_extr/_ALL.json'))
byid = {a['id']: a for a in acts}

NOISE = {"lata","lta","pct","pcte","pacote","pet","tb","gf","cada","un","und","unid","unidade","sabores","sabor","fragrancias","fragrancia","tipos","tipo","kg","g","ml","l"}
def nrm(s):
    s = unicodedata.normalize("NFD", str(s).lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    s = re.sub(r"[^a-z0-9 ]"," ",s)
    return frozenset(t for t in s.split() if t and t not in NOISE)

def prods_of_action(aid):
    a = byid[aid]
    out = []
    for pg in a['paginas']:
        out += prods.get(pg.replace('.jpg',''), [])
    return out

def prods_of_extr(sc):
    out = []
    for pg in allc[sc]['paginas'].values():
        out += pg
    return out

def names(lst): return [p['n'] for p in lst]

def overlap(newsc, existid):
    en = prods_of_extr(newsc)
    ex = prods_of_action(existid)
    exsets = [nrm(p['n']) for p in ex]
    hit = 0
    for p in en:
        k = nrm(p['n'])
        if any(k == e or (k and e and (k <= e or e <= k)) for e in exsets):
            hit += 1
    print('  novo {} ({} prod) vs {} ({} prod): {}/{} nomes do novo batem no existente'.format(newsc, len(en), existid, len(ex), hit, len(en)))

print('=== DbWsmQaE-4V (Favorito) ===')
print('  titulo:', byid['DbWsmQaE-4V']['titulo'], '|', byid['DbWsmQaE-4V']['inicio'], byid['DbWsmQaE-4V']['fim'])
print('  produtos:', names(prods_of_action('DbWsmQaE-4V')))
overlap('DbYj6vunJbL','DbWsmQaE-4V')
overlap('DbYWhRTlR2X','DbWsmQaE-4V')

print('=== DbWwLXUFve3 (Santo Antonio) ===')
print('  titulo:', byid['DbWwLXUFve3']['titulo'], '|', byid['DbWwLXUFve3']['inicio'], byid['DbWwLXUFve3']['fim'])
print('  primeiros nomes:', names(prods_of_action('DbWwLXUFve3'))[:20])
overlap('DbYbtIgFhdW','DbWwLXUFve3')
print('  novo DbYbtIgFhdW nomes:', names(prods_of_extr('DbYbtIgFhdW')))
