#!/usr/bin/env python3
"""Coleta diária de encartes dos concorrentes no Instagram (perfis públicos, sem login).

Passos: para cada perfil em profiles.json, busca os 12 posts mais recentes via
endpoint web público, identifica candidatos a encarte pela legenda, baixa as
imagens novas em data/pages/ e registra os posts novos em data/fila_novos.json
para o passo de extração (Claude) classificar e indexar os produtos.
"""
import json, os, re, subprocess, sys, time, datetime

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, 'data')
PAGES = os.path.join(DATA, 'pages')
os.makedirs(PAGES, exist_ok=True)

UA = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/126.0 Safari/537.36')
APP_ID = '936619743392459'

# legenda que sugere ação de encarte/oferta com produto
KEYWORDS = re.compile(
    r'encarte|oferta|ofertaço|promoç|válid[ao]s?\s|feirão|festival|fecha\s*m[êe]s|'
    r'hortifr|sextou|sabadão|dia\s*show|terça|preço|economi', re.I)

def sh(args, **kw):
    return subprocess.run(args, capture_output=True, text=True, timeout=60, **kw)

def fetch_profile(username):
    r = sh(['curl', '-sk', '--compressed', '-A', UA,
            '-H', f'x-ig-app-id: {APP_ID}',
            f'https://i.instagram.com/api/v1/users/web_profile_info/?username={username}'])
    d = json.loads(r.stdout)
    return d['data']['user']

def download(url, path):
    sh(['curl', '-sk', '--compressed', '-A', UA,
        '-H', 'Accept: image/avif,image/webp,image/*,*/*;q=0.8',
        '-H', 'Referer: https://www.instagram.com/', '-o', path, url])
    with open(path, 'rb') as f:
        ok = not f.read(20).lstrip().startswith(b'<')
    if not ok:
        os.remove(path)
    return ok

def main():
    profiles = json.load(open(os.path.join(BASE, 'profiles.json')))
    seen_path = os.path.join(DATA, 'posts_vistos.json')
    seen = set(json.load(open(seen_path))) if os.path.exists(seen_path) else set()
    fila_path = os.path.join(DATA, 'fila_novos.json')
    fila = json.load(open(fila_path)) if os.path.exists(fila_path) else []
    novos = 0

    for p in profiles:
        user = p['username']
        try:
            u = fetch_profile(user)
        except Exception as e:
            print(f'[erro] {user}: {e}', file=sys.stderr)
            continue
        for e in u['edge_owner_to_timeline_media']['edges']:
            n = e['node']
            sc = n['shortcode']
            if sc in seen or n['__typename'] == 'GraphVideo':
                continue
            cap_edges = n['edge_media_to_caption']['edges']
            cap = cap_edges[0]['node']['text'] if cap_edges else ''
            if not KEYWORDS.search(cap):
                seen.add(sc)
                continue
            kids = n.get('edge_sidecar_to_children', {}).get('edges')
            urls = ([k['node']['display_url'] for k in kids if not k['node'].get('is_video')]
                    if kids else [n['display_url']])
            files = []
            for j, url in enumerate(urls):
                fn = f'{sc}_p{j+1}.jpg'
                if download(url, os.path.join(PAGES, fn)):
                    files.append(fn)
                time.sleep(0.5)
            if files:
                fila.append({
                    'shortcode': sc, 'perfil': user, 'banner': p['banner'],
                    'segmento': p['segmento'], 'caption': cap,
                    'taken_at': n['taken_at_timestamp'],
                    'carrossel': bool(kids), 'paginas': files,
                    'coletado_em': datetime.date.today().isoformat(),
                })
                novos += 1
            seen.add(sc)
        time.sleep(2)  # gentil com o Instagram

    json.dump(sorted(seen), open(seen_path, 'w'))
    json.dump(fila, open(fila_path, 'w'), ensure_ascii=False, indent=1)
    print(f'{novos} posts novos candidatos a encarte na fila')

if __name__ == '__main__':
    main()
