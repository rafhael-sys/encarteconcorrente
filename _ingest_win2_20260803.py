#!/usr/bin/env python3
"""Ingestao da 2a janela de 2026-08-03 (fila coletada ao longo do dia).

Consome data/_extract/<shortcode>.json (um por post da fila; formato do
INSTRUCOES.md: {shortcode, discard, discard_reason, inicio, fim, titulo,
pages:{pagekey: [ {n,p,u,x,y,w,h} ]}}). Metadados vem de data/fila_novos.json.

Regras (iguais ao pipeline ingest_20260803.py):
- discard=true / 0 produto / teaser / B2B / fora-RN / sorteio -> DESCARTE.
- pid do produto = nome do arquivo SEM .jpg (feed E story), igual ao build_painel.
- DEDUP por sobreposicao de tokens contra acoes de MESMO banner e MESMO periodo
  (existentes + as mantidas nesta janela com MAIS produtos): overlap >= 0.6 -> dup.
  Para Mar Vermelho e Favorito (postam varios carrosseis no mesmo periodo) a
  regra e mais conservadora: so descarta se 0 produto NOVO (memoria do projeto).
- canon: nrm_tokens (igual ao pipeline); NUNCA une pares marcados DIFERENTES.
- toda acao NOVA recebe adicionado_em = HOJE (acende a tag 'Novo' no painel).

DRY_RUN por padrao. Rode 'python3 _ingest_win2_20260803.py commit' p/ gravar.
"""
import json
import os
import re
import shutil
import sys
import unicodedata

BASE = os.path.dirname(os.path.abspath(__file__))
HOJE = "2026-08-03"
DRY_RUN = not (len(sys.argv) > 1 and sys.argv[1] == "commit")

NOISE = {"lata", "lta", "pct", "pcte", "pacote", "pet", "tb", "gf", "cada", "un",
         "und", "unid", "unidade", "sabores", "sabor", "fragrancias",
         "fragrancia", "tipos", "tipo"}

MV_FAV = {"Mar Vermelho Atacado", "Favorito Super / Atacado Favorito"}


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
        if line.lstrip().startswith("- DIFERENTES:"):
            m = re.findall(r"«([^»]*)»", line)
            if len(m) == 2:
                diferentes.add(frozenset((nrm_name(m[0]), nrm_name(m[1]))))

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


# --- carrega extracao por post ---
def load_extract(sc):
    fp = path("data/_extract", sc + ".json")
    if not os.path.exists(fp):
        return None
    return json.load(open(fp, encoding="utf-8"))


def post_pages(sc):
    """(key, items) das paginas da fila que tem >=1 produto extraido, em ordem."""
    ex = load_extract(sc) or {}
    pages = ex.get("pages", {})
    out = []
    for pg in byshort.get(sc, {}).get("paginas", []):
        key = pg[:-4] if pg.endswith(".jpg") else pg
        items = pages.get(key) or []
        if items:
            out.append((key, items))
    return out


def meta_periodo(sc, ex):
    """inicio/fim/fonte/link/titulo do post. Web = confiavel da fila."""
    src = byshort.get(sc, {})
    if src.get("fonte") == "web" and src.get("validade_confiavel"):
        ini, fim = src.get("inicio"), src.get("fim")
        fonte, link = "web", src.get("link", "")
    else:
        ini = (ex or {}).get("inicio") or src.get("inicio")
        fim = (ex or {}).get("fim") or src.get("fim") or ini
        fonte = src.get("fonte") or ("story" if sc.startswith("story_") else "feed")
        link = src.get("link", "")
    if not ini:
        ini = HOJE
    if not fim:
        fim = ini
    titulo = (ex or {}).get("titulo") or ""
    return ini, fim, fonte, link, titulo


# --- 1a passada: coleta candidatos mantidos (com tokens) ---
cand = {}   # sc -> dict(pages, ini, fim, banner, tokens, nprod, fonte, link, titulo)
report = {"novos": [], "dedup": [], "discard": []}

for sc in byshort:
    ex = load_extract(sc)
    if ex is None:
        report["discard"].append((sc, "sem arquivo de extracao"))
        continue
    if ex.get("discard"):
        report["discard"].append((sc, "extrator: " + (ex.get("discard_reason") or "?")))
        continue
    pages = post_pages(sc)
    if not pages:
        report["discard"].append((sc, "sem pagina com produto/preco"))
        continue
    ini, fim, fonte, link, titulo = meta_periodo(sc, ex)
    tokens = {nrm_tokens(it["n"]) for _, v in pages for it in v}
    cand[sc] = dict(pages=pages, ini=ini, fim=fim, banner=byshort[sc]["banner"],
                    tokens=tokens, nprod=sum(len(v) for _, v in pages),
                    fonte=fonte, link=link, titulo=titulo)


def twin_tokens(sc):
    """Tokens de acoes de MESMO banner e MESMO periodo: existentes + candidatos
    desta janela com MAIS produtos (desempate deterministico)."""
    c = cand[sc]
    toks, n = set(), 0
    for a in actions:
        if a["banner"] == c["banner"] and a.get("inicio") == c["ini"] and a.get("fim") == c["fim"]:
            tot = 0
            for pg in a["paginas"]:
                for it in products.get(pg[:-4], []):
                    toks.add(nrm_tokens(it["n"]))
                    tot += 1
            if tot:
                n += 1
    for osc, oc in cand.items():
        if osc == sc:
            continue
        if oc["banner"] == c["banner"] and oc["ini"] == c["ini"] and oc["fim"] == c["fim"]:
            # desempate: so conta como "gemea" quem tem mais produtos (ou igual e sc menor)
            if (oc["nprod"], osc) > (c["nprod"], sc):
                toks |= oc["tokens"]
                n += 1
    return toks, n


# --- 2a passada: dedup ---
plan_novos = []
for sc in list(cand):
    c = cand[sc]
    tw, ntw = twin_tokens(sc)
    inter = [t for t in c["tokens"] if t in tw]
    frac = (len(inter) / len(c["tokens"])) if c["tokens"] else 0.0
    novos_prod = len(c["tokens"]) - len(inter)
    # DEDUP só quando o post não acrescenta NENHUM produto novo (duplicata real)
    # contra gêmeas de mesmo banner+período. Preferimos preservar preços novos
    # (Incidência é acumulativa) a evitar toda sobreposição — bloatar é mais
    # seguro que perder um preço de concorrente. MV_FAV mantido explícito para
    # deixar a intenção clara (postam vários carrosséis no mesmo período).
    dup = ntw > 0 and novos_prod == 0
    if dup:
        report["dedup"].append((sc, c["banner"], c["ini"], c["fim"], c["nprod"],
                                round(frac, 2), novos_prod, ntw))
    else:
        report["novos"].append((sc, c["banner"], f'{c["ini"]}..{c["fim"]}',
                                c["nprod"], round(frac, 2), novos_prod, ntw))
        plan_novos.append(sc)

print("=" * 74)
print("DRY_RUN" if DRY_RUN else "COMMIT", "- _ingest_win2_20260803")
print("=" * 74)
print("\n[NOVAS acoes] (sc | banner | periodo | nprod | overlap | novos | ntwins)")
for r in sorted(report["novos"]):
    print("  +", *r)
print("\n[DEDUP descartado] (sc | banner | ini | fim | nprod | overlap | novos | ntwins)")
for r in sorted(report["dedup"]):
    print("  x", *r)
print("\n[DISCARD] (sc | motivo)")
for r in sorted(report["discard"]):
    print("  -", *r)
print("\nTotais: novos=%d dedup=%d discard=%d (fila=%d)" % (
    len(report["novos"]), len(report["dedup"]), len(report["discard"]), len(byshort)))

if DRY_RUN:
    print("\n(dry-run: nada gravado. rode 'python3 _ingest_win2_20260803.py commit')")
    sys.exit(0)

# ================= COMMIT =================
for f in ("data/actions.json", "data/products.json", "data/canon.json"):
    shutil.copy(path(f), path(f + ".bak-win2-20260803"))

total_prod = 0
banners_novos = {}
for sc in plan_novos:
    c = cand[sc]
    src = byshort.get(sc, {})
    paginas = []
    for key, items in c["pages"]:
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
        titulo = c["titulo"] or f'Ofertas {c["banner"]} — story ({dd})'
    else:
        titulo = c["titulo"] or c["banner"]
    actions.append({
        "id": sc,
        "perfil": src.get("perfil", ""),
        "titulo": titulo,
        "banner": c["banner"],
        "segmento": src.get("segmento", ""),
        "inicio": c["ini"],
        "fim": c["fim"],
        "carrossel": len(paginas) > 1,
        "shortcode": sc,
        "caption": src.get("caption", ""),
        "paginas": paginas,
        "adicionado_em": HOJE,
        "fonte": c["fonte"],
        "link": c["link"],
    })
    byid[sc] = actions[-1]
    banners_novos[c["banner"]] = banners_novos.get(c["banner"], 0) + 1

json.dump(actions, open(path("data/actions.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
json.dump(products, open(path("data/products.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
json.dump(canon, open(path("data/canon.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

print("\nGRAVADO. novos=%d | produtos_novos=%d | canon: %d novos, %d encaixes, %d bloq_dif" % (
    len(plan_novos), total_prod, log["novos"], log["merges"], log["bloq_dif"]))
print("Banners com novidade:", banners_novos)
