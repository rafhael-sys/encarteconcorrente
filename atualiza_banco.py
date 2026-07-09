#!/usr/bin/env python3
"""Sincroniza os JSONs do projeto para data/encartes.db (SQLite).

Os JSONs continuam sendo a fonte da verdade do painel; o banco é a camada de
consulta histórica (série de preços por produto/rede ao longo do tempo).
Regras de segurança:
  - UPSERT sem DELETE: uma linha que entrou no banco nunca sai, mesmo que o
    JSON um dia perca dados — o banco é o arquivo durável de preços.
  - Transação única: ou grava tudo, ou nada (queda no meio não corrompe).
Roda em segundos e é idempotente — pode executar quantas vezes quiser.
"""
import datetime
import json
import os
import re
import sqlite3
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, 'data')
DB = os.path.join(DATA, 'encartes.db')

SCHEMA = """
CREATE TABLE IF NOT EXISTS acoes(
  id            TEXT PRIMARY KEY,
  banner        TEXT NOT NULL,
  segmento      TEXT,
  titulo        TEXT,
  perfil        TEXT,
  inicio        TEXT,          -- AAAA-MM-DD
  fim           TEXT,          -- AAAA-MM-DD
  shortcode     TEXT,
  link          TEXT,
  fonte         TEXT,          -- 'web' ou NULL (Instagram)
  adicionado_em TEXT
);
CREATE TABLE IF NOT EXISTS produtos(
  pid         TEXT NOT NULL,   -- página (ex.: rss_diashow_p1)
  idx         INTEGER NOT NULL,-- posição do produto na página
  acao_id     TEXT NOT NULL REFERENCES acoes(id),
  nome        TEXT NOT NULL,
  preco_texto TEXT,            -- como está impresso ('39,99', 'Leve 3 Pague 2')
  preco       REAL,            -- numérico; NULL quando não é preço (promoção)
  unidade     TEXT,
  canon       TEXT,            -- nome do grupo canônico (mesmo produto entre redes)
  PRIMARY KEY(pid, idx)
);
CREATE INDEX IF NOT EXISTS idx_produtos_canon  ON produtos(canon);
CREATE INDEX IF NOT EXISTS idx_produtos_acao   ON produtos(acao_id);
CREATE INDEX IF NOT EXISTS idx_acoes_periodo   ON acoes(inicio, fim);
CREATE VIEW IF NOT EXISTS precos AS
  SELECT p.canon, p.nome, p.preco, p.preco_texto, p.unidade,
         a.banner, a.segmento, a.inicio, a.fim, a.id AS acao, a.titulo
  FROM produtos p JOIN acoes a ON a.id = p.acao_id;
"""


def preco_num(txt):
    """Mesma regra do painel: último número do texto ('1.299,90' -> 1299.90).
    Devolve None para promoções sem preço ('Leve 3 Pague 2', '20%') — números
    de promoção NÃO podem virar preço, senão poluem o histórico de mínimos."""
    t = str(txt or '')
    if '%' in t or re.search(r'\bleve\b.*\bpague\b', t, re.I):
        return None
    m = re.findall(r'\d{1,3}(?:\.\d{3})+,\d{2}|\d+,\d{2}|\d+(?:\.\d{1,2})?', t)
    if not m:
        return None
    v = m[-1].replace('.', '').replace(',', '.') if ',' in m[-1] else m[-1]
    try:
        return round(float(v), 2)
    except ValueError:
        return None


def carrega(nome, default):
    try:
        with open(os.path.join(DATA, nome)) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def main():
    actions = carrega('actions.json', [])
    products = carrega('products.json', {})
    canon = carrega('canon.json', [])
    if not actions:
        print('nada a sincronizar (actions.json vazio ou ausente)')
        return

    # pid -> nome canônico (mesma montagem de pid do build_painel.py)
    canon_de = {}
    for c in canon:
        for ref in c.get('m', []):
            canon_de[ref] = c['n']

    pid_para_acao = {}
    for a in actions:
        # ação malformada não pode congelar o banco: pula aqui também
        if not a.get('id') or not isinstance(a.get('paginas'), list):
            continue
        for i, fname in enumerate(a['paginas']):
            pid = f"{a['id']}_p{i+1}" if not fname.startswith(a['id']) else fname.replace('.jpg', '')
            pid_para_acao[pid] = a['id']

    con = sqlite3.connect(DB)
    con.executescript(SCHEMA)
    n_acoes = n_prod = 0
    orfaos = []
    ruins = 0
    with con:  # transação única
        for a in actions:
            # registro malformado não pode congelar o banco para sempre:
            # pula com aviso e sincroniza o resto
            if not a.get('id') or not a.get('banner'):
                ruins += 1
                continue
            con.execute(
                'INSERT INTO acoes(id,banner,segmento,titulo,perfil,inicio,fim,'
                'shortcode,link,fonte,adicionado_em) VALUES(?,?,?,?,?,?,?,?,?,?,?) '
                'ON CONFLICT(id) DO UPDATE SET banner=excluded.banner,'
                'segmento=excluded.segmento,titulo=excluded.titulo,'
                'perfil=excluded.perfil,inicio=excluded.inicio,fim=excluded.fim,'
                'shortcode=excluded.shortcode,link=excluded.link,'
                'fonte=excluded.fonte,adicionado_em=excluded.adicionado_em',
                (a['id'], a['banner'], a.get('segmento'), a.get('titulo'),
                 a.get('perfil'), a.get('inicio'), a.get('fim'), a.get('shortcode'),
                 a.get('link'), a.get('fonte'), a.get('adicionado_em')))
            n_acoes += 1
        for pid, lista in products.items():
            acao = pid_para_acao.get(pid)
            if not acao:
                orfaos.append(pid)
                continue
            for i, p in enumerate(lista):
                if not isinstance(p, dict) or not p.get('n'):
                    ruins += 1
                    continue
                con.execute(
                    'INSERT INTO produtos(pid,idx,acao_id,nome,preco_texto,preco,'
                    'unidade,canon) VALUES(?,?,?,?,?,?,?,?) '
                    'ON CONFLICT(pid,idx) DO UPDATE SET nome=excluded.nome,'
                    'preco_texto=excluded.preco_texto,preco=excluded.preco,'
                    'unidade=excluded.unidade,canon=excluded.canon',
                    (pid, i, acao, p['n'], str(p.get('p', '')),
                     preco_num(p.get('p')), p.get('u'), canon_de.get(f'{pid}#{i}')))
                n_prod += 1
            # página re-extraída com MENOS itens: remove o excedente antigo,
            # senão a correção convive com linhas fantasma da extração anterior
            # (a durabilidade sem DELETE vale para páginas ausentes do JSON,
            # não para o conteúdo atual de uma página presente)
            con.execute('DELETE FROM produtos WHERE pid=? AND idx>=?',
                        (pid, len(lista)))
    tot_a, tot_p = (con.execute(f'SELECT COUNT(*) FROM {t}').fetchone()[0]
                    for t in ('acoes', 'produtos'))
    con.close()
    if orfaos:
        print(f'[aviso] {len(orfaos)} páginas de products.json sem ação correspondente '
              f'(ignoradas): {", ".join(orfaos[:5])}', file=sys.stderr)
    if ruins:
        print(f'[aviso] {ruins} registros malformados nos JSONs pulados na '
              f'sincronização do banco', file=sys.stderr)
    print(f'banco atualizado: {n_acoes} ações e {n_prod} produtos sincronizados '
          f'(total no banco: {tot_a} ações, {tot_p} produtos)')


if __name__ == '__main__':
    main()
