#!/usr/bin/env python3
"""Gera painel-encartes.html a partir de data/actions.json + data/products.json + data/pages/*.jpg."""
import base64
import datetime
import json
import os
import re
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

# ordem do painel: Rede Mais sempre primeiro; abaixo, do mais novo para o
# mais antigo (data de início), sem separar varejo de atacarejo
actions.sort(key=lambda a: (a['inicio'], a.get('fim', '')), reverse=True)
actions.sort(key=lambda a: 0 if a['segmento'] == 'propria' else 1)

# o painel mostra expirados até 30 dias; depois disso a IMAGEM sai do HTML
# (agilidade) e o JPG vai para data/arquivo/pages (pesquisa futura). A ação
# permanece em __ACTIONS__ para sempre: é ela que sustenta o histórico de
# preços da Incidência (RES no template resolve canon -> ação).
JANELA_PAINEL_DIAS = 30
corte = (datetime.date.today() - datetime.timedelta(days=JANELA_PAINEL_DIAS)).isoformat()
ARQUIVO = os.path.join(DATA, 'arquivo', 'pages')
os.makedirs(ARQUIVO, exist_ok=True)

# --- redimensionamento de imagens: Pillow (multiplataforma, usado na nuvem).
# Se o Pillow não estiver instalado, cai para o `sips` do macOS. ---
try:
    from PIL import Image as _PILImage
    _HAS_PIL = True
except Exception:
    _HAS_PIL = False


def _img_lado_max(src):
    """Maior lado da imagem em px (0 se ilegível)."""
    if _HAS_PIL:
        try:
            with _PILImage.open(src) as im:
                return max(im.size)
        except Exception:
            return 0
    g = subprocess.run(['sips', '-g', 'pixelWidth', '-g', 'pixelHeight', src],
                       capture_output=True, text=True).stdout
    dims = [int(ln.split()[-1]) for ln in g.splitlines()
            if ln.split() and ln.split()[-1].isdigit() and 'pixel' in ln]
    return max(dims, default=0)


def _recomprime(src, dst, zw, q, reduzir):
    """Grava dst como JPEG (qualidade q); reduz para no máx zw px de lado se
    `reduzir`. Devolve True se gerou o arquivo. Pillow, com sips (macOS) de
    reserva — nunca derruba o build."""
    if _HAS_PIL:
        try:
            with _PILImage.open(src) as im:
                if im.mode not in ('RGB', 'L'):
                    im = im.convert('RGB')
                if reduzir:
                    im.thumbnail((zw, zw))
                im.save(dst, 'JPEG', quality=int(q))
            return True
        except Exception:
            return False
    cmd = ['sips', '-s', 'format', 'jpeg', '-s', 'formatOptions', str(q), src, '--out', dst]
    if reduzir:
        cmd[1:1] = ['-Z', str(zw)]
    r = subprocess.run(cmd, capture_output=True)
    return r.returncode == 0 and os.path.exists(dst)

data_actions, images = [], {}
with tempfile.TemporaryDirectory() as tmp:
    for a in actions:
        embutir = a['fim'] >= corte
        if not embutir:
            for fname in a['paginas']:
                antigo = os.path.join(PAGES, fname)
                if os.path.exists(antigo):
                    os.replace(antigo, os.path.join(ARQUIVO, fname))
        page_ids = []
        for i, fname in enumerate(a['paginas']):
            pid = f"{a['id']}_p{i+1}" if not fname.startswith(a['id']) else fname.replace('.jpg', '')
            src = os.path.join(PAGES, fname)
            if not os.path.exists(src):
                arquivada = os.path.join(ARQUIVO, fname)
                if embutir and os.path.exists(arquivada):
                    # a data fim voltou para dentro da janela (correção de
                    # data errada): a página sai do arquivo e volta ao painel
                    os.replace(arquivada, src)
                elif not embutir:
                    # página arquivada (ou até perdida): entra no índice mesmo
                    # assim — se a ação antiga sumir de __ACTIONS__, a
                    # Incidência perde o histórico de preços dela em silêncio
                    page_ids.append(pid)
                    continue
                else:
                    continue
            if embutir:
                # REGRA: vigentes na melhor nitidez possível; expirados recentes 800px/q45.
                # O Instagram já entrega no máximo 1080px — recomprimir isso (q62) borrava
                # os preços pequenos. Então, para vigentes já dentro do teto, embutimos o
                # JPEG ORIGINAL sem recomprimir; só reduzimos/recomprimimos o que passa do teto.
                vig = a['fim'] >= datetime.date.today().isoformat()
                zw, q = (1600, '80') if vig else (800, '45')
                # dimensões via Pillow (nuvem/Linux) — cai para sips no macOS.
                # sem dimensão legível -> não redimensiona, só recomprime (nunca derruba o build)
                lado_max = _img_lado_max(src)
                usou_original = False
                if vig and 0 < lado_max <= zw:
                    with open(src, 'rb') as f:
                        raw = f.read()
                    if raw[:2] == b'\xff\xd8':  # JPEG válido: embute sem recomprimir
                        images[pid] = 'data:image/jpeg;base64,' + base64.b64encode(raw).decode()
                        usou_original = True
                if not usou_original:
                    small = os.path.join(tmp, fname)
                    if _recomprime(src, small, zw, q, lado_max > zw):
                        images[pid] = 'data:image/jpeg;base64,' + base64.b64encode(open(small, 'rb').read()).decode()
                    else:
                        print(f'[aviso] recompressão falhou em {fname}; página fica sem imagem embutida', file=sys.stderr)
            page_ids.append(pid)
        if page_ids:
            data_actions.append({'id': a['id'], 'banner': a['banner'], 'perfil': a['perfil'],
                                 'titulo': a['titulo'], 'seg': a['segmento'], 'ini': a['inicio'],
                                 'fim': a['fim'], 'sc': a['shortcode'], 'pgs': page_ids,
                                 'add': a.get('adicionado_em', ''),
                                 'lk': a.get('link', '')})

# aba Logs (só no HTML local): problemas e conclusões da rotina, por dia,
# extraídos de data/rotina.log — últimos 30 dias, traduzidos para linguagem
# simples (o texto técnico original fica no campo 'd', vira tooltip no painel)
TRADUCOES = [
    # sites web PRIMEIRO: 'assai: Expecting value' casaria na regra genérica
    # do Instagram e seria traduzido errado (ordem importa)
    (r'^atacadao: página obtida pelo navegador.*', 'Atacadão barrou o método leve — o navegador (plano B) resolveu sozinho'),
    (r'^atacadao: __NEXT_DATA__ não encontrado.*', 'Site do Atacadão bloqueou a coleta nesta janela — tenta de novo na próxima'),
    (r'^atacadao (.+): ([^:]*?)(?:; fica para a próxima)?$', r'Encarte "\1" do Atacadão falhou (\2) — tenta na próxima janela'),
    (r'^atacadao: (.*)', r'Coleta do site do Atacadão falhou (\1)'),
    (r'^assai (\S+): nenhuma página baixou.*', r'Encarte \1 do Assaí: nenhuma página baixou — fica para a próxima janela'),
    (r'^assai: (.*)', r'Coleta do site do Assaí falhou (\1)'),
    (r'^coleta web .*falhou.*', 'Coleta dos sites (Assaí/Atacadão) falhou nesta janela'),
    # Instagram
    (r'^(\S+): Expecting value.*', r'Instagram não respondeu para o perfil \1 (bloqueio passageiro de rede)'),
    (r"^(\S+): Command .*timed out.*", r'Instagram demorou demais para responder o perfil \1 (tempo esgotado)'),
    (r'^(\S+): perfil indisponível.*', r'Instagram limitou o acesso ao perfil \1 (ou o perfil mudou de nome)'),
    (r"^(\S+): '[^']*'$", r'Instagram respondeu em formato inesperado para o perfil \1'),
    (r'^coleta falhou \(re-tentativa (\d)/3.*', r'Coleta falhou — nova tentativa automática em 2 minutos (\1ª de 3)'),
    (r'^(\S+): só (\d+)/(\d+) páginas baixaram.*', r'Encarte \1: só \2 de \3 páginas baixaram'),
    (r'^(\S+): nenhuma página baixada.*', r'Nenhuma página do post \1 baixou — fica para a próxima janela'),
    # publicação (linhas [netlify] e cabeçalho datado do publicar_painel.sh)
    (r'^painel publicado em (\S+).*', r'Painel PUBLICADO na internet — a equipe já vê a versão de hoje (\1)'),
    (r'.*token não encontrado.*', 'Publicação: falta configurar o token do Netlify'),
    (r'^publicação no Netlify falhou.*', 'Publicação do painel na internet falhou nesta janela'),
    (r'.*painel ainda não foi gerado hoje.*', 'Publicação adiada: o painel do dia ainda não estava pronto'),
    (r'^falha no deploy: .*', 'Publicação na internet falhou (erro do Netlify)'),
    (r'^rotina em andamento há 45 min.*', 'Publicação adiada: a rotina ainda estava rodando'),
    (r'^painel-encartes\.html não existe.*', 'Publicação: o painel ainda não existe nesta máquina'),
    # rotina / arquivos
    (r'^FALHA: coleta do Instagram \(janela (\d+)h, tentativa (\d)/3\).*', r'Coleta do Instagram falhou (janela das \1h, tentativa \2 de 3)'),
    (r'^FALHA: análise com claude.*', 'Análise dos encartes (Claude) falhou nesta janela'),
    (r'^FALHA: geração do painel.*', 'Geração do painel falhou'),
    (r'^FALHA: (.*)', r'Falhou: \1'),
    (r'^iniciando \(janela (\d+)h, tentativa (\d)/3\).*', r'Rotina iniciada — janela das \1h (tentativa \2 de 3)'),
    (r'^iniciando.*', 'Rotina iniciada'),
    (r'^fila vazia.*', 'Sem posts novos — análise dispensada nesta janela'),
    (r'^painel já gerado hoje.*', 'Painel já estava atualizado hoje — geração dispensada'),
    (r'^sips falhou em (\S+).*', r'Falha ao comprimir a imagem \1 — página fica sem foto no painel'),
    (r'.* corrompido; recomeçando.*', 'Um arquivo de controle estava corrompido e foi reiniciado (sem perda de encartes)'),
    (r'^atualização do banco de preços falhou.*', 'Banco de preços (SQLite) não atualizou nesta janela'),
    (r'^validações de similaridade: (.*)', r'Aprendizado de similaridade — \1'),
    (r'^validações: (.*)', r'Validações de similaridade — \1'),
    (r'^similaridade: (.*)', r'Similaridade automática — \1'),
    # linhas antigas de recursos removidos (radar semanal) que ficaram no log
    (r'^radar: (.*)', r'Radar Scanntech (recurso removido) — \1'),
    (r'^radar (\S.*?): download falhou.*', r'Radar Scanntech (recurso removido): download de \1 falhou'),
    (r'^aplicação das validações de similaridade falhou.*', 'Validações de similaridade não aplicaram nesta janela (tenta na próxima)'),
]


def traduz(m):
    for padrao, simples in TRADUCOES:
        r = re.sub(padrao, simples, m)
        if r != m:
            return r
    return m


def parse_logs(caminho, dias=30):
    corte_log = (datetime.date.today() - datetime.timedelta(days=dias)).isoformat()
    logs, dia, hora_ctx = {}, None, ''

    def entra(hora, tipo, msg):
        e = {'h': hora, 't': tipo, 'm': traduz(msg)}
        if e['m'] != msg:
            e['d'] = msg  # texto técnico original, vira tooltip
        logs.setdefault(dia, []).append(e)

    try:
        with open(caminho, encoding='utf-8', errors='replace') as f:
            for ln in f:
                ln = ln.strip()
                m = re.match(r'^=== (\d{4}-\d{2}-\d{2}) (\d{2}:\d{2}) (.+?) ===$', ln)
                if m:
                    d, hora_ctx, resto = m.groups()
                    dia = d if d >= corte_log else None
                    if not dia:
                        continue
                    if 'FALHA' in resto:
                        entra(hora_ctx, 'falha', resto)
                    elif resto.startswith('concluído'):
                        entra(hora_ctx, 'ok', 'Rotina concluída com sucesso')
                    elif resto.startswith('iniciando'):
                        entra(hora_ctx, 'ok', resto)
                    # demais cabeçalhos (ex.: 'publicação (Netlify)' do
                    # publicar_painel.sh) só datam as linhas seguintes
                elif dia and (ln.startswith('[erro]') or ln.startswith('[aviso]')
                              or ln.startswith('[netlify]') or ln.startswith('[info]')):
                    if ln.startswith('[netlify]'):
                        tipo = 'pub' if 'painel publicado em' in ln else 'aviso'
                    elif ln.startswith('[info]'):
                        tipo = 'ok'
                    else:
                        tipo = 'erro' if ln.startswith('[erro]') else 'aviso'
                    entra(hora_ctx, tipo, ln.split('] ', 1)[-1])
    except OSError:
        pass
    return logs

# a similaridade entre produtos agora é decidida pela análise diária de forma
# automática e VISUAL (similaridade_auto.py gera candidatos; o Claude compara
# as fotos e só une com certeza total) — a aba de validação manual foi removida
n_products = sum(len(products.get(p, [])) for a in data_actions for p in a['pgs'])

# JSON embutido em <script>: um '</' vindo de legenda/log viraria '</script>'
# e encerraria o bloco no meio ('<\/' é escape válido de JSON e de JS).
# '<!--' também é neutralizado: se aparecesse num dado, poderia imitar os
# marcadores dos blocos só-locais e confundir a remoção na publicação.
def jdump(o):
    return (json.dumps(o, ensure_ascii=False)
            .replace('</', '<\\/').replace('<!--', '<\\u0021--'))

html = open(f'{BASE}/painel_template.html', encoding='utf-8').read()
html = html.replace('__ACTIONS__', jdump(data_actions))
html = html.replace('__PRODUCTS__', jdump(products))
html = html.replace('__IMAGES__', jdump(images))
html = html.replace('__CANON__', jdump(canon))
fontes = {}
if os.path.exists(f'{DATA}/coleta_status.json'):
    try:
        fontes = json.load(open(f'{DATA}/coleta_status.json'))
    except Exception:
        fontes = {}
html = html.replace('__FONTES__', jdump(fontes))
html = html.replace('__LOGS__', jdump(parse_logs(f'{DATA}/rotina.log')))
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
# horário da versão que está no ar (gravado pelo publicar_painel.sh no deploy)
pub_quando = _le(f'{DATA}/netlify_pub_em')
if re.match(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}$', pub_quando):
    pub_quando = f'{pub_quando[8:10]}/{pub_quando[5:7]} às {pub_quando[11:16]}'
else:
    pub_quando = '(ainda não publicado)'
html = html.replace('__PUB_QUANDO__', pub_quando)

out = f'{BASE}/painel-encartes.html'
# escrita atômica: quem ler o arquivo (ex.: publicação do meio-dia) nunca vê
# uma versão truncada no meio da gravação dos ~40 MB
tmp_out = f'{out}.tmp'
open(tmp_out, 'w', encoding='utf-8').write(html)
os.replace(tmp_out, out)
print(f'{out} — {os.path.getsize(out)/1024/1024:.2f} MB, {n_products} produtos, {len(data_actions)} encartes')
