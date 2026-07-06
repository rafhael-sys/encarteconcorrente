#!/usr/bin/env python3
"""Coleta de encartes de fontes WEB (fora do Instagram).

Fonte ativa: Assaí Atacadista (loja Natal) — JSON nacional público com os ciclos
de oferta e as páginas do encarte em JPEG (CloudFront). Validade vem do JSON.
Documentação da descoberta: docs_assai_api.md. Atacadão documentado em
docs_atacadao_api.md (pendente: encarte em PDF exige conversor de imagem).
"""
import json, os, subprocess, sys, time, datetime

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, 'data')
PAGES = os.path.join(DATA, 'pages')
os.makedirs(PAGES, exist_ok=True)

UA = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36')
ASSAI_JSON = 'https://www.assai.com.br/sites/default/files/static/ofertas_assai.json'
ASSAI_EID, ASSAI_NID = 19, 120  # loja Natal
ASSAI_LINK = 'https://www.assai.com.br/ofertas/rio-grande-do-norte/assai-natal'


def sh(args, **kw):
    return subprocess.run(args, capture_output=True, text=True, timeout=90, **kw)


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


def download(url, path):
    try:
        sh(['curl', '-sk', '--compressed', '-A', UA, '-o', path, url])
        if os.path.getsize(path) < 1024:
            raise ValueError
        with open(path, 'rb') as f:
            if f.read(20).lstrip().startswith(b'<'):
                raise ValueError
        return True
    except (OSError, ValueError, subprocess.SubprocessError):
        try:
            os.remove(path)
        except OSError:
            pass
        return False


def coleta_assai(seen, fila):
    r = sh(['curl', '-sS', '-A', UA, ASSAI_JSON])
    dados = json.loads(r.stdout)
    novos = 0
    hoje = datetime.date.today().isoformat()
    for o in dados.get('ofertas', []):
        if not any(l.get('eid') == ASSAI_EID and l.get('nid') == ASSAI_NID
                   for l in o.get('lojas', [])):
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


def main():
    seen_path = os.path.join(DATA, 'posts_vistos.json')
    fila_path = os.path.join(DATA, 'fila_novos.json')
    seen = set(load_json(seen_path, []))
    fila = load_json(fila_path, [])
    try:
        novos = coleta_assai(seen, fila)
    except Exception as e:
        print(f'[erro] assai: {e}', file=sys.stderr)
        sys.exit(1)
    save_json(seen_path, sorted(seen))
    save_json(fila_path, fila)
    print(f'{novos} ciclos de oferta web novos na fila')


if __name__ == '__main__':
    main()
