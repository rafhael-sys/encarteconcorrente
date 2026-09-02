#!/usr/bin/env python3
"""Merge da janela 2026-09-02: extrações -> actions.json / products.json / canon.json.

- Só ingere os shortcodes aprovados em ACTION_META (descartes ficam de fora):
  queiroz_565406bd4f (encarte velho de mar/2025, lojas Mossoró/Assú) e
  supershow_cb1f745eef (duplicata exata da ação DcriSVWj4E7) NÃO entram.
- b09397a8ec: fim corrigido para 07/09 (faixa impressa "02/09 A 07/09/2026";
  o JSON da fonte trouxe fim=02/09, artefato de coleta).
- Canon: procura grupo existente por nome exato, nome normalizado ou conjunto
  de tokens sem palavras de embalagem; respeita pares DIFERENTES das
  validações humanas (similaridade_decisoes.json). Nunca remove nada.
"""
import json
import os
import unicodedata

HOJE = "2026-09-02"
EXTRACT_DIR = "data/_extract/w0902"

# shortcode -> (titulo, inicio, fim, paginas_zeradas)
ACTION_META: dict[str, tuple[str, str, str, list[str]]] = {
    "assai_171164-572": ("Assaí — Ofertas (02 e 03/09)",
                         "2026-09-02", "2026-09-03", []),
    "atacadao_63182e38b6": ("Atacadão — Boa do Dia (02/09)",
                            "2026-09-02", "2026-09-02", []),
    "atacadao_06a8f44ac3": ("Atacadão — Super Ofertas (01 a 07/09)",
                            "2026-09-01", "2026-09-07", []),
    "atacadao_b09397a8ec": ("Atacadão — Super Ofertas Betânia (02 a 07/09)",
                            "2026-09-02", "2026-09-07", []),
    "atacadao_0ca3ad8ffb": ("Atacadão — Super Ofertas Danone (02 a 07/09)",
                            "2026-09-02", "2026-09-07", []),
    "atacadao_e765c34b02": ("Atacadão — Festival Perfumaria e Limpeza (01 a 10/09)",
                            "2026-09-01", "2026-09-10", []),
    "nosso_fcbfa134b4": ("Nosso Atacarejo — Nossa Quarta & Quinta (02 e 03/09)",
                         "2026-09-02", "2026-09-03", []),
    "nosso_7a203ffc72": ("Nosso Atacarejo — Encarte do Mês (01 a 14/09)",
                         "2026-09-01", "2026-09-14", []),
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
