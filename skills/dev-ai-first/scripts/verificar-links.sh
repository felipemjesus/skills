#!/usr/bin/env bash
# Confere se os links relativos dos documentos Markdown apontam para arquivos
# e âncoras que existem. Documento com link quebrado ensina caminho errado ao agente.
#
# Uso: verificar-links.sh [pasta] [--alterados [ref]]
#   sem opção:    todos os .md da pasta
#   --alterados:  só os .md alterados ou novos em relação a ref (padrão HEAD), num repositório git;
#                 use para conferir o que você gerou sem herdar links quebrados antigos do projeto
# Sai com código 1 se houver link quebrado (útil no CI).
# Ignora: links externos (http, mailto), links com marcador {{...}}, blocos de código e pastas de dependências.

set -uo pipefail

raiz='' alterados='' ref=HEAD
while [ $# -gt 0 ]; do
  case "$1" in
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

printf '%s\n' "$lista" | grep -v '^$' | perl -CO -Mutf8 -e '
  use strict; use warnings;
  use Encode qw(decode);
  use File::Basename qw(dirname);
  use File::Spec;
  my %ancoras;  # cache: arquivo -> { slug => 1 }

  sub slug {
    my $t = lc shift;
    $t =~ s/`//g;
    $t =~ s/\[([^\]]*)\]\([^)]*\)/$1/g;
    $t =~ s/[^\p{L}\p{N} _-]//g;
    $t =~ s/ /-/g;
    return $t;
  }
  sub ancoras_de {
    my $arq = shift;
    return $ancoras{$arq} if $ancoras{$arq};
    my %s; my $codigo = 0;
    if (open my $fh, "<", $arq) {
      while (my $l = <$fh>) {
        $l = decode("UTF-8", $l);  # arquivo fora de UTF-8: caractere inválido vira U+FFFD, sem abortar
        if ($l =~ /^```/) { $codigo = !$codigo; next }
        next if $codigo;
        if ($l =~ /^#+\s+(.*?)\s*$/) { $s{ slug($1) } = 1 }
      }
    }
    return $ancoras{$arq} = \%s;
  }

  my ($total, $quebrados) = (0, 0);
  while (my $arq = <STDIN>) {
    chomp $arq;
    next unless -f $arq;
    open my $fh, "<", $arq or next;
    my $dir = dirname($arq);
    my $nome = decode("UTF-8", $arq);
    my $codigo = 0;
    while (my $l = <$fh>) {
      $l = decode("UTF-8", $l);
      if ($l =~ /^```/) { $codigo = !$codigo; next }
      next if $codigo;
      while ($l =~ /\]\(([^)\s]+)\)/g) {
        my $link = $1;
        next if $link =~ /^(https?:|mailto:)/ || $link =~ /\{\{/;
        $total++;
        my ($caminho, $ancora) = split /#/, $link, 2;
        my $alvo = $caminho eq "" ? $arq : File::Spec->catfile($dir, Encode::encode("UTF-8", $caminho));
        if (!-e $alvo) { print "$nome: arquivo não existe: $link\n"; $quebrados++; next }
        if (defined $ancora && $ancora ne "" && -f $alvo && !ancoras_de($alvo)->{$ancora}) {
          print "$nome: âncora não existe: $link\n"; $quebrados++;
        }
      }
    }
  }
  print "links verificados: $total, quebrados: $quebrados\n";
  exit($quebrados ? 1 : 0);
'
