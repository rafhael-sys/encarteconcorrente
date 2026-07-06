# Prompt aprovado — Correções de monitoramento (06/07/2026)

Contexto: painel local vanilla (painel_template.html + build_painel.py + data/*.json),
rotina 3/3h (run_daily.sh), design ChatGPT, português, desktop-only, sem nuvem.
Objetivo da ferramenta: MONITORAR (comparação é secundária).

1. Feed "Desde sua última visita" — topo de Vigentes, só com novidade; uma linha por
   encarte novo (clique abre o visor; máx. 8 + "e mais N"); linha agregada de expirados
   desde a visita; última visita via localStorage; recarregar = visto.
2. Saúde das fontes — coletores gravam data/coleta_status.json (por fonte: última coleta
   ok + último erro; escrita atômica); pílula "Fontes ✓/⚠" no header, clique abre lista
   (verde <24h, âmbar >24h, vermelho >48h/erro).
3. Notificação informativa — análise escreve data/resumo_notificacao.txt (1 linha);
   run_daily.sh usa como corpo da notificação, com fallback ao texto padrão.

Restrições: design system existente; nunca apagar histórico; escritas atômicas;
validação py_compile + zsh -n + JavaScriptCore + rebuild; commits separados.
Fora de escopo: abertura instantânea, timeline por concorrente, hover-prévia,
expirados por semana, sparkline.
