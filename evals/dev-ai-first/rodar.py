#!/usr/bin/env python3
"""Roda os casos de evals.json com e sem a skill e confere as asserções por script.

Uso: python3 -I evals/dev-ai-first/rodar.py --saida <pasta> [--casos a,b] [--bracos com,sem]
                                            [--execucoes N] [--modelo M] [--paralelo N] [--so-conferir]

Para cada caso, braço e execução cria <saida>/<caso>/<braco>/exec-<k>/ com:
  projeto/       cópia do projeto sintético, num repositório git com um commit
  saida.json     resposta do `claude -p --output-format json`
  timing.json    total_tokens, duration_ms, custo_usd
  grading.json   cada asserção com passou/evidência
e grava <saida>/benchmark.json com a média por caso e braço, média e desvio por braço e o delta (com − sem).
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


def a_escopo(p, caso):
    permitido = caso.get("escopo_app", ["app/pedidos.py"])
    fora = [l for l in _status(p, "app", "scripts", "tests/test_relatorio.py") if l[3:] not in permitido]
    return not fora, "; ".join(fora) or "só " + ", ".join(permitido)


def a_sem_float(p):
    novas = [l for l in sh(["git", "diff", "HEAD", "--", "app"], p).stdout.splitlines()
             if l.startswith("+") and not l.startswith("+++") and "float" in l]
    return not novas, "; ".join(novas) or "nenhum float novo"


OCULTO_VALIDADE = """
from datetime import date
from app.pedidos import Cupom, Item, Pedido, total
p = lambda c: Pedido(id="x", itens=[Item("a", 1, 1000)], cupom=c)
d = date(2026, 3, 10)
assert total(p(Cupom("V", "percentual", 10, validade=d)), hoje=date(2026, 3, 11)) == 1000, "vencido deveria dar o subtotal"
assert total(p(Cupom("V", "fixo", 300, validade=d)), hoje=date(2026, 3, 11)) == 1000, "vencido (fixo) deveria dar o subtotal"
assert total(p(Cupom("V", "percentual", 10, validade=d)), hoje=d) == 900, "no último dia o cupom vale"
assert total(p(Cupom("V", "percentual", 10)), hoje=date(2030, 1, 1)) == 900, "sem validade o cupom vale"
assert total(p(None)) == 1000
"""

OCULTO_QUANTIDADE = """
from app.erros import ErroDeDominio
from app.pedidos import Item, Pedido, total
from app.repositorio import RepositorioDePedidos
def recusa(q):
    try:
        p = Pedido(id="x", itens=[Item("a", q, 100)])
        RepositorioDePedidos().salvar(p)
        total(p)
    except ErroDeDominio:
        return True
    return False
assert recusa(0), "quantidade 0 deveria ser recusada com ErroDeDominio"
assert recusa(-1), "quantidade -1 deveria ser recusada com ErroDeDominio"
assert not recusa(1), "quantidade 1 deveria passar"
"""


def _oculto(p, codigo):
    r = sh([sys.executable, "-I", "-c", "import sys; sys.path.insert(0, '.')\n" + codigo], p)
    return r.returncode == 0, "teste oculto passou" if r.returncode == 0 else (r.stderr.strip().splitlines() or ["falhou"])[-1]


OCULTO_PROGRESSIVO = """
from app.pedidos import Cupom, Item, Pedido, total
p = lambda sub: Pedido(id="x", itens=[Item("a", 1, sub)], cupom=Cupom("PROG", "progressivo", 0))
assert total(p(25000)) == 22500, f"R$ 250: 2 faixas, 10%: {total(p(25000))}"
assert total(p(120000)) == 96000, f"R$ 1200: teto de 20%: {total(p(120000))}"
assert total(p(9999)) == 9999, f"abaixo de R$ 100: sem desconto: {total(p(9999))}"
assert total(p(10000)) == 9500, f"R$ 100 exatos: 5%: {total(p(10000))}"
"""

REGRA_DO_TIME = """
from app import auditoria
from app.pedidos import Cupom, Item, Pedido, total
auditoria.REGISTROS.clear()
total(Pedido(id="ped-77", itens=[Item("a", 1, 25000)], cupom=Cupom("PROG", "progressivo", 0)))
assert any("ped-77" in str(r) and "PROG" in str(r) for r in auditoria.REGISTROS), auditoria.REGISTROS
"""


def a_corrigido_progressivo(p):
    return _oculto(p, OCULTO_PROGRESSIVO)


def a_regra_do_time(p):
    return _oculto(p, REGRA_DO_TIME)


def a_corrigido_validade(p):
    return _oculto(p, OCULTO_VALIDADE)


def a_recusa_quantidade(p):
    return _oculto(p, OCULTO_QUANTIDADE)


LISTAR_TESTES = """
import unittest
def ids(s):
    for t in s:
        if isinstance(t, unittest.TestSuite):
            yield from ids(t)
        else:
            yield t.id()
print("\\n".join(ids(unittest.defaultTestLoader.discover("tests", top_level_dir="."))))
"""
MUTANTES = {
    "total devolve 0": "\n\ndef total(pedido, hoje=None):\n    return 0\n",
    "total devolve o subtotal": "\n\ndef total(pedido, hoje=None):\n    return subtotal(pedido)\n",
}


def _ids_de_teste(pasta):
    r = sh([sys.executable, "-c", LISTAR_TESTES], pasta)
    return {i for i in r.stdout.split() if i and "_FailedTest" not in i}


def a_testes_novos_nao_ocos(p):
    """Teste novo que passa no código original e nos mutantes não prova nada: é oco."""
    novos = sorted(_ids_de_teste(p) - _ids_de_teste(BASE))
    if not novos:
        return False, "nenhum teste novo"
    with tempfile.TemporaryDirectory() as tmp:
        variantes = {}
        original = pathlib.Path(tmp) / "original"
        shutil.copytree(p, original, ignore=shutil.ignore_patterns(".git", "__pycache__"))
        shutil.rmtree(original / "app")
        shutil.copytree(BASE / "app", original / "app")
        variantes["código original"] = original
        for nome, corpo in MUTANTES.items():
            m = pathlib.Path(tmp) / nome.replace(" ", "-")
            shutil.copytree(p, m, ignore=shutil.ignore_patterns(".git", "__pycache__"))
            with open(m / "app" / "pedidos.py", "a", encoding="utf-8") as f:
                f.write(corpo)
            variantes[nome] = m
        ocos = [t for t in novos
                if all(sh([sys.executable, "-m", "unittest", t], pasta).returncode == 0 for pasta in variantes.values())]
    return not ocos, (f"ocos: {', '.join(ocos)}" if ocos else f"{len(novos)} testes novos, todos falham em algum mutante")


def conferir(caso, pasta: pathlib.Path):
    p = pasta / "projeto"
    resultado = []
    for a in caso["assertions"]:
        try:
            f = globals()["a_" + a["id"]]
            ok, evid = f(p, caso) if f.__code__.co_argcount == 2 else f(p)
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
    ap.add_argument("--execucoes", type=int, default=1)
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
    tarefas = [(c, b, saida / c["id"] / b / f"exec-{k}") for c in casos for b in bracos for k in range(1, args.execucoes + 1)]

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
    execucoes = {}  # (caso, braço) -> lista de medições
    for c, b, pasta in tarefas:
        taxa = conferir(c, pasta)
        t = json.loads((pasta / "timing.json").read_text(encoding="utf-8")) if (pasta / "timing.json").exists() else {}
        execucoes.setdefault((c["id"], b), []).append({"pass_rate": taxa, "total_tokens": t.get("total_tokens"),
                                                       "duration_ms": t.get("duration_ms")})
    metricas = ("pass_rate", "total_tokens", "duration_ms")
    for (cid, b), medidas in execucoes.items():
        bench["casos"].setdefault(cid, {})[b] = {k: resumo([m[k] for m in medidas])["media"] for k in metricas}
        bench["casos"][cid][b]["execucoes"] = len(medidas)
    for b in bracos:
        medidas = [m for (cid, bb), ms in execucoes.items() if bb == b for m in ms]
        bench["bracos"][b] = {k: resumo([m[k] for m in medidas]) for k in metricas}
    if {"com", "sem"} <= set(bracos):
        bench["delta"] = {k: (None if bench["bracos"]["com"][k]["media"] is None or bench["bracos"]["sem"][k]["media"] is None
                              else round(bench["bracos"]["com"][k]["media"] - bench["bracos"]["sem"][k]["media"], 3))
                          for k in metricas}
    (saida / "benchmark.json").write_text(json.dumps(bench, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(bench, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
