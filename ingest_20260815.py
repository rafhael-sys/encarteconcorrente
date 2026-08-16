#!/usr/bin/env python3
"""Ingestao da janela de 2026-08-15 (analise diaria do Claude).

Adiciona as 5 acoes NOVAS decididas manualmente (classificacao/dedup ja feita
por leitura das imagens). Descartes desta janela nao entram.

canon: canonicalizacao por nrm_tokens (mesma logica de ingest_20260813.py);
NUNCA une pares marcados DIFERENTES em regras_similaridade.md.

DRY_RUN por padrao. Rode 'python3 ingest_20260815.py commit' p/ gravar.
"""
import json
import os
import re
import shutil
import sys
import unicodedata

BASE = os.path.dirname(os.path.abspath(__file__))
HOJE = "2026-08-15"
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


# --- Produtos por pagina (pagekey = nome do arquivo sem .jpg) ---
PRODUCTS = {
    # Rasga Preco RedeMAIS (14 a 17/08) - pagina unica
    "Db_vcVXynbw_p1": [
        {"n": "Coxa de Frango Resfriada", "p": "8,98", "u": "kg", "x": 15, "y": 36, "w": 25, "h": 22},
        {"n": "Filezinho Sassami Lar Envelopado", "p": "13,98", "u": "kg", "x": 38, "y": 35, "w": 30, "h": 25},
        {"n": "Linguiça de Frango Bom Todo", "p": "12,98", "u": "kg", "x": 62, "y": 37, "w": 33, "h": 25},
        {"n": "Salsicha Hot Dog Bom Todo", "p": "5,99", "u": "kg", "x": 16, "y": 56, "w": 30, "h": 26},
        {"n": "Capa de Filé Bovina", "p": "29,98", "u": "kg", "x": 42, "y": 60, "w": 26, "h": 26},
        {"n": "Carne Bovina Chã de Fora Resfriada", "p": "36,98", "u": "kg", "x": 64, "y": 57, "w": 33, "h": 25},
        {"n": "Peito de Frango OiFrango", "p": "10,98", "u": "kg", "x": 8, "y": 74, "w": 22, "h": 12},
        {"n": "Contra Filé Bovino", "p": "44,90", "u": "kg", "x": 30, "y": 74, "w": 22, "h": 12},
        {"n": "Coxinha da Asa de Frango Resfriada", "p": "11,98", "u": "kg", "x": 52, "y": 74, "w": 22, "h": 12},
        {"n": "Uva Vitória Luvvi 400g Sem Sementes Bandeja", "p": "5,89", "u": "cada", "x": 74, "y": 74, "w": 22, "h": 12},
        {"n": "Cerveja Devassa Lata 350ml", "p": "2,69", "u": "cada", "x": 6, "y": 86, "w": 22, "h": 12},
        {"n": "Refrigerante Guaraná Antarctica 2L", "p": "8,99", "u": "cada", "x": 28, "y": 86, "w": 22, "h": 12},
        {"n": "Cerveja Praya 330ml Long Neck", "p": "Leve 06 Pague 05", "u": "a unidade sai por R$ 5,57", "x": 50, "y": 86, "w": 24, "h": 12},
        {"n": "Pizza RedeMAIS", "p": "13,98", "u": "cada", "x": 74, "y": 86, "w": 22, "h": 12},
    ],
    # Favoritaco Gondola - Parnamirim e Macaiba (12 a 18/08)
    "DcD5UvHnENc_p1": [{"n": "Farinha Láctea Nestlé SH 160g Tradicional", "p": "5,49", "u": "cada (de R$ 6,99)", "x": 8, "y": 34, "w": 88, "h": 62}],
    "DcD5UvHnENc_p2": [{"n": "Biscoito Rosquinha Parati 250g (Sabor Chocolate)", "p": "3,99", "u": "cada (de R$ 5,59)", "x": 3, "y": 32, "w": 95, "h": 62}],
    "DcD5UvHnENc_p3": [{"n": "Desodorante Aerosol Nivea 150ml Derma Restaura", "p": "11,99", "u": "cada (de R$ 15,49) - Preço exclusivo Clube Favorito", "x": 3, "y": 20, "w": 95, "h": 68}],
    "DcD5UvHnENc_p4": [{"n": "Ovo Vermelho Ômega Avine c/20", "p": "12,99", "u": "cada (de R$ 17,99)", "x": 3, "y": 13, "w": 92, "h": 80}],
    "DcD5UvHnENc_p5": [{"n": "Lava Roupas Brilhante Bag 1,6kg Perfumada Poderosa", "p": "16,99", "u": "cada (de R$ 21,99)", "x": 3, "y": 28, "w": 95, "h": 68}],
    "DcD5UvHnENc_p6": [{"n": "Água Sanitária Dragão 1L", "p": "2,19", "u": "un", "x": 13, "y": 24, "w": 85, "h": 72}],
    # Favoritaco Gondola - Varejo Ponta Negra e Ayrton Senna (12 a 18/08)
    "DcBYm4OnESg_p1": [{"n": "Granola Tia Sônia Tradicional 200g", "p": "12,99", "u": "un (de R$ 17,99)", "x": 26, "y": 22, "w": 52, "h": 62}],
    "DcBYm4OnESg_p2": [{"n": "Azeite de Oliva Extra Virgem Condesa Antunes 500ml", "p": "27,99", "u": "cada (de R$ 42,99)", "x": 4, "y": 18, "w": 76, "h": 78}],
    "DcBYm4OnESg_p3": [{"n": "Molho de Tomate Passata NOR Foods 680g", "p": "11,99", "u": "cada (de R$ 14,99)", "x": 2, "y": 8, "w": 95, "h": 86}],
    "DcBYm4OnESg_p4": [{"n": "Leite Condensado Piracanjuba TP 395g", "p": "5,99", "u": "cada (de R$ 7,29)", "x": 28, "y": 8, "w": 50, "h": 72}],
    "DcBYm4OnESg_p5": [{"n": "Pão de Forma Bauducco Fermentação Natural 37% Integral 390g", "p": "4,99", "u": "cada (de R$ 11,49)", "x": 0, "y": 30, "w": 72, "h": 68}],
    # Atacado Favorito Ayrton Senna e Zona Norte - Fim de Semana (14 a 16/08)
    "DcDwqSNIDqX_p1": [],
    "DcDwqSNIDqX_p2": [{"n": "Cerveja Itaipava Lata 350ml", "p": "2,59", "u": "un", "x": 17, "y": 33, "w": 56, "h": 22}],
    "DcDwqSNIDqX_p3": [{"n": "Papel Higiênico Caprice Neutro 20m Folha Dupla", "p": "10,90", "u": "un", "x": 6, "y": 30, "w": 48, "h": 50}],
    "DcDwqSNIDqX_p4": [{"n": "Café Solúvel São Braz 40g Família ou Extra Forte", "p": "Leve 3 Pague 2", "u": "cada unidade sai R$ 3,86", "x": 5, "y": 52, "w": 86, "h": 26}],
    "DcDwqSNIDqX_p5": [{"n": "Whisky Chivas 1L 12 Anos", "p": "109,99", "u": "un", "x": 8, "y": 45, "w": 78, "h": 40}],
    "DcDwqSNIDqX_p6": [{"n": "Vassoura Condor V200 Madri Pop c/Cabo", "p": "8,99", "u": "un", "x": 47, "y": 30, "w": 51, "h": 68}],
    "DcDwqSNIDqX_p7": [{"n": "Refrigerante Guaraná Antarctica 350ml Zero", "p": "2,79", "u": "un", "x": 29, "y": 14, "w": 38, "h": 18}],
    "DcDwqSNIDqX_p8": [{"n": "Chocolate Nestlé Kit Kat 41,5g Sabores", "p": "3,99", "u": "un", "x": 12, "y": 57, "w": 45, "h": 34}],
    "DcDwqSNIDqX_p9": [],
    # Atacadao Boa do Dia (16/08) - web
    "atacadao_5d2fae043a_p1": [{"n": "Farinha Láctea Nestlé SH 160g Tradicional", "p": "5,49", "u": "cada (de R$ 6,99)", "x": 10, "y": 33, "w": 86, "h": 60}],
}

# --- Acoes NOVAS (metadados) ---
NEW_ACTIONS = [
    {"id": "Db_vcVXynbw", "titulo": "Rasga Preço RedeMAIS (14 a 17/08)",
     "banner": "Rede Mais", "segmento": "propria",
     "inicio": "2026-08-14", "fim": "2026-08-17"},
    {"id": "DcD5UvHnENc", "titulo": "Favoritaço Gôndola — Parnamirim e Macaíba (12 a 18/08)",
     "banner": "Favorito Super / Atacado Favorito", "segmento": "varejo",
     "inicio": "2026-08-12", "fim": "2026-08-18"},
    {"id": "DcBYm4OnESg", "titulo": "Favoritaço Gôndola — Varejo Ponta Negra e Ayrton Senna (12 a 18/08)",
     "banner": "Favorito Super / Atacado Favorito", "segmento": "varejo",
     "inicio": "2026-08-12", "fim": "2026-08-18"},
    {"id": "DcDwqSNIDqX", "titulo": "Atacado Favorito Ayrton Senna e Zona Norte — Fim de Semana (14 a 16/08)",
     "banner": "Favorito Super / Atacado Favorito", "segmento": "atacarejo",
     "inicio": "2026-08-14", "fim": "2026-08-16"},
    {"id": "atacadao_5d2fae043a", "titulo": "Boa do Dia (16/08)",
     "banner": "Atacadão", "segmento": "atacarejo",
     "inicio": "2026-08-16", "fim": "2026-08-16"},
]


def main():
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

    n_act = n_prod = 0
    for spec in NEW_ACTIONS:
        sid = spec["id"]
        if sid in byid:
            print(f"[pula] acao ja existe: {sid}")
            continue
        src = byshort.get(sid)
        if not src:
            print(f"[aviso] shortcode ausente na fila: {sid}")
            continue
        act = {
            "id": sid,
            "perfil": src.get("perfil"),
            "titulo": spec["titulo"],
            "banner": spec["banner"],
            "segmento": spec["segmento"],
            "inicio": spec["inicio"],
            "fim": spec["fim"],
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
        for fname in src.get("paginas", []):
            pid = fname[:-4] if fname.endswith(".jpg") else fname
            lista = PRODUCTS.get(pid, [])
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
