#!/usr/bin/env bash
# Diz em que situação está a pasta: vazio, codigo ou preparado.
# Também lista manifestos, lockfiles, documentos para agentes e subprojetos,
# para o agente saber por onde começar a leitura.
#
# Uso: detectar-projeto.sh [pasta]   (padrão: pasta atual)
# Saída: linhas "chave: valor", fáceis de ler por pessoa e por agente.

set -euo pipefail

raiz="${1:-.}"
if [ ! -d "$raiz" ]; then
  echo "erro: '$raiz' não é uma pasta" >&2
  exit 2
fi
cd "$raiz"

ignorar='-name node_modules -o -name vendor -o -name .git -o -name dist -o -name build -o -name .next -o -name target -o -name .venv -o -name __pycache__'

# Arquivos que não contam como código: uma pasta só com eles é "vazia".
nao_codigo='^(README(\..*)?|LICENSE(\..*)?|\.gitignore|\.gitattributes|\.editorconfig)$'

conteudo=$(find . -mindepth 1 -maxdepth 1 ! -name .git | sed 's|^\./||' | sort)
codigo=$(printf '%s\n' "$conteudo" | grep -Ev "$nao_codigo" | grep -v '^$' || true)

manifestos='package.json composer.json pyproject.toml requirements.txt go.mod Cargo.toml pom.xml build.gradle build.gradle.kts Gemfile mix.exs *.csproj *.sln deno.json'
lockfiles='package-lock.json pnpm-lock.yaml yarn.lock bun.lockb bun.lock composer.lock poetry.lock uv.lock Pipfile.lock go.sum Cargo.lock Gemfile.lock mix.lock packages.lock.json'

procurar() { # $1 = lista de nomes; profundidade até 3, sem pastas ignoradas
  local args=() n
  set -f  # não expandir *.csproj contra a pasta atual
  for n in $1; do args+=(-o -name "$n"); done
  # shellcheck disable=SC2086
  find . -maxdepth 3 \( $ignorar \) -prune -o -type f \( -false "${args[@]}" \) -print | sed 's|^\./||' | sort
  set +f
}

achados_manifestos=$(procurar "$manifestos")
achados_lockfiles=$(procurar "$lockfiles")

docs_agentes=''
for f in AGENTS.md CLAUDE.md CODEBASE_MAP.md ARCHITECTURE.md CODING_GUIDELINES.md .cursorrules .cursor/rules .github/copilot-instructions.md .windsurfrules GEMINI.md; do
  [ -e "$f" ] && docs_agentes+="$f "
done

# Kit presente = AGENTS.md com as seções que só o kit tem.
kit=nao
if [ -f AGENTS.md ] && grep -q '^## Checklist de design' AGENTS.md && grep -q '^## Ordem de verdade' AGENTS.md; then
  kit=sim
fi

if [ "$kit" = sim ]; then
  situacao=preparado
elif [ -z "$codigo" ]; then
  situacao=vazio
else
  situacao=codigo
fi

# Subprojetos: pastas de 1º e 2º nível com manifesto próprio (monorepo ou pasta com vários repositórios).
subprojetos=$(printf '%s\n' "$achados_manifestos" | sed -n 's|/[^/]*$||p' | sort -u | tr '\n' ' ')

git_repo=nao
git rev-parse --is-inside-work-tree >/dev/null 2>&1 && git_repo=sim

echo "pasta: $(pwd)"
echo "situacao: $situacao"
echo "repositorio_git: $git_repo"
[ "$git_repo" = sim ] && echo "branch_atual: $(git branch --show-current 2>/dev/null || echo '?')"
[ "$git_repo" = sim ] && echo "alteracoes_nao_commitadas: $(git status --porcelain 2>/dev/null | wc -l | tr -d ' ')"
echo "manifestos: $(printf '%s' "$achados_manifestos" | tr '\n' ' ')"
echo "lockfiles: $(printf '%s' "$achados_lockfiles" | tr '\n' ' ')"
echo "subprojetos: ${subprojetos:-nenhum}"
echo "docs_para_agentes: ${docs_agentes:-nenhum}"
echo "kit_dev_ai_first: $kit"

if [ "$kit" = sim ]; then
  pendentes=$(grep -rhoE '\{\{(AGENTE|USUARIO):' --include='*.md' . 2>/dev/null | wc -l | tr -d ' ')
  echo "marcadores_pendentes: $pendentes"
fi

case "$situacao" in
  vazio)     echo "proximo_passo: preparar (entrevista) — ver references/preparar.md §Pasta vazia" ;;
  codigo)    echo "proximo_passo: preparar (leitura do código) — ver references/preparar.md §Código existente" ;;
  preparado) echo "proximo_passo: entregar, ou diagnóstico se o dev pediu preparar — ver SKILL.md" ;;
esac

if [ -n "$subprojetos" ] && [ ! -f package.json ] && [ ! -f composer.json ] && [ ! -f pyproject.toml ] && [ ! -f go.mod ]; then
  echo "aviso: a raiz não tem manifesto, mas há subprojetos. Pergunte ao dev se prepara cada um (repositórios separados) ou a raiz (monorepo)."
fi
