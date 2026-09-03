import json
actions=json.load(open('data/actions.json'))
products=json.load(open('data/products.json'))
def pc(act):
    t=0
    for pg in act.get('paginas',[]):
        k=pg[:-4] if pg.endswith('.jpg') else pg
        t+=len(products.get(k,[]))
    return t
want=['DcriSVWj4E7','Dcw8xKmnZnF','Dcw9kodTISl','DcmaaO7Gsqe','DcmanVTH2KW','Dcw2dlQGyRm','Dcme_Z9oExB']
by={a['shortcode']:a for a in actions if a['shortcode'] in want}
for sc in want:
    a=by.get(sc)
    if not a: print(sc,'NAO ENCONTRADO'); continue
    print('====',sc,'| banner=',a['banner'],'| perfil=',a['perfil'])
    print('   periodo',a['inicio'],'->',a['fim'],'| prods=',pc(a),'| titulo=',a.get('titulo'))
    print('   paginas=',a['paginas'])
    print('   adicionado_em=',a.get('adicionado_em'))
