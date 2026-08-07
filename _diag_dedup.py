import json, re, unicodedata, os

NOISE = {"lata","lta","pct","pcte","pacote","pet","tb","gf","cada","un","und",
         "unid","unidade","sabores","sabor","fragrancias","fragrancia","tipos","tipo"}
def toks(s):
    s = unicodedata.normalize("NFD", str(s).lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    return tuple(sorted(t for t in s.split() if t and t not in NOISE))
def ov(ai,af,bi,bf): return bool(ai and af and bi and bf) and ai<=bf and bi<=af

actions=json.load(open('data/actions.json'))
products=json.load(open('data/products.json'))
BANNER_MULTI={"Queiroz Atacadão","Leva Mais Atacarejo"}

def diag(sc, extract_file, banner, perfil, ini, fim):
    d=json.load(open(extract_file))
    myitems=[it for v in d.values() for it in v]
    mytoks={toks(it['n']) for it in myitems}
    print("\n### %s (%s) %s..%s | %d prod, %d toks distintos" % (sc,banner,ini,fim,len(myitems),len(mytoks)))
    # find covering twins
    for a in actions:
        if a['banner']!=banner: continue
        if banner in BANNER_MULTI and a.get('perfil')!=perfil: continue
        if not ov(a.get('inicio'),a.get('fim'),ini,fim): continue
        atoks=set()
        for pg in a['paginas']:
            for it in products.get(pg[:-4],[]):
                atoks.add(toks(it['n']))
        if not atoks: continue
        cov=sum(1 for t in mytoks if t in atoks)
        if cov:
            print("   twin %-40s %s..%s pg=%d : cobre %d/%d" % (a['id'][:40],a['inicio'],a['fim'],len(a['paginas']),cov,len(mytoks)))
    # show sample product names+prices of mine
    print("   meus produtos (nome | preço):")
    for it in myitems[:12]:
        print("      - %s | %s" % (it['n'][:55], it['p']))

diag("Dbs_FcJDiHM","data/_extract/w0806b_Dbs_FcJDiHM.json","Rede Super Show","redesuper.show","2026-08-06","2026-08-10")
diag("DbskJQtm5WH","data/_extract/w0806b_DbskJQtm5WH.json","Mar Vermelho Atacado","marvermelhoatacado","2026-08-06","2026-08-07")
