#!/bin/zsh
# Troca a senha do painel publicado — dê dois cliques neste arquivo no Finder.
# Pede a nova senha numa janelinha, grava em ~/.config/painel_senha,
# republica o site na hora e regenera o painel local (engrenagem atualizada).

BASE="$HOME/encartes-concorrentes"

SENHA=$(osascript -e 'text returned of (display dialog "Nova senha do painel (mínimo 6 caracteres):" default answer "" with title "Encartes · Rede Mais" buttons {"Cancelar","Trocar"} default button "Trocar" with hidden answer)' 2>/dev/null) || exit 0

if (( ${#SENHA} < 6 )); then
  osascript -e 'display alert "Senha muito curta" message "Use pelo menos 6 caracteres." as warning'
  exit 1
fi

mkdir -p "$HOME/.config"
printf '%s' "$SENHA" > "$HOME/.config/painel_senha"
chmod 600 "$HOME/.config/painel_senha"

echo "Republicando o painel com a nova senha…"
if "$BASE/publicar_painel.sh"; then
  /usr/bin/python3 "$BASE/build_painel.py" >/dev/null 2>&1 || true
  osascript -e 'display notification "Senha trocada e painel republicado. Avise os colegas!" with title "Encartes · Rede Mais" sound name "Glass"'
else
  osascript -e 'display alert "A republicação falhou" message "A senha foi gravada, mas o site ainda está com a anterior. Veja o Terminal ou peça ajuda ao Claude." as critical'
fi
