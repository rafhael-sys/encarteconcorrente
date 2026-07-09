#!/bin/zsh
# Publica o painel no Netlify protegido por senha — só precisa de curl, zip e python3.
#
# O que sobe: index.html (página que pede a senha) + painel.enc (painel
# criptografado com AES-256; a senha nunca sai da máquina). A engrenagem
# local é removida antes de criptografar (gera_gate.py garante).
#
# Pré-requisitos (uma única vez):
#   ~/.config/netlify_token — token pessoal do Netlify
#   ~/.config/painel_senha  — senha que os colegas usam para entrar
#
# Uso:
#   ./publicar_painel.sh            publica agora (manual)
#   ./publicar_painel.sh --diario   publica no máximo 1x por dia (rotina)

set -euo pipefail
BASE="$(cd "$(dirname "$0")" && pwd)"
TOKEN_FILE="$HOME/.config/netlify_token"
SENHA_FILE="$HOME/.config/painel_senha"
SITE_FILE="$BASE/data/netlify_site_id"
URL_FILE="$BASE/data/netlify_url"
STAMP_FILE="$BASE/data/.pub_stamp"
LOCK="$BASE/data/.lock"
PAINEL="$BASE/painel-encartes.html"
API="https://api.netlify.com/api/v1"
CURL=(curl -sS --connect-timeout 20)

DIARIO=0
[[ "${1:-}" == "--diario" ]] && DIARIO=1
HOJE=$(date +%Y-%m-%d)
if (( DIARIO )) && [[ "$(cat "$STAMP_FILE" 2>/dev/null)" == "$HOJE" ]]; then
  exit 0   # a publicação de hoje já foi
fi
# cabeçalho datado: dá dia/hora corretos às linhas [netlify] na aba Logs,
# inclusive nos caminhos de pulo/falha abaixo (que não têm outro cabeçalho)
echo "=== $(date '+%Y-%m-%d %H:%M') publicação (Netlify) ==="

[[ -s "$PAINEL" ]] || { echo "[netlify] painel-encartes.html não existe — nada a publicar"; exit 1; }
# na rotina diária, não gasta a publicação do dia com um painel que a equipe
# JÁ recebeu (ex.: janela das 7h ainda rodando às 9h) — mas se o painel local
# for mais novo que a última publicação (coleta falhando há dias, painel de
# ontem à tarde nunca publicado), publica assim mesmo: melhor a versão de
# ontem do que deixar a equipe presa numa ainda mais velha.
PAINEL_DIA=$(stat -f %Sm -t %Y-%m-%d "$PAINEL" 2>/dev/null || echo "1970-01-01")
ULT_PUB=$(cat "$STAMP_FILE" 2>/dev/null || echo "1970-01-01")
if (( DIARIO )) && [[ "$PAINEL_DIA" != "$HOJE" ]] && [[ ! "$PAINEL_DIA" > "$ULT_PUB" ]]; then
  echo "[netlify] painel ainda não foi gerado hoje — publicação fica para a próxima janela"
  exit 0
fi
[[ -s "$TOKEN_FILE" ]] || { echo "[netlify] token não encontrado em $TOKEN_FILE"; exit 1; }
[[ -s "$SENHA_FILE" ]] || { echo "[netlify] senha não encontrada em $SENHA_FILE — não publico sem proteção"; exit 1; }
TOKEN="$(tr -d '[:space:]' < "$TOKEN_FILE")"

# trava compartilhada com run_daily.sh: nunca ler o painel enquanto a rotina
# pode estar reescrevendo-o. Quando o run_daily nos chama, ele já segura a
# trava e avisa via ENCARTES_LOCK_HERDADA=1.
TRAVA_MINHA=0
if [[ "${ENCARTES_LOCK_HERDADA:-0}" != "1" ]]; then
  ESPERA=0
  until mkdir "$LOCK" 2>/dev/null; do
    if [[ -n "$(find "$LOCK" -maxdepth 0 -mmin +120 2>/dev/null)" ]]; then
      rm -rf "$LOCK" 2>/dev/null; continue                    # trava órfã (>2h)
    fi
    if (( ESPERA >= 2700 )); then
      echo "[netlify] rotina em andamento há 45 min — deixo para a próxima janela"
      exit 1
    fi
    sleep 60; ESPERA=$((ESPERA + 60))
  done
  TRAVA_MINHA=1
  echo $$ > "$LOCK/dono"   # só removemos a trava se ela ainda for nossa
fi
TMP=$(mktemp -d)
limpa(){ rm -rf "$TMP"; (( TRAVA_MINHA )) && [[ "$(cat "$LOCK/dono" 2>/dev/null)" == "$$" ]] && rm -rf "$LOCK"; return 0; }
trap limpa EXIT

json_get() {  # json_get <campo> — lê um campo do JSON no stdin; vazio se não for JSON
  /usr/bin/python3 -c "
import sys, json
try:
    print(json.load(sys.stdin).get('$1') or '')
except Exception:
    print('')"
}

# ---- cria o site na primeira vez ----
if [[ ! -s "$SITE_FILE" ]]; then
  RESP=$("${CURL[@]}" --max-time 60 -X POST "$API/sites" \
    -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
    -d '{"name":"encartes-redemais"}')
  SITE_ID=$(echo "$RESP" | json_get id)
  if [[ -z "$SITE_ID" ]]; then
    # nome ocupado ou erro recuperável: deixa o Netlify sortear um nome
    RESP=$("${CURL[@]}" --max-time 60 -X POST "$API/sites" \
      -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d '{}')
    SITE_ID=$(echo "$RESP" | json_get id)
  fi
  [[ -n "$SITE_ID" ]] || { echo "[netlify] falha ao criar o site: ${RESP:0:300}"; exit 1; }
  echo "$SITE_ID" > "$SITE_FILE"
fi
SITE_ID="$(cat "$SITE_FILE")"

# ---- porta com senha + painel criptografado ----
/usr/bin/python3 "$BASE/gera_gate.py" "$PAINEL" "$TMP" "$SENHA_FILE"
(cd "$TMP" && /usr/bin/zip -q site.zip index.html painel.enc)

# ---- publica ----
RESP=$("${CURL[@]}" --max-time 900 -X POST "$API/sites/$SITE_ID/deploys" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/zip" \
  --data-binary "@$TMP/site.zip")
DEPLOY_ID=$(echo "$RESP" | json_get id)
[[ -n "$DEPLOY_ID" ]] || { echo "[netlify] falha no deploy: ${RESP:0:300}"; exit 1; }

# deploy confirmado: o carimbo diário entra já, antes de qualquer passo opcional
(( DIARIO )) && echo "$HOJE" > "$STAMP_FILE"
# horário da versão no ar — a engrenagem do painel local mostra este valor
date '+%Y-%m-%dT%H:%M' > "$BASE/data/netlify_pub_em"

URL=$("${CURL[@]}" --max-time 60 "$API/sites/$SITE_ID" -H "Authorization: Bearer $TOKEN" | json_get ssl_url || true)
[[ -n "$URL" ]] && echo "$URL" > "$URL_FILE"
[[ -z "$URL" ]] && URL="$(cat "$URL_FILE" 2>/dev/null || echo '(URL indisponível agora — veja data/netlify_url mais tarde)')"
echo "[netlify] painel publicado em $URL (protegido por senha)"
