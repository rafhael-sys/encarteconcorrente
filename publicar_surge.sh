#!/usr/bin/env bash
# Publica o painel no SURGE protegido por senha — espelho do publicar_painel.sh.
#
# Só troca o DESTINO (Netlify -> Surge). Tudo mais é igual:
#   - os 3 arquivos do gate saem do gera_gate.py: index.html + painel.enc + imagens.enc
#   - a senha continua CLIENT-SIDE (AES-256 no navegador) — funciona em qualquer
#     host estático, então o Surge protege igual ao Netlify
#   - deploy via `npx surge <pasta> encartes-redemais.surge.sh`
#
# Por que Surge: o grátis do Netlify é medido (banda/build) e o painel de ~45 MB
# republicado todo dia estoura o limite. O grátis do Surge não mede banda assim.
#
# Pré-requisitos (uma vez):
#   ~/.config/painel_senha  — senha de acesso (ou variável PAINEL_SENHA)
#   login do Surge já feito na máquina (`npx surge login`) — fica no ~/.netrc
#
# Uso:
#   ./publicar_surge.sh            publica agora (manual)
#   ./publicar_surge.sh --diario   publica no máximo 1x por dia (rotina)

set -euo pipefail
BASE="$(cd "$(dirname "$0")" && pwd)"
SENHA_FILE="$HOME/.config/painel_senha"
URL_FILE="$BASE/data/surge_url"
PUBEM_FILE="$BASE/data/surge_pub_em"
STAMP_FILE="$BASE/data/.pub_stamp"
LOCK="$BASE/data/.lock"
PAINEL="$BASE/painel-encartes.html"
DOMINIO="encartes-redemais.surge.sh"

DIARIO=0
[[ "${1:-}" == "--diario" ]] && DIARIO=1
HOJE=$(date +%Y-%m-%d)
if (( DIARIO )) && [[ "$(cat "$STAMP_FILE" 2>/dev/null)" == "$HOJE" ]]; then
  exit 0   # a publicação de hoje já foi
fi
echo "=== $(date '+%Y-%m-%d %H:%M') publicação (Surge) ==="

[[ -s "$PAINEL" ]] || { echo "[surge] painel-encartes.html não existe — nada a publicar"; exit 1; }

# na rotina diária, não gasta a publicação do dia com um painel que a equipe JÁ
# recebeu; mas publica um painel antigo se ele for mais novo que a última publicação
PAINEL_DIA=$(stat -c %y "$PAINEL" 2>/dev/null | cut -d' ' -f1)
[[ -n "$PAINEL_DIA" ]] || PAINEL_DIA=$(stat -f %Sm -t %Y-%m-%d "$PAINEL" 2>/dev/null)
[[ -n "$PAINEL_DIA" ]] || PAINEL_DIA="1970-01-01"
ULT_PUB=$(cat "$STAMP_FILE" 2>/dev/null || echo "1970-01-01")
if (( DIARIO )) && [[ "$PAINEL_DIA" != "$HOJE" ]] && [[ ! "$PAINEL_DIA" > "$ULT_PUB" ]]; then
  echo "[surge] painel ainda não foi gerado hoje — publicação fica para a próxima janela"
  exit 0
fi

# senha: do arquivo local (macOS) OU da variável de ambiente
if [[ ! -s "$SENHA_FILE" ]]; then
  if [[ -n "${PAINEL_SENHA:-}" ]]; then
    SENHA_FILE="$(mktemp)"; printf '%s' "$PAINEL_SENHA" > "$SENHA_FILE"
  else
    echo "[surge] senha não encontrada (nem $SENHA_FILE nem \$PAINEL_SENHA) — não publico sem proteção"; exit 1
  fi
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
      echo "[surge] rotina em andamento há 45 min — deixo para a próxima janela"; exit 1
    fi
    sleep 60; ESPERA=$((ESPERA + 60))
  done
  TRAVA_MINHA=1
  echo $$ > "$LOCK/dono"
fi
TMP=$(mktemp -d)
limpa(){ rm -rf "$TMP"; (( TRAVA_MINHA )) && [[ "$(cat "$LOCK/dono" 2>/dev/null)" == "$$" ]] && rm -rf "$LOCK"; return 0; }
trap limpa EXIT

# porta com senha + painel criptografado (miolo + fotos separadas) — idêntico ao Netlify
python3 "$BASE/gera_gate.py" "$PAINEL" "$TMP" "$SENHA_FILE"

# deploy no Surge (login vem do ~/.netrc; --yes evita o prompt do npx no launchd)
if ! npx --yes surge "$TMP" "$DOMINIO" > "$TMP/surge.log" 2>&1; then
  echo "[surge] falha no deploy:"; grep -viE "npm warn|npm notice" "$TMP/surge.log" | tail -6 || true
  exit 1
fi
grep -viE "npm warn|npm notice" "$TMP/surge.log" | tail -3 || true

# deploy confirmado: carimbos (o build_painel.py lê data/surge_url e data/surge_pub_em)
URL="https://$DOMINIO"
echo "$URL" > "$URL_FILE"
date '+%Y-%m-%dT%H:%M' > "$PUBEM_FILE"
(( DIARIO )) && echo "$HOJE" > "$STAMP_FILE"
echo "[surge] painel publicado em $URL (protegido por senha)"
