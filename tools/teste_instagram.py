#!/usr/bin/env python3
"""Teste de fumaça das FONTES a partir deste servidor.

Só LÊ (não baixa imagens, não altera nada, não commita). Serve para saber,
ANTES de migrar de vez, se o Instagram / Assaí / Atacadão bloqueiam o IP da
nuvem. Use o mesmo endpoint/cabeçalhos da coleta real (collect.py/collect_web.py)
para o resultado ser fiel.
"""
import json
import os
import random
import subprocess
import time

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UA = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/126.0 Safari/537.36')
APP_ID = '936619743392459'


def sh(args, timeout=60):
    return subprocess.run(args, capture_output=True, text=True, timeout=timeout)


def testa_ig(username):
    try:
        r = sh(['curl', '-sk', '--compressed', '-A', UA, '-H', f'x-ig-app-id: {APP_ID}',
                f'https://i.instagram.com/api/v1/users/web_profile_info/?username={username}'])
        u = json.loads(r.stdout).get('data', {}).get('user')
        if not u:
            return False, 'data.user=null (rate-limit ou login exigido)'
        n = len(u['edge_owner_to_timeline_media']['edges'])
        return True, f'{n} posts recentes lidos'
    except Exception as e:
        return False, f'{type(e).__name__}: {e}'


def main():
    profiles = json.load(open(os.path.join(BASE, 'profiles.json')))
    print('== Teste das fontes a partir do IP deste servidor (nuvem) ==\n')
    print('-- Instagram (perfis dos concorrentes) --')
    ok = 0
    for p in profiles:
        good, msg = testa_ig(p['username'])
        ok += good
        print(f'  [{"OK  " if good else "BLOQ"}] {p["banner"]:<42} {msg}')
        time.sleep(2 + random.uniform(0, 1))  # gentil, como a coleta real
    print(f'\n  => {ok}/{len(profiles)} perfis do Instagram responderam\n')

    print('-- Fontes web --')
    try:
        r = sh(['curl', '-sS', '-A', UA,
                'https://www.assai.com.br/sites/default/files/static/ofertas_assai.json'])
        d = json.loads(r.stdout)
        print(f'  [OK  ] Assaí (JSON de ofertas): {len(d.get("ofertas", []))} ofertas nacionais')
    except Exception as e:
        print(f'  [BLOQ] Assaí: {type(e).__name__}: {e}')
    try:
        r = sh(['curl', '-sL', '-A', UA, 'https://www.atacadao.com.br/loja/natal-sul'])
        tem = '__NEXT_DATA__' in r.stdout
        print(f'  [{"OK  " if tem else "BLOQ"}] Atacadão (página da loja): '
              + ('dados encontrados' if tem else 'sem __NEXT_DATA__ (challenge/bloqueio)'))
    except Exception as e:
        print(f'  [BLOQ] Atacadão: {type(e).__name__}: {e}')

    print('\nComo ler: se a MAIORIA respondeu OK, a nuvem deve coletar bem. '
          'Se vier muito BLOQ, o IP da nuvem está sendo barrado e precisaremos '
          'de um proxy. (O Assaí quase sempre responde; o Instagram é o mais sensível.)')


if __name__ == '__main__':
    main()
