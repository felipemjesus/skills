"""Testes dos scripts da skill dev-ai-first, cada um numa pasta temporária."""
import pathlib
import shutil
import subprocess
import tempfile
import unittest

SKILL = pathlib.Path(__file__).resolve().parents[2] / "skills" / "dev-ai-first"
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

    def test_agents_md_de_outra_origem_e_governado(self):
        self.escrever("AGENTS.md", "# regras do time\n")
        self.escrever("src/app.js")
        saida = campos(rodar("detectar-projeto.sh", str(self.pasta)).stdout)
        self.assertEqual(saida["situacao"], "governado")
        self.assertIn("AGENTS.md", saida["docs_para_agentes"])

    def test_instrucoes_para_agentes_em_subpasta_contam(self):
        self.escrever("src/app.js")
        self.escrever("modulos/x/AGENTS.md", "regras locais")
        self.escrever(".claude/skills/y/SKILL.md", "skill local")
        saida = campos(rodar("detectar-projeto.sh", str(self.pasta)).stdout)
        self.assertEqual(saida["situacao"], "governado")
        self.assertIn("modulos/x/AGENTS.md", saida["docs_para_agentes"])
        self.assertIn(".claude/skills/y/SKILL.md", saida["docs_para_agentes"])

    def test_sem_manifesto_mostra_linguagem_e_avisa(self):
        self.escrever("lib/a.php", "<?php")
        self.escrever("lib/b.php", "<?php")
        resultado = rodar("detectar-projeto.sh", str(self.pasta))
        saida = campos(resultado.stdout)
        self.assertIn("php:2", saida["linguagens"])
        self.assertIn("sem manifesto", resultado.stdout)

    def test_manifesto_na_profundidade_quatro(self):
        self.escrever("apps/web/cliente/painel/package.json", "{}")
        saida = campos(rodar("detectar-projeto.sh", str(self.pasta)).stdout)
        self.assertIn("apps/web/cliente/painel/package.json", saida["manifestos"])

    def test_sinais_de_modulos_e_forja(self):
        self.escrever("package.json", '{"dependencies": {"react": "1", "express": "1", "bullmq": "1"}}')
        self.escrever(".gitlab-ci.yml", "x: 1")
        self.escrever("docker-compose.yml", "services: {}")
        saida = campos(rodar("detectar-projeto.sh", str(self.pasta)).stdout)
        self.assertEqual(saida["modulos_sugeridos"].split(), ["api", "eventos", "gitlab"])
        self.assertEqual(saida["perfil_sugerido"], "fullstack (frontend: spa)")
        self.assertEqual(saida["forja"], "gitlab")
        self.assertIn("docker-compose.yml", saida["ambiente_local"])

    def test_arquivo_fora_de_utf8_gera_aviso(self):
        (self.pasta / "a.php").write_bytes("<?php // ação".encode("latin-1"))
        resultado = rodar("detectar-projeto.sh", str(self.pasta))
        self.assertIn("1 de 1", campos(resultado.stdout)["codificacao"])
        self.assertIn("grep -a", resultado.stdout)

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
    MODULOS = "api,eventos,observabilidade,claude,github,gitlab,estados,cli,bdd,verificacao-arquitetura"

    def indice(self):
        linhas = (SKILL / "assets" / "kit-indice.tsv").read_text(encoding="utf-8").splitlines()[1:]
        return [linha.split("\t")[:2] for linha in linhas]

    def copiar(self, destino, *args):
        return rodar("copiar-kit.sh", str(destino), *args)

    def test_exige_estrutura_e_perfil(self):
        self.assertEqual(self.copiar(self.pasta).returncode, 2)
        self.assertEqual(self.copiar(self.pasta, "--estrutura", "projeto").returncode, 2)
        sem_variante = self.copiar(self.pasta, "--estrutura", "projeto", "--perfil", "frontend")
        self.assertEqual(sem_variante.returncode, 2)
        self.assertIn("--frontend", sem_variante.stderr)

    def test_estrutura_projeto_backend_copia_so_o_nucleo(self):
        resultado = self.copiar(self.pasta, "--estrutura", "projeto", "--perfil", "backend")
        self.assertEqual(resultado.returncode, 0, resultado.stderr)
        nucleo = [arq for modulo, arq in self.indice() if modulo == "nucleo"]  # minimo fica de fora
        self.assertIn(f"copiados: {len(nucleo)}", resultado.stdout)
        self.assertTrue((self.pasta / "docs" / "VERIFICACAO.md").is_file())
        self.assertFalse((self.pasta / "docs" / "FRONTEND.md").exists())
        self.assertFalse((self.pasta / "docs" / "adr" / "0005-framework-first.md").exists())

    def test_perfil_e_estrutura_kit_trazem_os_arquivos_deles(self):
        self.copiar(self.pasta, "--estrutura", "kit", "--perfil", "fullstack", "--frontend", "spa", "--modulos", "api")
        self.assertTrue((self.pasta / "docs" / "FRONTEND.md").is_file())
        self.assertTrue((self.pasta / "docs" / "API_GUIDELINES.md").is_file())
        self.assertTrue((self.pasta / "docs" / "adr" / "0005-framework-first.md").is_file())
        self.assertFalse((self.pasta / "docs" / "EVENTS.md").exists())

    def test_modulo_desconhecido_ou_de_backend_em_frontend_falha(self):
        self.assertEqual(self.copiar(self.pasta, "--estrutura", "projeto", "--perfil", "backend", "--modulos", "xyz").returncode, 2)
        r = self.copiar(self.pasta, "--estrutura", "projeto", "--perfil", "frontend", "--frontend", "spa", "--modulos", "api")
        self.assertEqual(r.returncode, 2)

    def test_todas_as_combinacoes_sem_marcador_sobrando_e_sem_link_quebrado(self):
        perfis = (("backend",), ("frontend", "--frontend", "spa"), ("frontend", "--frontend", "servidor"),
                  ("fullstack", "--frontend", "spa"), ("fullstack", "--frontend", "servidor"))
        for estrutura in ("projeto", "kit"):
            for perfil in perfis:
                for modulos in (None, self.MODULOS):
                    if modulos and perfil[0] == "frontend":
                        modulos = "observabilidade,claude,github,gitlab,estados,cli,bdd,verificacao-arquitetura"
                    with self.subTest(estrutura=estrutura, perfil=perfil, modulos=bool(modulos)):
                        destino = pathlib.Path(tempfile.mkdtemp(dir=self.pasta))
                        args = ["--estrutura", estrutura, "--perfil", *perfil] + (["--modulos", modulos] if modulos else [])
                        r = self.copiar(destino, *args)
                        self.assertEqual(r.returncode, 0, r.stderr)
                        for arq in destino.rglob("*.md"):
                            texto = arq.read_text(encoding="utf-8")
                            self.assertNotIn("<!-- se:", texto, arq)
                            self.assertNotIn("<!-- fim:", texto, arq)
                            self.assertNotRegex(texto, r"estilo-(kit|atual)", arq)
                        links = rodar("verificar-links.sh", str(destino))
                        self.assertEqual(links.returncode, 0, links.stdout)

    def test_agents_md_cabe_no_limite(self):
        destino = pathlib.Path(tempfile.mkdtemp(dir=self.pasta))
        self.copiar(destino, "--estrutura", "kit", "--perfil", "fullstack", "--frontend", "spa", "--modulos", self.MODULOS)
        self.assertLessEqual(len((destino / "AGENTS.md").read_bytes()), 3584)

    def test_arquivos_e_manifesto(self):
        r = self.copiar(self.pasta, "--estrutura", "projeto", "--perfil", "backend", "--arquivos", "AGENTS.md,docs/VERIFICACAO.md")
        self.assertIn("copiados: 2", r.stdout)
        manifesto = (self.pasta / ".dev-ai-first" / "kit.lst").read_text(encoding="utf-8")
        self.assertIn("AGENTS.md", manifesto)
        self.assertIn("--estrutura projeto --perfil backend", manifesto)
        de_novo = self.copiar(self.pasta, "--estrutura", "projeto", "--perfil", "backend", "--arquivos", "AGENTS.md,CLAUDE.md", "--modulos", "claude")
        self.assertIn("copiados: 1", de_novo.stdout)
        self.assertIn("já copiados antes pela skill (mantidos): 1", de_novo.stdout)
        self.assertNotIn("mesclar à mão", de_novo.stdout)

    def test_minimo_copia_so_os_quatro_documentos_e_e_preparado(self):
        for perfil in (("backend",), ("frontend", "--frontend", "spa"), ("fullstack", "--frontend", "servidor")):
            with self.subTest(perfil=perfil):
                destino = pathlib.Path(tempfile.mkdtemp(dir=self.pasta))
                r = self.copiar(destino, "--minimo", "--perfil", *perfil)
                self.assertEqual(r.returncode, 0, r.stderr)
                gerados = sorted(str(p.relative_to(destino)) for p in destino.rglob("*.md"))
                self.assertEqual(gerados, ["AGENTS.md", "docs/IA_FIRST.md", "docs/PRINCIPIOS.md", "docs/VERIFICACAO.md"])
                self.assertEqual(rodar("verificar-links.sh", str(destino)).returncode, 0)
                principios = (destino / "docs" / "PRINCIPIOS.md").read_text(encoding="utf-8")
                self.assertNotIn("{{", principios)
                self.assertNotIn("<!-- se:", principios)
                self.assertLessEqual(len((destino / "AGENTS.md").read_bytes()), 1700)
                self.assertEqual(campos(rodar("detectar-projeto.sh", str(destino)).stdout)["situacao"], "preparado")

    def test_verificacao_do_minimo_igual_a_do_kit(self):
        kit = (SKILL / "assets" / "kit" / "docs" / "VERIFICACAO.md").read_bytes()
        minimo = (SKILL / "assets" / "minimo" / "docs" / "VERIFICACAO.md").read_bytes()
        self.assertEqual(kit, minimo, "atualize as duas cópias de VERIFICACAO.md juntas")

    def test_minimo_governado_com_arquivos(self):
        self.escrever("AGENTS.md", "regras do time")
        r = self.copiar(self.pasta, "--minimo", "--perfil", "backend", "--arquivos", "docs/PRINCIPIOS.md,docs/IA_FIRST.md")
        self.assertIn("copiados: 2", r.stdout)
        self.assertEqual((self.pasta / "AGENTS.md").read_text(encoding="utf-8"), "regras do time")

    def test_nao_sobrescreve_e_lista_o_que_ja_existia(self):
        agents = self.escrever("AGENTS.md", "regras do time")
        resultado = self.copiar(self.pasta, "--estrutura", "projeto", "--perfil", "backend")
        self.assertEqual(agents.read_text(encoding="utf-8"), "regras do time")
        self.assertIn("mesclar à mão", resultado.stdout)
        self.assertIn("AGENTS.md", resultado.stdout)


class ListarMarcadores(PastaTemporaria):
    def test_conta_por_quem_decide_e_falha_com_pendencia(self):
        self.escrever("AGENTS.md", "{{AGENTE: CMD_CHECK}} e {{USUARIO: META}}\n{{AGENTE: FRAMEWORK}}\n")
        resultado = rodar("listar-marcadores.sh", str(self.pasta), "--resumo")
        self.assertIn("AGENTE (o agente preenche a partir do projeto): 2", resultado.stdout)
        self.assertIn("USUARIO (decisão do dev): 1", resultado.stdout)
        self.assertEqual(resultado.returncode, 1)

    def test_argumentos_em_qualquer_ordem_e_verificar(self):
        self.escrever("AGENTS.md", "{{VERIFICAR: VERSAO_EM_PRODUCAO}} {{AGENTE: ...}}\n")
        resultado = rodar("listar-marcadores.sh", "--resumo", str(self.pasta))
        self.assertIn("VERIFICAR (fato que o dev confirma): 1", resultado.stdout)
        self.assertIn("AGENTE (o agente preenche a partir do projeto): 0", resultado.stdout)
        self.assertEqual(resultado.returncode, 0)  # só AGENTE pendente reprova

    def test_com_manifesto_olha_so_o_que_a_skill_copiou(self):
        self.escrever("AGENTS.md", "{{AGENTE: X}}")
        self.escrever("notas.md", "{{AGENTE: Y}} {{USUARIO: Z}}")
        self.escrever(".dev-ai-first/kit.lst", "# copiar-kit: x\nAGENTS.md\n")
        resultado = rodar("listar-marcadores.sh", str(self.pasta), "--resumo")
        self.assertIn("AGENTE (o agente preenche a partir do projeto): 1", resultado.stdout)
        self.assertIn("USUARIO (decisão do dev): 0", resultado.stdout)
        tudo = rodar("listar-marcadores.sh", str(self.pasta), "--resumo", "--tudo")
        self.assertIn("AGENTE (o agente preenche a partir do projeto): 2", tudo.stdout)

    def test_opcao_desconhecida_falha(self):
        self.assertEqual(rodar("listar-marcadores.sh", str(self.pasta), "--xyz").returncode, 2)

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


class VerificarLinksAlterados(PastaTemporaria):
    def git(self, *args):
        subprocess.run(["git", "-C", str(self.pasta), *args], check=True, capture_output=True)

    def test_alterados_ignora_links_quebrados_antigos(self):
        self.escrever("antigo.md", "[x](nao-existe.md)\n")
        self.git("init", "-q")
        self.git("add", "-A")
        self.git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "x")
        self.escrever("novo.md", "[y](antigo.md)\n")
        resultado = rodar("verificar-links.sh", str(self.pasta), "--alterados")
        self.assertEqual(resultado.returncode, 0, resultado.stdout)
        self.assertIn("links verificados: 1", resultado.stdout)
        self.assertEqual(rodar("verificar-links.sh", str(self.pasta)).returncode, 1)

    def test_arquivo_fora_de_utf8_nao_aborta(self):
        (self.pasta / "a.md").write_bytes("# Ação\n[x](b.md)\n".encode("latin-1"))
        self.escrever("b.md", "# b\n")
        resultado = rodar("verificar-links.sh", str(self.pasta))
        self.assertEqual(resultado.returncode, 0, resultado.stdout + resultado.stderr)


class DetectarPerfilESegredos(PastaTemporaria):
    def test_telas_no_servidor_sao_fullstack_servidor(self):
        self.escrever("composer.json", '{"require": {"laravel/framework": "1"}}')
        self.escrever("resources/views/a.blade.php", "x")
        self.escrever("app/A.php", "<?php")
        saida = campos(rodar("detectar-projeto.sh", str(self.pasta)).stdout)
        self.assertEqual(saida["perfil_sugerido"], "fullstack (frontend: servidor)")

    def test_so_frontend(self):
        self.escrever("package.json", '{"dependencies": {"react": "1"}}')
        self.escrever("src/App.tsx", "x")
        saida = campos(rodar("detectar-projeto.sh", str(self.pasta)).stdout)
        self.assertEqual(saida["perfil_sugerido"], "frontend (frontend: spa)")

    def test_segredo_versionado_e_cli(self):
        self.escrever("config/app.php", "<?php $x = ['password' => 'senhaMuitoSecreta123'];")
        self.escrever("app/Console/Commands/Limpar.php", "<?php")
        resultado = rodar("detectar-projeto.sh", str(self.pasta))
        saida = campos(resultado.stdout)
        self.assertTrue(saida["possiveis_segredos_versionados"].startswith("1 arquivos"))
        self.assertIn("config/app.php:1", saida["possiveis_segredos_versionados"])
        self.assertNotIn("senhaMuitoSecreta123", resultado.stdout)
        self.assertIn("cli", saida["modulos_sugeridos"])
        self.assertIn("nunca copie o valor", resultado.stdout)


class VerificarCitacoes(PastaTemporaria):
    def test_mostrar_imprime_a_linha_citada(self):
        self.escrever("src/app.js", "primeira\nsegunda\n")
        self.escrever("AGENTS.md", "ver `src/app.js:2`\n")
        resultado = rodar("verificar-citacoes.sh", str(self.pasta), "--mostrar")
        self.assertIn("src/app.js:2 => segunda", resultado.stdout)

    def test_caminho_relativo_a_subpasta_e_pacote_nao_geram_aviso(self):
        self.escrever("frontend/src/components/Botao.vue", "x")
        self.escrever("package.json", '{"dependencies": {"@vue/runtime-core": "1"}}')
        self.escrever("AGENTS.md", "`src/components/Botao.vue` e `@vue/runtime-core` e `components/`\n")
        resultado = rodar("verificar-citacoes.sh", str(self.pasta))
        self.assertIn("caminhos inexistentes (aviso): 0", resultado.stdout)

    def test_citacao_valida_passa(self):
        self.escrever("src/app.js", "a\nb\nc\n")
        self.escrever("AGENTS.md", "ver `src/app.js:2` e `src/app.js:1-3`\n")
        resultado = rodar("verificar-citacoes.sh", str(self.pasta))
        self.assertEqual(resultado.returncode, 0, resultado.stdout)
        self.assertIn("citacoes arquivo:linha: 2, erros: 0", resultado.stdout)

    def test_linha_fora_e_arquivo_inexistente_reprovam(self):
        self.escrever("src/app.js", "a\n")
        self.escrever("AGENTS.md", "`src/app.js:9` e `src/sumiu.js:1`\n")
        resultado = rodar("verificar-citacoes.sh", str(self.pasta))
        self.assertEqual(resultado.returncode, 1)
        self.assertIn("linha fora do arquivo", resultado.stdout)
        self.assertIn("arquivo citado não existe", resultado.stdout)

    def test_exemplo_do_kit_que_sobrou_reprova_so_se_nao_existe_no_codigo(self):
        self.escrever("AGENTS.md", "imite o handler de Pedido\n")
        self.assertEqual(rodar("verificar-citacoes.sh", str(self.pasta)).returncode, 1)
        self.escrever("src/Pedido.php", "class Pedido {}")
        self.assertEqual(rodar("verificar-citacoes.sh", str(self.pasta)).returncode, 0)

    def test_caminho_inexistente_e_aviso(self):
        self.escrever("AGENTS.md", "pasta `src/nao/existe` e `src/**/*.ts`\n")
        resultado = rodar("verificar-citacoes.sh", str(self.pasta))
        self.assertEqual(resultado.returncode, 0)
        self.assertIn("caminhos inexistentes (aviso): 1", resultado.stdout)


if __name__ == "__main__":
    unittest.main()
