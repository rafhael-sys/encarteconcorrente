#!/usr/bin/env python3
"""Coleta de encartes de fontes WEB (fora do Instagram).

Fontes ativas: Assaí Atacadista (loja Natal), Atacadão (loja Natal-Sul) e
Nosso Atacarejo (loja Assú/RN). Validade vem dos dados de cada site.
Documentação das descobertas: docs_assai_api.md, docs_atacadao_api.md e
docs_nosso_api.md.
"""
import json
import os
import random
import subprocess
import sys
import time
import datetime

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, 'data')
PAGES = os.path.join(DATA, 'pages')
os.makedirs(PAGES, exist_ok=True)

UA = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36')
ASSAI_JSON = 'https://www.assai.com.br/sites/default/files/static/ofertas_assai.json'
ASSAI_EID, ASSAI_NID = 19, 120  # loja Natal
ASSAI_LINK = 'https://www.assai.com.br/ofertas/rio-grande-do-norte/assai-natal'


def sh(args, timeout=90, **kw):
    return subprocess.run(args, capture_output=True, text=True, timeout=timeout, **kw)


def load_json(path, default):
    try:
        with open(path) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def save_json(path, data):
    tmp = f'{path}.tmp'
    with open(tmp, 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    os.replace(tmp, path)


def br_date(s):
    """DD/MM/AAAA -> AAAA-MM-DD (tolerante)."""
    try:
        d, m, y = s.strip().split('/')
        return f'{y}-{int(m):02d}-{int(d):02d}'
    except Exception:
        return ''


def download(url, path, tentativas=4):
    """Baixa a imagem re-tentando alguns soluços passageiros do CDN (Assaí/
    Atacadão/Nosso) NA MESMA coleta, em vez de deixar para a próxima. True só se
    baixou uma imagem plausível; nunca deixa arquivo lixo para trás."""
    motivo = '?'
    for t in range(1, tentativas + 1):
        try:
            r = sh(['curl', '-sk', '--compressed', '-A', UA, '-o', path,
                    '-w', '%{http_code}', url])
            codigo = r.stdout.strip() or 'sem resposta'
            if os.path.getsize(path) < 1024:
                raise ValueError(f'http {codigo}, corpo pequeno demais')
            with open(path, 'rb') as f:
                if f.read(20).lstrip().startswith(b'<'):
                    raise ValueError(f'http {codigo}, corpo HTML (erro do CDN)')
            return True
        except (OSError, ValueError, subprocess.SubprocessError) as e:
            motivo = str(e) or e.__class__.__name__
            try:
                os.remove(path)
            except OSError:
                pass
            if t < tentativas:
                time.sleep(min(8, 1.5 ** t) + random.uniform(0, 0.8))
    # o motivo no log transforma "não baixou" num problema diagnosticável
    print(f'[aviso] download falhou ({motivo}): {url[:90]}', file=sys.stderr)
    return False


def coleta_assai(seen, fila):
    # o JSON nacional às vezes responde vazio/erro num soluço do CDN; re-tentar
    # aqui (como o Atacadão já faz) evita perder o Assaí por uma queda passageira
    dados = None
    for t in range(3):
        try:
            # O CDN do Assaí ALTERNA entre um nó atual e um nó VELHO (cache
            # defasado, só com ofertas antigas já expiradas) — se cair no velho, a
            # coleta não acha nada novo. Um parâmetro de cache-busting força o nó
            # atual (testado: retorna as ofertas vigentes de forma consistente).
            r = sh(['curl', '-sS', '-A', UA, f'{ASSAI_JSON}?_={int(time.time() * 1000)}'])
            d = json.loads(r.stdout)
            if not isinstance(d, dict):
                # 200 com corpo válido mas não-objeto (ex.: '[]' num soluço do
                # CDN) — trata como falha e re-tenta, senão o dados.get quebra
                raise ValueError('resposta não é um objeto JSON')
            dados = d
            break
        except (json.JSONDecodeError, ValueError, subprocess.SubprocessError):
            if t < 2:
                time.sleep(15)
    if dados is None:
        raise ValueError('JSON de ofertas do Assaí indisponível/inválido (curl 3x)')
    novos = 0
    hoje = datetime.date.today().isoformat()
    for o in dados.get('ofertas', []):
        if not any(loja.get('eid') == ASSAI_EID and loja.get('nid') == ASSAI_NID
                   for loja in o.get('lojas', [])):
            continue
        oid = str(o.get('id_oferta', '')).strip()
        if not oid:
            continue
        aid = f'assai_{oid}'
        chave = f'assai:{oid}'
        if chave in seen:
            continue
        ini, fim = br_date(o.get('start_date', '')), br_date(o.get('end_date', ''))
        if fim and fim < hoje:
            seen.add(chave)  # ciclo já vencido, não interessa coletar
            continue
        files = []
        for j, img in enumerate(o.get('images', [])):
            url = img.get('url') if isinstance(img, dict) else img
            if not url:
                continue
            fn = f'{aid}_p{j+1}.jpg'
            if download(url, os.path.join(PAGES, fn)):
                files.append(fn)
            time.sleep(0.5)
        if files:
            fila.append({
                'shortcode': aid, 'perfil': 'assai.com.br', 'banner': 'Assaí Atacadista',
                'segmento': 'atacarejo', 'caption': o.get('custom_text', '') or 'Ofertas Assaí',
                'taken_at': 0, 'carrossel': len(files) > 1, 'paginas': files,
                'coletado_em': hoje,
                'fonte': 'web', 'link': ASSAI_LINK,
                'validade_confiavel': True, 'inicio': ini, 'fim': fim,
            })
            novos += 1
            seen.add(chave)
        else:
            print(f'[aviso] assai {oid}: nenhuma página baixou, fica para a próxima', file=sys.stderr)
    return novos


def html_via_navegador(url, seletor):
    """Plano B: Chrome DE VERDADE via playwright-core (tools/fetch_pagina.js).
    Um navegador real passa pelos desafios anti-robô (Cloudflare) que barram
    o curl esporadicamente. Devolve '' em falha — o chamador decide."""
    node = os.path.expanduser('~/.local/bin/node')
    if not os.path.exists(node):
        node = 'node'
    try:
        # o navegador tem orçamento interno de ~65s; o teto aqui precisa ser
        # maior, senão o kill do timeout deixa um Chrome órfão na máquina
        r = sh([node, os.path.join(BASE, 'tools', 'fetch_pagina.js'), url, seletor],
               timeout=150)
        return r.stdout if r.returncode == 0 else ''
    except (OSError, subprocess.SubprocessError):
        return ''


ATACADAO_LOJA = 'https://www.atacadao.com.br/loja/natal-sul'
ATACADAO_PDF = 'https://apigw.cloud.carrefour.com.br/api-middleware-flyer-services/api/v2/Flyer/?id={fid}'


def pdf_para_jpg(pdf, prefixo, largura=1400):
    """Converte um PDF em JPGs (prefixo_pN.jpg) e devolve os caminhos gerados.
    No macOS usa o binário nativo tools/pdf2jpg (Swift); na nuvem/Linux usa o
    conversor Python tools/pdf2jpg.py (PyMuPDF). Devolve [] se nada converteu."""
    nativo = os.path.join(BASE, 'tools', 'pdf2jpg')
    tentativas = []
    if sys.platform == 'darwin' and os.path.exists(nativo) and os.access(nativo, os.X_OK):
        tentativas.append([nativo, pdf, prefixo, str(largura)])
    tentativas.append([sys.executable, os.path.join(BASE, 'tools', 'pdf2jpg.py'),
                       pdf, prefixo, str(largura)])
    for cmd in tentativas:
        try:
            r = sh(cmd, timeout=120)
            linhas = [ln for ln in r.stdout.strip().splitlines() if ln.strip()]
            if r.returncode == 0 and linhas:
                return linhas
        except subprocess.SubprocessError:
            continue
    return []


def coleta_atacadao(seen, fila):
    import re
    import hashlib
    # o edge do site às vezes responde uma página sem o __NEXT_DATA__ (challenge
    # momentâneo); re-tentar aqui evita perder a janela por um soluço passageiro
    m = None
    for t in range(3):
        try:
            r = sh(['curl', '-sL', '-A', UA, ATACADAO_LOJA])
            m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', r.stdout, re.S)
        except subprocess.SubprocessError:
            m = None  # curl pendurado (timeout) é tão passageiro quanto — re-tenta
        if m:
            break
        if t < 2:
            time.sleep(15)
    if not m:
        # curl barrado 3x: abre a página num Chrome real (plano B)
        html = html_via_navegador(ATACADAO_LOJA, 'script#__NEXT_DATA__')
        m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.S)
        if m:
            print('[info] atacadao: página obtida pelo navegador (plano B)', file=sys.stderr)
    if not m:
        raise ValueError('__NEXT_DATA__ não encontrado (curl 3x e navegador)')
    flyers = (json.loads(m.group(1)).get('props', {}).get('pageProps', {})
              .get('storeInfo', {}) or {}).get('flyers') or []
    novos = 0
    hoje = datetime.date.today().isoformat()
    for f in flyers:
        fid = str(f.get('id', '')).strip()
        if not fid:
            continue
        chave = f'atacadao:{fid}'
        if chave in seen:
            continue
        val = f.get('validity') or {}
        ini = str(val.get('initial', ''))[:10]
        fim = str(val.get('final', ''))[:10]
        if fim and fim < hoje:
            seen.add(chave)
            continue
        nome = f.get('name') or f.get('title') or 'Encarte Atacadão'
        aid = 'atacadao_' + hashlib.md5(fid.encode()).hexdigest()[:10]
        pdf = os.path.join(PAGES, f'{aid}.pdf')
        try:
            sh(['curl', '-sL', '-A', UA, '-o', pdf, ATACADAO_PDF.format(fid=fid)])
            if os.path.getsize(pdf) < 10000 or open(pdf, 'rb').read(5) != b'%PDF-':
                raise ValueError('PDF inválido')
            # 1600px: o PDF é vetorial — renderizar maior que os antigos 1400px
            # dá nitidez real aos preços pequenos, e 1600 é EXATAMENTE o teto de
            # embutir-intacto do build_painel.py: a página entra no painel sem
            # segunda recompressão (mudar um dos dois exige mudar o outro)
            linhas = pdf_para_jpg(pdf, os.path.join(PAGES, aid), 1600)
            files = [os.path.basename(ln) for ln in linhas]
            if not files:
                raise ValueError('conversão do PDF não gerou páginas')
        except Exception as e:
            print(f'[aviso] atacadao {nome}: {e}; fica para a próxima', file=sys.stderr)
            continue
        finally:
            try:
                os.remove(pdf)
            except OSError:
                pass
        if files:
            fila.append({
                'shortcode': aid, 'perfil': 'atacadao.com.br', 'banner': 'Atacadão',
                'segmento': 'atacarejo', 'caption': nome,
                'taken_at': 0, 'carrossel': len(files) > 1, 'paginas': files,
                'coletado_em': hoje,
                'fonte': 'web', 'link': ATACADAO_LOJA,
                'validade_confiavel': bool(ini and fim), 'inicio': ini, 'fim': fim,
            })
            novos += 1
            seen.add(chave)
        time.sleep(2)
    return novos


NOSSO_LOJA = 5  # loja 5 = Assú/RN (1 = Pau dos Ferros, 2 = São Miguel)
# qualquer página de encarte da loja traz o catálogo completo embutido; se um
# slug sair do ar, os outros dois conhecidos servem de porta de entrada
NOSSO_SLUGS = ('quarta-e-quinta-rn', 'nosso-final-de-semana-rn', 'encarte-do-mes-rn')
NOSSO_LINK = f'https://www.nossoatacarejo.com.br/encarte/{NOSSO_SLUGS[0]}/{NOSSO_LOJA}'


def _nosso_flyers(html):
    """Extrai o array 'flyers' do payload Next.js (self.__next_f) embutido no
    HTML da página do encarte — ver docs_nosso_api.md. [] se não achar."""
    import re
    pedacos = []
    for m in re.finditer(r'self\.__next_f\.push\(\[1,("(?:[^"\\]|\\.)*")\]\)', html):
        try:
            pedacos.append(json.loads(m.group(1)))
        except json.JSONDecodeError:
            pass
    fluxo = ''.join(pedacos)
    i = fluxo.find('"flyers":[')
    if i < 0:
        return []
    i += len('"flyers":')
    # recorta o array respeitando aninhamento e strings
    prof, em_str, esc = 0, False, False
    for j in range(i, len(fluxo)):
        c = fluxo[j]
        if em_str:
            if esc:
                esc = False
            elif c == '\\':
                esc = True
            elif c == '"':
                em_str = False
        elif c == '"':
            em_str = True
        elif c == '[':
            prof += 1
        elif c == ']':
            prof -= 1
            if prof == 0:
                try:
                    return json.loads(fluxo[i:j + 1])
                except json.JSONDecodeError:
                    return []
    return []


def png_para_jpg(src, dst):
    """Converte a página PNG (formato do CDN do Nosso) para o JPG que todo o
    resto do projeto espera. Pillow (nuvem); sips no macOS de reserva."""
    try:
        from PIL import Image
        with Image.open(src) as im:
            if im.mode not in ('RGB', 'L'):
                im = im.convert('RGB')
            im.save(dst, 'JPEG', quality=92, optimize=True, subsampling=0)
        return True
    except Exception:
        try:
            r = sh(['sips', '-s', 'format', 'jpeg', '-s', 'formatOptions', '92',
                    src, '--out', dst])
            return r.returncode == 0 and os.path.exists(dst)
        except (OSError, subprocess.SubprocessError):
            return False


def coleta_nosso(seen, fila):
    import hashlib
    flyers = []
    for slug in NOSSO_SLUGS:
        url = f'https://www.nossoatacarejo.com.br/encarte/{slug}/{NOSSO_LOJA}'
        for t in range(2):
            try:
                r = sh(['curl', '-sL', '--compressed', '-A', UA, url])
                flyers = _nosso_flyers(r.stdout)
            except subprocess.SubprocessError:
                flyers = []
            if flyers:
                break
            if t < 1:
                time.sleep(10)
        if flyers:
            break
    if not flyers:
        # curl barrado: abre a página num Chrome real (plano B)
        flyers = _nosso_flyers(html_via_navegador(NOSSO_LINK, '#main-content-flyer'))
    if not flyers:
        raise ValueError('catálogo de encartes não encontrado na página (curl e navegador)')
    novos = 0
    hoje = datetime.date.today().isoformat()
    for f in flyers:
        fid = str(f.get('id', '')).strip()
        imgs = sorted(f.get('images') or [], key=lambda i: i.get('order') or 0)
        if not fid or not imgs:
            continue
        ini = str(f.get('start_date', ''))[:10]
        fim = str(f.get('end_date', ''))[:10]
        # o id do flyer é fixo por campanha (só as imagens/datas trocam a cada
        # ciclo), então a chave de "já visto" precisa incluir o período
        chave = f'nosso:{fid}:{ini}:{fim}'
        if chave in seen:
            continue
        if fim and fim < hoje:
            seen.add(chave)  # ciclo já vencido, não interessa coletar
            continue
        nome = f.get('name') or 'Encarte Nosso Atacarejo'
        aid = 'nosso_' + hashlib.md5(chave.encode()).hexdigest()[:10]
        files = []
        for j, img in enumerate(imgs):
            url = img.get('image_url')
            if not url:
                continue
            png = os.path.join(PAGES, f'{aid}_p{j+1}.png')
            fn = f'{aid}_p{j+1}.jpg'
            if download(url, png) and png_para_jpg(png, os.path.join(PAGES, fn)):
                files.append(fn)
            try:
                os.remove(png)
            except OSError:
                pass
            time.sleep(0.5)
        if files:
            slug = f.get('slug', '')
            fila.append({
                'shortcode': aid, 'perfil': 'nossoatacarejo.com.br', 'banner': 'Nosso Atacarejo',
                'segmento': 'atacarejo', 'caption': nome,
                'taken_at': 0, 'carrossel': len(files) > 1, 'paginas': files,
                'coletado_em': hoje,
                'fonte': 'web',
                'link': f'https://www.nossoatacarejo.com.br/encarte/{slug}/{NOSSO_LOJA}' if slug else NOSSO_LINK,
                'validade_confiavel': bool(ini and fim), 'inicio': ini, 'fim': fim,
            })
            novos += 1
            seen.add(chave)
        else:
            print(f'[aviso] nosso {nome}: nenhuma página baixou, fica para a próxima', file=sys.stderr)
    return novos


def main():
    seen_path = os.path.join(DATA, 'posts_vistos.json')
    fila_path = os.path.join(DATA, 'fila_novos.json')
    status_path = os.path.join(DATA, 'coleta_status.json')
    seen = set(load_json(seen_path, []))
    fila = load_json(fila_path, [])
    status = load_json(status_path, {})
    agora = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    total, falhas = 0, []
    fontes_web = [('assai', 'Assaí Atacadista', coleta_assai),
                  ('atacadao', 'Atacadão', coleta_atacadao),
                  ('nosso', 'Nosso Atacarejo', coleta_nosso)]
    for nome, rotulo, fonte in fontes_web:
        try:
            total += fonte(seen, fila)
            status[rotulo] = {'ultima_coleta_ok': agora, 'ultimo_erro': None}
        except Exception as e:
            falhas.append(nome)
            ent = status.get(rotulo, {})
            ent['ultimo_erro'] = f'{agora}: {e}'
            status[rotulo] = ent
            print(f'[erro] {nome}: {e}', file=sys.stderr)
    save_json(seen_path, sorted(seen))
    save_json(fila_path, fila)
    save_json(status_path, status)
    print(f'{total} ciclos de oferta web novos na fila')
    if len(falhas) == len(fontes_web):
        sys.exit(1)  # só falha se TODAS as fontes web falharem


if __name__ == '__main__':
    main()
