"""
painel_offline.py
------------------------------------------------------------
Junta vários .sql exportados do app (de análises/setores
diferentes) e gera um resumo offline — o "painel geral" que
saiu do front, só que rodando no seu computador.

Uso:
    python painel_offline.py caminho/da/pasta/com/os/sql

Instalar antes (uma vez só):
    pip install pandas
------------------------------------------------------------
"""
import sqlite3
import sys
from pathlib import Path
import pandas as pd


def carregar_sql_em_dataframes(caminho_arquivo: Path) -> dict:
    """Roda um .sql num banco temporário e devolve cada tabela como DataFrame."""
    conn = sqlite3.connect(":memory:")
    sql_texto = caminho_arquivo.read_text(encoding="utf-8")
    conn.executescript(sql_texto)

    tabelas = pd.read_sql_query(
        "SELECT name FROM sqlite_master WHERE type='table'", conn
    )["name"].tolist()

    dados = {}
    for tabela in tabelas:
        df = pd.read_sql_query(f"SELECT * FROM {tabela}", conn)
        df["_arquivo_origem"] = caminho_arquivo.name
        dados[tabela] = df

    conn.close()
    return dados


def juntar_pasta(caminho_pasta: str) -> dict:
    pasta = Path(caminho_pasta)
    arquivos_sql = sorted(pasta.glob("*.sql"))
    if not arquivos_sql:
        print(f"❌ Nenhum arquivo .sql encontrado em: {pasta}")
        sys.exit(1)

    print(f"Encontrados {len(arquivos_sql)} arquivo(s) .sql:")
    for a in arquivos_sql:
        print(f"  - {a.name}")
    print()

    tabelas_juntas = {}
    for arquivo in arquivos_sql:
        dados = carregar_sql_em_dataframes(arquivo)
        for nome_tabela, df in dados.items():
            if nome_tabela not in tabelas_juntas:
                tabelas_juntas[nome_tabela] = []
            tabelas_juntas[nome_tabela].append(df)

    return {nome: pd.concat(lista, ignore_index=True) for nome, lista in tabelas_juntas.items()}


def gerar_relatorio(tabelas: dict):
    analises = tabelas.get("analises", pd.DataFrame())
    causas = tabelas.get("ishikawa_causas", pd.DataFrame())
    acoes = tabelas.get("acoes_5w2h", pd.DataFrame())

    print("=" * 60)
    print("VISÃO GERAL")
    print("=" * 60)
    print(f"Total de análises juntadas: {len(analises)}")
    print(f"Total de causas mapeadas:   {len(causas)}")
    print(f"Total de ações (5W2H):      {len(acoes)}")
    if not acoes.empty and "concluida" in acoes.columns:
        concluidas = acoes["concluida"].astype(str).str.lower().isin(["1", "true"]).sum()
        pct = (concluidas / len(acoes) * 100) if len(acoes) else 0
        print(f"Ações concluídas:           {concluidas} ({pct:.0f}%)")

    if not causas.empty:
        print()
        print("=" * 60)
        print("CAUSAS QUE MAIS SE REPETEM (entre todas as análises juntadas)")
        print("=" * 60)
        repetidas = (
            causas.assign(texto_normalizado=causas["texto"].str.strip().str.lower())
            .groupby("texto_normalizado")
            .agg(
                ocorrencias=("texto_normalizado", "count"),
                exemplo_original=("texto", "first"),
            )
            .sort_values("ocorrencias", ascending=False)
        )
        repetidas = repetidas[repetidas["ocorrencias"] > 1]
        if repetidas.empty:
            print("Nenhuma causa se repete entre as análises juntadas (todas únicas).")
        else:
            for _, linha in repetidas.head(10).iterrows():
                print(f"  {linha['ocorrencias']}x  —  {linha['exemplo_original']}")

    if not acoes.empty and not analises.empty and "score_gut" in acoes.columns:
        print()
        print("=" * 60)
        print("SCORE MÉDIO DE GUT POR ANÁLISE (use o nome como proxy de 'setor')")
        print("=" * 60)
        acoes_com_nome = acoes.merge(
            analises[["id", "nome"]], left_on="analise_id", right_on="id", how="left"
        )
        media_gut = (
            acoes_com_nome.groupby("nome")["score_gut"]
            .mean()
            .round(1)
            .sort_values(ascending=False)
        )
        for nome, media in media_gut.items():
            print(f"  {media:>6}  —  {nome}")

    print()
    print("=" * 60)
    print("O QUE NÃO DÁ PRA CALCULAR AINDA")
    print("=" * 60)
    print("'Tempo médio entre causa raiz encontrada e ação concluída' precisa de")
    print("datas de quando cada causa foi confirmada e quando cada ação foi")
    print("concluída — o export de hoje não guarda esses dois carimbos de tempo.")
    print("Se quiser esse indicador, é um ajuste pequeno no app (adicionar")
    print("'confirmado_em' e 'concluido_em' nas tabelas). Só avisar.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python painel_offline.py caminho/da/pasta/com/os/sql")
        sys.exit(1)

    tabelas = juntar_pasta(sys.argv[1])
    gerar_relatorio(tabelas)