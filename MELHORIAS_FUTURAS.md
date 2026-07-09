# Melhorias futuras (backlog) — painel de encartes

Ideias combinadas com o Rafhael para um review dedicado. Nada aqui é urgente;
a rotina já funciona na nuvem. Objetivo: deixar a ferramenta mais inteligente e
eficiente, sem mudar o que ela já entrega bem.

## 1. Aba "Agressivos" — detectar guerra de preços (não só 10% abaixo do costume)
**Hoje:** um produto entra se o preço vigente está ≥10% abaixo do preço mais
praticado (moda) de todo o histórico dele.

**Problema (feeling do Rafhael):** isso não captura a *tendência* de queda entre
concorrentes. Ex.: A põe a 10,00 hoje; B a 9,50 amanhã; C a 8,99 duas semanas
depois. Cada passo é pequeno (<10%), mas o movimento pra baixo **é agressivo**.

**Direção da melhoria:**
- Comparar o melhor preço vigente com o **valor recente que estava rolando**
  (ex.: mediana/moda dos últimos ~30-45 dias), não com a moda de todo o histórico.
- **Remover o corte fixo de 10%** (ou baixá-lo bastante) e valorizar a
  **direção/tendência** de queda ao longo do tempo entre lojas.
- Considerar sinalizar "guerra de preços" quando 2+ concorrentes vão se
  cortando pra baixo em sequência.
- Manter o guarda de queda >65% (filtra agrupamento errado).
- Rankear por: tamanho do corte vs. valor recente + consistência da queda.

## 2. Casamento de produtos iguais (canon) — vários sinais, só com certeza
**Feeling do Rafhael:** o Claude deve decidir se dois produtos são o mesmo
usando **vários indicadores juntos** e só unir quando tiver **certeza**:
- **marca**, **tamanho/variante**, **descrição/nome**, **foto** (já usados)
- **preço parecido** como sinal ADICIONAL (ainda não usado)
- Dúvida → **não unir** (deixa para reavaliar quando houver mais dados)
- A precisão **melhora com o acúmulo** de fotos e histórico de preços.

**Direção da melhoria:** reforçar o prompt diário do Claude para pesar o
**preço parecido** junto com marca/descrição/foto ao decidir "mesmo produto",
mantendo o critério de CERTEZA TOTAL e o registro de pares incertos.

## 3. Ponte da validação manual na nuvem
O botão de exportar validações do painel (marcar "mesmo/diferente") caía em
`~/Downloads` e era lido pelo `aplica_validacoes.py`. Na nuvem não existe
`~/Downloads`, então essa correção manual não é aplicada sozinha. A comparação
**automática por foto (Claude) continua funcionando**. Falta uma ponte para o
usuário conseguir corrigir agrupamentos manualmente também na nuvem (ex.:
commitar o JSON exportado em `data/validacoes_inbox/`).

## 4. Review de eficiência ("fazer mais com menos")
Varredura do código procurando: trabalho desnecessário, coisas relidas/
recalculadas à toa, repetições, e passos puláveis quando não há novidade — para
a rotina ficar mais rápida e usar menos o Claude/Max, sem mudar o resultado.

## 5. Observação sobre o Assaí
Quando o Assaí anuncia a oferta mas ainda não subiu a imagem do encarte, não há
o que baixar (nem re-tentando). A oferta entra na próxima coleta, quando a arte
for publicada. Isso é comportamento correto, não bug.
