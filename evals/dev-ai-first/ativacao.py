#!/usr/bin/env python3
"""Teste de ativação da descrição da skill (agentskills.io, "Optimizing descriptions").

Uso: python3 -I evals/dev-ai-first/ativacao.py --saida <pasta> [--repeticoes 3] [--modelo M] [--paralelo 4]

Cada pedido de ativacao.json roda N vezes com `claude -p` numa pasta vazia, só com ferramentas de leitura.
Conta como ativada a execução em que o agente chama a ferramenta Skill com dev-ai-first.
Grava <saida>/ativacao-resultado.json com a taxa por pedido e o acerto por grupo (treino, validacao).
Gasta tokens da conta do Claude Code: rode sob demanda, nunca no CI.
Códigos de saída: 0 ok; 2 uso errado.
"""
import argparse
import concurrent.futures
import json
import pathlib
import re
import subprocess

AQUI = pathlib.Path(__file__).resolve().parent
SKILL_MD = AQUI.parents[1] / "skills" / "dev-ai-first" / "SKILL.md"


def ativou(texto, pasta, modelo):
    cmd = ["claude", "-p", texto, "--output-format", "stream-json", "--verbose", "--max-turns", "3",
           "--allowedTools", "Skill", "Read", "Glob", "Grep", "--disallowedTools", "Bash", "Edit", "Write"]
    if modelo:
        cmd += ["--model", modelo]
    r = subprocess.run(cmd, cwd=pasta, capture_output=True, text=True, timeout=600)
    for linha in r.stdout.splitlines():
        try:
            ev = json.loads(linha)
        except json.JSONDecodeError:
            continue
        for bloco in (ev.get("message") or {}).get("content") or []:
            if isinstance(bloco, dict) and bloco.get("type") == "tool_use" and bloco.get("name") == "Skill" \
                    and "dev-ai-first" in json.dumps(bloco.get("input", {})):
                return True
    return False


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--saida", required=True)
    ap.add_argument("--repeticoes", type=int, default=3)
    ap.add_argument("--modelo")
    ap.add_argument("--paralelo", type=int, default=4)
    args = ap.parse_args()

    saida = pathlib.Path(args.saida).resolve()
    vazia = saida / "pasta-vazia"
    vazia.mkdir(parents=True, exist_ok=True)
    pedidos = json.loads((AQUI / "ativacao.json").read_text(encoding="utf-8"))["pedidos"]
    with concurrent.futures.ThreadPoolExecutor(args.paralelo) as ex:
        futuros = {(i, k): ex.submit(ativou, p["texto"], vazia, args.modelo)
                   for i, p in enumerate(pedidos) for k in range(args.repeticoes)}
        res = {chave: f.result() for chave, f in futuros.items()}

    linhas, grupos = [], {}
    for i, p in enumerate(pedidos):
        taxa = sum(res[(i, k)] for k in range(args.repeticoes)) / args.repeticoes
        acertou = (taxa > 0.5) == p["ativar"]
        linhas.append({**p, "taxa": round(taxa, 2), "acertou": acertou})
        g = grupos.setdefault(p["grupo"], [0, 0])
        g[0] += acertou
        g[1] += 1
    m = re.search(r"^description: (.*)$", SKILL_MD.read_text(encoding="utf-8"), re.M)
    resultado = {"descricao": m.group(1) if m else None, "repeticoes": args.repeticoes,
                 "acerto": {g: f"{a}/{n}" for g, (a, n) in grupos.items()}, "pedidos": linhas}
    (saida / "ativacao-resultado.json").write_text(json.dumps(resultado, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({"acerto": resultado["acerto"], "erros": [l["texto"] for l in linhas if not l["acertou"]]}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
