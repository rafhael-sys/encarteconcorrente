#!/usr/bin/env python3
"""Ingestao da 2a janela de 2026-08-17 (analise diaria do Claude).

Le os extracts produzidos pelos subagentes em data/_extract_win2_20260817/*.json
(cada arquivo = lista de posts com decision keep/discard + paginas/produtos),
cria as acoes NOVAS (decision == keep) e canonicaliza os produtos usando a mesma
logica do ingest_20260817.py (nrm_tokens; NUNCA une pares DIFERENTES das
regras_similaridade.md).

Metadados (banner, segmento, perfil, caption, paginas, fonte/link) vem da
fila_novos.json pelo shortcode. Para posts fonte:web o inicio/fim vem da fila
(confiavel); para os demais, do proprio extract.

DRY_RUN por padrao. Rode 'python3 ingest_20260817b.py commit' p/ gravar.
"""
import glob
import json
import os
import re
import shutil
import sys
import unicodedata

BASE = os.path.dirname(os.path.abspath(__file__))
HOJE = "2026-08-17"
EXTRACT_DIR = os.path.join(BASE, "data", "_extract_win2_20260817")
DRY_RUN = not (len(sys.argv) > 1 and sys.argv[1] == "commit")

NOISE = {"lata", "lta", "pct", "pcte", "pacote", "pet", "tb", "gf", "cada", "un",
         "und", "unid", "unidade", "sabores", "sabor", "fragrancias",
         "fragrancia", "tipos", "tipo"}


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


def salva(p, data):
    tmp = f"{p}.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    os.replace(tmp, p)


def carrega_extracts():
    """Le todos os *.json do EXTRACT_DIR (menos sim_*.json) e devolve
    {shortcode: post_result}."""
    posts = {}
    for fp in sorted(glob.glob(os.path.join(EXTRACT_DIR, "*.json"))):
        nome = os.path.basename(fp)
        if nome.startswith("sim_"):
            continue
        with open(fp, encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            data = [data]
        for post in data:
            sc = post.get("shortcode")
            if sc:
                posts[sc] = post
    return posts


def main():
    actions = json.load(open(path("data/actions.json"), encoding="utf-8"))
    products = json.load(open(path("data/products.json"), encoding="utf-8"))
    canon = json.load(open(path("data/canon.json"), encoding="utf-8"))
    fila = json.load(open(path("data/fila_novos.json"), encoding="utf-8"))
    byshort = {p["shortcode"]: p for p in fila}
    byid = {a["id"]: a for a in actions}

    posts = carrega_extracts()

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

    log = {"novos_canon": 0, "merges_canon": 0, "bloq_dif": 0}

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
            log["novos_canon"] += 1
        else:
            if ref not in g["m"]:
                g["m"].append(ref)
            log["merges_canon"] += 1

    # PRODUCTS por pagekey (a partir dos extracts das paginas)
    PRODUCTS = {}
    for sc, post in posts.items():
        if post.get("decision") != "keep":
            continue
        for pg in post.get("paginas", []):
            PRODUCTS[pg["key"]] = pg.get("produtos", [])

    keeps = [sc for sc, p in posts.items() if p.get("decision") == "keep"]
    keeps.sort(key=lambda sc: byshort.get(sc, {}).get("taken_at", 0))

    n_act = n_prod = 0
    resumo = []
    for sid in keeps:
        post = posts[sid]
        if sid in byid:
            print(f"[pula] acao ja existe: {sid}")
            continue
        src = byshort.get(sid)
        if not src:
            print(f"[aviso] shortcode ausente na fila: {sid}")
            continue
        eh_web = src.get("fonte") == "web"
        inicio = src.get("inicio") if eh_web else post.get("inicio")
        fim = src.get("fim") if eh_web else post.get("fim")
        act = {
            "id": sid,
            "perfil": src.get("perfil"),
            "titulo": post.get("titulo") or src.get("banner"),
            "banner": src.get("banner"),
            "segmento": src.get("segmento"),
            "inicio": inicio,
            "fim": fim,
            "carrossel": src.get("carrossel", False),
            "shortcode": sid,
            "caption": src.get("caption", ""),
            "adicionado_em": HOJE,
            "paginas": list(src.get("paginas", [])),
        }
        if src.get("fonte"):
            act["fonte"] = src["fonte"]
        if src.get("link"):
            act["link"] = src["link"]
        actions.append(act)
        byid[sid] = act
        n_act += 1
        pcount = 0
        for fname in src.get("paginas", []):
            pid = fname[:-4] if fname.endswith(".jpg") else fname
            lista = PRODUCTS.get(pid, [])
            products[pid] = lista
            for i, p in enumerate(lista):
                n_prod += 1
                pcount += 1
                canon_add(p["n"], p.get("u", "un"), f"{pid}#{i}")
        resumo.append(f"  {sid} | {act['banner']} | {inicio}->{fim} | {pcount} prod | {act['titulo']}")

    print(f"{'DRY-RUN' if DRY_RUN else 'COMMIT'}: {n_act} acoes novas, {n_prod} produtos, "
          f"canon: {log['novos_canon']} grupos novos, {log['merges_canon']} merges, "
          f"{log['bloq_dif']} bloqueios DIFERENTES")
    print("\n".join(resumo))
    descartes = [sc for sc, p in posts.items() if p.get("decision") != "keep"]
    print(f"descartes ({len(descartes)}): {', '.join(sorted(descartes))}")

    if DRY_RUN:
        return
    stamp = HOJE.replace("-", "")
    for nome in ("actions.json", "products.json", "canon.json"):
        pth = path("data", nome)
        if os.path.exists(pth):
            shutil.copy2(pth, f"{pth}.bak-{stamp}-ingestb")
    salva(path("data/actions.json"), actions)
    salva(path("data/products.json"), products)
    salva(path("data/canon.json"), canon)
    print("gravado.")


if __name__ == "__main__":
    main()
