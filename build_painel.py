#!/usr/bin/env python3
"""Gera painel-encartes.html a partir de data/actions.json + data/products.json + data/pages/*.jpg."""
import base64
import datetime
import json
import os
import subprocess
import sys
import tempfile

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, 'data')
PAGES = os.path.join(DATA, 'pages')

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
                # REGRA: vigentes sempre na melhor qualidade (resolução original, teto 1600px,
                # JPEG q62 — o zoom do painel precisa de nitidez); expirados recentes 800px/q45.
                # Nunca ampliar imagem menor que o teto (sips -Z também aumenta).
                vig = a['fim'] >= datetime.date.today().isoformat()
                zw, q = (1600, '62') if vig else (800, '45')
                g = subprocess.run(['sips', '-g', 'pixelWidth', '-g', 'pixelHeight', src],
                                   capture_output=True, text=True).stdout
                dims = [int(ln.split()[-1]) for ln in g.splitlines()
                        if ln.split() and ln.split()[-1].isdigit() and 'pixel' in ln]
                # sem dimensão legível -> não redimensiona, só recomprime (nunca derruba o build)
                lado_max = max(dims, default=0)
                small = os.path.join(tmp, fname)
                cmd = ['sips', '-s', 'format', 'jpeg', '-s', 'formatOptions', q,
                       src, '--out', small]
                if lado_max > zw:
                    cmd[1:1] = ['-Z', str(zw)]
                r = subprocess.run(cmd, capture_output=True)
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
html = html.replace('__UPDATED_ISO__', datetime.datetime.now().strftime('%Y-%m-%dT%H:%M'))

# engrenagem local: link e senha da publicação (o bloco inteiro é removido
# pelo gera_gate.py antes de subir, então nada disso vai para o site)
import html as _html
def _le(caminho):
    try:
        return open(os.path.expanduser(caminho), encoding='utf-8').read().strip()
    except OSError:
        return ''
url_pub = _le(f'{DATA}/netlify_url')
senha_pub = _le('~/.config/painel_senha')
html = html.replace('__PUB_URL__', _html.escape(url_pub) or 'ainda não publicado')
html = html.replace('__PUB_SENHA__', _html.escape(senha_pub) or 'sem senha definida')

out = f'{BASE}/painel-encartes.html'
# escrita atômica: quem ler o arquivo (ex.: publicação do meio-dia) nunca vê
# uma versão truncada no meio da gravação dos ~40 MB
tmp_out = f'{out}.tmp'
open(tmp_out, 'w', encoding='utf-8').write(html)
os.replace(tmp_out, out)
print(f'{out} — {os.path.getsize(out)/1024/1024:.2f} MB, {n_products} produtos, {len(data_actions)} encartes')
