#!/usr/bin/env python3
"""TEMPORÁRIO — sonda 2 do nossoatacarejo.com.br (roda no GitHub Actions).
Verifica se o HTML vem completo via curl e extrai os trechos com dados do
encarte (flyer/validade) embutidos pelo Next.js."""
import re
import subprocess
import sys

UA = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36')


def curl(url):
    r = subprocess.run(['curl', '-sL', '-A', UA, url], capture_output=True,
                       text=True, timeout=60)
    return r.stdout


for u in ('https://www.nossoatacarejo.com.br/robots.txt',
          'https://www.nossoatacarejo.com.br/sitemap.xml'):
    print(f'===== {u}')
    print(curl(u)[:2000])

for url in ('https://www.nossoatacarejo.com.br/encarte/quarta-e-quinta-rn/5',
            'https://www.nossoatacarejo.com.br/'):
    print(f'===== {url}')
    h = curl(url)
    print(f'tamanho: {len(h)}')
    print('tem __NEXT_DATA__:', '__NEXT_DATA__' in h)
    print('tem __next_f:', '__next_f' in h)
    print('imagens de flyer:',
          re.findall(r'https://cdn\.nossoatacarejo\.com\.br/[^"\\\s]*flyers[^"\\\s]*', h)[:10])
    for termo in ('flyer', 'encarte', 'valid', 'loja'):
        trechos = [m.group(0) for m in re.finditer(
            r'.{200}' + termo + r'.{600}', h, re.I)][:6]
        for t in trechos:
            print(f'--- trecho com "{termo}":')
            print(t.replace('\n', ' ')[:820])
    print()
sys.exit(0)
