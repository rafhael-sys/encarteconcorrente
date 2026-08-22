#!/usr/bin/env python3
"""Finaliza a janela 2026-08-22: esvazia fila e candidatos, grava resumo."""
import json
import os


def salva(p, data):
    with open(p + '.tmp', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    os.replace(p + '.tmp', p)


salva('data/similaridade_candidatos.json', [])
salva('data/fila_novos.json', [])

resumo = ('6 concorrentes com encarte novo (Favorito, Mar Vermelho, Leva Mais, '
          'Santo Antônio, Atacadão e Nosso) — 9 ações, 114 produtos')
with open('data/resumo_notificacao.txt.tmp', 'w', encoding='utf-8') as f:
    f.write(resumo + '\n')
os.replace('data/resumo_notificacao.txt.tmp', 'data/resumo_notificacao.txt')

print('fila e candidatos esvaziados; resumo gravado:')
print(resumo)
