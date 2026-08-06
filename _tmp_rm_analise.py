import json, re, unicodedata
NOISE={'lata','lta','pct','pcte','pacote','pet','tb','gf','cada','un','und','unid','unidade','sabores','sabor','fragrancias','fragrancia','tipos','tipo'}
def nt(s):
    s=unicodedata.normalize('NFD',str(s).lower())
    s=''.join(c for c in s if unicodedata.category(c)!='Mn')
    s=re.sub(r'[^a-z0-9 ]',' ',s)
    return tuple(sorted(t for t in s.split() if t and t not in NOISE))
def ov(ai,af,bi,bf): return ai<=bf and bi<=af
actions=json.load(open('data/actions.json'))
products=json.load(open('data/products.json'))
new=json.load(open('data/_extract/w0806_story_redemaisrn_20260806.json'))
ini,fim='2026-08-01','2026-08-10'
twin_tok=set(); twins=[]
for a in actions:
    if a['banner']!='Rede Mais': continue
    if not ov(a.get('inicio'),a.get('fim'),ini,fim): continue
    toks=set()
    for pg in a['paginas']:
        for it in products.get(pg[:-4],[]):
            toks.add(nt(it['n']))
    if toks:
        twins.append((a['id'],a['inicio'],a['fim'],len(toks)))
        twin_tok|=toks
print('TWINS Rede Mais sobrepostos:')
for t in twins: print('   ',t)
print()
allitems=[it for pg in new.values() for it in pg]
novos=0
for it in allitems:
    k=nt(it['n'])
    isnew = k not in twin_tok
    if isnew: novos+=1
    tag = '*** NOVO ***' if isnew else 'ja existe'
    print('  [%s] %s -- %s' % (tag, it['n'], it['p']))
print()
print('Total itens: %d | novos: %d | overlap=%.2f' % (len(allitems), novos, 1-novos/len(allitems)))
