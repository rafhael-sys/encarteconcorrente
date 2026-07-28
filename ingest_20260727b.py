#!/usr/bin/env python3
"""Ingestão 27/07/2026 — janela da NOITE (feed + stories).

Consome scratchpad/results_ev/*.json (extração por visão desta rodada) e monta
ações/produtos/canon com a MESMA canonicalização do pipeline (nrm_tokens/
canon_add), agora respeitando data/regras_similaridade.md (pares MESMO/
DIFERENTES validados pelo usuário) ao encaixar produtos no canon.

Descartes desta janela (NÃO entram):
  DbT4fyTzGs5   Favorito  — teaser "Sextou com Sabadão está chegando" (sem preços)
  DbTPImBjydl   Miramar   — receita "Gelatina Colorida" (sem preços)
  DbTMDKnG7gZ   Mar Verm. — vaga de emprego (institucional)
  DbTBoiKFZyg   Leva Mais Macau — Televendas B2B (comerciante)
  DbTBh6ilqR4   Leva Mais JC    — Televendas B2B (comerciante)
  DbTyC_-GxDn   Mar Verm. — 25-27/07: todos os 10 produtos já em DbMYQHYm-2W +
                DbO2Np8m9UU (compilação repetida, 0 produto novo)
  DbTWbgcG00H   Mar Verm. — 24-30/07: 6/6 produtos idênticos a DbStPdYG-Nd (repost)
  DbTe0Y2nA5b   Favorito  — gôndola varejo 22-28: 6/6 já em DbE_K9DDHaM/DbN6VExnMX7
  story_superfacilatacado — sem preço (só teaser de lançamento)
"""
import glob
import json
import os
import re
import shutil
import unicodedata

BASE = os.path.dirname(os.path.abspath(__file__))


def path(*p: str) -> str:
    """Monta caminho absoluto a partir da raiz do projeto."""
    return os.path.join(BASE, *p)


HOJE = "2026-07-27"
RESULTS_DIR = path("scratchpad/results_ev")

# reposts/duplicatas com decision=keep no arquivo, mas que NÃO devem entrar
SKIP = {"DbTyC_-GxDn", "DbTWbgcG00H", "DbTe0Y2nA5b"}

NOISE = {"lata", "lta", "pct", "pcte", "pacote", "pet", "tb", "gf", "cada", "un",
         "und", "unid", "unidade", "sabores", "sabor", "fragrancias",
         "fragrancia", "tipos", "tipo"}

TITULOS = {
    "DbT_N-5D8EV": "Encarte Rede Super Show (28/07 a 02/08)",
    "DbTnIQMnaSt": "Ofertas de Gôndola Favorito — Parnamirim e Macaíba (22 a 28/07)",
    "DbUCMpODx1k": "Dia Q Queiroz Natal (28 e 29/07)",
    "DbUGqN-G8NE": "Grandes Ofertas MarZap Mar Vermelho (28 e 29/07)",
    "DbUCRqxFYz1": "Dia Q Queiroz João Câmara (28 e 29/07)",
    "DbUMT_0AJQS": "Terça da Carne Santo Antônio (28/07)",
    "DbUEf7Djik8": "Terça da Carne Supercop (28/07)",
    "story_miramarsupermercado_20260727": "Miramar Terça da Carne — story (28/07)",
    "story_levamaisjc_20260727": "Ofertas Leva Mais João Câmara — story",
    "story_supernordestaonatal_20260727": "Ofertas Super Nordestão — story",
    "story_levamaismacau_20260727": "Ofertas Leva Mais Macau — story",
    "story_redemaisrn_20260727": "Ofertas Rede Mais — story",
    "story_cortefacil.atacarejo_20260727": "Ofertas Corte Fácil — story",
    "story_superfacilvaledosol_20260727": "Ofertas SuperFácil Vale do Sol — story",
    "story_queirozatacadaojoaocamara_20260727": "Ofertas Queiroz João Câmara — story",
    "story_mirassolatacado_20260727": "Ofertas Mirassol Atacado — story",
    "story_queirozatacadaonatal__20260727": "Ofertas Queiroz Natal — story",
    "story_redesuper.show_20260727": "Ofertas Rede Super Show — story",
    "story_atacarejo_santoantonio.ofc_20260727": "Ofertas Santo Antônio — story",
    "story_redesupercop_20260727": "Ofertas Rede Supercop — story",
    "story_favoritosuper_20260727": "Ofertas Favorito — story",
    "story_marvermelhoatacado_20260727": "Ofertas Mar Vermelho — story",
}


def nrm_tokens(s: str) -> tuple:
    """Normaliza nome para tokens ordenados sem acento/ruído de embalagem."""
    s = unicodedata.normalize("NFD", str(s).lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    return tuple(sorted(t for t in s.split() if t and t not in NOISE))


def nrm_full(s: str) -> str:
    """Normalização das regras: minúsculas, sem acento, espaços colapsados."""
    s = unicodedata.normalize("NFD", str(s).lower())
    return " ".join("".join(c for c in s if unicodedata.category(c) != "Mn").split())


def norm_preco(p: str) -> str:
    """Remove prefixo R$ e usa vírgula como separador decimal."""
    t = str(p or "").strip()
    t = re.sub(r"^r\$\s*", "", t, flags=re.I).strip()
    if re.fullmatch(r"\d+\.\d{2}", t):
        t = t.replace(".", ",")
    return t


def carrega_regras() -> tuple:
    """Lê data/regras_similaridade.md -> (pares_diferentes, pares_mesmo)."""
    diff = set()
    same = []
    reg = path("data/regras_similaridade.md")
    if not os.path.exists(reg):
        return diff, same
    par = re.compile(r"«([^»]*)»\s*(==|!=)\s*«([^»]*)»")
    for linha in open(reg, encoding="utf-8"):
        m = par.search(linha)
        if not m:
            continue
        a, op, b = nrm_full(m.group(1)), m.group(2), nrm_full(m.group(3))
        if op == "!=":
            diff.add(frozenset((a, b)))
        else:
            same.append((a, b))
    return diff, same


actions = json.load(open(path("data/actions.json"), encoding="utf-8"))
products = json.load(open(path("data/products.json"), encoding="utf-8"))
canon = json.load(open(path("data/canon.json"), encoding="utf-8"))
fila = json.load(open(path("data/fila_novos.json"), encoding="utf-8"))
byshort = {p["shortcode"]: p for p in fila}

for f in ("data/actions.json", "data/products.json", "data/canon.json"):
    shutil.copy(path(f), path(f + ".bak-20260727b-ingest"))

diff_pairs, same_pairs = carrega_regras()

by_key: dict = {}       # nrm_tokens -> grupo (maior)
by_nrm: dict = {}       # nrm_full(n) -> grupo
for g in canon:
    k = nrm_tokens(g["n"])
    if k not in by_key or len(g["m"]) > len(by_key[k]["m"]):
        by_key[k] = g
    by_nrm.setdefault(nrm_full(g["n"]), g)

# índice de MESMO: nrm_full -> lista de parceiros
same_map: dict = {}
for a, b in same_pairs:
    same_map.setdefault(a, []).append(b)
    same_map.setdefault(b, []).append(a)

log = {"novos": 0, "merges": 0, "diff_bloqueados": 0, "mesmo_redirect": 0}


def canon_add(name: str, unit: str, ref: str) -> None:
    """Encaixa a ocorrência num grupo canônico, respeitando regras_similaridade.

    - DIFERENTES: nunca junta em grupo cujo nome-representante seja par proibido.
    - MESMO: se o nome deveria estar no grupo de um parceiro validado, usa esse.
    """
    k = nrm_tokens(name)
    nf = nrm_full(name)
    g = by_key.get(k)

    # guarda DIFERENTES: bloqueia encaixe em grupo proibido
    if g is not None and frozenset((nf, nrm_full(g["n"]))) in diff_pairs:
        g = None
        log["diff_bloqueados"] += 1

    # redirect MESMO: prefere o grupo de um parceiro validado
    if g is None:
        for parc in same_map.get(nf, []):
            gp = by_nrm.get(parc) or by_key.get(nrm_tokens(parc))
            if gp is not None and frozenset((nf, nrm_full(gp["n"]))) not in diff_pairs:
                g = gp
                log["mesmo_redirect"] += 1
                break

    if g is None:
        g = {"n": name, "u": unit, "m": [ref]}
        canon.append(g)
        by_key[k] = g
        by_nrm.setdefault(nf, g)
        log["novos"] += 1
    else:
        if ref not in g["m"]:
            g["m"].append(ref)
        by_key.setdefault(k, g)
        by_nrm.setdefault(nf, g)
        log["merges"] += 1


existing_ids = {a["id"] for a in actions}
kept, total_prod = [], 0
banners_novos: dict = {}

for arq in sorted(glob.glob(os.path.join(RESULTS_DIR, "*.json"))):
    doc = json.load(open(arq, encoding="utf-8"))
    sc = doc.get("shortcode") or os.path.basename(arq)[:-5]
    if doc.get("decision") != "keep" or sc in SKIP:
        continue
    if sc in existing_ids:
        print(f"[skip] ação {sc} já existe")
        continue
    pages_res = doc.get("pages", {}) or {}

    paginas = []
    for key, itens_raw in pages_res.items():
        itens = []
        for it in itens_raw:
            p = norm_preco(it.get("p"))
            if not p:
                continue
            itens.append({"n": it["n"], "p": p, "u": it.get("u", "un"),
                          "x": it["x"], "y": it["y"], "w": it["w"], "h": it["h"]})
        if not itens:
            continue
        if key in products:
            print(f"[skip] página {key} já em products.json")
            continue
        products[key] = itens
        paginas.append(key + ".jpg")
        total_prod += len(itens)
        for idx, it in enumerate(itens):
            canon_add(it["n"], it.get("u", "un"), f"{key}#{idx}")
    if not paginas:
        print(f"[skip] {sc} sem páginas com produto")
        continue

    src = byshort.get(sc, {})
    banner = src.get("banner") or doc.get("banner") or ""
    fonte = src.get("fonte") or ("story" if sc.startswith("story_") else "feed")
    actions.append({
        "id": sc,
        "perfil": src.get("perfil", doc.get("perfil", "")),
        "titulo": TITULOS.get(sc, doc.get("titulo", "")),
        "banner": banner,
        "segmento": src.get("segmento", doc.get("segmento", "")),
        "inicio": doc["inicio"],
        "fim": doc["fim"],
        "carrossel": len(paginas) > 1,
        "shortcode": sc,
        "caption": src.get("caption", ""),
        "paginas": paginas,
        "adicionado_em": HOJE,
        "fonte": fonte,
        "link": src.get("link", ""),
    })
    existing_ids.add(sc)
    kept.append(sc)
    banners_novos[banner] = banners_novos.get(banner, 0) + 1

json.dump(actions, open(path("data/actions.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
json.dump(products, open(path("data/products.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
json.dump(canon, open(path("data/canon.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

print("OK — ações novas:", len(kept), "| produtos:", total_prod,
      "| canon:", len(canon),
      f"({log['novos']} novos, {log['merges']} encaixes, "
      f"{log['diff_bloqueados']} diff-bloq, {log['mesmo_redirect']} mesmo-redir)")
print("Banners:", banners_novos)
print("IDs:", kept)
