"""Testes do validador de skills (scripts/validar-skills.py)."""
import pathlib
import shutil
import subprocess
import tempfile
import unittest

VALIDADOR = pathlib.Path(__file__).resolve().parents[2] / "scripts" / "validar-skills.py"


class ValidarSkills(unittest.TestCase):
    def setUp(self):
        self.raiz = pathlib.Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.raiz)

    def skill(self, pasta: str, frontmatter: str, corpo: str = "# Skill\n") -> None:
        destino = self.raiz / pasta
        destino.mkdir(parents=True)
        (destino / "SKILL.md").write_text(f"---\n{frontmatter}\n---\n{corpo}", encoding="utf-8")

    def validar(self) -> subprocess.CompletedProcess:
        return subprocess.run(["python3", "-I", str(VALIDADOR), str(self.raiz)], capture_output=True, text=True)

    def test_skill_valida_com_metadata(self):
        self.skill("boa-skill", 'name: boa-skill\ndescription: Faz algo. Use quando...\nmetadata:\n  version: "1.0.0"')
        self.assertEqual(self.validar().returncode, 0)

    def test_name_diferente_da_pasta(self):
        self.skill("pasta", "name: outro-nome\ndescription: x")
        resultado = self.validar()
        self.assertEqual(resultado.returncode, 1)
        self.assertIn("difere da pasta", resultado.stdout)

    def test_name_com_hifen_duplo_ou_maiuscula(self):
        self.skill("a--b", "name: a--b\ndescription: x")
        self.skill("Maiuscula", "name: Maiuscula\ndescription: x")
        self.assertEqual(self.validar().stdout.count("inválido"), 2)

    def test_description_longa_demais(self):
        self.skill("longa", "name: longa\ndescription: " + "x" * 1025)
        self.assertIn("1025 caracteres", self.validar().stdout)

    def test_corpo_acima_500_linhas(self):
        self.skill("grande", "name: grande\ndescription: x", "linha\n" * 501)
        self.assertIn("501 linhas", self.validar().stdout)

    def test_campo_fora_da_especificacao(self):
        self.skill("extra", "name: extra\ndescription: x\nversion: 1")
        self.assertIn("campo 'version'", self.validar().stdout)


if __name__ == "__main__":
    unittest.main()
