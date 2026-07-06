#!/usr/bin/env python3
"""Gera painel-encartes.html a partir de data/actions.json + data/products.json + data/pages/*.jpg."""
import json, os, base64, subprocess, tempfile

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, 'data')
PAGES = os.path.join(DATA, 'pages')

import sys
if not (os.path.exists(f'{DATA}/actions.json') and os.path.exists(f'{DATA}/products.json')):
    print('nada para construir ainda (actions.json/products.json ausentes)')
    sys.exit(0)
actions = json.load(open(f'{DATA}/actions.json'))
products = json.load(open(f'{DATA}/products.json'))
canon = json.load(open(f'{DATA}/canon.json')) if os.path.exists(f'{DATA}/canon.json') else None
if canon is None:
    canon = [{'n': p['n'], 'u': p.get('u',''), 'm': [f'{pid}#{i}']}
             for pid, ps in products.items() for i, p in enumerate(ps)]

seg_rank = {'propria': 0, 'varejo': 1, 'atacarejo': 2}
actions.sort(key=lambda a: (seg_rank.get(a['segmento'], 2), a['banner'], a['inicio']))

import datetime
# incidência acumula para sempre, mas só embute imagens dos encartes recentes
# (mais antigos continuam no ranking; o clique abre o post no Instagram)
JANELA_IMAGENS_DIAS = 14
corte = (datetime.date.today() - datetime.timedelta(days=JANELA_IMAGENS_DIAS)).isoformat()

data_actions, images = [], {}
with tempfile.TemporaryDirectory() as tmp:
    for a in actions:
        embutir = a['fim'] >= corte
        page_ids = []
        for i, fname in enumerate(a['paginas']):
            pid = f"{a['id']}_p{i+1}" if not fname.startswith(a['id']) else fname.replace('.jpg', '')
            src = os.path.join(PAGES, fname)
            if not os.path.exists(src):
                continue
            if embutir:
                # vigentes em alta; expirados recentes em qualidade média (histórico)
                vig = a['fim'] >= datetime.date.today().isoformat()
                zw, q = ('940', '42') if vig else ('560', '38')
                small = os.path.join(tmp, fname)
                r = subprocess.run(['sips', '-Z', zw, '-s', 'format', 'jpeg',
                                    '-s', 'formatOptions', q, src, '--out', small],
                                   capture_output=True)
                if r.returncode == 0 and os.path.exists(small):
                    images[pid] = 'data:image/jpeg;base64,' + base64.b64encode(open(small, 'rb').read()).decode()
                else:
                    print(f'[aviso] sips falhou em {fname}; página fica sem imagem embutida', file=sys.stderr)
            page_ids.append(pid)
        if page_ids:
            data_actions.append({'id': a['id'], 'banner': a['banner'], 'perfil': a['perfil'],
                                 'titulo': a['titulo'], 'seg': a['segmento'], 'ini': a['inicio'],
                                 'fim': a['fim'], 'sc': a['shortcode'], 'pgs': page_ids,
                                 'add': a.get('adicionado_em', ''),
                                 'lk': a.get('link', '')})

n_products = sum(len(products.get(p, [])) for a in data_actions for p in a['pgs'])
import datetime
html = open(f'{BASE}/painel_template.html', encoding='utf-8').read()
html = html.replace('__ACTIONS__', json.dumps(data_actions, ensure_ascii=False))
html = html.replace('__PRODUCTS__', json.dumps(products, ensure_ascii=False))
html = html.replace('__IMAGES__', json.dumps(images))
html = html.replace('__CANON__', json.dumps(canon, ensure_ascii=False))
fontes = {}
if os.path.exists(f'{DATA}/coleta_status.json'):
    try:
        fontes = json.load(open(f'{DATA}/coleta_status.json'))
    except Exception:
        fontes = {}
html = html.replace('__FONTES__', json.dumps(fontes, ensure_ascii=False))
html = html.replace('__NPROD__', str(n_products))
html = html.replace('__NPAG__', str(len(images)))
html = html.replace('__GENDATE__', datetime.date.today().strftime('%d/%m/%Y'))
html = html.replace('__UPDATED__', datetime.datetime.now().strftime('%d/%m às %H:%M'))

out = f'{BASE}/painel-encartes.html'
open(out, 'w', encoding='utf-8').write(html)
print(f'{out} — {os.path.getsize(out)/1024/1024:.2f} MB, {n_products} produtos, {len(data_actions)} encartes')
