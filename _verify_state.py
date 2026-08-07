import json
actions = json.load(open('data/actions.json'))
products = json.load(open('data/products.json'))
canon = json.load(open('data/canon.json'))
print("actions:", len(actions))
print("product page-keys:", len(products))
print("canon groups:", len(canon))
# show the extended cortefacil action
a = next(x for x in actions if x['id'] == 'story_cortefacil.atacarejo_20260806')
print("cortefacil extend -> paginas agora:", len(a['paginas']), "| fim:", a['fim'])
# confirm all 17 new ids present with adicionado_em today
newids = ["Dbs5VqqnEiW","Dbs9t7tnMZ5","Dbs_FcJDiHM","DbsqkoamA7r","Dbt-3PLGsMS","Dbt2BYFltiY","Dbt2CUwCAk9","Dbt2ZLiH6mK","Dbt3yRTD4fl","DbtJaAuFUIj","DbtOzrESL85","DbtpyCFAf9_","DbtvODJmLU-","story_favoritosuper_20260806","story_miramarsupermercado_20260806","story_superfacilvaledosol_20260806","story_supernordestaonatal_20260806"]
byid = {a['id']: a for a in actions}
miss = [i for i in newids if i not in byid]
print("faltando:", miss)
print("todos com adicionado_em=2026-08-06:", all(byid[i].get('adicionado_em')=='2026-08-06' for i in newids if i in byid))
