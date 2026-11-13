"""Valida as skills de skills/<skill>/ contra a especificação Agent Skills.

Confere o frontmatter do SKILL.md (https://agentskills.io/specification):
- name: 1 a 64 caracteres, a-z, 0-9 e hífen, sem hífen no início, no fim ou duplo,
  igual ao nome da pasta;
- description: 1 a 1024 caracteres;
- compatibility: até 500 caracteres, se existir;
- metadata: mapa de texto para texto, se existir;
e o corpo do SKILL.md com até 500 linhas.

Uso: python3 -I scripts/validar-skills.py [raiz]   (padrão: pasta skills/ do repositório)
Sai com código 1 se alguma skill for inválida.
"""
import pathlib
import re
import sys

NOME = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
CAMPOS = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}


def ler_frontmatter(texto: str):
    """Lê o frontmatter YAML simples usado em SKILL.md (chaves de topo e um nível em metadata)."""
    if not texto.startswith("---\n"):
        return None, texto
    fim = texto.find("\n---\n", 4)
    if fim == -1:
        return None, texto
    campos, atual = {}, None
    for linha in texto[4:fim].splitlines():
        if not linha.strip():
            continue
        if linha.startswith("  ") and atual == "metadata":
            chave, _, valor = linha.strip().partition(":")
            campos["metadata"][chave.strip()] = valor.strip().strip('"')
            continue
        chave, _, valor = linha.partition(":")
        atual = chave.strip()
        valor = valor.strip()
        campos[atual] = {} if atual == "metadata" and not valor else desaspar(valor)
    return campos, texto[fim + 5 :]


def desaspar(valor: str) -> str:
    """Tira as aspas de um escalar YAML: 'a''b' vira a'b; "a" vira a."""
    if len(valor) >= 2 and valor[0] == valor[-1] == "'":
        return valor[1:-1].replace("''", "'")
    if len(valor) >= 2 and valor[0] == valor[-1] == '"':
        return valor[1:-1]
    return valor


def problemas_yaml(texto: str) -> list[str]:
    """Valores de topo sem aspas que um parser YAML estrito recusa ou lê errado (GitHub, CLIs)."""
    fim = texto.find("\n---\n", 4)
    problemas = []
    for numero, linha in enumerate(texto[4:fim].splitlines(), start=2):
        if not linha or linha.startswith(" "):
            continue
        chave, _, valor = linha.partition(":")
        valor = valor.strip()
        if not valor or valor[0] in "'\"":
            continue
        if ": " in valor or " #" in valor or valor[0] in "[]{}&*!|>%@`,?-":
            problemas.append(f"linha {numero}, campo '{chave.strip()}'")
    return problemas


def validar(skill: pathlib.Path) -> list[str]:
    arquivo = skill / "SKILL.md"
    if not arquivo.is_file():
        return [f"{skill}: falta SKILL.md. Faça isto: crie o arquivo com frontmatter name e description."]
    campos, corpo = ler_frontmatter(arquivo.read_text(encoding="utf-8"))
    if campos is None:
        return [f"{arquivo}: sem frontmatter. Faça isto: comece o arquivo com um bloco --- name/description ---."]
    erros = []
    for problema in problemas_yaml(arquivo.read_text(encoding="utf-8")):
        erros.append(
            f"{arquivo}: {problema}: valor sem aspas com ': ', ' #' ou caractere especial no início quebra o YAML. "
            "Faça isto: ponha o valor entre aspas simples (aspa simples interna vira '')."
        )
    nome = campos.get("name", "")
    if not (1 <= len(nome) <= 64 and NOME.match(nome)):
        erros.append(f"{arquivo}: name '{nome}' inválido. Faça isto: use 1 a 64 caracteres a-z, 0-9 e hífen simples.")
    if nome != skill.name:
        erros.append(f"{arquivo}: name '{nome}' difere da pasta '{skill.name}'. Faça isto: renomeie um dos dois.")
    descricao = campos.get("description", "")
    if not 1 <= len(descricao) <= 1024:
        erros.append(f"{arquivo}: description com {len(descricao)} caracteres. Faça isto: escreva entre 1 e 1024.")
    if "compatibility" in campos and not 1 <= len(campos["compatibility"]) <= 500:
        erros.append(f"{arquivo}: compatibility com {len(campos['compatibility'])} caracteres. Faça isto: até 500.")
    if "metadata" in campos and not isinstance(campos["metadata"], dict):
        erros.append(f"{arquivo}: metadata não é um mapa. Faça isto: use pares chave: valor indentados.")
    for extra in sorted(set(campos) - CAMPOS):
        erros.append(f"{arquivo}: campo '{extra}' fora da especificação. Faça isto: mova para metadata.")
    linhas = corpo.count("\n")
    if linhas > 500:
        erros.append(f"{arquivo}: corpo com {linhas} linhas. Faça isto: mova o detalhe para references/ (limite 500).")
    return erros


def main():
    raiz = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path(__file__).resolve().parent.parent / "skills"
    skills = sorted(p.parent for p in raiz.glob("*/SKILL.md"))
    if not skills:
        sys.exit(f"nenhuma skill encontrada em {raiz}/<skill>/SKILL.md")
    erros = [e for s in skills for e in validar(s)]
    for e in erros:
        print(e)
    print(f"skills validadas: {len(skills)}, erros: {len(erros)}")
    sys.exit(1 if erros else 0)


if __name__ == "__main__":
    main()
