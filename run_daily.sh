#!/bin/zsh
# Rotina diária dos encartes: roda 1x por dia a partir das 07:00.
# O launchd chama este script a cada 30 min; ele sai de imediato se já rodou
# hoje ou se ainda não deu 7h — assim, se o Mac estava dormindo/desligado às 7h,
# a atualização acontece na primeira meia hora depois que você abrir o Mac.

BASE="$HOME/encartes-concorrentes"
STAMP="$BASE/data/.ultima_execucao"
LOG="$BASE/data/rotina.log"
mkdir -p "$BASE/data"

HOJE=$(date +%Y-%m-%d)
HORA=$(date +%H)

[[ -f "$STAMP" && "$(cat "$STAMP")" == "$HOJE" ]] && exit 0   # já rodou hoje
[[ "$HORA" -lt 7 ]] && exit 0                                  # antes das 7h

{
  echo "=== $(date '+%Y-%m-%d %H:%M') iniciando coleta ==="
  /usr/bin/python3 "$BASE/collect.py" || exit 1

  # Extração/classificação com Claude (headless): classifica os posts da fila,
  # extrai validade e produtos com posição, atualiza o painel.
  if command -v claude >/dev/null 2>&1; then
    claude -p "Rotina diária dos encartes em $BASE: leia data/fila_novos.json; para cada post decida se é ação de encarte com produtos e preços — a regra é: se nenhuma página do post tem produto com preço, é publicidade pura e deve ser DESCARTADA (teasers, institucionais, artes de campanha, avisos); descarte também ações B2B dirigidas a revenda (Alô Comerciante, Televendas, Food Service). NUNCA duplique a mesma oferta: se a mesma campanha (mesmo período de validade e mesma rede/bandeira) já existe em data/actions.json — por exemplo repostada em outro perfil da mesma rede ou repetida no mesmo perfil — ignore o post novo. Extraia o período de validade em datas absolutas preferencialmente do que está IMPRESSO nas próprias páginas do encarte (faixas tipo 'ofertas válidas de X a Y' na capa, topo ou rodapé); use a legenda do post só como confirmação ou fallback (a data de término é o que move o encarte para a aba Expirados automaticamente). Para cada página em data/pages/ do post, leia a imagem e extraia todos os produtos com preço e posição (x,y,w,h em % da imagem); atualize data/actions.json e data/products.json no mesmo formato já usado; atualize também data/canon.json (agrupamento de produtos similares para a aba Incidência: cada produto novo entra no grupo canônico existente se for o mesmo produto — mesmo tipo, marca e tamanho, mesmo com nomenclatura diferente — ou vira grupo novo; formato [{n: nome canônico, u: unidade, m: [chaves pageId#indice]}]); NUNCA apague ações ou produtos antigos de actions.json/products.json/canon.json — a aba Incidência é acumulativa e usa o histórico completo (vigentes e expirados); esvazie a fila do que foi processado; rode python3 build_painel.py para regerar painel-encartes.html; por fim republique painel-encartes.html com a ferramenta Artifact no MESMO artefato existente, passando url=https://claude.ai/code/artifact/f6a6969f-72b7-40d0-b563-35d5ff77bae7 e favicon 🛒 (se a ferramenta Artifact não estiver disponível na sessão, apenas mantenha o HTML local atualizado)." \
      --allowedTools "Read,Write,Edit,Bash,Artifact" >> "$LOG" 2>&1
  fi

  echo "$HOJE" > "$STAMP"
  osascript -e 'display notification "Encartes dos concorrentes atualizados." with title "Encartes · Rede Mais" sound name "Glass"'
  echo "=== $(date '+%Y-%m-%d %H:%M') concluído ==="
} >> "$LOG" 2>&1
