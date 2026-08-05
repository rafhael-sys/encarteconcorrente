#!/usr/bin/env python3
"""Ingestao da janela de 2026-08-04.

Consome data/_extract/w0804_*.json (produtos por pagina, extraidos por visao).
Metadados vem de data/fila_novos.json. Regras (iguais ao pipeline):
- Posts sem preco / teaser / educativo / B2B-comerciante -> DESCARTADOS
  (batch vazio ja cai fora por "sem pagina com produto").
- shortcode de STORY ja em actions.json -> ESTENDE (nao ocorre nesta janela).
- shortcode novo (feed/web/story) -> cria acao NOVA, com DEDUP por overlap:
  se existir acao de MESMO banner cujo periodo SOBREPOE o do post novo e cujos
  produtos ja cobrem >= LIMIAR dos produtos do post novo -> DEDUP. As acoes ja
  criadas NESTA rodada tambem contam como "gemeas" (pega story que so repete o
  feed do dia). Overrides manuais em KEEP/DISCARD.
- Banner ja separa unidade (ex.: 'Leva Mais Atacarejo' x '... Joao Camara',
  'SuperFacil Atacado' x '... Vale do Sol'), entao dedup por banner e seguro.
- canon: canonicalizacao por nrm_tokens; NUNCA une pares marcados DIFERENTES
  em regras_similaridade.md.

DRY_RUN por padrao. Rode 'python3 ingest_20260804.py commit' p/ gravar.
"""
import json
import os
import re
import shutil
import sys
import unicodedata

BASE = os.path.dirname(os.path.abspath(__file__))
HOJE = "2026-08-04"
LIMIAR = 0.6
DRY_RUN = not (len(sys.argv) > 1 and sys.argv[1] == "commit")

NOISE = {"lata", "lta", "pct", "pcte", "pacote", "pet", "tb", "gf", "cada", "un",
         "und", "unid", "unidade", "sabores", "sabor", "fragrancias",
         "fragrancia", "tipos", "tipo"}

# ---- Metadados dos posts FEED aprovados (periodo do que esta IMPRESSO) ----
FEED_META = {
    "Dbosa-HATU9": dict(inicio="2026-08-05", fim="2026-08-06",
                        titulo="Feirão de Hortifruti (Qua/Qui)", fonte="feed"),
    "Dbolo7RDzd1": dict(inicio="2026-08-05", fim="2026-08-06",
                        titulo="Super Feirão de Hortifruti (Qua/Qui)", fonte="feed"),
    "DbouPkoCSdu": dict(inicio="2026-08-05", fim="2026-08-11",
                        titulo="Ofertas Favorito (Parnamirim e Macaíba)", fonte="feed"),
    "DbouNqxidfB": dict(inicio="2026-08-05", fim="2026-08-11",
                        titulo="Favoritaço (Ponta Negra e Ayrton Senna)", fonte="feed"),
    "DbouJ4Uidlo": dict(inicio="2026-08-05", fim="2026-08-06",
                        titulo="Quarta e Quinta Verde (Hortifruti)", fonte="feed"),
    "Dbn-MLyE6Ck": dict(inicio="2026-07-29", fim="2026-08-04",
                        titulo="Ofertas Favorito (Ponta Negra e Ayrton Senna)", fonte="feed"),
    "Dbnb57WG_B2": dict(inicio="2026-07-29", fim="2026-08-04",
                        titulo="Ofertas Favorito (Ponta Negra e Ayrton Senna)", fonte="feed"),
    "Dbo6tx9m927": dict(inicio="2026-08-04", fim="2026-08-05",
                        titulo="Mês dos Pais — Ofertas Especiais", fonte="feed"),
    "Dbozt_TmzDP": dict(inicio="2026-07-31", fim="2026-08-06",
                        titulo="Mês dos Pais — Grandes Ofertas (até 3x)", fonte="feed"),
    "DbosqDEG413": dict(inicio="2026-08-05", fim="2026-08-05",
                        titulo="Quarta da Padaria", fonte="feed"),
    "DblBTqfFYyN": dict(inicio="2026-08-04", fim="2026-08-13",
                        titulo="Novo Encarte Leva Mais (Macau)", fonte="feed"),
    "DblBd4GFks4": dict(inicio="2026-08-04", fim="2026-08-13",
                        titulo="Novo Encarte Leva Mais (João Câmara)", fonte="feed"),
    "Dbog_f0IG_Q": dict(inicio="2026-07-31", fim="2026-08-10",
                        titulo="Saldão de Bazar", fonte="feed"),
    "DboglVNGD1V": dict(inicio="2026-08-05", fim="2026-08-19",
                        titulo="Encarte do Mês (Natal)", fonte="feed"),
    "DbohkQXINE5": dict(inicio="2026-07-31", fim="2026-08-10",
                        titulo="Saldão de Bazar em Casa", fonte="feed"),
    "Dboha-IjymB": dict(inicio="2026-07-31", fim="2026-08-10",
                        titulo="Saldão de Bazar em Casa", fonte="feed"),
    "Dbolj3xn03X": dict(inicio="2026-08-05", fim="2026-08-06",
                        titulo="Ofertas Hortifruti", fonte="feed"),
    "DbotBBkAsNN": dict(inicio="2026-08-05", fim="2026-08-09",
                        titulo="Ofertas da Semana (Aniversário)", fonte="feed"),
}

# ---- Metadados das acoes de STORY novas (colecao do dia) ----
STORY_META = {
    "story_miramarsupermercado_20260804": dict(inicio="2026-08-03", fim="2026-08-17",
        titulo="Miramar — carnes, geral, bebidas e vinhos (story)"),
    "story_mirassolatacado_20260804": dict(inicio="2026-07-28", fim="2026-08-10",
        titulo="Mirassol Atacado — ofertas gerais (story)"),
    "story_redesuper.show_20260804": dict(inicio="2026-08-03", fim="2026-08-06",
        titulo="Rede Super Show — Terça Show e Super Feirão (story)"),
    "story_cortefacil.atacarejo_20260804": dict(inicio="2026-07-31", fim="2026-08-09",
        titulo="Corte Fácil — Festival dos Queijos (story)"),
    "story_favoritosuper_20260804": dict(inicio="2026-07-29", fim="2026-08-04",
        titulo="Favoritaço — encarte Favorito (story)"),
    "story_supernordestaonatal_20260804": dict(inicio="2026-08-04", fim="2026-08-06",
        titulo="Super Nordestão — ofertas em loja (story)"),
    "story_queirozatacadaojoaocamara_20260804": dict(inicio="2026-08-03", fim="2026-08-09",
        titulo="Queiroz Atacadão João Câmara — encartes e ofertas (story)"),
    "story_redesupercop_20260804": dict(inicio="2026-08-01", fim="2026-08-05",
        titulo="Rede Supercop — Barato de Verdade (story)"),
    "story_queirozatacadaonatal__20260804": dict(inicio="2026-08-03", fim="2026-08-16",
        titulo="Queiroz Atacadão — encartes Saudável e São Braz (story)"),
    "story_marvermelhoatacado_20260804": dict(inicio="2026-08-04", fim="2026-08-05",
        titulo="Mar Vermelho — ofertas do dia (story)"),
    "story_atacarejo_santoantonio.ofc_20260804": dict(inicio="2026-08-05", fim="2026-08-06",
        titulo="Atacarejo Santo Antônio — Quarta e Quinta Verde (story)"),
}

# Descartes explicitos (alem dos batches vazios, que caem sozinhos)
DESCARTE = {
    "Dbn-tg8FBVN": "B2B 'Alô Comerciante/Televendas' (Queiroz Natal)",
    "Dbn-8x_nYLF": "B2B 'Alô Comerciante/Televendas' (Queiroz João Câmara)",
    "DbnWxZEoOOD": "sorteio Cremogema/Maizena (número da sorte, sem preços)",
    "DboAqMngUhZ": "evento 2ª Corrida de Rua (institucional, sem produtos)",
    "DboTDlYjz7s": "sorteio Kit Churrasco / moto (sem preços de venda)",
    "DbnVCBnCkLT": "teaser Terça do Cashback (sem preços)",
    "DboVWLCzGOh": "teaser Faz o PIX Favorito (sem preços)",
    "DboNiOUoMml": "teaser Quarta e Quinta Verde 'amanhã' (sem preços)",
    "Dbnm_6PO4y3": "teaser institucional SuperFácil (sem preços)",
    "DbnmziVuou4": "teaser institucional Super Nordestão (sem preços)",
    "DboPwkppq-l": "teaser 'Mira na Bebida' — encarte real está no story",
}

# Story do Mar Vermelho repete os cards avulsos + padaria do FEED do MESMO dia
# (Dbo6tx9m927/Dbozt_TmzDP/DbosqDEG413), que sao mantidos — story descartada.
DISCARD_OVERRIDE = {"story_marvermelhoatacado_20260804"}
# Mar Vermelho: carrosseis avulsos de 1 produto/pagina sao conteudo DISTINTO do
# flyer/story (regra do dono) — mantidos mesmo com overlap.
KEEP_OVERRIDE = {"Dbo6tx9m927", "Dbozt_TmzDP", "DbosqDEG413"}

# Banners compartilhados por unidades diferentes (mesma string de banner):
# NAO deduplicar uma unidade contra a outra — casar tambem por perfil.
BANNER_MULTIUNIDADE = {"Queiroz Atacadão"}


def path(*p):
    return os.path.join(BASE, *p)


def nrm_tokens(s):
    s = unicodedata.normalize("NFD", str(s).lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    return tuple(sorted(t for t in s.split() if t and t not in NOISE))


def nrm_name(s):
    s = unicodedata.normalize("NFD", str(s).lower())
    return " ".join("".join(c for c in s if unicodedata.category(c) != "Mn").split())


def overlaps(ai, af, bi, bf):
    """True se os periodos [ai,af] e [bi,bf] se sobrepoem (datas 'YYYY-MM-DD')."""
    if not (ai and af and bi and bf):
        return False
    return ai <= bf and bi <= af


# --- carrega extracao (w0804_*.json) ---
extract = {}          # pagekey -> [produtos]
post_batch = {}       # shortcode -> {pagekey: [...]}
edir = path("data/_extract")
for fn in sorted(os.listdir(edir)):
    m = re.match(r"w0804_(.+)\.json$", fn)
    if not m:
        continue
    sc = m.group(1)
    d = json.load(open(os.path.join(edir, fn), encoding="utf-8"))
    post_batch[sc] = d
    for k, v in d.items():
        extract[k] = v

actions = json.load(open(path("data/actions.json"), encoding="utf-8"))
products = json.load(open(path("data/products.json"), encoding="utf-8"))
canon = json.load(open(path("data/canon.json"), encoding="utf-8"))
fila = json.load(open(path("data/fila_novos.json"), encoding="utf-8"))
byshort = {p["shortcode"]: p for p in fila}
byid = {a["id"]: a for a in actions}

# pares DIFERENTES (jamais unir)
diferentes = set()
rp = path("data/regras_similaridade.md")
if os.path.exists(rp):
    for line in open(rp, encoding="utf-8"):
        if line.startswith("- DIFERENTES:"):
            mm = re.findall(r"«([^»]*)»", line)
            if len(mm) == 2:
                diferentes.add(frozenset((nrm_name(mm[0]), nrm_name(mm[1]))))

by_key = {}
for g in canon:
    k = nrm_tokens(g["n"])
    if k not in by_key or len(g["m"]) > len(by_key[k]["m"]):
        by_key[k] = g

log = {"novos": 0, "merges": 0, "bloq_dif": 0}


def canon_add(name, unit, ref):
    k = nrm_tokens(name)
    g = by_key.get(k)
    if g is not None and frozenset((nrm_name(name), nrm_name(g["n"]))) in diferentes:
        g = None
        log["bloq_dif"] += 1
    if g is None:
        g = {"n": name, "u": unit, "m": [ref]}
        canon.append(g)
        by_key[nrm_tokens(name)] = g
        log["novos"] += 1
    else:
        if ref not in g["m"]:
            g["m"].append(ref)
        log["merges"] += 1


# "gemeas" = acoes JA EXISTENTES em actions.json (a regra do dono compara o
# post novo apenas com o que ja existe; posts da MESMA rodada nao deduplicam
# entre si — ex.: Favorito Ponta Negra/Ayrton Senna x Parnamirim/Macaiba sao
# lojas diferentes e ambos entram).
def twin_cover(banner, perfil, ini, fim, tokset):
    """Fracao de tokset coberta por acoes JA EXISTENTES de MESMO banner (e mesmo
    perfil, quando o banner e compartilhado por unidades) com periodo sobreposto."""
    twin_toks, n_twins = set(), 0
    for a in actions:
        if a["banner"] != banner:
            continue
        if banner in BANNER_MULTIUNIDADE and a.get("perfil") != perfil:
            continue
        if not overlaps(a.get("inicio"), a.get("fim"), ini, fim):
            continue
        tot = 0
        for pg in a["paginas"]:
            for it in products.get(pg[:-4], []):
                twin_toks.add(nrm_tokens(it["n"]))
                tot += 1
        if tot:
            n_twins += 1
    if not tokset:
        return 0.0, n_twins
    inter = sum(1 for t in tokset if t in twin_toks)
    return inter / len(tokset), n_twins


def post_pages(sc):
    """Paginas (na ordem da fila) do post com >=1 produto extraido."""
    src = byshort.get(sc, {})
    out = []
    for pg in src.get("paginas", []):
        key = pg[:-4]
        items = post_batch.get(sc, {}).get(key) or []
        if items:
            out.append((key, items))
    return out


report = {"novos": [], "dedup": [], "discard": []}
plan_novos = []

order = sorted(byshort, key=lambda s: (s.startswith("story_"), s))

for sc in order:
    if sc in DESCARTE:
        report["discard"].append((sc, DESCARTE[sc]))
        continue
    pages = post_pages(sc)
    if not pages:
        report["discard"].append((sc, "sem página com produto/preço"))
        continue
    nprod = sum(len(v) for _, v in pages)
    src = byshort.get(sc, {})
    banner = src.get("banner", "")
    perfil = src.get("perfil", "")

    if sc in byid:  # story ja existente -> nao ocorre nesta janela
        report["discard"].append((sc, "id já existente (ver extend manual)"))
        continue

    if sc.startswith("story_"):
        meta = STORY_META.get(sc, {})
        ini = meta.get("inicio", HOJE)
        fim = meta.get("fim", "2026-08-06")
    else:
        meta = FEED_META.get(sc, {})
        ini = meta.get("inicio") or src.get("inicio") or HOJE
        fim = meta.get("fim") or src.get("fim") or ini

    tokset = {nrm_tokens(it["n"]) for _, v in pages for it in v}
    frac, n_twins = twin_cover(banner, perfil, ini, fim, tokset)
    gatilho = n_twins > 0 and frac >= LIMIAR
    if sc in KEEP_OVERRIDE:
        gatilho = False
    if sc in DISCARD_OVERRIDE:
        gatilho = True

    if gatilho:
        report["dedup"].append((sc, banner, f"{ini}..{fim}", nprod,
                                round(frac, 2), n_twins))
        continue

    report["novos"].append((sc, banner, f"{ini}..{fim}", nprod,
                            round(frac, 2), n_twins))
    plan_novos.append((sc, pages, ini, fim, meta))

# ---------- relatorio ----------
print("=" * 72)
print("DRY_RUN" if DRY_RUN else "COMMIT", "- ingest_20260804")
print("=" * 72)
print("\n[NOVAS acoes] (sc | banner | periodo | nprod | overlap | ntwins)")
for r in report["novos"]:
    print("  +", *r)
print("\n[DEDUP re-post descartado] (sc | banner | periodo | nprod | overlap | ntwins)")
for r in report["dedup"]:
    print("  x", *r)
print("\n[DISCARD] (sc | motivo)")
for r in report["discard"]:
    print("  -", *r)
print("\nTotais: novos=%d dedup=%d discard=%d" % (
    len(report["novos"]), len(report["dedup"]), len(report["discard"])))

if DRY_RUN:
    print("\n(dry-run: nada gravado. rode 'python3 ingest_20260804.py commit')")
    # desfaz os products provisorios inseridos so p/ o twin_cover
    sys.exit(0)

# ================= COMMIT =================
# recarrega products limpo (removendo provisorios) e regrava do zero
products = json.load(open(path("data/products.json"), encoding="utf-8"))

for f in ("data/actions.json", "data/products.json", "data/canon.json"):
    shutil.copy(path(f), path(f + ".bak-20260804"))

total_prod = 0
banners_novos = {}

for sc, pages, ini, fim, meta in plan_novos:
    src = byshort.get(sc, {})
    banner = src.get("banner", "")
    paginas = []
    for key, items in pages:
        if key in products:
            continue
        products[key] = items
        paginas.append(key + ".jpg")
        total_prod += len(items)
        for idx, it in enumerate(items):
            canon_add(it["n"], it.get("u", "un"), f"{key}#{idx}")
    if not paginas:
        continue
    if sc.startswith("story_"):
        dd = HOJE[8:10] + "/" + HOJE[5:7]
        titulo = meta.get("titulo") or f"Ofertas {banner} — story ({dd})"
        fonte = "story"
        link = ""
    else:
        titulo = meta.get("titulo", "")
        fonte = meta.get("fonte") or src.get("fonte") or "feed"
        link = src.get("link", "")
    actions.append({
        "id": sc,
        "perfil": src.get("perfil", ""),
        "titulo": titulo,
        "banner": banner,
        "segmento": src.get("segmento", ""),
        "inicio": ini,
        "fim": fim,
        "carrossel": len(paginas) > 1,
        "shortcode": sc,
        "caption": src.get("caption", ""),
        "paginas": paginas,
        "adicionado_em": HOJE,
        "fonte": fonte,
        "link": link,
    })
    byid[sc] = actions[-1]
    banners_novos[banner] = banners_novos.get(banner, 0) + 1

json.dump(actions, open(path("data/actions.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
json.dump(products, open(path("data/products.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
json.dump(canon, open(path("data/canon.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

print("\nGRAVADO. novas=%d | produtos_novos=%d | canon: %d novos, %d encaixes, %d bloq_dif" % (
    len(plan_novos), total_prod, log["novos"], log["merges"], log["bloq_dif"]))
print("Banners com novidade:", banners_novos)
