import os, json
q=json.load(open('data/fila_novos.json'))
missing=[]
allpages=[]
for post in q:
    for pg in post['paginas']:
        allpages.append((post['shortcode'],pg))
        if not os.path.exists('data/pages/'+pg):
            missing.append(pg)
print('total paginas na fila:',len(allpages))
print('faltando:',missing)
# tamanho dos jpgs para ordenar leitura
