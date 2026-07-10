# Orientações do projeto (encartes concorrentes)

## Princípio nº 1 — Essencial, sempre

O dono do projeto gosta de **tudo no essencial**: simples, limpo, sem excesso.
Este é o princípio que manda em qualquer decisão de design, código ou texto.

Na prática, ao mexer neste projeto:

- **Interface (painel):** só o necessário. Nada de textos supérfluos, selos,
  rótulos, avisos ou enfeites que não ajudem de fato. Menos é mais. Se um
  elemento não for essencial para a pessoa decidir/entender, ele não entra.
- **Código:** prefira sempre a solução mais simples que resolve. Nada de camadas,
  dependências ou complexidade que não sejam realmente precisas. Evite "gambiarra"
  e evite over-engineering — o meio-termo enxuto.
- **Funcionalidades:** não adicione recurso que ninguém pediu. Resolva o problema
  pedido, sem "brindes". Ideias extras vão para `MELHORIAS_FUTURAS.md`, não para
  dentro do produto sem combinar.
- **Comunicação:** o dono é leigo em programação ("vibe code"). Explique em
  português simples, direto, e **sempre mande o link** quando falar de algo que
  ele precise abrir/clicar.

Na dúvida entre duas opções, escolha a mais **enxuta**.

## Princípio nº 2 — Rápido, sempre

**O sistema não pode ficar lento.** Tudo é pensado para eficiência e
velocidade, e para que uma pessoa do setor comercial — leiga, no celular,
com pressa — use com muita facilidade.

- **Painel:** carregamento leve (fotos fora do miolo, em segundo plano),
  busca instantânea, cliques respondendo na hora. Botões com rótulo claro e
  alvo grande.
- **Recurso novo só entra se não pesar:** nada de servidor extra, biblioteca
  externa ou processamento pesado no aparelho. O que puder ser feito no
  navegador com o que já está na página, é assim que se faz.
- **Na dúvida, meça antes de publicar** (peso do painel e tempo de resposta).

## Como a rotina roda (resumo)

- Roda 100% na nuvem (GitHub Actions), 3x/dia (~07h/13h/20h de Natal), sem
  depender de Mac. O maestro é o `run_cloud.sh`; o agendamento fica em
  `.github/workflows/encartes.yml`.
- A rotina coleta encartes (Instagram + web), o Claude lê os preços, monta o
  painel e publica no Netlify (mesmo link, protegido por senha).
- Regras por concorrente ficam em `profiles.json` (campo `regra`) — ex.: o
  SuperFácil ignora ofertas de João Pessoa/PB (só monitoramos o RN).
