#!/usr/bin/env python3
"""Coleta diária de encartes dos concorrentes no Instagram (perfis públicos, sem login).

Passos: para cada perfil em profiles.json, busca os 12 posts mais recentes via
endpoint web público, identifica candidatos a encarte pela legenda, baixa as
imagens novas em data/pages/ e registra os posts novos em data/fila_novos.json
para o passo de extração (Claude) classificar e indexar os produtos.
"""
import json
import os
import random
import re
import subprocess
import sys
import time
import datetime

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, 'data')
PAGES = os.path.join(DATA, 'pages')
os.makedirs(PAGES, exist_ok=True)

UA = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/126.0 Safari/537.36')
APP_ID = '936619743392459'

# Cookie de sessão logada (opcional): a requisição AUTENTICADA tem limite muito
# maior que a anônima — some quase sempre com o erro 'data'/rate-limit. Vem de
# ~/.config/ig_cookie ou da variável IG_COOKIE. Aceita o cookie completo
# ("sessionid=...; ds_user_id=...") ou só o valor do sessionid. Sem cookie,
# segue anônimo (comportamento antigo).
def _carrega_cookie():
    c = (os.environ.get('IG_COOKIE') or '').strip()
    if not c:
        try:
            c = open(os.path.expanduser('~/.config/ig_cookie'), encoding='utf-8').read().strip()
        except OSError:
            c = ''
    if c and '=' not in c:            # colaram só o valor do sessionid
        c = f'sessionid={c}'
    return c
COOKIE = _carrega_cookie()

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


def fetch_profile(username, tentativas=4):
    # resposta inválida (sem 'data', ou user=null) é quase sempre estrangulamento
    # passageiro do Instagram — comum quando o Mac acorda e dispara os 11 perfis
    # de uma vez. Re-tenta com espera exponencial + jitter (~4-8s, 8-12s, 16-20s)
    # deixar o rate-limit passar antes de desistir do perfil.
    ultimo = None
    for t in range(1, tentativas + 1):
        try:
            cmd = ['curl', '-sk', '--compressed', '-A', UA,
                   '-H', f'x-ig-app-id: {APP_ID}']
            if COOKIE:
                cmd += ['-H', f'Cookie: {COOKIE}']
            cmd.append(f'https://i.instagram.com/api/v1/users/web_profile_info/?username={username}')
            r = sh(cmd)
            if not r.stdout.strip():
                # corpo vazio = bloqueio/estrangulamento do Instagram (a mensagem
                # crua do json seria um "Expecting value" indecifrável no log)
                raise ValueError(f'resposta vazia do Instagram (curl código {r.returncode})')
            u = json.loads(r.stdout)['data']['user']
            if not u:
                # user=null é o formato clássico de rate-limit — também re-tenta
                raise ValueError('perfil indisponível (user=null: rate-limit, renomeado ou removido)')
            return u
        except (json.JSONDecodeError, KeyError, TypeError, ValueError, subprocess.SubprocessError) as e:
            ultimo = e
            if t == tentativas:
                raise
            time.sleep(min(30, 4 * 2 ** (t - 1)) + random.uniform(0, 4))
    raise ultimo  # inalcançável, mas mantém o tipo de erro explícito


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


def best_url(node):
    # regra: sempre a imagem de maior resolução disponível
    res = node.get('display_resources') or []
    res = [r for r in res if r.get('src')]
    if res:
        return max(res, key=lambda r: r.get('config_width', 0))['src']
    return node.get('display_url')


def processa_perfil(p, seen, fila, status, agora):
    """Coleta um perfil. Devolve (ok, novos). ok=False só em falha de rede/IG
    ou resposta malformada (o perfil entra na fila de re-tentativa); qualquer
    post problemático é apenas pulado sem derrubar o perfil nem a coleta toda."""
    user = p['username']
    fonte = p.get('banner', user)
    try:
        u = fetch_profile(user)
        edges = u['edge_owner_to_timeline_media']['edges']
    except Exception as e:
        # inclui o caso raro de o IG devolver 200 com um 'user' sem os campos
        # esperados: tratamos como falha do perfil (re-tenta), nunca como crash
        print(f'[erro] {user}: {e}', file=sys.stderr)
        ent = status.get(fonte, {})
        ent['ultimo_erro'] = f'{agora}: {e}'
        status[fonte] = ent
        return False, 0
    status[fonte] = {'ultima_coleta_ok': agora, 'ultimo_erro': None}
    novos = 0
    for e in edges:
        try:
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
            urls = ([best_url(k['node']) for k in kids if not k['node'].get('is_video')]
                    if kids else [best_url(n)])
            urls = [x for x in urls if x]
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
                item = {
                    'shortcode': sc, 'perfil': user, 'banner': p['banner'],
                    'segmento': p['segmento'], 'caption': cap,
                    'taken_at': n['taken_at_timestamp'],
                    'carrossel': bool(kids), 'paginas': files,
                    'coletado_em': datetime.date.today().isoformat(),
                }
                # regra opcional do perfil (ex.: SuperFácil ignora ofertas de
                # João Pessoa/PB) — vai junto para a análise decidir descartar.
                if p.get('regra'):
                    item['regra'] = p['regra']
                fila.append(item)
                novos += 1
                seen.add(sc)
            else:
                # nada baixou: NÃO marca como visto — tenta de novo na próxima execução
                print(f'[aviso] {sc}: nenhuma página baixada, fica para a próxima', file=sys.stderr)
        except Exception as ex:
            # um post com formato inesperado é pulado sem derrubar o perfil
            print(f'[aviso] {user}: post ignorado por formato inesperado ({ex})', file=sys.stderr)
            continue
    return True, novos


def main():
    profiles = json.load(open(os.path.join(BASE, 'profiles.json')))
    seen_path = os.path.join(DATA, 'posts_vistos.json')
    fila_path = os.path.join(DATA, 'fila_novos.json')
    status_path = os.path.join(DATA, 'coleta_status.json')
    seen = set(load_json(seen_path, []))
    fila = load_json(fila_path, [])
    status = load_json(status_path, {})
    agora = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    novos = 0

    # Coleta em rodadas: quem falha por estrangulamento do Instagram volta para
    # a fila e é re-tentado após um descanso maior, em vez de ficar de fora até
    # a próxima janela (3h). Assim uma queda passageira não perde o perfil.
    ok_final = {}  # username -> conseguiu em alguma rodada?
    pendentes = list(profiles)
    RODADAS = 2
    for rodada in range(1, RODADAS + 1):
        falhados = []
        random.shuffle(pendentes)  # ordem variada a cada rodada: menos cara de robô
        for p in pendentes:
            ok, n = processa_perfil(p, seen, fila, status, agora)
            novos += n
            ok_final[p['username']] = ok_final.get(p['username'], False) or ok
            if not ok:
                falhados.append(p)
            time.sleep(random.uniform(7, 14))  # ritmo moderado (~2-4 min p/ os 16 perfis)
        # persiste o progresso a cada rodada: uma interrupção não perde o que já veio
        save_json(seen_path, sorted(seen))
        save_json(fila_path, fila)
        save_json(status_path, status)
        if not falhados:
            break
        if rodada < RODADAS:
            nomes = ', '.join(pp['username'] for pp in falhados)
            print(f'[info] {len(falhados)} perfil(is) falharam nesta rodada; '
                  f'nova tentativa em 60s ({nomes})', file=sys.stderr)
            time.sleep(60)  # descanso deixa o rate-limit do Instagram passar
        pendentes = falhados

    perfis_ok = sum(1 for v in ok_final.values() if v)
    ainda_falhos = [u for u, v in ok_final.items() if not v]
    if ainda_falhos:
        print(f'[erro] mesmo após {RODADAS} rodadas seguem sem coletar: '
              f'{", ".join(ainda_falhos)}', file=sys.stderr)
    print(f'{novos} posts novos candidatos a encarte na fila ({perfis_ok}/{len(profiles)} perfis lidos)')
    if perfis_ok == 0:
        sys.exit(1)  # falha total (provável rate-limit) — sinaliza para a rotina


if __name__ == '__main__':
    main()
