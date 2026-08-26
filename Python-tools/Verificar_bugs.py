"""
verificar_bugs.py
------------------------------------------------------------
Confere o index.html em busca dos erros mais comuns de
copiar-e-colar: ids duplicados, botões sem elemento
correspondente, chaves/parênteses desbalanceados no <script>,
e tags HTML não fechadas.

100% local — só lê o arquivo, não acessa rede nem API nenhuma.

Uso:
    python verificar_bugs.py caminho/do/index.html
------------------------------------------------------------
"""
import re
import sys
from pathlib import Path
from html.parser import HTMLParser

TAGS_AUTOFECHADAS = {
    "area", "base", "br", "col", "embed", "hr", "img", "input",
    "link", "meta", "param", "source", "track", "wbr"
}


class VerificadorTags(HTMLParser):
    def __init__(self):
        super().__init__()
        self.pilha = []
        self.erros = []

    def handle_starttag(self, tag, attrs):
        if tag not in TAGS_AUTOFECHADAS:
            self.pilha.append((tag, self.getpos()))

    def handle_startendtag(self, tag, attrs):
        pass

    def handle_endtag(self, tag):
        if not self.pilha:
            self.erros.append(f"linha {self.getpos()[0]}: fechando </{tag}> sem abertura correspondente")
            return
        aberto_tag, aberto_pos = self.pilha[-1]
        if aberto_tag == tag:
            self.pilha.pop()
        else:
            achou = False
            for i in range(len(self.pilha) - 1, -1, -1):
                if self.pilha[i][0] == tag:
                    esquecidas = self.pilha[i + 1:]
                    for esq_tag, esq_pos in esquecidas:
                        self.erros.append(f"linha {esq_pos[0]}: <{esq_tag}> parece não ter sido fechada")
                    self.pilha = self.pilha[:i]
                    achou = True
                    break
            if not achou:
                self.erros.append(f"linha {self.getpos()[0]}: </{tag}> não bate com nada aberto")


def checar_ids_duplicados(html: str) -> list:
    ids = re.findall(r'id=["\']([^"\']+)["\']', html)
    vistos = {}
    duplicados = []
    for i in ids:
        vistos[i] = vistos.get(i, 0) + 1
    for id_, qtd in vistos.items():
        if qtd > 1:
            duplicados.append(f'id="{id_}" aparece {qtd} vezes (deveria ser único)')
    return duplicados


def checar_getelementbyid_orfaos(html: str) -> list:
    ids_existentes = set(re.findall(r'id=["\']([^"\']+)["\']', html))
    chamadas = re.findall(r"getElementById\(\s*['\"]([^'\"]+)['\"]\s*\)", html)
    orfaos = []
    vistos = set()
    for id_ in chamadas:
        if id_ not in ids_existentes and id_ not in vistos:
            orfaos.append(f"getElementById('{id_}') — não existe nenhum elemento com esse id no HTML")
            vistos.add(id_)
    return orfaos


def checar_balanceamento_js(html: str) -> list:
    blocos = re.findall(r"<script(?:\s[^>]*)?>(.*?)</script>", html, re.DOTALL)
    problemas = []
    pares = {'{': '}', '(': ')', '[': ']'}
    fechamentos = {v: k for k, v in pares.items()}

    for idx, bloco in enumerate(blocos, start=1):
        limpo = re.sub(r"//[^\n]*", "", bloco)
        limpo = re.sub(r"/\*.*?\*/", "", limpo, flags=re.DOTALL)
        limpo = re.sub(r"`(?:[^`\\]|\\.)*`", "``", limpo)
        limpo = re.sub(r'"(?:[^"\\]|\\.)*"', '""', limpo)
        limpo = re.sub(r"'(?:[^'\\]|\\.)*'", "''", limpo)

        pilha = []
        for pos, ch in enumerate(limpo):
            if ch in pares:
                pilha.append(ch)
            elif ch in fechamentos:
                if not pilha or pilha[-1] != fechamentos[ch]:
                    linha = limpo[:pos].count("\n") + 1
                    problemas.append(
                        f'bloco <script> #{idx}, por volta da linha {linha}: "{ch}" sem abertura correspondente'
                    )
                    break
                pilha.pop()
        else:
            if pilha:
                problemas.append(
                    f'bloco <script> #{idx}: sobrou {len(pilha)} abertura(s) sem fechar ({", ".join(pilha)})'
                )
    return problemas


def rodar(caminho_html: str):
    caminho = Path(caminho_html)
    if not caminho.exists():
        print(f"❌ Arquivo não encontrado: {caminho}")
        sys.exit(1)

    html = caminho.read_text(encoding="utf-8")
    total_problemas = 0

    print("== IDs duplicados ==")
    duplicados = checar_ids_duplicados(html)
    if duplicados:
        for d in duplicados:
            print(f"  ⚠️  {d}")
        total_problemas += len(duplicados)
    else:
        print("  ✅ nenhum")

    print("\n== getElementById apontando pra id inexistente ==")
    orfaos = checar_getelementbyid_orfaos(html)
    if orfaos:
        for o in orfaos:
            print(f"  ⚠️  {o}")
        total_problemas += len(orfaos)
    else:
        print("  ✅ nenhum")

    print("\n== Chaves/parênteses/colchetes desbalanceados no JS ==")
    desbalanceado = checar_balanceamento_js(html)
    if desbalanceado:
        for d in desbalanceado:
            print(f"  ⚠️  {d}")
        total_problemas += len(desbalanceado)
    else:
        print("  ✅ nenhum")

    print("\n== Tags HTML não fechadas ==")
    verificador = VerificadorTags()
    verificador.feed(html)
    if verificador.erros:
        for e in verificador.erros:
            print(f"  ⚠️  {e}")
        total_problemas += len(verificador.erros)
    else:
        print("  ✅ nenhuma")

    print(f"\n{'='*50}")
    if total_problemas == 0:
        print("✅ Nenhum problema encontrado.")
    else:
        print(f"⚠️  {total_problemas} ponto(s) pra revisar (veja acima).")
    sys.exit(0 if total_problemas == 0 else 1)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python verificar_bugs.py caminho/do/index.html")
        sys.exit(1)
    rodar(sys.argv[1])