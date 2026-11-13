#!/usr/bin/env bash
# Diz em que situação está a pasta e o que o agente precisa saber antes de ler código:
# situação, stack provável, ambiente local, forja, codificação, instruções para agentes
# já existentes e os módulos do kit sugeridos pelos sinais do projeto.
#
# Uso: detectar-projeto.sh [pasta]   (padrão: pasta atual)
# Saída: linhas "chave: valor", fáceis de ler por pessoa e por agente.
# Situações: vazio | codigo | governado (já tem instruções para agentes, sem o kit) | preparado (kit presente)

set -euo pipefail

raiz="${1:-.}"
if [ ! -d "$raiz" ]; then
  echo "erro: '$raiz' não é uma pasta" >&2
  exit 2
fi
cd "$raiz"

# Uma listagem só, até a profundidade 5, sem pastas de dependência e de build.
arquivos=$(find . -maxdepth 5 \( -name node_modules -o -name vendor -o -name .git -o -name dist -o -name build \
  -o -name .next -o -name target -o -name .venv -o -name __pycache__ \) -prune -o -type f -print | sed 's|^\./||' | sort)
nomes_em() { printf '%s\n' "$arquivos" | RE="$1" awk -F/ '$NF ~ ENVIRON["RE"]' || true; }
resumir() { # lista em uma linha, no máximo $2 itens
  local itens n
  itens=$(printf '%s\n' "$1" | grep -v '^$' || true)
  n=$(printf '%s' "$itens" | grep -c . || true)
  if [ "$n" -gt "$2" ]; then printf '%s (+%s)' "$(printf '%s\n' "$itens" | head -n "$2" | tr '\n' ' ')" "$((n - $2))"
  else printf '%s' "$(printf '%s\n' "$itens" | tr '\n' ' ')"; fi
}

# Arquivos que não contam como código: uma pasta só com eles é "vazia".
nao_codigo='^(README(\..*)?|LICENSE(\..*)?|\.gitignore|\.gitattributes|\.editorconfig)$'
codigo=$(find . -mindepth 1 -maxdepth 1 ! -name .git | sed 's|^\./||' | grep -Ev "$nao_codigo" | grep -v '^$' || true)

manifestos=$(nomes_em '^(package\.json|composer\.json|pyproject\.toml|requirements\.txt|go\.mod|Cargo\.toml|pom\.xml|build\.gradle(\.kts)?|Gemfile|mix\.exs|.*\.csproj|.*\.sln|deno\.json|setup\.py|Pipfile|build\.xml)$')
lockfiles=$(nomes_em '^(package-lock\.json|pnpm-lock\.yaml|yarn\.lock|bun\.lockb?|composer\.lock|poetry\.lock|uv\.lock|Pipfile\.lock|go\.sum|Cargo\.lock|Gemfile\.lock|mix\.lock|packages\.lock\.json)$')
ambiente=$(nomes_em '^(Dockerfile.*|docker-compose.*\.ya?ml|compose\.ya?ml|Makefile|justfile|devcontainer\.json|\.tool-versions|\.nvmrc)$' | awk -F/ 'NF <= 3')

# Instruções para agentes em qualquer nível (o projeto pode já ter regras próprias).
instrucoes=$(printf '%s\n' "$arquivos" | grep -E '(^|/)(AGENTS\.md|CLAUDE\.md|GEMINI\.md|\.cursorrules|\.windsurfrules|copilot-instructions\.md)$|(^|/)\.github/instructions/|(^|/)\.cursor/rules/|(^|/)\.claude/|(^|/)\.agents/|(^|/)SKILL\.md$' || true)
n_instrucoes=$(printf '%s' "$instrucoes" | grep -c . || true)

# Linguagens prováveis: extensões de código mais frequentes.
linguagens=$(printf '%s\n' "$arquivos" | grep -oE '\.(php|js|jsx|ts|tsx|vue|svelte|py|rb|go|rs|java|kt|cs|ex|exs|scala|swift|dart|c|cc|cpp|h|sql|sh)$' \
  | sort | uniq -c | sort -rn | head -5 | awk '{ sub(/^\./, "", $2); printf "%s:%s ", $2, $1 }' || true)

# Kit presente = AGENTS.md com as seções que só o kit tem.
kit=nao
if [ -f AGENTS.md ] && { grep -q '^<!-- dev-ai-first -->' AGENTS.md || { grep -q '^## Checklist de design' AGENTS.md && grep -q '^## Ordem de verdade' AGENTS.md; }; }; then
  kit=sim
fi

if [ "$kit" = sim ]; then situacao=preparado
elif [ -z "$codigo" ]; then situacao=vazio
elif [ "$n_instrucoes" -gt 0 ]; then situacao=governado
else situacao=codigo
fi

# Subprojetos: pastas com manifesto próprio (monorepo ou pasta com vários repositórios).
subprojetos=$(printf '%s\n' "$manifestos" | sed -n 's|/[^/]*$||p' | sort -u)

git_repo=nao
git rev-parse --is-inside-work-tree >/dev/null 2>&1 && git_repo=sim

# Forja: pasta de CI ou remoto.
remoto=''
[ "$git_repo" = sim ] && remoto=$(git remote get-url origin 2>/dev/null || true)
forja=desconhecida
if [ -d .github ] || printf '%s' "$remoto" | grep -q github; then forja=github
elif [ -f .gitlab-ci.yml ] || [ -d .gitlab ] || printf '%s' "$remoto" | grep -q gitlab; then forja=gitlab
elif [ -f bitbucket-pipelines.yml ] || printf '%s' "$remoto" | grep -q bitbucket; then forja=bitbucket
fi

# Codificação: amostra de até 200 arquivos de código e texto.
amostra=$(printf '%s\n' "$arquivos" | grep -E '\.(php|js|jsx|ts|tsx|vue|py|rb|go|java|kt|cs|sql|html|md|txt|xml|yml|yaml)$' | head -200 || true)
n_amostra=0 n_nao_utf8=0
while IFS= read -r f; do
  [ -n "$f" ] || continue
  n_amostra=$((n_amostra + 1))
  iconv -f UTF-8 -t UTF-8 "$f" >/dev/null 2>&1 || n_nao_utf8=$((n_nao_utf8 + 1))
done <<< "$amostra"
charset=$(grep -hE '^[[:space:]]*charset' .editorconfig 2>/dev/null | head -1 | sed -E 's/.*=[[:space:]]*//' || true)

# Sinais para os módulos do kit (conteúdo dos manifestos).
conteudo=''
while IFS= read -r m; do [ -n "$m" ] && conteudo+=$(cat "$m" 2>/dev/null)$'\n'; done <<< "$manifestos"
tem() { printf '%s' "$conteudo" | grep -Eqi "$1"; }
# Perfil: backend, frontend (spa ou servidor) ou fullstack.
spa=nao servidor=nao backend=nao
tem '"(react|vue|svelte|@angular/core|next|nuxt|solid-js|preact|lit)"' && spa=sim
printf '%s\n' "$arquivos" | grep -Eq '\.(blade\.php|twig|html\.erb|erb|jinja2?|j2|jsp|cshtml|phtml|tpl|hbs|ejs|njk|liquid)$|(^|/)(templates|views)/[^/]+\.(html|php)$' && servidor=sim
printf '%s' "$linguagens" | grep -Eq '(^| )(php|py|rb|go|rs|java|kt|cs|ex|exs|scala):' && backend=sim
tem '"(express|fastify|@nestjs/core|koa|hono|next|nuxt|@remix-run/node|@sveltejs/kit)"' && backend=sim
if [ "$backend" = sim ] && { [ "$spa" = sim ] || [ "$servidor" = sim ]; }; then perfil=fullstack
elif [ "$backend" = sim ]; then perfil=backend
elif [ "$spa" = sim ] || [ "$servidor" = sim ]; then perfil=frontend
else perfil=indefinido
fi
variante=''
if [ "$perfil" = fullstack ] || [ "$perfil" = frontend ]; then
  if [ "$spa" = sim ] && [ "$servidor" = sim ]; then variante='spa ou servidor (os dois aparecem; pergunte)'
  elif [ "$spa" = sim ]; then variante=spa
  else variante=servidor
  fi
fi

# Sinais no código (amostra dos arquivos de backend), para eventos e tarefas agendadas.
codigo_amostra=$(printf '%s\n' "$arquivos" | grep -E '\.(php|ts|js|py|rb|go|java|kt|cs|ex)$' | grep -vE '(^|/)(tests?|spec|__tests__)/' | head -3000 || true)
grep_codigo() { [ -n "$codigo_amostra" ] && printf '%s\n' "$codigo_amostra" | tr '\n' '\0' | xargs -0 grep -lEa -m1 -- "$1" 2>/dev/null | head -1 | grep -q .; }

# Possíveis segredos versionados (só a contagem; o agente confere e nunca copia o valor).
aspa="[\"']"; valor="[^\"'[:space:]\$%{<]"
padrao_segredo="-----BEGIN ([A-Z]+ )?PRIVATE KEY-----|AKIA[0-9A-Z]{16}|gh[pousr]_[A-Za-z0-9]{36}|glpat-[A-Za-z0-9_-]{20}|[a-z][a-z0-9+.-]*://[^/[:space:]:@\"']+:[^/[:space:]@\"'$%{<]{6,}@|xox[baprs]-[A-Za-z0-9-]{10,}|(password|passwd|senha|secret|api[_-]?key|access[_-]?token)${aspa}?[[:space:]]*[:=>]+[[:space:]]*${aspa}${valor}{8,}${aspa}"
segredos=$(printf '%s\n' "$arquivos" | grep -vE '\.(md|lock|svg|png|jpg|gif|ico|woff2?|map)$|(^|/)(tests?|spec|fixtures|__tests__|__mocks__)/|\.(test|spec)\.[a-z]+$|\.(example|sample|dist|template)(\.[a-z]+)?$' | head -5000 \
  | tr '\n' '\0' | xargs -0 grep -nIEao -- "$padrao_segredo" 2>/dev/null | cut -d: -f1,2 | sort -u || true)
locais_segredo=$(printf '%s\n' "$segredos" | grep -v '^$' | head -5 | tr '\n' ' ' || true)
segredos=$(printf '%s\n' "$segredos" | grep -v '^$' | cut -d: -f1 | sort -u | grep -c . || true)

sinais=''
{ tem '"(express|fastify|@nestjs/core|koa|hono)"|laravel/framework|symfony/http-kernel|slim/slim|django|flask|fastapi|spring-boot-starter-web|gin-gonic|rails' \
  || printf '%s\n' "$arquivos" | grep -Eq '(^|/)(openapi|swagger)\.(ya?ml|json)$'; } && sinais+='api '
{ tem 'bullmq|"bull"|kafkajs|amqplib|@nestjs/event-emitter|@nestjs/bull|celery|pika|laravel/horizon|symfony/messenger|spring-kafka|php-amqplib' \
  || grep_codigo '@OnEvent\(|@EventPattern\(|ShouldQueue|EventSubscriberInterface|Event::listen|@EventListener|@KafkaListener|implements ShouldBroadcast|extends (Listener|Subscriber)\b'; } && sinais+='eventos '
{ tem 'node-cron|"cron"|symfony/console|commander|yargs|apscheduler|"agenda"' \
  || printf '%s\n' "$arquivos" | grep -Eq '(^|/)(Console/Commands|commands|cron|crontab|jobs|schedulers?)/|\.cron$|(^|/)crontab' \
  || grep_codigo '@Cron\(|->schedule\(|Schedule::|@Scheduled|setInterval\(' ; } && sinais+='cli '
tem '@opentelemetry|@sentry|sentry/sentry|sentry-sdk|dd-trace|prom-client|newrelic|opentelemetry' && sinais+='observabilidade '
{ tem 'cucumber|behat|pytest-bdd' || printf '%s\n' "$arquivos" | grep -q '\.feature$'; } && sinais+='bdd '
tem 'dependency-cruiser|deptrac|archunit|pest-plugin-arch|eslint-plugin-boundaries' && sinais+='verificacao-arquitetura '
case "$forja" in github|gitlab) sinais+="$forja " ;; esac
printf '%s\n' "$instrucoes" | grep -qE '(^|/)(CLAUDE\.md|\.claude/)' && sinais+='claude '

echo "pasta: $(pwd)"
echo "situacao: $situacao"
echo "repositorio_git: $git_repo"
[ "$git_repo" = sim ] && echo "branch_atual: $(git branch --show-current 2>/dev/null || echo '?')"
[ "$git_repo" = sim ] && echo "alteracoes_nao_commitadas: $(git status --porcelain 2>/dev/null | wc -l | tr -d ' ')"
echo "linguagens: ${linguagens:-nenhuma reconhecida}"
echo "manifestos: $(resumir "$manifestos" 10)"
echo "lockfiles: $(resumir "$lockfiles" 10)"
echo "subprojetos: $(resumir "$subprojetos" 10 | sed 's/^$/nenhum/')"
echo "ambiente_local: $(resumir "$ambiente" 8 | sed 's/^$/nenhum/')"
echo "forja: $forja"
echo "codificacao: $([ "$n_nao_utf8" -eq 0 ] && echo utf-8 || echo "$n_nao_utf8 de $n_amostra arquivos amostrados não são UTF-8")${charset:+ (editorconfig: $charset)}"
echo "docs_para_agentes: $(resumir "$instrucoes" 12 | sed 's/^$/nenhum/')"
echo "kit_dev_ai_first: $kit"
echo "perfil_sugerido: $perfil${variante:+ (frontend: $variante)}"
echo "modulos_sugeridos: ${sinais:-nenhum}"
echo "possiveis_segredos_versionados: $segredos arquivos${locais_segredo:+ (arquivo:linha, sem o valor: $locais_segredo)}"

if [ "$kit" = sim ]; then
  pendentes=$(grep -rhoE '\{\{(AGENTE|USUARIO|VERIFICAR): [^}]*\}\}' --include='*.md' --exclude='0000-template*.md' . 2>/dev/null | grep -vcF ': ...}}' || true)
  echo "marcadores_pendentes: $pendentes"
fi

case "$situacao" in
  vazio)     echo "proximo_passo: preparar (entrevista) — ver references/preparar.md §Pasta vazia" ;;
  codigo)    echo "proximo_passo: preparar (leitura do código) — ver references/preparar.md §Código existente" ;;
  governado) echo "proximo_passo: preparar complementando as instruções existentes — ver references/preparar.md §Projeto já governado" ;;
  preparado) echo "proximo_passo: entregar, ou diagnóstico se o dev pediu preparar — ver SKILL.md" ;;
esac

[ -z "$linguagens" ] && [ "$situacao" != vazio ] && echo "aviso: nenhuma linguagem reconhecida pelas extensões; leia a árvore antes de supor a stack."
[ -z "$manifestos" ] && [ -n "$linguagens" ] && echo "aviso: sem manifesto de dependências; versões e comandos podem vir do ambiente hospedeiro ou do README. Não invente."
[ "$n_nao_utf8" -gt 0 ] && echo "aviso: há arquivos fora de UTF-8; use grep -a e preserve a codificação ao editar código."
[ "$segredos" -gt 0 ] && echo "aviso: $segredos arquivo(s) parecem ter segredo versionado; confira, registre no diagnóstico (prioridade alta) e nunca copie o valor."
[ "$perfil" = indefinido ] && [ "$situacao" != vazio ] && echo "aviso: perfil não identificado; pergunte ao dev se é backend, frontend ou fullstack." 
if [ -n "$subprojetos" ] && [ ! -f package.json ] && [ ! -f composer.json ] && [ ! -f pyproject.toml ] && [ ! -f go.mod ]; then
  echo "aviso: a raiz não tem manifesto, mas há subprojetos. Pergunte ao dev se prepara cada um (repositórios separados) ou a raiz (monorepo)."
fi
exit 0
