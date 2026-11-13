#!/usr/bin/env bash
# Lista os marcadores do kit que ainda faltam preencher, separados por quem resolve:
#   {{AGENTE: ...}}    o agente preenche a partir do projeto
#   {{USUARIO: ...}}   decisão do dev: o agente pergunta ou deixa como está
#   {{VERIFICAR: ...}} fato que o agente não alcança: o dev confirma
# Os modelos (0000-template.md, modelos de PR/MR) usam {{...}} sem prefixo
# e são preenchidos a cada documento novo, por isso ficam de fora.
#
# Uso: listar-marcadores.sh [pasta] [--resumo] [--tudo]   (argumentos em qualquer ordem)
#   Com .dev-ai-first/kit.lst (gravado pelo copiar-kit.sh), olha só os arquivos que a skill copiou;
#   --tudo olha todos os .md do projeto.
# Sai com código 1 se ainda houver marcador AGENTE (trabalho do agente por fazer); USUARIO e VERIFICAR
# são decisões do dev e não reprovam.

set -euo pipefail

raiz='' modo='' tudo=''
for arg in "$@"; do
  case "$arg" in
    --resumo) modo=--resumo ;;
    --tudo) tudo=1 ;;
    -*) echo "erro: opção desconhecida: $arg" >&2; exit 2 ;;
    *) [ -z "$raiz" ] || { echo "erro: mais de uma pasta informada" >&2; exit 2; }; raiz="$arg" ;;
  esac
done
raiz="${raiz:-.}"
[ -d "$raiz" ] || { echo "erro: '$raiz' não é uma pasta" >&2; exit 2; }
cd "$raiz"

escopo=''
if [ -z "$tudo" ] && [ -f .dev-ai-first/kit.lst ]; then
  escopo=$(grep -v '^#' .dev-ai-first/kit.lst | grep '\.md$' | grep -vE '(^|/)0000-template[^/]*\.md$|pull_request_template\.md$|merge_request_templates/' \
    | while IFS= read -r f; do [ -f "$f" ] && printf '%s\n' "$f"; done || true)
fi

listar() { # $1 = AGENTE | USUARIO | VERIFICAR; ignora a forma "{{X: ...}}", que só explica a convenção
  if [ -n "$escopo" ]; then
    printf '%s\n' "$escopo" | tr '\n' '\0' | xargs -0 grep -HnoE "\{\{$1: [^}]*\}\}" 2>/dev/null \
      | grep -vF "{{$1: ...}}" || true
    return
  fi
  grep -rnoE "\{\{$1: [^}]*\}\}" --include='*.md' \
    --exclude='0000-template*.md' --exclude='pull_request_template.md' --exclude-dir=merge_request_templates \
    --exclude-dir=node_modules --exclude-dir=vendor --exclude-dir=.git . 2>/dev/null \
    | grep -vF "{{$1: ...}}" | sed 's|^\./||' || true
}

agente=$(listar AGENTE)
usuario=$(listar USUARIO)
verificar=$(listar VERIFICAR)
contar() { printf '%s' "$1" | grep -c . || true; }
n_agente=$(contar "$agente")
n_usuario=$(contar "$usuario")
n_verificar=$(contar "$verificar")

[ -n "$escopo" ] && echo "escopo: arquivos copiados pela skill (.dev-ai-first/kit.lst); --tudo para todos os .md"
echo "AGENTE (o agente preenche a partir do projeto): $n_agente"
echo "USUARIO (decisão do dev): $n_usuario"
echo "VERIFICAR (fato que o dev confirma): $n_verificar"

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
  for tipo in USUARIO VERIFICAR; do
    if [ "$tipo" = USUARIO ]; then lista=$usuario; n=$n_usuario; else lista=$verificar; n=$n_verificar; fi
    if [ "$n" -gt 0 ]; then
      echo
      echo "## $tipo, agrupados (pergunte em rodadas, cada um com recomendação)"
      printf '%s\n' "$lista" | sed -E 's/^[^:]+:[0-9]+://' | sort | uniq -c | sort -rn
    fi
  done
fi

[ "$n_agente" -eq 0 ]
