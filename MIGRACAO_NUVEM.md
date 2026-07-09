# Rodar os encartes na nuvem (sem o Mac)

Este guia liga a rotina dos encartes no **GitHub Actions** — de graça, sem
depender do seu Mac ligado. A rotina passa a rodar sozinha nos horários
7h / 13h / 19h (horário de Natal).

## O que mudou no projeto (já está pronto)

As peças que só funcionavam no Mac foram trocadas por versões que rodam no Linux:

| Peça de Mac | Trocada por |
|---|---|
| `pdf2jpg` (Swift/Apple) — converte o PDF do Atacadão | `tools/pdf2jpg.py` (PyMuPDF) |
| `sips` — redimensiona as imagens do painel | Pillow (dentro do `build_painel.py`) |
| `launchd` — agendador do Mac | agendador do GitHub (`.github/workflows/encartes.yml`) |
| `osascript` — notificações do Mac | removidas (não fazem falta na nuvem) |
| senhas em `~/.config/...` | "Segredos" do GitHub (variáveis de ambiente) |

O `run_cloud.sh` é o novo "maestro" na nuvem (equivalente ao `run_daily.sh`).
Nada disso quebra o Mac — os scripts continuam funcionando nas duas máquinas.

---

## Passo 1 — Adicionar os 3 segredos no GitHub

No GitHub, abra o repositório → **Settings** → (menu esquerdo) **Secrets and
variables** → **Actions** → botão **New repository secret**. Crie estes 3:

| Name (exatamente assim) | Value (o que colar) |
|---|---|
| `NETLIFY_TOKEN` | seu token do Netlify — no Mac: `cat ~/.config/netlify_token` |
| `PAINEL_SENHA` | a senha do painel — no Mac: `cat ~/.config/painel_senha` |
| `CLAUDE_CODE_OAUTH_TOKEN` | rode `claude setup-token` no Mac e cole o token gerado |

> Alternativa ao Claude: se preferir pagar por uso em vez do plano Max, crie
> uma chave em https://console.anthropic.com/settings/keys e salve como segredo
> `ANTHROPIC_API_KEY` (em vez do `CLAUDE_CODE_OAUTH_TOKEN`).

## Passo 2 — Subir as imagens dos encartes (preserva a visão de hoje)

As imagens ficam só no Mac hoje. Sem elas, o painel na nuvem sai sem os
encartes. No Mac, mande o Claude Code subir a pasta `data/pages` (e o arquivo
histórico `data/arquivo`, se existir).

## Passo 3 — Ligar e testar

1. Aba **Actions** do repositório → workflow **"Encartes — coleta e
   publicação"** → botão **Run workflow** (isso roda uma vez na hora, pra testar).
2. Acompanhe os passos. Ao final, abra o painel no Netlify e confira se os
   encartes e as imagens apareceram.
3. Deu certo? Então faça o **merge para o branch `main`** — é isso que liga o
   **agendamento automático** (o schedule só roda a partir do `main`).

## Passo 4 — Desligar o Mac (só depois que a nuvem estiver 100%)

Quando o painel na nuvem estiver atualizando sozinho por 1–2 dias, aí sim você
pode desativar a rotina do Mac (o `launchd`) e parar de depender dele.

---

## Coisas para saber

- **Custo:** GitHub Actions é grátis para repositório privado dentro da cota
  mensal (larga para este uso). O Claude usa seu plano Max (via o token) ou a
  API paga, se você escolher essa opção.
- **Horário:** o agendador do GitHub não é exato — pode atrasar alguns minutos.
- **Instagram:** a coleta passa a sair de um IP de data center; o Instagram
  bloqueia esses IPs com mais frequência do que o da sua casa. Se a coleta ficar
  instável, a solução é adicionar um "proxy" (peça ajuda ao Claude).
- **Limitação conhecida:** a correção manual de produtos parecidos feita pelo
  botão de exportar do painel (que hoje cai em `~/Downloads`) **não** é ingerida
  sozinha na nuvem. A comparação **automática** por foto (feita pelo Claude)
  continua funcionando normalmente.
