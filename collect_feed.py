#!/usr/bin/env python3
"""Coleta o feed dos perfis pelo endpoint AUTENTICADO feed/user/{id} (com cookie).

Contorna o bug intermitente do endpoint web_profile_info (erro de schema
"ig_business_category_subvertical"). Reaproveita helpers do collect.py
(download, KEYWORDS, fila/seen/status). Precisa do cookie em ~/.config/ig_cookie.

O user_id de cada perfil é obtido da página HTML (uma vez) e guardado em
data/ig_user_ids.json para as próximas execuções.
"""
from __future__ import annotations

import datetime
import json
import os
import random
import re
import subprocess
import sys
import time

import collect  # download, KEYWORDS, PAGES, save_json, load_json, UA, APP_ID, COOKIE

DATA = collect.DATA
UIDS_PATH = os.path.join(DATA, 'ig_user_ids.json')
UA_WEB = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 '
          '(KHTML, like Gecko) Version/17.0 Safari/605.1.15')


class RateLimit(Exception):
    """O Instagram pediu para esperar ('Please wait a few minutes'). Não é para
    re-tentar na hora — martelar só prolonga o bloqueio; o certo é aguardar."""


def carrega_contas() -> list[str]:
    """Cookies das contas de coleta, para dividir a carga e não estourar o
    rate-limit do IG. IG_COOKIE (env) força CONTA ÚNICA (runs manuais); senão usa
    ~/.config/ig_cookie e ~/.config/ig_cookie_2 (as que existirem). Cada valor já
    vem no formato de header ('sessionid=...')."""
    env = (os.environ.get('IG_COOKIE') or '').strip()
    if env:
        return [env if '=' in env else f'sessionid={env}']
    contas = []
    for nome in ('ig_cookie', 'ig_cookie_2'):
        try:
            c = open(os.path.expanduser(f'~/.config/{nome}'), encoding='utf-8').read().strip()
        except OSError:
            continue
        if c:
            contas.append(c if '=' in c else f'sessionid={c}')
    return contas


def _sh(args: list[str]) -> str:
    """Roda um curl e devolve stdout (texto), com timeout curto."""
    if collect.PROXY and '--proxy' not in args and '-x' not in args:
        if args and args[0] == 'curl':
            args = [args[0], '--proxy', collect.PROXY] + args[1:]
    return subprocess.run(args, capture_output=True, text=True, timeout=40).stdout


def get_user_id(username: str, cache: dict[str, str]) -> str | None:
    """Devolve o user_id numérico do perfil, do cache ou raspando o HTML.

    Args:
        username: @ do perfil (ex.: 'redemaisrn').
        cache: dicionário username -> user_id já conhecido (é atualizado).

    Returns:
        O user_id como string, ou None se não achou.
    """
    if username in cache:
        return cache[username]
    html = _sh(['curl', '-sL', '--compressed', '-A', UA_WEB,
                '-H', f'Cookie: {collect.COOKIE}',
                f'https://www.instagram.com/{username}/'])
    for pat in (r'"profile_id":"(\d+)"', r'"user_id":"(\d+)"',
                r'instagram://user\?username=[^&]+&id=(\d+)',
                r'"props":\{"id":"(\d+)"', r'\\"user_id\\":\\"(\d+)\\"'):
        m = re.search(pat, html)
        if m:
            cache[username] = m.group(1)
            return m.group(1)
    return None


def fetch_feed(user_id: str, cookie: str, count: int = 12) -> list[dict]:
    """Busca os posts recentes pelo endpoint autenticado feed/user/{id}.

    Args:
        user_id: id numérico do perfil.
        cookie: cookie da conta a usar (header 'sessionid=...').
        count: quantos posts recentes pedir.

    Returns:
        Lista de items (formato da API v1). Vazia se a resposta não trouxe items.

    Raises:
        RateLimit: o IG pediu para esperar ('Please wait a few minutes').
        ValueError: resposta vazia ou sem 'items' (outro erro/cookie inválido).
    """
    body = _sh(['curl', '-sk', '--compressed', '-A', UA_WEB,
                '-H', f'x-ig-app-id: {collect.APP_ID}',
                '-H', f'Cookie: {cookie}',
                f'https://i.instagram.com/api/v1/feed/user/{user_id}/?count={count}'])
    if not body.strip():
        raise ValueError('resposta vazia (rate-limit ou cookie inválido)')
    d = json.loads(body)
    items = d.get('items')
    if items is None:
        msg = str(d.get('message') or '')
        if 'wait a few minutes' in msg.lower() or d.get('status') == 'fail' and 'wait' in msg.lower():
            raise RateLimit(msg or 'rate-limit')
        raise ValueError(f'sem items (status={d.get("status")}, msg={msg})')
    return items


def _melhor_url(node: dict) -> str | None:
    """Maior resolução disponível de uma mídia (image_versions2)."""
    cands = (node.get('image_versions2') or {}).get('candidates') or []
    cands = [c for c in cands if c.get('url')]
    if not cands:
        return None
    return max(cands, key=lambda c: c.get('width', 0))['url']


def _urls_do_item(item: dict) -> list[str]:
    """URLs de imagem de um post (trata carrossel e ignora vídeos)."""
    if item.get('carousel_media'):
        urls = [_melhor_url(k) for k in item['carousel_media']
                if k.get('media_type') != 2]
    elif item.get('media_type') == 2:  # vídeo puro
        urls = []
    else:
        urls = [_melhor_url(item)]
    return [u for u in urls if u]


def processa(p: dict, seen: set, fila: list, status: dict, agora: str,
             cache: dict[str, str], cookie: str) -> tuple[bool, int]:
    """Coleta um perfil pelo feed autenticado (na conta `cookie`). Devolve (ok, novos)."""
    user = p['username']
    fonte = p.get('banner', user)
    try:
        uid = get_user_id(user, cache)
        if not uid:
            raise ValueError('user_id não encontrado no HTML')
        items = fetch_feed(uid, cookie)
    except RateLimit:
        raise  # o main() tenta outra conta / aguarda — não é falha do perfil
    except Exception as e:
        print(f'[erro] {user}: {e}', file=sys.stderr)
        ent = status.get(fonte, {})
        ent['ultimo_erro'] = f'{agora}: {e}'
        status[fonte] = ent
        return False, 0

    status[fonte] = {**status.get(fonte, {}), 'ultima_coleta_ok': agora, 'ultimo_erro': None}
    novos = 0
    for item in items:
        try:
            sc = item.get('code')
            if not sc or sc in seen:
                continue
            cap = (item.get('caption') or {}).get('text', '') or ''
            if not collect.KEYWORDS.search(cap):
                seen.add(sc)
                continue
            urls = _urls_do_item(item)
            if not urls:
                seen.add(sc)
                continue
            files = []
            for j, url in enumerate(urls):
                fn = f'{sc}_p{j + 1}.jpg'
                if collect.download(url, os.path.join(collect.PAGES, fn)):
                    files.append(fn)
                time.sleep(0.5)
            if not files:
                print(f'[aviso] {sc}: nenhuma página baixada, fica para a próxima', file=sys.stderr)
                continue
            if len(files) < len(urls):
                print(f'[aviso] {sc}: só {len(files)}/{len(urls)} páginas baixaram', file=sys.stderr)
            entrada = {
                'shortcode': sc, 'perfil': user, 'banner': p['banner'],
                'segmento': p['segmento'], 'caption': cap,
                'taken_at': item.get('taken_at'),
                'carrossel': bool(item.get('carousel_media')), 'paginas': files,
                'coletado_em': datetime.date.today().isoformat(),
            }
            if p.get('regra'):
                entrada['regra'] = p['regra']
            fila.append(entrada)
            novos += 1
            seen.add(sc)
        except Exception as ex:
            print(f'[aviso] {user}: post ignorado por formato inesperado ({ex})', file=sys.stderr)
            continue
    return True, novos


def main() -> None:
    """Percorre todos os perfis pelo feed autenticado (2 contas) e alimenta a fila."""
    contas = carrega_contas()
    if not contas:
        sys.exit('[feed] sem cookie (~/.config/ig_cookie ou ig_cookie_2) — exige login. Abortei.')
    profiles = json.load(open(os.path.join(collect.BASE, 'profiles.json')))
    seen_path = os.path.join(DATA, 'posts_vistos.json')
    fila_path = os.path.join(DATA, 'fila_novos.json')
    status_path = os.path.join(DATA, 'coleta_status.json')
    seen = set(collect.load_json(seen_path, []))
    fila = collect.load_json(fila_path, [])
    status = collect.load_json(status_path, {})
    cache = collect.load_json(UIDS_PATH, {})
    agora = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')

    def _salva() -> None:
        """Persiste o progresso — uma interrupção não perde o que já veio."""
        collect.save_json(seen_path, sorted(seen))
        collect.save_json(fila_path, fila)
        collect.save_json(status_path, status)
        collect.save_json(UIDS_PATH, cache)

    # Coleta PERSISTENTE, gentil e com DUAS CONTAS (divide a carga p/ não estourar
    # o rate-limit do IG). Cada perfil tem uma conta PRIMÁRIA (repartida por igual);
    # se ela estiver limitada, tenta a(s) outra(s) como FALLBACK — assim um perfil
    # só falha se TODAS as contas estiverem limitadas.
    # - ordem embaralhada e ritmo humano (15-25s) reduzem a cara de robô;
    # - se TODAS as contas pedem para esperar, NÃO martela: dorme (espera escalonada
    #   5, 10, 15 min) e RETOMA o mesmo perfil. O contador zera quando um perfil passa;
    # - erro que não é rate-limit é re-tentado até MAX_TENT vezes;
    # - orçamento GENEROSO (45 min): a rodada é de madrugada, sem pressa, e completar
    #   os 16 vale mais que terminar rápido. O que faltar entra na próxima janela.
    COOLDOWN_BASE = 300      # 1º passo de espera quando TODAS as contas limitam (5 min)
    COOLDOWN_MAX = 900       # teto por espera (15 min)
    ORCAMENTO_S = 45 * 60    # teto total da coleta do feed
    MAX_TENT = 3             # tentativas por perfil em erro que NÃO é rate-limit
    inicio = time.monotonic()

    pendentes = list(profiles)
    random.shuffle(pendentes)
    # conta primária de cada perfil: reparte igualmente (perfil i -> conta i % N)
    primaria = {p['username']: i % len(contas) for i, p in enumerate(profiles)}
    tentativas: dict[str, int] = {}
    rl_seguidas = 0          # rate-limits em TODAS as contas seguidos (escalona a espera)
    novos = ok = 0
    print(f'[feed] {len(contas)} conta(s) de IG; dividindo {len(profiles)} perfis',
          file=sys.stderr)

    while pendentes and (time.monotonic() - inicio) < ORCAMENTO_S:
        p = pendentes.pop(0)
        user = p['username']
        # tenta a conta primária do perfil; se limitada, tenta as outras (fallback)
        prim = primaria.get(user, 0)
        ordem = [prim] + [i for i in range(len(contas)) if i != prim]
        resultado = None
        for idx in ordem:
            try:
                resultado = processa(p, seen, fila, status, agora, cache, contas[idx])
                break  # a conta respondeu (sucesso ou erro comum) — não tenta outra
            except RateLimit:
                continue  # esta conta está limitada: tenta a próxima

        if resultado is None:  # TODAS as contas limitadas para este perfil
            pendentes.insert(0, p)
            rl_seguidas += 1
            restante = ORCAMENTO_S - (time.monotonic() - inicio)
            espera = int(min(COOLDOWN_BASE * rl_seguidas, COOLDOWN_MAX, restante))
            if espera <= 0:
                break
            print(f'[feed] todas as contas pediram para esperar — aguardando {espera}s e '
                  f'retomando ({len(pendentes)} na fila, espera #{rl_seguidas})', file=sys.stderr)
            _salva()
            time.sleep(espera)
            continue

        rl_seguidas = 0  # passou um perfil: zera a escalada
        sucesso, n = resultado
        novos += n
        ok += sucesso
        _salva()
        if sucesso:
            time.sleep(random.uniform(15, 25))  # ritmo humano entre perfis OK
        else:
            tentativas[user] = tentativas.get(user, 0) + 1
            if tentativas[user] < MAX_TENT:
                pendentes.append(p)  # erro comum: tenta de novo mais tarde
            time.sleep(random.uniform(10, 18))

    faltaram = [p['username'] for p in pendentes]
    if faltaram:
        print(f'[feed] {len(faltaram)} perfil(is) não coletados no orçamento '
              f'(entram na próxima janela): {", ".join(faltaram)}', file=sys.stderr)
    print(f'[feed] {ok}/{len(profiles)} perfis coletados, {novos} post(s) novos na fila',
          file=sys.stderr)
    if ok == 0:
        sys.exit(1)


if __name__ == '__main__':
    main()
