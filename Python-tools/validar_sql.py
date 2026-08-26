"""
validar_sql.py
------------------------------------------------------------
Roda o .sql exportado do app contra um banco SQLite local,
só pra pegar erro ANTES de colar no Supabase.

Uso:
    python validar_sql.py caminho/do/arquivo.sql

Não precisa instalar nada — sqlite3 já vem com o Python.
------------------------------------------------------------
"""
import sqlite3
import sys
import re
from pathlib import Path


def validar(caminho_sql: str) -> bool:
    caminho = Path(caminho_sql)
    if not caminho.exists():
        print(f"❌ Arquivo não encontrado: {caminho}")
        return False

    sql_texto = caminho.read_text(encoding="utf-8")

    conn = sqlite3.connect(":memory:")
    cur = conn.cursor()

    try:
        cur.executescript(sql_texto)
    except sqlite3.Error as erro:
        print(f"❌ Erro ao rodar o SQL: {erro}\n")
        _apontar_trecho_com_erro(sql_texto, str(erro))
        conn.close()
        return False

    print(f"✅ SQL rodou sem erros: {caminho.name}\n")

    cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tabelas = [linha[0] for linha in cur.fetchall()]

    print("Resumo:")
    for tabela in tabelas:
        cur.execute(f"SELECT COUNT(*) FROM {tabela}")
        total = cur.fetchone()[0]
        print(f"  - {tabela}: {total} linha(s)")

    conn.close()
    return True


def _apontar_trecho_com_erro(sql_texto: str, mensagem_erro: str):
    """Acha e mostra a linha do INSERT/CREATE que provavelmente causou o erro,
    lendo o nome da tabela/coluna citado na própria mensagem do sqlite3."""
    m = re.search(r"(?:table|column)s?:?\s+([\w\.]+)", mensagem_erro, re.IGNORECASE)
    if not m:
        return
    termo = m.group(1).split(".")[-1]
    linhas = sql_texto.splitlines()
    achou = False
    for i, linha in enumerate(linhas, start=1):
        if termo.lower() in linha.lower() and ("insert" in linha.lower() or "create" in linha.lower()):
            print(f"   possível linha do problema ({i}): {linha.strip()[:120]}")
            achou = True
    if not achou:
        print("   (não consegui apontar a linha exata — revise manualmente perto de:", termo, ")")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python validar_sql.py caminho/do/arquivo.sql")
        sys.exit(1)

    ok = validar(sys.argv[1])
    sys.exit(0 if ok else 1)