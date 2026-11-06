#!/usr/bin/env bash
# Confere se os links relativos dos documentos Markdown apontam para arquivos
# e âncoras que existem. Documento com link quebrado ensina caminho errado ao agente.
#
# Uso: verificar-links.sh [pasta]
# Sai com código 1 se houver link quebrado (útil no CI).
# Ignora: links externos (http, mailto), links com marcador {{...}} e pastas de dependências.

set -uo pipefail
# Locale UTF-8 para que letras acentuadas contem como letras nas âncoras.
# C.UTF-8 existe no Linux; no macOS o equivalente é en_US.UTF-8.
if locale -a 2>/dev/null | grep -qiE '^c\.utf-?8$'; then
  export LC_ALL=C.UTF-8
else
  export LC_ALL=en_US.UTF-8
fi

raiz="${1:-.}"
cd "$raiz" || exit 2

# Minúsculas com acentos: GNU sed tem \L; no macOS (BSD sed) usa perl.
if printf 'A' | sed 's/.*/\L&/' 2>/dev/null | grep -q '^a$'; then
  minusculas() { sed 's/.*/\L&/'; }
else
  minusculas() { perl -CSD -pe '$_ = lc'; }
fi

# Âncora no formato do GitHub: minúsculas, sem pontuação, espaço vira hífen.
slug() {
  printf '%s' "$1" | sed -E 's/`//g; s/\[([^]]*)\]\([^)]*\)/\1/g' \
    | minusculas \
    | sed -E 's/[^[:alnum:] _-]//g; s/ /-/g'
}

ancoras() { # títulos de um arquivo, um slug por linha (fora de blocos de código)
  awk '/^```/ { dentro = !dentro; next } !dentro && /^#+ / { sub(/^#+ +/, ""); print }' "$1" \
    | while IFS= read -r t; do slug "$t"; echo; done
}

quebrados=0
total=0

while IFS= read -r -d '' arq; do
  dir=$(dirname "$arq")
  # links [texto](destino) fora de blocos de código
  links=$(awk '/^```/ { dentro = !dentro; next } !dentro' "$arq" \
    | grep -oE '\]\([^)[:space:]]+\)' | sed -E 's/^\]\(//; s/\)$//' || true)
  [ -z "$links" ] && continue
  while IFS= read -r link; do
    case "$link" in http*|mailto:*|*'{{'*) continue ;; esac
    total=$((total + 1))
    caminho="${link%%#*}"
    ancora=""
    [ "$caminho" != "$link" ] && ancora="${link#*#}"
    if [ -z "$caminho" ]; then alvo="$arq"; else alvo="$dir/$caminho"; fi
    if [ ! -e "$alvo" ]; then
      echo "$arq: arquivo não existe: $link"
      quebrados=$((quebrados + 1))
      continue
    fi
    if [ -n "$ancora" ] && [ -f "$alvo" ]; then
      # guarda antes de comparar: grep -q no pipe quebraria o pipeline (pipefail)
      lista=$(ancoras "$alvo")
      if ! printf '%s\n' "$lista" | grep -xF -- "$ancora" >/dev/null; then
        echo "$arq: âncora não existe: $link"
        quebrados=$((quebrados + 1))
      fi
    fi
  done <<< "$links"
done < <(find . \( -name node_modules -o -name vendor -o -name .git \) -prune -o -type f -name '*.md' -print0)

echo "links verificados: $total, quebrados: $quebrados"
[ "$quebrados" -eq 0 ]
