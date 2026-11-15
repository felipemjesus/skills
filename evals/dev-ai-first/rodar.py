#!/usr/bin/env python3
"""Roda os casos de evals.json com e sem a skill e confere as asserções por script.

Uso: python3 -I evals/dev-ai-first/rodar.py --saida <pasta> [--casos a,b] [--bracos com,sem]
                                            [--modelo M] [--paralelo N] [--so-conferir]

Para cada caso e braço cria <saida>/<caso>/<braco>/ com:
  projeto/       cópia do projeto sintético, num repositório git com um commit
  saida.json     resposta do `claude -p --output-format json`
  timing.json    total_tokens, duration_ms, custo_usd
  grading.json   cada asserção com passou/evidência
e grava <saida>/benchmark.json com média e desvio por braço e o delta (com − sem).
--so-conferir refaz só as asserções e o benchmark, sem chamar o agente.
Gasta tokens da conta do Claude Code: rode sob demanda, nunca no CI.
Códigos de saída: 0 ok; 2 uso errado.
"""
import argparse
import concurrent.futures
import functools
import json
import pathlib
import re
import shutil
import statistics
import subprocess
import sys
import tempfile

AQUI = pathlib.Path(__file__).resolve().parent
SKILL = AQUI.parents[1] / "skills" / "dev-ai-first"
BASE = AQUI / "projetos" / "pedidos"
FERRAMENTAS = ["Bash", "Read", "Edit", "Write", "Glob", "Grep"]


def sh(cmd, cwd, timeout=600):
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout)


def preparar_projeto(caso, destino: pathlib.Path):
    if destino.exists():
        shutil.rmtree(destino)
    for origem in caso["files"]:
        shutil.copytree(AQUI / origem, destino, dirs_exist_ok=True)
    for cmd in (["git", "init", "-q", "-b", "main"], ["git", "add", "-A"],
                ["git", "-c", "user.name=eval", "-c", "user.email=eval@exemplo.invalid", "commit", "-qm", "inicial"]):
        sh(cmd, destino)


def rodar_agente(caso, braco, pasta: pathlib.Path, modelo):
    projeto = pasta / "projeto"
    prompt = caso["prompt"]
    cmd = ["claude", "-p", ("/dev-ai-first " + prompt) if braco == "com" else prompt,
           "--output-format", "json", "--permission-mode", "acceptEdits", "--allowedTools", *FERRAMENTAS]
    cmd += ["--add-dir", str(SKILL)] if braco == "com" else ["--disallowedTools", "Skill"]
    if modelo:
        cmd += ["--model", modelo]
    r = sh(cmd, projeto, timeout=1800)
    (pasta / "saida.json").write_text(r.stdout or json.dumps({"erro": r.stderr[-2000:]}), encoding="utf-8")
    try:
        dados = json.loads(r.stdout)
    except json.JSONDecodeError:
        dados = {}
    uso = dados.get("modelUsage") or {}
    if uso:
        total = sum(m.get(k, 0) for m in uso.values()
                    for k in ("inputTokens", "outputTokens", "cacheReadInputTokens", "cacheCreationInputTokens"))
    else:
        u = dados.get("usage") or {}
        total = sum(u.get(k, 0) for k in ("input_tokens", "output_tokens", "cache_read_input_tokens", "cache_creation_input_tokens"))
    timing = {"total_tokens": total, "duration_ms": dados.get("duration_ms"), "custo_usd": dados.get("total_cost_usd"),
              "turnos": dados.get("num_turns"), "erro": dados.get("is_error", not dados)}
    (pasta / "timing.json").write_text(json.dumps(timing, indent=2), encoding="utf-8")


# ---- asserções: cada uma devolve (passou, evidência) ----

def _agents(p):
    return p / "AGENTS.md"


def _md(p):
    return [f for f in p.rglob("*.md") if ".git" not in f.parts]


def _status(p, *caminhos):
    return [l for l in sh(["git", "status", "--porcelain", "--", *caminhos], p).stdout.splitlines() if l.strip()]


def a_agents_existe(p):
    return _agents(p).is_file(), "AGENTS.md " + ("existe" if _agents(p).is_file() else "ausente")


def a_agents_curto(p):
    n = _agents(p).stat().st_size if _agents(p).is_file() else 0
    return 0 < n <= 3072, f"{n} bytes"


def a_agents_comando(p):
    t = _agents(p).read_text(encoding="utf-8") if _agents(p).is_file() else ""
    m = re.search(r"scripts/check\.sh|unittest", t)
    return bool(m), m.group(0) if m else "nenhum comando de verificação"


def a_agents_regra_centavos(p):
    t = _agents(p).read_text(encoding="utf-8").lower() if _agents(p).is_file() else ""
    return "centavo" in t, "cita centavos" if "centavo" in t else "não cita"


def a_sem_marcador_agente(p):
    achados = [str(f.relative_to(p)) for f in _md(p)
               if re.search(r"\{\{AGENTE: (?!\.\.\.\}\})", f.read_text(encoding="utf-8", errors="replace"))]
    return not achados, ", ".join(achados) or "nenhum"


def a_citacoes_validas(p):
    r = sh(["bash", str(SKILL / "scripts" / "verificar-citacoes.sh"), str(p), "--limite", "10"], p)
    return r.returncode == 0, (r.stdout.strip().splitlines() or ["sem saída"])[-1]


def a_links_validos(p):
    r = sh(["bash", str(SKILL / "scripts" / "verificar-links.sh"), str(p), "--limite", "10"], p)
    return r.returncode == 0, (r.stdout.strip().splitlines() or ["sem saída"])[-1]


def a_codigo_intacto(p):
    s = _status(p, "app", "tests", "scripts")
    return not s, "; ".join(s) or "sem mudanças"


PERFIS = [["--perfil", "backend"], ["--perfil", "frontend", "--frontend", "spa"], ["--perfil", "frontend", "--frontend", "servidor"],
          ["--perfil", "fullstack", "--frontend", "spa"], ["--perfil", "fullstack", "--frontend", "servidor"]]


@functools.lru_cache(maxsize=None)
def _principios_do_kit():
    """O PRINCIPIOS.md que o copiar-kit.sh gera em cada perfil (os blocos condicionais já resolvidos)."""
    versoes = []
    for perfil in PERFIS:
        with tempfile.TemporaryDirectory() as tmp:
            sh(["bash", str(SKILL / "scripts" / "copiar-kit.sh"), tmp, "--minimo", *perfil, "--arquivos", "docs/PRINCIPIOS.md"], tmp)
            alvo = pathlib.Path(tmp) / "docs" / "PRINCIPIOS.md"
            if alvo.exists():
                versoes.append(alvo.read_bytes())
    return tuple(versoes)


def a_principios_intactos(p):
    f = p / "docs" / "PRINCIPIOS.md"
    if not f.exists():
        return True, "não existe (n/a)"
    igual = f.read_bytes() in _principios_do_kit()
    return igual, "idêntico ao gerado pelo copiar-kit" if igual else "editado"


def a_agents_intacto(p):
    igual = _agents(p).is_file() and _agents(p).read_bytes() == (AQUI / "projetos" / "governado" / "AGENTS.md").read_bytes()
    return igual, "intacto" if igual else "alterado ou removido"


def a_check_verde(p):
    r = sh(["bash", "scripts/check.sh"], p)
    return r.returncode == 0, (r.stderr.strip().splitlines() or ["sem saída"])[-1]


OCULTO = """
from app.pedidos import Cupom, Item, Pedido, total
p = lambda c: Pedido(id="x", itens=[Item("a", 1, 1000)], cupom=c)
assert total(p(Cupom("M", "fixo", 1500))) == 0, total(p(Cupom("M", "fixo", 1500)))
assert total(p(Cupom("I", "fixo", 1000))) == 0
assert total(p(Cupom("C", "fixo", 300))) == 700
assert total(p(Cupom("D", "percentual", 10))) == 900
assert total(p(None)) == 1000
"""


def a_corrigido(p):
    r = sh([sys.executable, "-I", "-c", "import sys; sys.path.insert(0, '.')\n" + OCULTO], p)
    return r.returncode == 0, "teste oculto passou" if r.returncode == 0 else (r.stderr.strip().splitlines() or ["falhou"])[-1]


def a_teste_reproduz(p):
    with tempfile.TemporaryDirectory() as tmp:
        copia = pathlib.Path(tmp) / "p"
        shutil.copytree(p, copia, ignore=shutil.ignore_patterns(".git", "__pycache__"))
        shutil.rmtree(copia / "app")
        shutil.copytree(BASE / "app", copia / "app")
        r = sh([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-t", "."], copia)
    return r.returncode != 0, "algum teste falha no código original" if r.returncode else "todos passam no código original"


def a_escopo(p):
    fora = [l for l in _status(p, "app", "scripts") if not l.endswith("app/pedidos.py")]
    return not fora, "; ".join(fora) or "só app/pedidos.py"


def a_sem_float(p):
    novas = [l for l in sh(["git", "diff", "HEAD", "--", "app"], p).stdout.splitlines()
             if l.startswith("+") and not l.startswith("+++") and "float" in l]
    return not novas, "; ".join(novas) or "nenhum float novo"


def conferir(caso, pasta: pathlib.Path):
    p = pasta / "projeto"
    resultado = []
    for a in caso["assertions"]:
        try:
            ok, evid = globals()["a_" + a["id"]](p)
        except Exception as e:  # asserção que quebra conta como falha, com o motivo
            ok, evid = False, f"erro ao conferir: {e}"
        resultado.append({"id": a["id"], "text": a["text"], "passed": bool(ok), "evidence": evid})
    taxa = sum(r["passed"] for r in resultado) / len(resultado)
    (pasta / "grading.json").write_text(json.dumps({"pass_rate": taxa, "assertions": resultado}, indent=2, ensure_ascii=False), encoding="utf-8")
    return taxa


def resumo(valores):
    v = [x for x in valores if x is not None]
    if not v:
        return {"media": None, "desvio": None}
    return {"media": round(statistics.mean(v), 3), "desvio": round(statistics.pstdev(v), 3)}


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--saida", required=True)
    ap.add_argument("--casos")
    ap.add_argument("--bracos", default="com,sem")
    ap.add_argument("--modelo")
    ap.add_argument("--paralelo", type=int, default=2)
    ap.add_argument("--so-conferir", action="store_true")
    args = ap.parse_args()

    casos = json.loads((AQUI / "evals.json").read_text(encoding="utf-8"))["evals"]
    if args.casos:
        pedidos = args.casos.split(",")
        desconhecidos = set(pedidos) - {c["id"] for c in casos}
        if desconhecidos:
            ap.error(f"caso desconhecido: {', '.join(sorted(desconhecidos))}")
        casos = [c for c in casos if c["id"] in pedidos]
    bracos = args.bracos.split(",")
    if set(bracos) - {"com", "sem"}:
        ap.error("--bracos aceita com e sem")
    saida = pathlib.Path(args.saida).resolve()
    tarefas = [(c, b, saida / c["id"] / b) for c in casos for b in bracos]

    if not args.so_conferir:
        for c, _, pasta in tarefas:
            pasta.mkdir(parents=True, exist_ok=True)
            preparar_projeto(c, pasta / "projeto")
        with concurrent.futures.ThreadPoolExecutor(args.paralelo) as ex:
            futuros = {ex.submit(rodar_agente, c, b, pasta, args.modelo): (c["id"], b) for c, b, pasta in tarefas}
            for f in concurrent.futures.as_completed(futuros):
                f.result()
                print(f"rodou: {futuros[f][0]} / {futuros[f][1]}", file=sys.stderr)

    bench = {"skill_name": "dev-ai-first", "casos": {}, "bracos": {}}
    for c, b, pasta in tarefas:
        taxa = conferir(c, pasta)
        t = json.loads((pasta / "timing.json").read_text(encoding="utf-8")) if (pasta / "timing.json").exists() else {}
        bench["casos"].setdefault(c["id"], {})[b] = {"pass_rate": round(taxa, 3), "total_tokens": t.get("total_tokens"),
                                                    "duration_ms": t.get("duration_ms")}
    for b in bracos:
        linhas = [v[b] for v in bench["casos"].values() if b in v]
        bench["bracos"][b] = {k: resumo([l[k] for l in linhas]) for k in ("pass_rate", "total_tokens", "duration_ms")}
    if {"com", "sem"} <= set(bracos):
        bench["delta"] = {k: (None if bench["bracos"]["com"][k]["media"] is None or bench["bracos"]["sem"][k]["media"] is None
                              else round(bench["bracos"]["com"][k]["media"] - bench["bracos"]["sem"][k]["media"], 3))
                          for k in ("pass_rate", "total_tokens", "duration_ms")}
    (saida / "benchmark.json").write_text(json.dumps(bench, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(bench, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
