#!/usr/bin/env bash
# Copia do kit só o que se aplica ao projeto, sem sobrescrever nada.
# Cada arquivo do kit pertence a um módulo (assets/kit-indice.tsv); dentro dos
# arquivos, trechos entre "<!-- se: X -->" e "<!-- fim: X -->" só ficam se X
# estiver ativo. O agente nunca recebe texto que não se aplica.
#
# Uso: copiar-kit.sh <projeto> --minimo --perfil backend|frontend|fullstack [--frontend spa|servidor] [--modulos claude,github,gitlab]
#      copiar-kit.sh <projeto> --estrutura projeto|kit --perfil backend|frontend|fullstack
#                    [--frontend spa|servidor] [--modulos a,b] [--arquivos x,y]
#   --minimo: o padrão em projeto existente: AGENTS.md mínimo, PRINCIPIOS.md fixo, VERIFICACAO.md e IA_FIRST.md
#      copiar-kit.sh --listar
#   --estrutura projeto: projeto existente; os documentos descrevem o padrão real
#   --estrutura kit:     projeto novo; o kit propõe a estrutura (ADRs 0002 a 0005)
#   --arquivos:          copia só estes arquivos (caminhos do índice), ex.: projeto já governado
# Grava em <projeto>/.dev-ai-first/kit.lst o que a skill copiou; rodar de novo só acrescenta.

set -euo pipefail

skill="$(cd "$(dirname "$0")/.." && pwd)"
kit="$skill/assets/kit"
indice="$skill/assets/kit-indice.tsv"
so_trechos='estados cli bdd verificacao-arquitetura'

uso() {
  echo "uso: copiar-kit.sh <projeto> --estrutura projeto|kit --perfil backend|frontend|fullstack [--frontend spa|servidor] [--modulos a,b] [--arquivos x,y] | --listar" >&2
  exit 2
}

destino='' estrutura='' perfil='' variante='' modulos='' arquivos='' minimo=''
while [ $# -gt 0 ]; do
  case "$1" in
    --listar)
      column -t -s "$(printf '\t')" "$indice" 2>/dev/null || cat "$indice"
      echo
      echo "estrutura: projeto | kit    perfil: backend | frontend | fullstack    frontend: spa | servidor"
      echo "módulos só de trechos (sem arquivo próprio): $so_trechos"
      exit 0 ;;
    --minimo) minimo=1; shift ;;
    --estrutura) estrutura="${2:-}"; shift 2 || uso ;;
    --perfil) perfil="${2:-}"; shift 2 || uso ;;
    --frontend) variante="${2:-}"; shift 2 || uso ;;
    --modulos) modulos="${2:-}"; shift 2 || uso ;;
    --arquivos) arquivos="${2:-}"; shift 2 || uso ;;
    -*) echo "erro: opção desconhecida: $1" >&2; uso ;;
    *) [ -z "$destino" ] || uso; destino="$1"; shift ;;
  esac
done

[ -n "$destino" ] || uso
[ -d "$destino" ] || { echo "erro: '$destino' não é uma pasta" >&2; exit 2; }
[ -n "$minimo" ] && estrutura="${estrutura:-projeto}"
case "$estrutura" in projeto|kit) ;; *) echo "erro: informe --estrutura projeto ou --estrutura kit (pergunte ao dev antes de copiar)" >&2; exit 2 ;; esac
case "$perfil" in backend|frontend|fullstack) ;; *) echo "erro: informe --perfil backend, frontend ou fullstack" >&2; exit 2 ;; esac
if [ "$perfil" != backend ]; then
  case "$variante" in spa|servidor) ;; *) echo "erro: com perfil $perfil, informe --frontend spa ou --frontend servidor" >&2; exit 2 ;; esac
elif [ -n "$variante" ]; then
  echo "erro: --frontend só vale com perfil frontend ou fullstack" >&2; exit 2
fi

if [ -n "$minimo" ]; then ativos=" minimo estrutura-$estrutura "; else ativos=" nucleo estrutura-$estrutura "; fi
case "$perfil" in
  backend) ativos+="backend " ;;
  frontend) ativos+="frontend frontend-$variante " ;;
  fullstack) ativos+="backend frontend frontend-$variante fullstack " ;;
esac

validos=" $(tail -n +2 "$indice" | cut -f1 | sort -u | tr '\n' ' ')$so_trechos "
for m in $(printf '%s' "$modulos" | tr ',' ' '); do
  case "$m" in
    nucleo|minimo|estrutura-*|backend|frontend*|fullstack) echo "erro: '$m' é definido por --estrutura/--perfil, não por --modulos" >&2; exit 2 ;;
  esac
  case "$validos" in *" $m "*) ;; *) echo "erro: módulo desconhecido: $m (veja --listar)" >&2; exit 2 ;; esac
  if [ "$perfil" = frontend ]; then
    case "$m" in api|eventos) echo "erro: o módulo '$m' descreve o backend; com perfil frontend o backend está em outro repositório" >&2; exit 2 ;; esac
  fi
  ativos+="$m "
done

so_estes=" $(printf '%s' "$arquivos" | tr ',' ' ') "
if [ -n "$arquivos" ]; then
  for a in $so_estes; do
    tail -n +2 "$indice" | cut -f2 | grep -qxF "$a" || { echo "erro: arquivo fora do índice: $a (veja --listar)" >&2; exit 2; }
  done
fi

manifesto="$destino/.dev-ai-first/kit.lst"
mkdir -p "$destino/.dev-ai-first"
touch "$manifesto"
grep -q '^# copiar-kit:' "$manifesto" || printf '# copiar-kit: %s--estrutura %s --perfil %s%s\n' "${minimo:+--minimo }" "$estrutura" "$perfil" "${variante:+ --frontend $variante}" >> "$manifesto"

copiados=0
existentes=() da_skill=()
while IFS="$(printf '\t')" read -r modulo arq _; do
  case "$ativos" in *" $modulo "*) ;; *) continue ;; esac
  # no modo mínimo, perfil só filtra trechos; arquivos vêm do mínimo e dos módulos pedidos
  if [ -n "$minimo" ] && [ "$modulo" != minimo ]; then case " $(printf '%s' "$modulos" | tr ',' ' ') " in *" $modulo "*) ;; *) continue ;; esac; fi
  if [ -n "$arquivos" ]; then case "$so_estes" in *" $arq "*) ;; *) continue ;; esac; fi
  alvo="$destino/$arq"
  if [ -e "$alvo" ]; then
    if grep -qxF "$arq" "$manifesto"; then da_skill+=("$arq"); else existentes+=("$arq"); fi
    continue
  fi
  origem="$kit/$arq"
  [ "$modulo" = minimo ] && [ -f "$skill/assets/minimo/$arq" ] && origem="$skill/assets/minimo/$arq"
  mkdir -p "$(dirname "$alvo")"
  awk -v ativos="$ativos" '
    /^<!-- se: [a-z-]+ -->[[:space:]]*$/ { m = $3; dentro = 1; manter = index(ativos, " " m " ") > 0; next }
    /^<!-- fim: [a-z-]+ -->[[:space:]]*$/ { dentro = 0; next }
    !dentro || manter { print }
  ' "$origem" > "$alvo"
  echo "$arq" >> "$manifesto"
  copiados=$((copiados + 1))
done < <(tail -n +2 "$indice")

echo "ativos: $(echo $ativos)"
echo "copiados: $copiados"
[ "${#da_skill[@]}" -gt 0 ] && echo "já copiados antes pela skill (mantidos): ${#da_skill[@]}"
if [ "${#existentes[@]}" -gt 0 ]; then
  echo "já existiam no projeto (não sobrescritos, mesclar à mão):"
  printf '  %s\n' "${existentes[@]}"
fi
echo "manifesto: .dev-ai-first/kit.lst"
