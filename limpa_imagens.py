#!/usr/bin/env python3
"""Apaga só as IMAGENS de encartes vencidos há mais de N dias (padrão 60).

Objetivo: impedir que o repositório cresça sem limite. PRESERVA todos os
dados — actions.json, products.json, canon.json e o banco de preços continuam
intactos. Só os arquivos .jpg das páginas são removidos (de data/pages e de
data/arquivo/pages). O histórico de preços (aba Incidência do painel) segue
funcionando normalmente mesmo sem as fotos.

O corte usa a data de término (campo 'fim') de cada encarte. Como o painel só
mostra as imagens até 30 dias após o vencimento, apagar as de 60+ dias nunca
tira imagem de nada que ainda esteja visível no painel.

Dias de retenção configuráveis pela variável de ambiente DIAS_MANTER_IMAGENS.
"""
import datetime
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, 'data')
PAGES = os.path.join(DATA, 'pages')
ARQUIVO = os.path.join(DATA, 'arquivo', 'pages')

try:
    DIAS = int(os.environ.get('DIAS_MANTER_IMAGENS', '60'))
except ValueError:
    DIAS = 60


def main():
    try:
        with open(os.path.join(DATA, 'actions.json')) as f:
            actions = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return

    corte = (datetime.date.today() - datetime.timedelta(days=DIAS)).isoformat()
    apagadas = 0
    for a in actions:
        fim = str(a.get('fim', '')).strip()
        if not fim or fim >= corte:
            continue  # sem data, ou ainda dentro da janela de retenção: mantém
        for fname in a.get('paginas', []):
            for pasta in (PAGES, ARQUIVO):
                caminho = os.path.join(pasta, fname)
                if os.path.exists(caminho):
                    try:
                        os.remove(caminho)
                        apagadas += 1
                    except OSError:
                        pass

    if apagadas:
        print(f'[limpeza] {apagadas} imagem(ns) de encartes vencidos há mais de '
              f'{DIAS} dias removida(s) — preços e datas preservados')


if __name__ == '__main__':
    main()
