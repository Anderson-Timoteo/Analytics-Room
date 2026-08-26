"""
verificar_seguranca.py
------------------------------------------------------------
Confere pontos de segurança do projeto (index.html + config.js)
de forma ESTÁTICA — só lê os arquivos no seu computador.
Não acessa o Supabase, não faz nenhuma chamada de rede.

Uso:
    python verificar_seguranca.py caminho/do/projeto
------------------------------------------------------------
"""
import base64
import json
import re
import sys
from pathlib import Path


def alerta(lista, texto):
    lista.append(texto)


def checar_innerhtml_perigoso(html: str, achados: list):
    for m in re.finditer(r"\.innerHTML\s*=\s*([^;]+);", html):
        expressao = m.group(1).strip()
        eh_vazio_ou_fixo = expressao in ("''", '""') or re.fullmatch(r"['\"][^'\"$+]*['\"]", expressao)
        if not eh_vazio_ou_fixo:
            linha = html[:m.start()].count("\n") + 1
            alerta(achados, f'linha {linha}: innerHTML recebendo conteúdo dinâmico — confirme que não inclui texto digitado por usuário sem tratar: {expressao[:60]}')


def checar_padroes_perigosos(html: str, achados: list):
    perigosos = {
        r"\beval\s*\(": "uso de eval() — evite, permite rodar texto como código",
        r"document\.write\s*\(": "uso de document.write() — pode ser vetor de injeção, prefira createElement/textContent",
    }
    for padrao, msg in perigosos.items():
        for m in re.finditer(padrao, html):
            linha = html[:m.start()].count("\n") + 1
            alerta(achados, f"linha {linha}: {msg}")


def checar_scripts_externos_sem_versao_travada(html: str, achados: list):
    for m in re.finditer(r'<script[^>]+src=["\']([^"\']+)["\']', html):
        src = m.group(1)
        if not src.startswith("http"):
            continue
        tem_versao_exata = re.search(r"@\d+\.\d+\.\d+", src)
        if not tem_versao_exata:
            alerta(achados, f'CDN sem versão travada (ex.: "@2" em vez de "@2.45.1"): {src} — risco: pode mudar de código sem avisar')


def checar_chaves_no_html_direto(html: str, achados: list):
    if re.search(r"SUPABASE_URL\s*=\s*['\"]https", html):
        alerta(achados, "SUPABASE_URL parece estar escrita direto no index.html — deveria vir só do config.js")
    if re.search(r"SUPABASE_ANON_KEY\s*=\s*['\"]ey", html):
        alerta(achados, "SUPABASE_ANON_KEY parece estar escrita direto no index.html — deveria vir só do config.js")


def decodificar_payload_jwt(token: str):
    partes = token.split(".")
    if len(partes) != 3:
        return None
    payload = partes[1]
    payload += "=" * (-len(payload) % 4)
    try:
        return json.loads(base64.urlsafe_b64decode(payload))
    except Exception:
        return None


def checar_tipo_da_chave_supabase(config_texto: str, achados: list):
    m = re.search(r"SUPABASE_ANON_KEY\s*=\s*['\"]([^'\"]+)['\"]", config_texto)
    if not m or not m.group(1):
        return
    token = m.group(1)
    payload = decodificar_payload_jwt(token)
    if payload is None:
        alerta(achados, "Não consegui ler a SUPABASE_ANON_KEY do config.js pra conferir o tipo dela (formato inesperado)")
        return
    papel = payload.get("role")
    if papel == "service_role":
        alerta(achados, "🚨 GRAVE: a chave no config.js é a 'service_role' (acesso total ao banco, ignora RLS) — "
                         "isso NUNCA pode ficar exposta no navegador. Troque pela 'anon key' no painel do Supabase.")
    elif papel != "anon":
        alerta(achados, f"A chave no config.js tem role='{papel}', esperava 'anon'. Confirme se é a chave certa.")


def checar_gitignore(pasta: Path, achados: list):
    gi = pasta / ".gitignore"
    if not gi.exists():
        alerta(achados, "Não achei um .gitignore na pasta — ajuda a não versionar lixo (node_modules, .DS_Store etc.)")


def rodar(caminho_pasta: str):
    pasta = Path(caminho_pasta)
    caminho_html = pasta / "index.html"
    caminho_config = pasta / "config.js"

    if not caminho_html.exists():
        print(f"❌ Não achei index.html em: {pasta}")
        sys.exit(1)

    html = caminho_html.read_text(encoding="utf-8")
    achados = []

    checar_innerhtml_perigoso(html, achados)
    checar_padroes_perigosos(html, achados)
    checar_scripts_externos_sem_versao_travada(html, achados)
    checar_chaves_no_html_direto(html, achados)
    checar_gitignore(pasta, achados)

    if caminho_config.exists():
        checar_tipo_da_chave_supabase(caminho_config.read_text(encoding="utf-8"), achados)
    else:
        alerta(achados, "Não achei config.js — ok se for intencional (app roda em modo visitante sem ele)")

    print("=" * 55)
    print("VERIFICAÇÃO DE SEGURANÇA (estática, sem rede)")
    print("=" * 55)
    if not achados:
        print("✅ Nenhum ponto de atenção encontrado.")
    else:
        for i, a in enumerate(achados, start=1):
            print(f"{i}. {a}")
    print()
    print(f"Total: {len(achados)} ponto(s).")
    print("\nLembrete: isso pega só o que dá pra ver no código. Ative 2FA no GitHub")
    print("e no Supabase, e confira Rate Limits + Confirm Email no painel do")
    print("Supabase — isso não tem como checar por aqui, é configuração da conta.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python verificar_seguranca.py caminho/do/projeto")
        sys.exit(1)
    rodar(sys.argv[1])