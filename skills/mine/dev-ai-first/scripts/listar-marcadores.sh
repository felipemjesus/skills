#!/usr/bin/env bash
# Lista os marcadores do kit que ainda faltam preencher, separados por quem decide:
#   {{AGENTE: ...}}  o agente preenche a partir do projeto
#   {{USUARIO: ...}} decisão do dev: o agente pergunta ou deixa como está
# Os modelos (0000-template.md, pull_request_template.md) usam {{...}} sem prefixo
# e são preenchidos a cada documento novo, por isso ficam de fora.
#
# Uso: listar-marcadores.sh [pasta] [--resumo]
# Sai com código 1 se ainda houver marcador pendente (útil no CI).

set -euo pipefail

raiz="${1:-.}"
modo="${2:-}"
[ "$raiz" = "--resumo" ] && { raiz=.; modo=--resumo; }
cd "$raiz"

listar() { # $1 = AGENTE | USUARIO
  grep -rnoE "\{\{$1: [^}]*\}\}" --include='*.md' \
    --exclude='0000-template*.md' --exclude='pull_request_template.md' \
    --exclude-dir=node_modules --exclude-dir=vendor --exclude-dir=.git . 2>/dev/null \
    | sed 's|^\./||' || true
}

agente=$(listar AGENTE)
usuario=$(listar USUARIO)
n_agente=$(printf '%s' "$agente" | grep -c . || true)
n_usuario=$(printf '%s' "$usuario" | grep -c . || true)

echo "AGENTE (o agente preenche a partir do projeto): $n_agente"
echo "USUARIO (decisão do dev): $n_usuario"

if [ "$modo" != "--resumo" ]; then
  if [ "$n_agente" -gt 0 ]; then
    echo
    echo "## AGENTE, por arquivo"
    printf '%s\n' "$agente" | awk '{
        arq = $0; sub(/:.*/, "", arq)          # arquivo
        resto = $0; sub(/^[^:]*:/, "", resto)  # linha:{{AGENTE: ...}}
        if (arq != atual) { print arq; atual = arq }
        print "  " resto
      }'
  fi
  if [ "$n_usuario" -gt 0 ]; then
    echo
    echo "## USUARIO, agrupados (pergunte em rodadas, cada um com recomendação)"
    printf '%s\n' "$usuario" | sed -E 's/^[^:]+:[0-9]+://' | sort | uniq -c | sort -rn
  fi
fi

[ $((n_agente + n_usuario)) -eq 0 ]
