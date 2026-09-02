#!/usr/bin/env python3
import json
import os
import re
import sys
import datetime
import math
import unicodedata
import subprocess

try:
    import Vision
    from Cocoa import NSURL
except ImportError:
    print("[erro] PyObjC Vision não disponível", file=sys.stderr)
    sys.exit(1)

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, 'data')
PAGES = os.path.join(DATA, 'pages')

HOJE = datetime.date.today().isoformat()

def normalize_str(s):
    if not s:
        return ""
    s = unicodedata.normalize('NFKD', s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r'\s+', ' ', s).strip().lower()

def extrai_datas(texto, fallback_inicio=HOJE, fallback_fim=HOJE):
    # Procura padrões de data como "02 a 03/09/2026", "02 a 03 de setembro", "31/08 a 03/09"
    meses = {
        'jan': '01', 'fev': '02', 'mar': '03', 'abr': '04', 'mai': '05', 'jun': '06',
        'jul': '07', 'ago': '08', 'set': '09', 'out': '10', 'nov': '11', 'dez': '12',
        'janeiro': '01', 'fevereiro': '02', 'marco': '03', 'março': '03', 'abril': '04',
        'maio': '05', 'junho': '06', 'julho': '07', 'agosto': '08', 'setembro': '09',
        'outubro': '10', 'novembro': '11', 'dezembro': '12'
    }
    
    # 1. Padrão DD/MM a DD/MM/AAAA ou DD a DD/MM/AAAA
    m = re.search(r'(\d{1,2})(?:/(\d{1,2}))?\s*(?:a|ate|à|ate o dia|-)\s*(\d{1,2})/(\d{1,2})(?:/(\d{2,4}))?', texto, re.I)
    if m:
        d1, m1, d2, m2, a = m.groups()
        ano = a if a else '2026'
        if len(ano) == 2: ano = '20' + ano
        mes_fim = m2.zfill(2)
        mes_ini = m1.zfill(2) if m1 else mes_fim
        ini = f"{ano}-{mes_ini}-{d1.zfill(2)}"
        fim = f"{ano}-{mes_fim}-{d2.zfill(2)}"
        return ini, fim
        
    # 2. Padrão DD a DD de [mes]
    m = re.search(r'(\d{1,2})\s*(?:a|ate|à|-)\s*(\d{1,2})\s*de\s*([a-zA-Zç]+)(?:\s*de\s*(\d{2,4}))?', texto, re.I)
    if m:
        d1, d2, mes_nome, a = m.groups()
        mes_num = meses.get(normalize_str(mes_nome), '09')
        ano = a if a else '2026'
        if len(ano) == 2: ano = '20' + ano
        ini = f"{ano}-{mes_num}-{d1.zfill(2)}"
        fim = f"{ano}-{mes_num}-{d2.zfill(2)}"
        return ini, fim

    # 3. Padrão "somente hoje" ou "valido apenas dia DD/MM"
    m = re.search(r'(\d{1,2})/(\d{1,2})(?:/(\d{2,4}))?', texto)
    if m:
        d, mes, a = m.groups()
        ano = a if a else '2026'
        if len(ano) == 2: ano = '20' + ano
        data_fmt = f"{ano}-{mes.zfill(2)}-{d.zfill(2)}"
        return data_fmt, data_fmt

    return fallback_inicio, fallback_fim

def ocr_imagem(caminho):
    url = NSURL.fileURLWithPath_(caminho)
    req = Vision.VNRecognizeTextRequest.alloc().init()
    req.setRecognitionLevel_(Vision.VNRequestTextRecognitionLevelAccurate)
    req.setRecognitionLanguages_(["pt-BR", "pt-PT", "en-US"])
    req.setUsesLanguageCorrection_(True)
    
    handler = Vision.VNImageRequestHandler.alloc().initWithURL_options_(url, None)
    handler.performRequests_error_([req], None)
    
    results = req.results()
    boxes = []
    if results:
        for obs in results:
            text = obs.topCandidates_(1)[0].string().strip()
            if not text: continue
            b = obs.boundingBox()
            # Vision coords: origin bottom-left (0..1). Converte para top-left % (0..100)
            x = round(b.origin.x * 100, 1)
            y = round((1.0 - (b.origin.y + b.size.height)) * 100, 1)
            w = round(b.size.width * 100, 1)
            h = round(b.size.height * 100, 1)
            boxes.append({'text': text, 'x': x, 'y': y, 'w': w, 'h': h})
    return boxes

def parse_produtos_pagina(boxes):
    """Agrupa textos e preços para formar produtos com posições."""
    # Encontra todos os blocos com preço (ex: R$ 12,99, 12,98, 1,99, etc.)
    # Ignora números soltos que sejam só datas (ex: 2026) ou CEP
    PRICE_PAT = re.compile(r'(?:R\$\s*)?(\d{1,3}[,\.]\d{2})\b')
    
    precos = []
    textos = []
    
    for b in boxes:
        t = b['text']
        m = PRICE_PAT.search(t)
        # Verifica se o bloco é essencialmente um preço
        if m and (len(t) <= 15 or 'R$' in t or 'cada' in t.lower() or 'kg' in t.lower() or 'un' in t.lower()):
            val = m.group(1).replace('.', ',')
            # Extrai unidade se estiver junto
            un = 'cada'
            if 'kg' in t.lower(): un = 'kg'
            elif '100g' in t.lower(): un = '100g'
            elif 'un' in t.lower() or 'und' in t.lower(): un = 'un'
            elif 'litro' in t.lower() or 'l' in t.lower(): un = 'un'
            precos.append({
                'preco': val,
                'un': un,
                'raw': t,
                'x': b['x'], 'y': b['y'], 'w': b['w'], 'h': b['h'],
                'cx': b['x'] + b['w']/2, 'cy': b['y'] + b['h']/2
            })
        else:
            # Texto comum (nome do produto ou ruído)
            if not any(k in t.lower() for k in ['ofertas válidas', 'enquanto durarem', 'proibida a venda', 'aprecie com moderação', 'imagens ilustrativas', 'beba com']):
                textos.append(b)

    produtos = []
    # Para cada preço, localiza os textos imediatamente ACIMA ou AO LADO (mesmo card visual)
    usados_textos = set()
    for p in precos:
        cands = []
        for i, t in enumerate(textos):
            if i in usados_textos: continue
            tx_cx = t['x'] + t['w']/2
            tx_cy = t['y'] + t['h']/2
            
            # Distância horizontal e vertical
            dx = abs(tx_cx - p['cx'])
            dy = p['y'] - (t['y'] + t['h']) # t acima de p
            
            # Textos diretamente acima do preço (até 18% de altura da imagem) e com alinhamento horizontal razoável
            if -5 <= dy <= 20 and dx <= max(p['w'], 22):
                cands.append((dy, t, i))
            # Ou texto logo à esquerda do preço (mesma linha)
            elif abs(t['y'] - p['y']) <= 5 and (p['x'] - (t['x'] + t['w'])) >= -2 and (p['x'] - (t['x'] + t['w'])) <= 15:
                cands.append((100, t, i))

        cands.sort(key=lambda c: (c[1]['y'], c[1]['x']))
        nomes = [c[1]['text'] for c in cands]
        nome_completo = " ".join(nomes).strip()
        
        # Se não achou texto acima, tenta pegar texto mais próximo num raio de 15%
        if not nome_completo:
            proximos = []
            for i, t in enumerate(textos):
                dist = math.hypot(t['x'] - p['x'], t['y'] - p['y'])
                if dist < 16:
                    proximos.append((dist, t, i))
            proximos.sort(key=lambda x: x[0])
            if proximos:
                nome_completo = proximos[0][1]['text']

        # Limpa o nome do produto
        nome_completo = re.sub(r'^(?:oferta|super|preço|rasga|dia)\s+', '', nome_completo, flags=re.I).strip()
        if len(nome_completo) >= 3 and not re.match(r'^\d+$', nome_completo):
            # Calcula bounding box conjunta
            all_b = [p] + [c[1] for c in cands]
            min_x = max(0, min(b['x'] for b in all_b) - 1)
            min_y = max(0, min(b['y'] for b in all_b) - 1)
            max_x = min(100, max(b['x'] + b['w'] for b in all_b) + 1)
            max_y = min(100, max(b['y'] + b['h'] for b in all_b) + 1)
            
            produtos.append({
                'n': nome_completo,
                'p': p['preco'],
                'u': p['un'],
                'x': round(min_x),
                'y': round(min_y),
                'w': round(max_x - min_x),
                'h': round(max_y - min_y)
            })

    return produtos

def main():
    fila_path = os.path.join(DATA, 'fila_novos.json')
    actions_path = os.path.join(DATA, 'actions.json')
    products_path = os.path.join(DATA, 'products.json')
    canon_path = os.path.join(DATA, 'canon.json')
    seen_path = os.path.join(DATA, 'posts_vistos.json')
    
    fila = json.load(open(fila_path)) if os.path.exists(fila_path) else []
    actions = json.load(open(actions_path)) if os.path.exists(actions_path) else []
    products = json.load(open(products_path)) if os.path.exists(products_path) else {}
    canon = json.load(open(canon_path)) if os.path.exists(canon_path) else []
    seen = set(json.load(open(seen_path))) if os.path.exists(seen_path) else set()

    existentes_ids = {a.get('id') or a.get('shortcode') for a in actions}

    B2B_PAT = re.compile(r"alô,?\s*comerciante|televendas|food\s*service|especial\s*do\s*comerciante|revenda", re.I)
    PB_PAT = re.compile(r"joão\s*pessoa|paraíba|\bPB\b", re.I)

    novas_acoes = 0
    novos_produtos_total = 0

    canon_map = {}
    for g in canon:
        norm = normalize_str(g.get('n', ''))
        if norm: canon_map[norm] = g

    for item in fila:
        sc = item.get('shortcode') or item.get('id')
        banner = item.get('banner', item.get('perfil', ''))
        cap = item.get('caption', '')
        perfil = item.get('perfil', '')
        segmento = item.get('segmento', 'varejo')
        paginas = item.get('paginas', [])
        
        # Filtros
        if "superfacil" in perfil and PB_PAT.search(cap):
            print(f"[descarte] {banner} ({sc}): fora do RN")
            seen.add(sc)
            continue
        if B2B_PAT.search(cap):
            print(f"[descarte] {banner} ({sc}): B2B / Televendas")
            seen.add(sc)
            continue
        if any(k in cap.lower() for k in ["setembro amarelo", "estaremos funcionando normalmente"]):
            print(f"[descarte] {banner} ({sc}): Institucional sem preços")
            seen.add(sc)
            continue
        if sc in existentes_ids:
            print(f"[ignora] {banner} ({sc}): já existe em actions.json")
            seen.add(sc)
            continue

        # Datas
        if item.get('validade_confiavel') and item.get('inicio') and item.get('fim'):
            ini, fim = item['inicio'], item['fim']
        else:
            ini, fim = extrai_datas(cap, HOJE, HOJE)

        # Processa cada página
        acao_produtos_count = 0
        titulo = cap.split('\n')[0].strip()[:60] if cap else f"Encarte {banner}"
        titulo = re.sub(r'^[^\w\s]+', '', titulo).strip() or f"Encarte {banner}"

        for fn in paginas:
            caminho = os.path.join(PAGES, fn)
            if not os.path.exists(caminho):
                continue
            pk = os.path.splitext(fn)[0]
            boxes = ocr_imagem(caminho)
            prods = parse_produtos_pagina(boxes)
            products[pk] = prods
            acao_produtos_count += len(prods)
            
            # Atualiza canon
            for i, p in enumerate(prods):
                p_norm = normalize_str(p['n'])
                m_key = f"{pk}#{i}"
                if p_norm in canon_map:
                    g = canon_map[p_norm]
                    if m_key not in g.get('m', []):
                        g.setdefault('m', []).append(m_key)
                else:
                    novo_g = {'n': p['n'], 'u': p.get('u', 'un'), 'm': [m_key]}
                    canon.append(novo_g)
                    canon_map[p_norm] = novo_g

        if acao_produtos_count == 0:
            print(f"[descarte] {banner} ({sc}): 0 produtos com preço visível")
            seen.add(sc)
            continue

        # Cria a nova ação
        nova_acao = {
            'id': sc,
            'perfil': perfil,
            'titulo': titulo,
            'banner': banner,
            'segmento': segmento,
            'inicio': ini,
            'fim': fim,
            'carrossel': len(paginas) > 1,
            'shortcode': sc,
            'caption': cap,
            'paginas': paginas,
            'adicionado_em': HOJE
        }
        if item.get('fonte') == 'web':
            nova_acao['fonte'] = 'web'
            if item.get('link'): nova_acao['link'] = item['link']

        actions.append(nova_acao)
        existentes_ids.add(sc)
        seen.add(sc)
        novas_acoes += 1
        novos_produtos_total += acao_produtos_count
        print(f"[ok] {banner} ({sc}): {acao_produtos_count} produtos extraídos ({ini} a {fim})")

    # Salva arquivos
    with open(actions_path, 'w') as f: json.dump(actions, f, ensure_ascii=False, indent=1)
    with open(products_path, 'w') as f: json.dump(products, f, ensure_ascii=False, indent=1)
    with open(canon_path, 'w') as f: json.dump(canon, f, ensure_ascii=False, indent=1)
    with open(seen_path, 'w') as f: json.dump(sorted(seen), f, ensure_ascii=False, indent=1)
    
    # Esvazia fila
    with open(fila_path, 'w') as f: json.dump([], f)
    
    # Resumo para notificação
    resumo_msg = f"{novas_acoes} encartes novos processados hoje ({novos_produtos_total} produtos extraídos)."
    with open(os.path.join(DATA, 'resumo_notificacao.txt'), 'w') as f:
        f.write(resumo_msg + "\n")

    print(f"\n=== EXTRAÇÃO CONCLUÍDA ===")
    print(f"Novas Ações: {novas_acoes}")
    print(f"Novos Produtos: {novos_produtos_total}")
    print(f"Total de Ações em actions.json: {len(actions)}")

if __name__ == '__main__':
    main()
