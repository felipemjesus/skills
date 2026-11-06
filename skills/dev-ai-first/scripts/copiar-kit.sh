#!/usr/bin/env bash
# Copia o kit de assets/kit/ para o projeto sem sobrescrever nada.
# Lista os arquivos que já existiam no projeto: esses o agente mescla à mão.
#
# Uso: copiar-kit.sh <pasta do projeto>

set -euo pipefail

destino="${1:?uso: copiar-kit.sh <pasta do projeto>}"
[ -d "$destino" ] || { echo "erro: '$destino' não é uma pasta" >&2; exit 2; }
kit="$(cd "$(dirname "$0")/../assets/kit" && pwd)"

copiados=0
existentes=()
while IFS= read -r -d '' arq; do
  rel="${arq#"$kit"/}"
  alvo="$destino/$rel"
  if [ -e "$alvo" ]; then
    existentes+=("$rel")
  else
    mkdir -p "$(dirname "$alvo")"
    cp "$arq" "$alvo"
    copiados=$((copiados + 1))
  fi
done < <(find "$kit" -type f -print0 | sort -z)

echo "copiados: $copiados"
if [ "${#existentes[@]}" -gt 0 ]; then
  echo "já existiam (não sobrescritos, mesclar à mão):"
  printf '  %s\n' "${existentes[@]}"
fi
