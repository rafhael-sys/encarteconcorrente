import glob
import json
import os
import re

BASE = '/Users/teste/encarteconcorrente'
fila = json.load(open(os.path.join(BASE, 'data/fila_novos.json'), encoding='utf-8'))
byshort = {p['shortcode']: p for p in fila}

for fp in sorted(glob.glob(os.path.join(BASE, 'data/_extract/w0826_*.json'))):
    bn = os.path.basename(fp)
    if bn.startswith('w0826_sim_'):
        continue
    try:
        ext = json.load(open(fp, encoding='utf-8'))
    except Exception as e:
        print(f'{bn}: ERRO JSON {e}')
        continue
    sc = ext.get('shortcode')
    src = byshort.get(sc)
    probs = []
    if src is None:
        probs.append('shortcode fora da fila')
    else:
        esperadas = set(p[:-4] for p in src['paginas'])
        chaves = set(ext.get('pages', {}).keys())
        if not ext.get('discard') and chaves != esperadas:
            probs.append(f'paginas divergem: faltam {esperadas-chaves}, sobram {chaves-esperadas}')
    npr = 0
    for pid, lista in ext.get('pages', {}).items():
        for it in lista:
            npr += 1
            if not re.match(r'^\d+,\d{2}$', str(it.get('p', ''))):
                probs.append(f'preco estranho em {pid}: {it.get("n","?")[:30]} p={it.get("p")!r}')
            for c in ('x', 'y', 'w', 'h'):
                v = it.get(c)
                if not isinstance(v, (int, float)) or v < 0 or v > 100:
                    probs.append(f'coord {c} invalida em {pid}: {it.get("n","?")[:30]} {c}={v!r}')
    d = ' DISCARD:' + ext.get('discard_reason', '') if ext.get('discard') else ''
    ini, fim = ext.get('inicio'), ext.get('fim')
    print(f'{bn}: {npr} prods, {len(ext.get("pages", {}))} pags, {ini}..{fim}{d}')
    for p in probs[:6]:
        print('   !', p)
