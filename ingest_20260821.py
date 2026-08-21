#!/usr/bin/env python3
"""Ingestao da janela de 2026-08-21 (analise diaria do Claude).

Adiciona acoes NOVAS (classificacao/dedup ja feita nesta sessao). Descartes e
decisoes de dedup ficam documentados em _new_data.json (campo "descartes").

canon: canonicalizacao por nrm_tokens (mesma logica de ingest_20260820.py);
NUNCA une pares marcados DIFERENTES em regras_similaridade.md.

Dados extraidos: _new_data.json (actions + products). Caption preservada da fila.
DRY_RUN por padrao. Rode 'python3 ingest_20260821.py commit' p/ gravar.
"""
import json
import os
import re
import shutil
import sys
import unicodedata

BASE = os.path.dirname(os.path.abspath(__file__))
HOJE = "2026-08-21"
DRY_RUN = not (len(sys.argv) > 1 and sys.argv[1] == "commit")

NOISE = {"lata", "lta", "pct", "pcte", "pacote", "pet", "tb", "gf", "cada", "un",
         "und", "unid", "unidade", "sabores", "sabor", "fragrancias",
         "fragrancia", "tipos", "tipo"}


def path(*p: str) -> str:
    """Junta caminhos a partir do diretorio do script."""
    return os.path.join(BASE, *p)


def nrm_tokens(s: str) -> tuple:
    """Normaliza um nome em tokens ordenados sem ruido de embalagem."""
    s = unicodedata.normalize("NFD", str(s).lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    return tuple(sorted(t for t in s.split() if t and t not in NOISE))


def nrm_name(s: str) -> str:
    """Normaliza um nome para comparacao 1:1 (sem acento/caixa)."""
    s = unicodedata.normalize("NFD", str(s).lower())
    return " ".join("".join(c for c in s if unicodedata.category(c) != "Mn").split())


def salva(p: str, data) -> None:
    """Grava JSON de forma atomica."""
    tmp = f"{p}.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    os.replace(tmp, p)


def main() -> None:
    """Ingesta acoes/produtos/canon da janela 2026-08-21."""
    actions = json.load(open(path("data/actions.json"), encoding="utf-8"))
    products = json.load(open(path("data/products.json"), encoding="utf-8"))
    canon = json.load(open(path("data/canon.json"), encoding="utf-8"))
    fila = json.load(open(path("data/fila_novos.json"), encoding="utf-8"))
    novo = json.load(open(path("_new_data.json"), encoding="utf-8"))

    byshort = {p["shortcode"]: p for p in fila}
    byid = {a["id"]: a for a in actions}
    new_products = novo["products"]

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

    def canon_add(name: str, unit: str, ref: str) -> None:
        """Adiciona ref ao grupo canonico do produto (ou cria grupo novo)."""
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

    n_act = n_prod = 0
    for spec in novo["actions"]:
        sid = spec["id"]
        if sid in byid:
            print(f"[pula] acao ja existe: {sid}")
            continue
        src = byshort.get(sid, {})
        act = {
            "id": sid,
            "perfil": spec.get("perfil") or src.get("perfil"),
            "titulo": spec["titulo"],
            "banner": spec["banner"],
            "segmento": spec["segmento"],
            "inicio": spec["inicio"],
            "fim": spec["fim"],
            "carrossel": spec.get("carrossel", src.get("carrossel", False)),
            "shortcode": sid,
            "caption": src.get("caption", spec.get("caption", "")),
            "adicionado_em": HOJE,
            "paginas": list(spec.get("paginas", src.get("paginas", []))),
        }
        if spec.get("fonte") or src.get("fonte"):
            act["fonte"] = spec.get("fonte") or src.get("fonte")
        if spec.get("link") or src.get("link"):
            act["link"] = spec.get("link") or src.get("link")
        actions.append(act)
        byid[sid] = act
        n_act += 1
        for fname in act["paginas"]:
            pid = fname[:-4] if fname.endswith(".jpg") else fname
            lista = new_products.get(pid, [])
            products[pid] = lista
            for i, p in enumerate(lista):
                n_prod += 1
                canon_add(p["n"], p.get("u", "un"), f"{pid}#{i}")

    print(f"{'DRY-RUN' if DRY_RUN else 'COMMIT'}: {n_act} acoes novas, {n_prod} produtos, "
          f"canon: {log['novos_canon']} grupos novos, {log['merges_canon']} merges, "
          f"{log['bloq_dif']} bloqueios DIFERENTES")

    if DRY_RUN:
        return
    stamp = HOJE.replace("-", "")
    for nome in ("actions.json", "products.json", "canon.json"):
        pth = path("data", nome)
        if os.path.exists(pth):
            shutil.copy2(pth, f"{pth}.bak-{stamp}-ingest")
    salva(path("data/actions.json"), actions)
    salva(path("data/products.json"), products)
    salva(path("data/canon.json"), canon)
    print("gravado.")


if __name__ == "__main__":
    main()
