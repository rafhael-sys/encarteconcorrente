import json, os

edir = 'data/_extract'

# ---- 1) Trim Mar Vermelho STORY: drop frames that duplicate the two MV feeds
mv = os.path.join(edir, 'w0806b_story_marvermelhoatacado_20260806.json')
d = json.load(open(mv))
# keep only the UNIQUE frames (Festival Vinhos, Festival da Casa x2, Café Santa Clara)
keep = {
    'story_marvermelhoatacado_3957801490824505120',  # Festival Vinhos (12)
    'story_marvermelhoatacado_3957816590897743181',  # Festival da Casa (12)
    'story_marvermelhoatacado_3957816825577435435',  # Festival da Casa (20)
    'story_marvermelhoatacado_3957963873797641888',  # Café Santa Clara (1)
}
before = sum(len(v) for v in d.values())
d = {k: v for k, v in d.items() if k in keep}
after = sum(len(v) for v in d.values())
json.dump(d, open(mv, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print("MV story trim: %d -> %d produtos (frames restantes=%d)" % (before, after, len(d)))

# ---- 2) Build meta (dates/titulo for KEEP; discard/reason for DISCARD)
meta = {}

def keep(sc, ini, fim, titulo):
    meta[sc] = {"inicio": ini, "fim": fim, "titulo": titulo}

def discard(sc, reason):
    meta[sc] = {"discard": True, "reason": reason}

# --- FEED keeps ---
keep("DbtJaAuFUIj", "2026-08-05", "2026-08-06", "Favorito — Quarta e Quinta Verde (hortifruti)")
keep("Dbs9t7tnMZ5", "2026-08-05", "2026-08-11", "Favorito — Favoritaço (Parnamirim e Macaíba)")
keep("Dbs5VqqnEiW", "2026-08-05", "2026-08-11", "Favorito — Varejo Ponta Negra e Ayrton Senna")
keep("Dbt3yRTD4fl", "2026-08-07", "2026-08-09", "Favorito — Faz o PIX Favorito")
keep("DbsqkoamA7r", "2026-08-04", "2026-08-18", "Super Nordestão — Especial Importados")
keep("Dbt2ZLiH6mK", "2026-08-07", "2026-08-13", "Mar Vermelho — Mês dos Pais")
keep("DbskJQtm5WH", "2026-08-06", "2026-08-07", "Mar Vermelho — Feirão Hortifruti")
keep("DbtvODJmLU-", "2026-08-07", "2026-08-09", "Rede Super Show — Super Dia Show")
keep("Dbs_FcJDiHM", "2026-08-07", "2026-08-10", "Rede Super Show — Bebidas e Perfumaria (Dia dos Pais)")
keep("Dbt-3PLGsMS", "2026-08-07", "2026-08-09", "Corte Fácil — Bom Todo (Dia dos Pais)")
keep("Dbt2CUwCAk9", "2026-08-07", "2026-08-08", "RedeMAIS — Oferta Nota 10 (26 anos)")
keep("DbtpyCFAf9_", "2026-08-07", "2026-08-24", "SuperFácil — Marca Exclusiva")
keep("DbtOzrESL85", "2026-08-07", "2026-08-09", "Leva Mais (Macau) — Paizão (Dia dos Pais)")
keep("Dbt2BYFltiY", "2026-08-07", "2026-08-09", "Leva Mais João Câmara — Paizão (Dia dos Pais)")

# --- STORY keeps ---
keep("story_favoritosuper_20260806", "2026-08-05", "2026-08-11", "Favorito — ofertas (story 06/08)")
keep("story_supernordestaonatal_20260806", "2026-08-05", "2026-08-18", "Super Nordestão — ofertas de loja (story 06/08)")
keep("story_miramarsupermercado_20260806", "2026-08-05", "2026-08-19", "Miramar — ofertas (story 06/08)")
keep("story_atacarejo_santoantonio.ofc_20260806", "2026-08-05", "2026-08-06", "Atacarejo Santo Antônio — Quarta e Quinta Verde (story 06/08)")
keep("story_marvermelhoatacado_20260806", "2026-08-05", "2026-08-30", "Mar Vermelho — Festival de Vinhos e da Casa (story 06/08)")
keep("story_redesuper.show_20260806", "2026-08-05", "2026-08-06", "Rede Super Show — Super Feirão Hortifruti (story 06/08)")
keep("story_queirozatacadaonatal__20260806", "2026-07-28", "2026-08-16", "Queiroz Atacadão (Natal) — +Saudável e São Braz (story 06/08)")
keep("story_queirozatacadaojoaocamara_20260806", "2026-07-28", "2026-08-16", "Queiroz Atacadão (João Câmara) — +Saudável, São Braz e Feirão (story 06/08)")
keep("story_mirassolatacado_20260806", "2026-07-28", "2026-08-10", "Mirassol Atacado — ofertas (story 06/08)")
keep("story_superfacilvaledosol_20260806", "2026-08-06", "2026-08-10", "SuperFácil Vale do Sol — ofertas (story 06/08)")
# story_cortefacil.atacarejo_20260806 -> EXTENDS existing action; no meta needed.

# --- DISCARDS ---
discard("DbtHtg2DDZx", "teaser 'É amanhã' do PIX Favorito — sem produto com preço")
discard("Dbtld-EGD-H", "Super Nordestão Dia da Cerveja — só 'Leve X Pague Y', sem preço em R$ impresso")
discard("DbstrgHEtu4", "Miramar teaser 'confira as ofertas nos stories' — sem produto com preço")
discard("DbtbYhEHbiw", "Rede Super Show — peça institucional (matéria AgoraRN), sem produto/preço")
discard("DbstNwXuaBY", "SuperFácil Atacado JOÃO PESSOA — oferta fora do RN (regra)")
discard("story_superfacilatacado_20260806", "SuperFácil Atacado — frames de João Pessoa/PB (regra), nada RN com preço")
discard("story_redesupercop_20260806", "Rede Supercop — frame institucional Dia dos Pais, sem preço")

json.dump(meta, open(os.path.join(edir, 'w0806b_meta.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print("meta gravado: %d entradas (keep=%d, discard=%d)" % (
    len(meta),
    sum(1 for v in meta.values() if not v.get('discard')),
    sum(1 for v in meta.values() if v.get('discard'))))
