"""Testes dos scripts da skill dev-ai-first, cada um numa pasta temporária."""
import pathlib
import shutil
import subprocess
import tempfile
import unittest

SKILL = pathlib.Path(__file__).resolve().parents[2] / "skills" / "mine" / "dev-ai-first"
SCRIPTS = SKILL / "scripts"


def rodar(script: str, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["bash", str(SCRIPTS / script), *args], capture_output=True, text=True)


def campos(saida: str) -> dict:
    return dict(linha.split(": ", 1) for linha in saida.splitlines() if ": " in linha)


class PastaTemporaria(unittest.TestCase):
    def setUp(self):
        self.pasta = pathlib.Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.pasta)

    def escrever(self, caminho: str, conteudo: str = "") -> pathlib.Path:
        arquivo = self.pasta / caminho
        arquivo.parent.mkdir(parents=True, exist_ok=True)
        arquivo.write_text(conteudo, encoding="utf-8")
        return arquivo


class DetectarProjeto(PastaTemporaria):
    def test_pasta_so_com_readme_e_vazia(self):
        self.escrever("README.md", "# novo")
        saida = campos(rodar("detectar-projeto.sh", str(self.pasta)).stdout)
        self.assertEqual(saida["situacao"], "vazio")

    def test_pasta_com_manifesto_e_codigo(self):
        self.escrever("package.json", "{}")
        self.escrever("src/app.js")
        saida = campos(rodar("detectar-projeto.sh", str(self.pasta)).stdout)
        self.assertEqual(saida["situacao"], "codigo")
        self.assertIn("package.json", saida["manifestos"])

    def test_agents_md_do_kit_e_preparado(self):
        self.escrever("AGENTS.md", "# AGENTS.md\n\n## Checklist de design\n\n## Ordem de verdade\n")
        saida = campos(rodar("detectar-projeto.sh", str(self.pasta)).stdout)
        self.assertEqual(saida["situacao"], "preparado")

    def test_agents_md_de_outra_origem_nao_e_preparado(self):
        self.escrever("AGENTS.md", "# regras do time\n")
        self.escrever("src/app.js")
        saida = campos(rodar("detectar-projeto.sh", str(self.pasta)).stdout)
        self.assertEqual(saida["situacao"], "codigo")
        self.assertIn("AGENTS.md", saida["docs_para_agentes"])

    def test_subprojetos_sem_manifesto_na_raiz_geram_aviso(self):
        self.escrever("backend/package.json", "{}")
        self.escrever("frontend/package.json", "{}")
        resultado = rodar("detectar-projeto.sh", str(self.pasta))
        saida = campos(resultado.stdout)
        self.assertEqual(saida["subprojetos"].split(), ["backend", "frontend"])
        self.assertIn("aviso", saida)

    def test_pasta_inexistente_falha(self):
        self.assertEqual(rodar("detectar-projeto.sh", str(self.pasta / "nao-existe")).returncode, 2)


class CopiarKit(PastaTemporaria):
    def test_copia_o_kit_inteiro_numa_pasta_vazia(self):
        resultado = rodar("copiar-kit.sh", str(self.pasta))
        self.assertEqual(resultado.returncode, 0, resultado.stderr)
        total = sum(1 for p in (SKILL / "assets" / "kit").rglob("*") if p.is_file())
        self.assertIn(f"copiados: {total}", resultado.stdout)
        self.assertTrue((self.pasta / "AGENTS.md").is_file())
        self.assertTrue((self.pasta / "docs" / "adr" / "README.md").is_file())

    def test_nao_sobrescreve_e_lista_o_que_ja_existia(self):
        agents = self.escrever("AGENTS.md", "regras do time")
        resultado = rodar("copiar-kit.sh", str(self.pasta))
        self.assertEqual(agents.read_text(encoding="utf-8"), "regras do time")
        self.assertIn("já existiam", resultado.stdout)
        self.assertIn("AGENTS.md", resultado.stdout)


class ListarMarcadores(PastaTemporaria):
    def test_conta_por_quem_decide_e_falha_com_pendencia(self):
        self.escrever("AGENTS.md", "{{AGENTE: CMD_CHECK}} e {{USUARIO: META}}\n{{AGENTE: FRAMEWORK}}\n")
        resultado = rodar("listar-marcadores.sh", str(self.pasta), "--resumo")
        self.assertIn("AGENTE (o agente preenche a partir do projeto): 2", resultado.stdout)
        self.assertIn("USUARIO (decisão do dev): 1", resultado.stdout)
        self.assertEqual(resultado.returncode, 1)

    def test_ignora_modelos_e_passa_sem_pendencia(self):
        self.escrever("docs/adr/0000-template.md", "{{AGENTE: X}}")
        self.escrever("AGENTS.md", "tudo preenchido")
        resultado = rodar("listar-marcadores.sh", str(self.pasta))
        self.assertIn(": 0", resultado.stdout)
        self.assertEqual(resultado.returncode, 0)


class VerificarLinks(PastaTemporaria):
    def test_kit_da_skill_nao_tem_link_quebrado(self):
        resultado = rodar("verificar-links.sh", str(SKILL / "assets" / "kit"))
        self.assertEqual(resultado.returncode, 0, resultado.stdout)

    def test_ancora_com_acento_e_secao_numerada(self):
        self.escrever("A.md", "## 4.1 Responsabilidades\n\n## Revisão de código\n")
        self.escrever("B.md", "[a](A.md#41-responsabilidades) [b](A.md#revisão-de-código)\n")
        resultado = rodar("verificar-links.sh", str(self.pasta))
        self.assertEqual(resultado.returncode, 0, resultado.stdout)

    def test_acusa_arquivo_e_ancora_inexistentes(self):
        self.escrever("A.md", "## Existe\n")
        self.escrever("B.md", "[a](C.md) [b](A.md#nao-existe)\n")
        resultado = rodar("verificar-links.sh", str(self.pasta))
        self.assertEqual(resultado.returncode, 1)
        self.assertIn("arquivo não existe: C.md", resultado.stdout)
        self.assertIn("âncora não existe: A.md#nao-existe", resultado.stdout)

    def test_ignora_links_externos_marcadores_e_blocos_de_codigo(self):
        self.escrever("A.md", "[x](https://exemplo.com) [y]({{AGENTE: LINK}})\n\n```\n[z](nao-existe.md)\n```\n")
        resultado = rodar("verificar-links.sh", str(self.pasta))
        self.assertEqual(resultado.returncode, 0, resultado.stdout)


if __name__ == "__main__":
    unittest.main()
