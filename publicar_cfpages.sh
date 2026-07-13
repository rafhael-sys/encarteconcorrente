#!/usr/bin/env bash
# Publica o painel no CLOUDFLARE PAGES protegido por senha.
#
# Espelho do publicar_surge.sh — só troca o DESTINO. Tudo mais é igual:
#   - os arquivos do gate saem do gera_gate.py: index.html + painel.enc +
#     imagens.enc.000, .001, … (fotos cifradas em pedaços)
#   - a senha continua CLIENT-SIDE (AES-256 no navegador) — funciona em
#     qualquer host estático, então o Cloudflare protege igual ao Netlify/Surge
#   - deploy via `wrangler pages deploy` no projeto encartes-redemais
#
# Por que Cloudflare Pages: grátis, banda ILIMITADA (resolve o custo do
# Netlify) e CONFIÁVEL — sem o erro 410 imprevisível do Surge para ~40 MB.
# Limite de 25 MB por arquivo; os pedaços do gera_gate.py já ficam bem abaixo.
#
# Pré-requisitos (uma vez):
#   ~/.config/painel_senha  — senha de acesso (ou variável PAINEL_SENHA)
#   login do Cloudflare já feito na máquina: `npx wrangler login`
#   (fica salvo; ou use a variável CLOUDFLARE_API_TOKEN)
#
# Uso:
#   ./publicar_cfpages.sh            publica agora (manual)
#   ./publicar_cfpages.sh --diario   publica no máximo 1x por dia (rotina)

set -euo pipefail
BASE="$(cd "$(dirname "$0")" && pwd)"
SENHA_FILE="$HOME/.config/painel_senha"
URL_FILE="$BASE/data/cfpages_url"
PUBEM_FILE="$BASE/data/cfpages_pub_em"
STAMP_FILE="$BASE/data/.pub_stamp"
LOCK="$BASE/data/.lock"
PAINEL="$BASE/painel-encartes.html"
PROJETO="encartes-redemais"
DOMINIO="$PROJETO.pages.dev"

DIARIO=0
[[ "${1:-}" == "--diario" ]] && DIARIO=1
HOJE=$(date +%Y-%m-%d)
if (( DIARIO )) && [[ "$(cat "$STAMP_FILE" 2>/dev/null)" == "$HOJE" ]]; then
  exit 0   # a publicação de hoje já foi
fi
echo "=== $(date '+%Y-%m-%d %H:%M') publicação (Cloudflare Pages) ==="

[[ -s "$PAINEL" ]] || { echo "[cf] painel-encartes.html não existe — nada a publicar"; exit 1; }

# na rotina diária, não gasta a publicação do dia com um painel que a equipe JÁ
# recebeu; mas publica um painel antigo se ele for mais novo que a última publicação.
# data de modificação do painel, portátil: macOS (stat -f) primeiro, depois
# Linux (stat -c). O encadeamento com || evita que uma variante que não existe
# na plataforma derrube o script por causa do `set -euo pipefail`.
PAINEL_DIA=$(stat -f %Sm -t %Y-%m-%d "$PAINEL" 2>/dev/null || stat -c %y "$PAINEL" 2>/dev/null | cut -d' ' -f1 || echo "1970-01-01")
ULT_PUB=$(cat "$STAMP_FILE" 2>/dev/null || echo "1970-01-01")
if (( DIARIO )) && [[ "$PAINEL_DIA" != "$HOJE" ]] && [[ ! "$PAINEL_DIA" > "$ULT_PUB" ]]; then
  echo "[cf] painel ainda não foi gerado hoje — publicação fica para a próxima janela"
  exit 0
fi

# senha: do arquivo local (macOS) OU da variável de ambiente
if [[ ! -s "$SENHA_FILE" ]]; then
  if [[ -n "${PAINEL_SENHA:-}" ]]; then
    SENHA_FILE="$(mktemp)"; printf '%s' "$PAINEL_SENHA" > "$SENHA_FILE"
  else
    echo "[cf] senha não encontrada (nem $SENHA_FILE nem \$PAINEL_SENHA) — não publico sem proteção"; exit 1
  fi
fi

# credencial do Cloudflare para deploy NÃO-interativo (rotina/launchd): a
# automação precisa de um API TOKEN — o `wrangler login` (OAuth) só vale em
# terminal interativo. Lê de ~/.config/cloudflare_token ou da variável de ambiente.
if [[ -z "${CLOUDFLARE_API_TOKEN:-}" ]] && [[ -s "$HOME/.config/cloudflare_token" ]]; then
  export CLOUDFLARE_API_TOKEN="$(tr -d '[:space:]' < "$HOME/.config/cloudflare_token")"
fi
if [[ -z "${CLOUDFLARE_API_TOKEN:-}" ]]; then
  echo "[cf] falta o API token do Cloudflare (defina CLOUDFLARE_API_TOKEN ou grave em ~/.config/cloudflare_token)"; exit 1
fi

# trava compartilhada com run_daily.sh: nunca ler o painel enquanto a rotina pode
# estar reescrevendo-o. Quando o run_daily nos chama, ele já segura a trava.
TRAVA_MINHA=0
if [[ "${ENCARTES_LOCK_HERDADA:-0}" != "1" ]]; then
  ESPERA=0
  until mkdir "$LOCK" 2>/dev/null; do
    if [[ -n "$(find "$LOCK" -maxdepth 0 -mmin +120 2>/dev/null)" ]]; then
      rm -rf "$LOCK" 2>/dev/null; continue                    # trava órfã (>2h)
    fi
    if (( ESPERA >= 2700 )); then
      echo "[cf] rotina em andamento há 45 min — deixo para a próxima janela"; exit 1
    fi
    sleep 60; ESPERA=$((ESPERA + 60))
  done
  TRAVA_MINHA=1
  echo $$ > "$LOCK/dono"
fi
TMP=$(mktemp -d)
limpa(){ rm -rf "$TMP"; (( TRAVA_MINHA )) && [[ "$(cat "$LOCK/dono" 2>/dev/null)" == "$$" ]] && rm -rf "$LOCK"; return 0; }
trap limpa EXIT

# porta com senha + painel criptografado (miolo + fotos em pedaços) — idêntico ao Netlify
python3 "$BASE/gera_gate.py" "$PAINEL" "$TMP" "$SENHA_FILE"

# garante que o projeto Pages existe (idempotente; ignora "já existe").
# produção fixada no branch main -> o deploy --branch=main serve no domínio raiz.
npx --yes wrangler pages project create "$PROJETO" --production-branch=main >/dev/null 2>&1 || true

# deploy no Cloudflare Pages (auth vem do wrangler login ou de CLOUDFLARE_API_TOKEN;
# --commit-dirty evita o aviso de "há mudanças não commitadas" no launchd)
if ! npx --yes wrangler pages deploy "$TMP" --project-name="$PROJETO" --branch=main --commit-dirty=true > "$TMP/cf.log" 2>&1; then
  echo "[cf] falha no deploy:"; grep -viE "npm warn|npm notice" "$TMP/cf.log" | tail -8 || true
  exit 1
fi
grep -viE "npm warn|npm notice" "$TMP/cf.log" | tail -4 || true

# deploy confirmado: carimbos (o build_painel.py lê data/cfpages_url e data/cfpages_pub_em)
URL="https://$DOMINIO"
echo "$URL" > "$URL_FILE"
date '+%Y-%m-%dT%H:%M' > "$PUBEM_FILE"
(( DIARIO )) && echo "$HOJE" > "$STAMP_FILE"
echo "[cf] painel publicado em $URL (protegido por senha)"
