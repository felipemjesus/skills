#!/usr/bin/env bash
# Verificação completa: compila e roda todos os testes.
set -euo pipefail
cd "$(dirname "$0")/.."
python3 -m compileall -q app
python3 -m unittest discover -s tests -t . "$@"
