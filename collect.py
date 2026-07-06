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
    r'hortifr|sextou|sabadão|dia\s*show|terça|preço|economi|rasga|dia\s*d', re.I)


def sh(args, **kw):
    return subprocess.run(args, capture_output=True, text=True, timeout=60, **kw)


def load_json(path, default):
    """Tolerante a arquivo ausente ou corrompido (queda no meio da escrita)."""
    try:
        with open(path) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        if os.path.exists(path):
            print(f'[aviso] {path} corrompido; recomeçando desse arquivo', file=sys.stderr)
        return default


def save_json(path, data):
    """Escrita atômica: tmp + rename, nunca deixa JSON truncado."""
    tmp = f'{path}.tmp'
    with open(tmp, 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    os.replace(tmp, path)


def fetch_profile(username):
    r = sh(['curl', '-sk', '--compressed', '-A', UA,
            '-H', f'x-ig-app-id: {APP_ID}',
            f'https://i.instagram.com/api/v1/users/web_profile_info/?username={username}'])
    u = json.loads(r.stdout)['data']['user']
    if not u:
        raise ValueError('perfil indisponível (user=null: rate-limit, renomeado ou removido)')
    return u


def download(url, path):
    """True somente se baixou uma imagem plausível; nunca deixa lixo para trás."""
    try:
        sh(['curl', '-sk', '--compressed', '-A', UA,
            '-H', 'Accept: image/avif,image/webp,image/*,*/*;q=0.8',
            '-H', 'Referer: https://www.instagram.com/', '-o', path, url])
        if os.path.getsize(path) < 1024:
            raise ValueError('arquivo pequeno demais')
        with open(path, 'rb') as f:
            if f.read(20).lstrip().startswith(b'<'):
                raise ValueError('corpo HTML (erro do CDN)')
        return True
    except (OSError, ValueError, subprocess.SubprocessError):
        try:
            os.remove(path)
        except OSError:
            pass
        return False


def main():
    profiles = json.load(open(os.path.join(BASE, 'profiles.json')))
    seen_path = os.path.join(DATA, 'posts_vistos.json')
    fila_path = os.path.join(DATA, 'fila_novos.json')
    status_path = os.path.join(DATA, 'coleta_status.json')
    seen = set(load_json(seen_path, []))
    fila = load_json(fila_path, [])
    status = load_json(status_path, {})
    agora = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    novos = perfis_ok = 0

    for p in profiles:
        user = p['username']
        fonte = p.get('banner', user)
        try:
            u = fetch_profile(user)
        except Exception as e:
            print(f'[erro] {user}: {e}', file=sys.stderr)
            ent = status.get(fonte, {})
            ent['ultimo_erro'] = f'{agora}: {e}'
            status[fonte] = ent
            continue
        status[fonte] = {'ultima_coleta_ok': agora, 'ultimo_erro': None}
        perfis_ok += 1
        for e in u['edge_owner_to_timeline_media']['edges']:
            n = e['node']
            sc = n['shortcode']
            if sc in seen:
                continue
            cap_edges = n['edge_media_to_caption']['edges']
            cap = cap_edges[0]['node']['text'] if cap_edges else ''
            if n['__typename'] == 'GraphVideo' or not KEYWORDS.search(cap):
                seen.add(sc)
                continue
            kids = n.get('edge_sidecar_to_children', {}).get('edges')
            urls = ([k['node']['display_url'] for k in kids if not k['node'].get('is_video')]
                    if kids else [n['display_url']])
            if not urls:
                seen.add(sc)
                continue
            files = []
            for j, url in enumerate(urls):
                fn = f'{sc}_p{j+1}.jpg'
                if download(url, os.path.join(PAGES, fn)):
                    files.append(fn)
                time.sleep(0.5)
            if files:
                if len(files) < len(urls):
                    print(f'[aviso] {sc}: só {len(files)}/{len(urls)} páginas baixaram', file=sys.stderr)
                fila.append({
                    'shortcode': sc, 'perfil': user, 'banner': p['banner'],
                    'segmento': p['segmento'], 'caption': cap,
                    'taken_at': n['taken_at_timestamp'],
                    'carrossel': bool(kids), 'paginas': files,
                    'coletado_em': datetime.date.today().isoformat(),
                })
                novos += 1
                seen.add(sc)
            else:
                # nada baixou: NÃO marca como visto — tenta de novo na próxima execução
                print(f'[aviso] {sc}: nenhuma página baixada, fica para a próxima', file=sys.stderr)
        time.sleep(2)  # gentil com o Instagram

    save_json(seen_path, sorted(seen))
    save_json(fila_path, fila)
    save_json(status_path, status)
    print(f'{novos} posts novos candidatos a encarte na fila ({perfis_ok}/{len(profiles)} perfis lidos)')
    if perfis_ok == 0:
        sys.exit(1)  # falha total (provável rate-limit) — sinaliza para a rotina


if __name__ == '__main__':
    main()
