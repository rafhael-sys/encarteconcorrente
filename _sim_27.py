import json, os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
c = json.load(open('data/similaridade_candidatos.json'))

mesmo = [0,1,3,4,6,19,21,31,32,37,47,48,49,50,54,58,59,64]
diferente = [2,7,8,9,10,11,14,16,17,18,20,22,23,24,25,26,29,33,34,35,40,41,42,43,44,45,51,52,53,55,56,57,60,62]
incertos = [5,12,13,15,27,28,30,36,38,39,46,61,63]
assert sorted(mesmo+diferente+incertos) == list(range(65)), "cobertura incompleta"

vals = []
for i in mesmo:
    vals.append({"a": c[i]["a"], "b": c[i]["b"], "veredito": "mesmo"})
for i in diferente:
    vals.append({"a": c[i]["a"], "b": c[i]["b"], "veredito": "diferente"})
os.makedirs('data/validacoes_inbox', exist_ok=True)
json.dump({"validacoes": vals}, open('data/validacoes_inbox/auto_2026-07-27.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)

inc = json.load(open('data/similaridade_incertos.json'))
for i in incertos:
    inc[c[i]["k"]] = "2026-07-27"
json.dump(inc, open('data/similaridade_incertos.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

json.dump([], open('data/similaridade_candidatos.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print("veredictos:", len(vals), "(mesmo", len(mesmo), "diferente", len(diferente), ") | incertos +",
      len(incertos), "-> total", len(inc))
