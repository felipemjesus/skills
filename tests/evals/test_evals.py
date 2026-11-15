"""Testes das asserções de evals/dev-ai-first, sem chamar o agente."""
import importlib.util
import json
import pathlib
import shutil
import tempfile
import unittest

RAIZ = pathlib.Path(__file__).resolve().parents[2]
EVALS = RAIZ / "evals" / "dev-ai-first"
_spec = importlib.util.spec_from_file_location("rodar", EVALS / "rodar.py")
rodar = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(rodar)
CASOS = {c["id"]: c for c in json.loads((EVALS / "evals.json").read_text(encoding="utf-8"))["evals"]}


class Evals(unittest.TestCase):
    def setUp(self):
        self.pasta = pathlib.Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.pasta)

    def notas(self, caso):
        rodar.conferir(CASOS[caso], self.pasta)
        dados = json.loads((self.pasta / "grading.json").read_text(encoding="utf-8"))
        return {a["id"]: a["passed"] for a in dados["assertions"]}

    def test_toda_assercao_tem_implementacao(self):
        for caso in CASOS.values():
            for a in caso["assertions"]:
                self.assertTrue(hasattr(rodar, "a_" + a["id"]), a["id"])

    def test_projeto_sintetico_passa_na_verificacao(self):
        rodar.preparar_projeto(CASOS["entregar-bug"], self.pasta / "projeto")
        self.assertTrue(rodar.a_check_verde(self.pasta / "projeto")[0])

    def test_bug_sem_mudanca_reprova_correcao_e_reproducao(self):
        rodar.preparar_projeto(CASOS["entregar-bug"], self.pasta / "projeto")
        n = self.notas("entregar-bug")
        self.assertEqual(n, {"check_verde": True, "corrigido": False, "teste_reproduz": False, "escopo": True, "sem_float": True})

    def test_bug_corrigido_com_teste_passa_em_tudo(self):
        p = self.pasta / "projeto"
        rodar.preparar_projeto(CASOS["entregar-bug"], p)
        codigo = (p / "app" / "pedidos.py").read_text(encoding="utf-8")
        (p / "app" / "pedidos.py").write_text(codigo.replace("return bruto - cupom.valor", "return max(bruto - cupom.valor, 0)"), encoding="utf-8")
        with open(p / "tests" / "test_pedidos.py", "a", encoding="utf-8") as f:
            f.write("\n\nclass CupomMaiorQueOSubtotal(unittest.TestCase):\n"
                    "    def test_total_fica_zero(self):\n"
                    "        self.assertEqual(total(pedido(Item('a', 1, 1000), cupom=Cupom('M', 'fixo', 1500))), 0)\n")
        self.assertTrue(all(self.notas("entregar-bug").values()))

    def test_bug_fora_do_escopo_reprova(self):
        p = self.pasta / "projeto"
        rodar.preparar_projeto(CASOS["entregar-bug"], p)
        (p / "app" / "relatorio.py").write_text("x = 1.5\n", encoding="utf-8")
        self.assertFalse(self.notas("entregar-bug")["escopo"])

    def test_preparar_sem_nada_reprova_agents(self):
        rodar.preparar_projeto(CASOS["preparar-codigo"], self.pasta / "projeto")
        n = self.notas("preparar-codigo")
        self.assertFalse(n["agents_existe"])
        self.assertTrue(n["codigo_intacto"])

    def test_preparar_com_agents_bom_passa(self):
        p = self.pasta / "projeto"
        rodar.preparar_projeto(CASOS["preparar-codigo"], p)
        (p / "AGENTS.md").write_text("# AGENTS.md\n\nVerificar: `bash scripts/check.sh`.\n\nDinheiro é int em centavos (`app/dinheiro.py:1`).\n", encoding="utf-8")
        self.assertTrue(all(self.notas("preparar-codigo").values()))

    def test_governado_reprova_agents_editado(self):
        p = self.pasta / "projeto"
        rodar.preparar_projeto(CASOS["preparar-governado"], p)
        self.assertTrue(self.notas("preparar-governado")["agents_intacto"])
        with open(p / "AGENTS.md", "a", encoding="utf-8") as f:
            f.write("\nlinha nova\n")
        self.assertFalse(self.notas("preparar-governado")["agents_intacto"])

    def test_principios_copiado_pelo_kit_conta_como_intacto(self):
        import subprocess
        p = self.pasta / "projeto"
        rodar.preparar_projeto(CASOS["preparar-codigo"], p)
        subprocess.run(["bash", str(rodar.SKILL / "scripts" / "copiar-kit.sh"), str(p), "--minimo", "--perfil", "backend",
                        "--arquivos", "docs/PRINCIPIOS.md"], check=True, capture_output=True)
        self.assertTrue(rodar.a_principios_intactos(p)[0])
        with open(p / "docs" / "PRINCIPIOS.md", "a", encoding="utf-8") as f:
            f.write("\nregra adaptada ao projeto\n")
        self.assertFalse(rodar.a_principios_intactos(p)[0])

    def test_pedidos_de_ativacao_balanceados(self):
        pedidos = json.loads((EVALS / "ativacao.json").read_text(encoding="utf-8"))["pedidos"]
        self.assertEqual(len(pedidos), 20)
        for grupo in ("treino", "validacao"):
            alvo = [p["ativar"] for p in pedidos if p["grupo"] == grupo]
            self.assertEqual(alvo.count(True), alvo.count(False), grupo)


if __name__ == "__main__":
    unittest.main()
