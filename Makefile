.DEFAULT_GOAL := help

PYTHON ?= python3
SKILL_DIRS := $(patsubst %/SKILL.md,%,$(wildcard skills/*/*/SKILL.md))
SCRIPTS := $(wildcard skills/*/*/scripts/*.sh)
# verificador de links da dev-ai-first, usado para todas as skills do repositório
VERIFICAR_LINKS := skills/mine/dev-ai-first/scripts/verificar-links.sh

.PHONY: help check test verify

help:
	@printf '%s\n' \
	  'make check    Valida as skills (frontmatter, links, sintaxe dos scripts)' \
	  'make test     Roda os testes dos scripts e do validador' \
	  'make verify   check + test (o que o CI roda)'

check:
	@$(PYTHON) -I scripts/validar-skills.py
	@for dir in $(SKILL_DIRS) docs; do bash $(VERIFICAR_LINKS) $$dir || exit 1; done
	@for script in $(SCRIPTS); do bash -n $$script || exit 1; done
	@if command -v shellcheck >/dev/null 2>&1; then shellcheck -S warning $(SCRIPTS); \
	  else echo "shellcheck não instalado: análise estática dos scripts pulada"; fi

test:
	@$(PYTHON) -I -m unittest discover -s tests -p 'test_*.py' -t . -v

verify: check test
