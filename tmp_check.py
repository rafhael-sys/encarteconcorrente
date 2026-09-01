"""Verifica se os produtos dos cartazes DcqTKGjFnWL ja estao no encarte DceqP_AD7K_."""
import json
import unicodedata


def nrm(s: str) -> str:
    """Normaliza nome para comparacao tolerante."""
    s = unicodedata.normalize('NFD', str(s).lower())
    return ' '.join(''.join(c for c in s if unicodedata.category(c) != 'Mn').split())


prods = json.load(open('data/products.json'))

flyer = []
for i in range(1, 8):
    flyer += prods.get(f'DceqP_AD7K__p{i}', [])

novos = [
    ("Filé de Peito de Frango Levo 1kg (Bandeja)", "15,99"),
    ("Massa Galo 400g (Parafuso)", "1,99"),
    ("Leite em Pó Aurora 750g (Integral)", "23,99"),
    ("Flocão de Milho Fortemilho 400g", "0,89"),
    ("Coxa de Frango Sadia IQF 1kg (Congelada)", "10,99"),
    ("Papel Higiênico Felitá Care 20mts c/12 Folha Dupla Neutro", "8,99"),
    ("Leite UHT Betânia ou Triângulo Mineiro 1L (Desnatado ou Integral)", "5,99"),
    ("Desodorante Aerossol Rexona 150ml (Fragrâncias)", "13,49"),
    ("Fraldas Descartáveis Cremer Shortinho Jumbo (Tamanhos)", "22,99"),
    ("Feijão Precioso 1kg (Preto)", "5,49"),
]

STOP = {'de', 'da', 'do', 'com', 'c/', 'e', 'ou', '-', 'em'}
for nome, preco in novos:
    toks = {t for t in nrm(nome).replace('(', ' ').replace(')', ' ').split() if t not in STOP}
    best = None
    best_score = 0.0
    for f in flyer:
        ftoks = {t for t in nrm(f['n']).replace('(', ' ').replace(')', ' ').split() if t not in STOP}
        if not toks or not ftoks:
            continue
        score = len(toks & ftoks) / len(toks | ftoks)
        if score > best_score:
            best_score, best = score, f
    ok = best and best['p'] == preco and best_score >= 0.4
    print(f"{'JA NO FLYER' if ok else 'NAO ACHOU '} | {nome} @{preco} -> "
          f"{best['n'] if best else '-'} @{best['p'] if best else '-'} (score {best_score:.2f})")
