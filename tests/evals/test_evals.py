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

    def _validade_corrigida(self, p):
        codigo = (p / "app" / "pedidos.py").read_text(encoding="utf-8")
        (p / "app" / "pedidos.py").write_text(codigo.replace(
            "    if cupom is None:\n        return bruto\n",
            "    if cupom is None or (cupom.validade is not None and hoje > cupom.validade):\n        return bruto\n"), encoding="utf-8")

    def test_validade_sem_mudanca_reprova(self):
        rodar.preparar_projeto(CASOS["entregar-validade"], self.pasta / "projeto")
        n = self.notas("entregar-validade")
        self.assertFalse(n["corrigido_validade"])
        self.assertFalse(n["testes_novos_nao_ocos"])
        self.assertTrue(n["escopo"])

    def test_validade_com_teste_bom_passa_em_tudo(self):
        p = self.pasta / "projeto"
        rodar.preparar_projeto(CASOS["entregar-validade"], p)
        self._validade_corrigida(p)
        (p / "tests" / "test_validade.py").write_text(
            "import unittest\nfrom datetime import date\nfrom app.pedidos import Cupom, Item, Pedido, total\n\n"
            "class Validade(unittest.TestCase):\n"
            "    def test_vencido_da_o_subtotal(self):\n"
            "        p = Pedido(id='x', itens=[Item('a', 1, 1000)], cupom=Cupom('V', 'percentual', 10, validade=date(2026, 1, 1)))\n"
            "        self.assertEqual(total(p, hoje=date(2026, 1, 2)), 1000)\n\n"
            "    def test_ultimo_dia_vale(self):\n"
            "        p = Pedido(id='x', itens=[Item('a', 1, 1000)], cupom=Cupom('V', 'percentual', 10, validade=date(2026, 1, 1)))\n"
            "        self.assertEqual(total(p, hoje=date(2026, 1, 1)), 900)\n", encoding="utf-8")
        self.assertTrue(all(self.notas("entregar-validade").values()))

    def test_validade_com_teste_oco_reprova(self):
        p = self.pasta / "projeto"
        rodar.preparar_projeto(CASOS["entregar-validade"], p)
        self._validade_corrigida(p)
        (p / "tests" / "test_validade.py").write_text(
            "import unittest\nfrom datetime import date\nfrom app.pedidos import Cupom, Item, Pedido, total\n\n"
            "class Validade(unittest.TestCase):\n"
            "    def test_vencido_devolve_inteiro(self):\n"
            "        p = Pedido(id='x', itens=[Item('a', 1, 1000)], cupom=Cupom('V', 'percentual', 10, validade=date(2026, 1, 1)))\n"
            "        self.assertIsInstance(total(p, hoje=date(2026, 1, 2)), int)\n", encoding="utf-8")
        n = self.notas("entregar-validade")
        self.assertTrue(n["corrigido_validade"])
        self.assertFalse(n["testes_novos_nao_ocos"])

    def test_quantidade_recusada_no_item_passa(self):
        p = self.pasta / "projeto"
        rodar.preparar_projeto(CASOS["entregar-quantidade"], p)
        with open(p / "app" / "erros.py", "a", encoding="utf-8") as f:
            f.write("\n\nclass ItemInvalido(ErroDeDominio):\n    pass\n")
        codigo = (p / "app" / "pedidos.py").read_text(encoding="utf-8")
        codigo = codigo.replace("from app.erros import CupomInvalido", "from app.erros import CupomInvalido, ItemInvalido")
        codigo = codigo.replace("    preco_unitario: int  # centavos\n",
                                "    preco_unitario: int  # centavos\n\n    def __post_init__(self):\n"
                                "        if self.quantidade <= 0:\n            raise ItemInvalido(self.quantidade)\n")
        (p / "app" / "pedidos.py").write_text(codigo, encoding="utf-8")
        (p / "tests" / "test_item.py").write_text(
            "import unittest\nfrom app.erros import ErroDeDominio\nfrom app.pedidos import Item\n\n"
            "class ItemQuantidade(unittest.TestCase):\n    def test_zero_recusado(self):\n"
            "        with self.assertRaises(ErroDeDominio):\n            Item('a', 0, 100)\n", encoding="utf-8")
        self.assertTrue(all(self.notas("entregar-quantidade").values()))

    def test_quantidade_com_relatorio_alterado_reprova_escopo(self):
        p = self.pasta / "projeto"
        rodar.preparar_projeto(CASOS["entregar-quantidade"], p)
        with open(p / "tests" / "test_relatorio.py", "a", encoding="utf-8") as f:
            f.write("\n# ajuste\n")
        self.assertFalse(self.notas("entregar-quantidade")["escopo"])

    def test_pedidos_de_ativacao_balanceados(self):
        pedidos = json.loads((EVALS / "ativacao.json").read_text(encoding="utf-8"))["pedidos"]
        self.assertEqual(len(pedidos), 20)
        for grupo in ("treino", "validacao"):
            alvo = [p["ativar"] for p in pedidos if p["grupo"] == grupo]
            self.assertEqual(alvo.count(True), alvo.count(False), grupo)


if __name__ == "__main__":
    unittest.main()
