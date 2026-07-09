#!/usr/bin/env python3
"""Converte um PDF em JPGs — substituto multiplataforma do pdf2jpg.swift (macOS).

Uso: pdf2jpg.py <entrada.pdf> <prefixo_saida> [larguraMax=1400]

Gera <prefixo>_p1.jpg, <prefixo>_p2.jpg, ... e imprime o caminho de cada
página gerada (uma por linha), exatamente como o binário Swift nativo — assim
o collect_web.py consome a saída sem precisar saber qual conversor rodou.
"""
import sys

try:
    import fitz  # PyMuPDF
except Exception as e:  # pragma: no cover
    sys.stderr.write(f'pdf2jpg.py: PyMuPDF (fitz) não instalado ({e})\n')
    sys.exit(1)


def main():
    if len(sys.argv) < 3:
        sys.stderr.write('uso: pdf2jpg.py entrada.pdf prefixo_saida [largura]\n')
        sys.exit(1)
    entrada, prefixo = sys.argv[1], sys.argv[2]
    max_w = float(sys.argv[3]) if len(sys.argv) > 3 else 1400.0

    doc = fitz.open(entrada)
    for i, page in enumerate(doc, start=1):
        largura_pt = page.rect.width or max_w
        escala = max_w / largura_pt
        pix = page.get_pixmap(matrix=fitz.Matrix(escala, escala), alpha=False)
        out = f'{prefixo}_p{i}.jpg'
        try:
            # 85: os encartes têm muito texto pequeno; 72 deixava os preços
            # com "sujeira" de compressão visível no zoom
            pix.save(out, jpg_quality=85)
        except TypeError:
            # versões antigas do PyMuPDF não aceitam jpg_quality
            pix.save(out)
        print(out)


if __name__ == '__main__':
    main()
