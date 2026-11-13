#!/usr/bin/env bash
# Confere as evidências citadas nos documentos Markdown contra o projeto:
#   erro:  `arquivo:linha` (ou `arquivo:inicio-fim`) cujo arquivo não existe ou cuja linha passa do fim
#   aviso: caminho entre crases (com /) que não existe no projeto
#   aviso: nome ilustrativo do kit (assets/kit-exemplos.txt) que não aparece no código: exemplo que sobrou
# Citação errada é afirmação falsa que o próximo agente vai seguir.
#
# Uso: verificar-citacoes.sh [pasta] [--alterados [ref]] [--mostrar]
#   --alterados: só os .md alterados ou novos em relação a ref (padrão HEAD), num repositório git
#   --mostrar:   imprime o conteúdo de cada linha citada, para conferir se ela diz o que o documento afirma
# Caminho relativo a uma subpasta (ex.: raiz do frontend) é aceito se existir um único caminho do projeto que termine nele.
# Sai com código 1 se houver erro ou exemplo do kit sobrando; avisos de caminho não reprovam.

set -uo pipefail

skill="$(cd "$(dirname "$0")/.." && pwd)"
raiz='' alterados='' ref=HEAD mostrar=''
while [ $# -gt 0 ]; do
  case "$1" in
    --mostrar) mostrar=1; shift ;;
    --alterados) alterados=1
                 if [ $# -gt 1 ] && [ "${2#-}" = "$2" ] && [ ! -d "$2" ]; then ref="$2"; shift; fi
                 shift ;;
    -*) echo "erro: opção desconhecida: $1" >&2; exit 2 ;;
    *) [ -z "$raiz" ] || { echo "erro: mais de uma pasta informada" >&2; exit 2; }; raiz="$1"; shift ;;
  esac
done
raiz="${raiz:-.}"
cd "$raiz" || exit 2

if [ -n "$alterados" ]; then
  git rev-parse --is-inside-work-tree >/dev/null 2>&1 || { echo "erro: --alterados exige repositório git" >&2; exit 2; }
  lista=$( { git diff --name-only --relative "$ref" -- '*.md' 2>/dev/null
             git ls-files --others --exclude-standard -- '*.md'; } | sort -u)
else
  lista=$(find . \( -name node_modules -o -name vendor -o -name .git \) -prune -o -type f -name '*.md' -print | sed 's|^\./||')
fi

# Nomes ilustrativos do kit que não existem no código do projeto (fora de .md).
ausentes=''
while IFS= read -r termo; do
  case "$termo" in ''|'#'*) continue ;; esac
  if ! grep -rqwF --exclude='*.md' --exclude-dir=node_modules --exclude-dir=vendor --exclude-dir=.git -- "$termo" . 2>/dev/null; then
    ausentes+="$termo"$'\n'
  fi
done < "$skill/assets/kit-exemplos.txt"

# Todos os caminhos do projeto (arquivos e pastas), para aceitar caminho relativo a subpasta.
caminhos=$(find . \( -name node_modules -o -name vendor -o -name .git \) -prune -o -print 2>/dev/null | sed 's|^\./||')
# Nomes de pacote declarados nos manifestos e branches: não são caminhos do projeto.
pacotes=$(cat package.json composer.json */package.json */composer.json 2>/dev/null | grep -oE '"[@a-z0-9._-]+/[a-z0-9._-]+"' | tr -d '"' | sort -u || true)
branches=$(git for-each-ref --format='%(refname:short)' refs/heads 2>/dev/null || true)

printf '%s\n' "$lista" | grep -v '^$' | CAMINHOS="$caminhos" PACOTES="$pacotes" BRANCHES="$branches" MOSTRAR="$mostrar" AUSENTES="$ausentes" perl -CO -Mutf8 -e '
  use strict; use warnings;
  use Encode qw(decode encode);
  use File::Basename qw(dirname);
  use File::Spec;
  my @ausentes = grep { length } split /\n/, decode("UTF-8", $ENV{AUSENTES} // "");
  my %ignorar = map { $_ => 1 } grep { length } split /\n/, ($ENV{PACOTES} // "") . "\n" . ($ENV{BRANCHES} // "");
  my %sufixo;  # "x/y" -> nº de caminhos do projeto que terminam em "/x/y"
  for my $c (split /\n/, $ENV{CAMINHOS} // "") {
    my @p = split m{/}, $c;
    for my $i (1 .. $#p) { $sufixo{ join "/", @p[$i .. $#p] }++ }
  }
  my %nome = map { (split m{/})[-1] => 1 } split /\n/, $ENV{CAMINHOS} // "";  # nomes de arquivo e pasta
  my %unico;   # sufixo -> caminho completo, quando há um só
  for my $c (split /\n/, $ENV{CAMINHOS} // "") {
    my @p = split m{/}, $c;
    for my $i (1 .. $#p) { my $k = join "/", @p[$i .. $#p]; $unico{$k} = $c if $sufixo{$k} == 1 }
  }
  # Nunca imprimir segredo: linha que pareça conter credencial sai mascarada no --mostrar.
  my $segredo = qr{-----BEGIN [A-Z ]*PRIVATE KEY-----|AKIA[0-9A-Z]{16}|gh[pousr]_[A-Za-z0-9]{36}|glpat-[A-Za-z0-9_-]{20}|xox[baprs]-|://[^/\s:@]+:[^/\s@]{6,}@|(?i:password|passwd|senha|secret|api[_-]?key|access[_-]?token|private[_-]?key)\W{0,3}\s*[:=>]};
  my %linhas;  # cache: arquivo -> nº de linhas
  sub n_linhas {
    my $f = shift;
    return $linhas{$f} if exists $linhas{$f};
    my $n = 0;
    if (open my $fh, "<", $f) { $n++ while <$fh> }
    return $linhas{$f} = $n;
  }
  sub resolve {  # caminho relativo à raiz ou à pasta do documento
    my ($c, $dir) = @_;
    my $b = encode("UTF-8", $c);
    return $b if -e $b;
    my $r = File::Spec->catfile($dir, $b);
    return $r if -e $r;
    return $unico{$b} if defined $unico{$b} && -e $unico{$b};  # relativo a uma subpasta, sem ambiguidade
    return undef;
  }

  my ($n_cit, $erros, $avisos, $sobras) = (0, 0, 0, 0);
  while (my $arq = <STDIN>) {
    chomp $arq;
    next unless -f $arq;
    next if $arq =~ m{(^|/)docs/PRINCIPIOS\.md$};  # texto fixo do kit: copiado sem edição
    open my $fh, "<", $arq or next;
    my $dir = dirname($arq);
    my $nome = decode("UTF-8", $arq);
    my ($codigo, $num) = (0, 0);
    while (my $l = <$fh>) {
      $num++;
      $l = decode("UTF-8", $l);
      if ($l =~ /^```/) { $codigo = !$codigo; next }
      next if $codigo;
      # arquivo:linha ou arquivo:inicio-fim (exige extensão; sem "/" só conta se o arquivo existir)
      while ($l =~ m{(?<![\w./:-])([\w@.+-]+(?:/[\w@.+-]+)*\.[A-Za-z0-9]+):(\d+)(?:-(\d+))?(?![\w/])}g) {
        my ($c, $ini, $fim) = ($1, $2, $3 // $2);
        next if $c =~ /\{\{/;
        my $alvo = resolve($c, $dir);
        if (!$alvo) {
          next if $c !~ m{/};
          $n_cit++; $erros++; print "$nome:$num: erro: arquivo citado não existe: $c:$ini\n"; next;
        }
        $n_cit++;
        my $n = n_linhas($alvo);
        if ($ini < 1 || $fim > $n || $fim < $ini) {
          $erros++; print "$nome:$num: erro: linha fora do arquivo ($n linhas): $c:$ini", ($fim != $ini ? "-$fim" : ""), "\n";
        } elsif ($ENV{MOSTRAR}) {
          if (open my $cf, "<", $alvo) {
            my $k = 0;
            while (my $t = <$cf>) { next unless ++$k == $ini; $t = decode("UTF-8", $t); $t =~ s/^\s+|\s+$//g; $t = "[linha com possível segredo: conteúdo omitido]" if $t =~ $segredo; print "$nome:$num: $c:$ini => ", substr($t, 0, 140), "\n"; last }
          }
        }
      }
      # caminho entre crases, com "/", sem marcador, glob ou variável
      while ($l =~ /`([^`\s]+\/[^`\s]*)`/g) {
        my $c = $1;
        next if $c =~ m{[*{}<>\$|]} || $c =~ m{^(https?:|/)} || $c =~ m{:\d};
        $c =~ s{/$}{};
        next if $ignorar{$c} || resolve($c, $dir);
        next if $c !~ m{/} && $nome{$c};  # nome de pasta citado sozinho (`x/`), que existe no projeto
        $avisos++; print "$nome:$num: aviso: caminho não existe: $c\n";
      }
      for my $t (@ausentes) {
        if ($l =~ /(?<![\p{L}\p{N}_])\Q$t\E(?![\p{L}\p{N}_])/) {
          $sobras++; print "$nome:$num: erro: exemplo do kit que não existe no projeto: $t\n";
        }
      }
    }
  }
  print "citacoes arquivo:linha: $n_cit, erros: $erros; caminhos inexistentes (aviso): $avisos; exemplos do kit sobrando: $sobras\n";
  exit(($erros || $sobras) ? 1 : 0);
'
