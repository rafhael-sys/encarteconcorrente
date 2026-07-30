import json, importlib.util, sys
spec = importlib.util.spec_from_file_location('ing', '/Users/teste/encarteconcorrente/ingest_20260729b.py')
# não executa o módulo; só relê as constantes via exec parcial seria complexo.
# Em vez disso, reimplementa a checagem lendo os mesmos conjuntos.
extr = json.load(open('data/_extr/_ALL.json'))
acts = json.load(open('data/actions.json'))
existing = {a['id'] for a in acts}
fila = json.load(open('data/fila_novos.json'))
todos = {p['shortcode'] for p in fila}

NOVOS = ["DbYYx07judi","DbY0w1mFW_g","DbYse9aFAr9","DbYj6vunJbL","DbYWhRTlR2X",
"DbY90YsoIlp","DbZEmcnkcKw","DbZP9aVm_MX","DbZdrvom9TF","DbZOjy2FYs7","DbZDJeumHPP",
"DbY9f5tGTKV","DbZOhmFlkho","DbX5nyDsy4y","DbZOReaFiMp","DbZPq9PDV7g","DbZIzTBDz1j",
"story_atacarejo_santoantonio.ofc_20260729","story_queirozatacadaonatal__20260729",
"story_mirassolatacado_20260729","story_redesupercop_20260729",
"story_supernordestaonatal_20260729","story_queirozatacadaojoaocamara_20260729",
"story_redesuper.show_20260729"]
MERGES = ["story_miramarsupermercado_20260729","story_marvermelhoatacado_20260729",
"story_cortefacil.atacarejo_20260729","story_favoritosuper_20260729","story_redemaisrn_20260729"]
DESC = ["DbY71_aTj0X","DbYbtIgFhdW","DbZHInKkZD1","story_levamaismacau_20260729","story_levamaisjc_20260729"]

print('cobertura: NOVOS+MERGES+DESC =', len(NOVOS)+len(MERGES)+len(DESC), 'de', len(todos), 'na fila')
falt = todos - set(NOVOS) - set(MERGES) - set(DESC)
extra = (set(NOVOS)|set(MERGES)|set(DESC)) - todos
print('  faltando no plano:', falt)
print('  no plano mas fora da fila:', extra)
print('NOVOS já existentes (ERRO se algum):', [s for s in NOVOS if s in existing])
print('MERGES ausentes em actions (ERRO se algum):', [s for s in MERGES if s not in existing])
print('NOVOS não-encarte na extração (ERRO):', [s for s in NOVOS if extr.get(s,{}).get('classificacao')!='encarte'])
print('MERGES não-encarte na extração (ERRO):', [s for s in MERGES if extr.get(s,{}).get('classificacao')!='encarte'])
print('DESC que na verdade são encarte c/ produto:', [s for s in DESC if extr.get(s,{}).get('classificacao')=='encarte'])
