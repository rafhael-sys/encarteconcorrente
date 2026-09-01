#!/usr/bin/env python3
"""Merge da janela 2026-09-01: extrações -> actions.json / products.json / canon.json.

- Só ingere os shortcodes aprovados em ACTION_META (descartes ficam de fora).
- Canon: procura grupo existente por nome exato, nome normalizado ou conjunto
  de tokens sem palavras de embalagem; respeita pares DIFERENTES das
  validações humanas (similaridade_decisoes.json). Nunca remove nada.
"""
import json
import os
import unicodedata

HOJE = "2026-09-01"
EXTRACT_DIR = "data/_extract/w0901"

# shortcode -> (titulo, inicio, fim, paginas_zeradas)
ACTION_META: dict[str, tuple[str, str, str, list[str]]] = {
    "DcriSVWj4E7": ("Aniversário 21 anos Super Show — encarte 31/08 a 03/09",
                    "2026-08-31", "2026-09-03", []),
    "DcuHEEEjwZ3": ("Terça Show de Aniversário — Açougue e Congelados (01/09)",
                    "2026-09-01", "2026-09-01", []),
    "Dcme_Z9oExB": ("Encarte Supercop (29/08 a 02/09)",
                    "2026-08-29", "2026-09-02", []),
    "DchVYErkj0q": ("Fecha Mês Supercop (27 e 28/08)",
                    "2026-08-27", "2026-08-28", ["DchVYErkj0q_p1"]),
    "DchUObMFh_Z": ("Quinta Verde Supercop (27/08)",
                    "2026-08-27", "2026-08-27", []),
    "DcrpGk-DHcf": ("Dia D+ RedeMAIS 26 Anos (31/08 e 01/09)",
                    "2026-08-31", "2026-09-01", []),
    "Dcj6tF0DFu4": ("Rasga Preço RedeMAIS (28 a 30/08)",
                    "2026-08-28", "2026-08-30", []),
    "DcgFBmZyiMg": ("Feirão do Hortifruti Leva Mais (26 e 27/08)",
                    "2026-08-26", "2026-08-27", []),
    "DchWYETIFog": ("Rasga Preço Santo Antônio (27 e 28/08)",
                    "2026-08-27", "2026-08-28", []),
    "DcrzdcCoFfE": ("Fecha Mês Santo Antônio — apenas 31/08",
                    "2026-08-31", "2026-08-31", []),
    "DcmaaO7Gsqe": ("Aniversário 35 Anos Queiroz — 1º encarte (29/08 a 02/09)",
                    "2026-08-29", "2026-09-02", []),
    "DchGt8zEk2h": ("Dia Q Queiroz (27 e 28/08)",
                    "2026-08-27", "2026-08-28", []),
    "DchDGXIErij": ("Hortifruti Queiroz (27 e 28/08)",
                    "2026-08-27", "2026-08-28", []),
    "DcmanVTH2KW": ("Aniversário 35 Anos Queiroz — 1º encarte (29/08 a 02/09)",
                    "2026-08-29", "2026-09-02", []),
    "DchDJhvnxZQ": ("Hortifruti Queiroz (27 e 28/08)",
                    "2026-08-27", "2026-08-28", []),
    "assai_170665-572": ("Assaí — Ofertas da semana (31/08 a 03/09)",
                         "2026-08-31", "2026-09-03", []),
    "assai_170679-572": ("Assaí — Ofertas (31/08 a 04/09)",
                         "2026-08-31", "2026-09-04", []),
    "assai_170719-572": ("Assaí — Ofertas (01 a 13/09)",
                         "2026-09-01", "2026-09-13", []),
    "atacadao_0b70eb111e": ("Atacadão — Boa do Dia (31/08)",
                            "2026-08-31", "2026-08-31", []),
    "atacadao_0e7895a02b": ("Atacadão — Super Ofertas (01 a 07/09)",
                            "2026-09-01", "2026-09-07", []),
    "atacadao_aba86d1eb4": ("Atacadão — Açougue, Padaria e Frios (01 a 03/09)",
                            "2026-09-01", "2026-09-03", []),
    "atacadao_53752fa680": ("Atacadão — Hortifrúti (01 a 03/09)",
                            "2026-09-01", "2026-09-03", []),
}

NOISE = {
    "lata", "lta", "pct", "pet", "tb", "gf", "cada", "un", "und", "unid",
    "sabores", "sabor", "fragrancias", "fragrancia", "tipos", "pacote",
    "com", "embalagem", "sc", "cx", "bdj", "bd", "vd", "fd", "frasco",
    "garrafa", "unidade", "unidades", "c", "kg", "peca", "pedaco",
}


def nrm(s: str) -> str:
    """Normaliza: minúsculas, sem acento, espaços únicos."""
    s = unicodedata.normalize("NFD", str(s).lower())
    return " ".join("".join(c for c in s if unicodedata.category(c) != "Mn").split())


def chave_par(a: str, b: str) -> str:
    """Chave canônica de um par de nomes (mesma regra do aplica_validacoes)."""
    return " || ".join(sorted([nrm(a), nrm(b)]))


def tokens(s: str) -> frozenset:
    """Conjunto de tokens sem palavras de embalagem/ruído."""
    t = nrm(s)
    for ch in "()/,.;:!?+*":
        t = t.replace(ch, " ")
    t = t.replace("-", " ")
    return frozenset(w for w in t.split() if w not in NOISE)


def main() -> None:
    """Faz o merge das extrações aprovadas nos três arquivos de dados."""
    fila = json.load(open("data/fila_novos.json"))
    por_sc = {p["shortcode"]: p for p in fila}
    actions = json.load(open("data/actions.json"))
    products = json.load(open("data/products.json"))
    canon = json.load(open("data/canon.json"))
    try:
        decisoes = json.load(open("data/similaridade_decisoes.json"))
    except FileNotFoundError:
        decisoes = {}

    ids_existentes = {a["id"] for a in actions}

    # índices do canon
    exato = {c["n"]: c for c in canon}
    por_nrm: dict[str, dict] = {}
    por_tok: dict[frozenset, dict] = {}
    for c in canon:
        por_nrm.setdefault(nrm(c["n"]), c)
        por_tok.setdefault(tokens(c["n"]), c)

    def eh_diferente(a: str, b: str) -> bool:
        d = decisoes.get(chave_par(a, b))
        return bool(d) and d["veredito"] == "diferente"

    def acha_grupo(nome: str):
        g = exato.get(nome) or por_nrm.get(nrm(nome))
        if g:
            return g
        g = por_tok.get(tokens(nome))
        if g and not eh_diferente(nome, g["n"]):
            return g
        return None

    novas_acoes = 0
    novos_produtos = 0
    grupos_novos = 0
    reaproveitados = 0

    for sc, (titulo, inicio, fim, zerar) in ACTION_META.items():
        if sc in ids_existentes:
            print(f"[pula] {sc} já existe em actions.json")
            continue
        post = por_sc.get(sc)
        extr_path = os.path.join(EXTRACT_DIR, f"{sc}.json")
        if not post or not os.path.exists(extr_path):
            print(f"[ERRO] {sc}: post na fila? {bool(post)} extract? "
                  f"{os.path.exists(extr_path)} — pulado")
            continue
        extr = json.load(open(extr_path))

        acao = {
            "id": sc,
            "perfil": post["perfil"],
            "titulo": titulo,
            "banner": post["banner"],
            "segmento": post["segmento"],
            "inicio": inicio,
            "fim": fim,
            "carrossel": post.get("carrossel", False),
            "shortcode": sc,
            "caption": post.get("caption", ""),
            "adicionado_em": HOJE,
            "paginas": post["paginas"],
        }
        if post.get("fonte") == "web":
            acao["fonte"] = "web"
            acao["link"] = post.get("link", "")
        actions.append(acao)
        novas_acoes += 1

        for pagina in post["paginas"]:
            chave = pagina.rsplit(".", 1)[0]
            itens = extr.get("paginas", {}).get(chave, [])
            if chave in zerar:
                itens = []
            if chave in products and products[chave]:
                print(f"[aviso] {chave} já tinha {len(products[chave])} "
                      f"produtos — mantido, extração ignorada")
                continue
            products[chave] = itens
            for i, prod in enumerate(itens):
                ref = f"{chave}#{i}"
                unidade = "kg" if str(prod.get("u", "")).startswith("kg") else "un"
                g = acha_grupo(prod["n"])
                if g:
                    if ref not in g["m"]:
                        g["m"].append(ref)
                    reaproveitados += 1
                else:
                    novo = {"n": prod["n"], "u": unidade, "m": [ref]}
                    canon.append(novo)
                    exato[novo["n"]] = novo
                    por_nrm.setdefault(nrm(novo["n"]), novo)
                    por_tok.setdefault(tokens(novo["n"]), novo)
                    grupos_novos += 1
                novos_produtos += 1

    for path, data in (("data/actions.json", actions),
                       ("data/products.json", products),
                       ("data/canon.json", canon)):
        tmp = f"{path}.tmp"
        with open(tmp, "w") as f:
            json.dump(data, f, ensure_ascii=False, indent=1)
        os.replace(tmp, path)

    print(f"[ok] {novas_acoes} ações novas | {novos_produtos} produtos | "
          f"{reaproveitados} em grupos existentes | {grupos_novos} grupos novos "
          f"| canon total {len(canon)}")


if __name__ == "__main__":
    main()
