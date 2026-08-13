# Backend — como ligar contas de verdade (Supabase)

Por que Supabase: é gratuito pra começar, já vem com autenticação
pronta (login/cadastro), o banco é **Postgres de verdade** (o mesmo
formato do `.sql` que o app já exporta), e se um dia você quiser sair
de lá, dá pra migrar — não é uma prisão de fornecedor.

Plano grátis atual: banco de até 500 MB, autenticação inclusa, e o
projeto só "pausa" (não apaga nada) depois de longos períodos sem uso —
volta a funcionar sozinho na primeira visita.

## Passo 1 — Criar o projeto

1. Crie uma conta grátis em **https://supabase.com**.
2. "New Project" → escolha um nome (ex.: `sala-de-analises`) e uma senha
   de banco (guarde essa senha, mas você não vai precisar dela no dia a
   dia — o app usa a chave de API, não essa senha).
3. Espere o projeto terminar de provisionar (1–2 minutos).

## Passo 2 — Rodar o schema

1. No painel do projeto, abra **SQL Editor** (menu lateral) → **New query**.
2. Cole todo o conteúdo de [`backend/schema.sql`](../backend/schema.sql) aqui.
3. Clique em **Run**.
4. Confirme em **Table Editor** que a tabela `kv_store` foi criada.

Isso já é suficiente pra tudo funcionar — é a tabela chave-valor que
guarda os dados de cada usuário, do jeito que o app já usa desde o
início.

## Passo 3 — Pegar as chaves da API

1. **Project Settings** (ícone de engrenagem) → **API**.
2. Copie:
   - **Project URL**
   - **anon / public key**

## Passo 4 — Preencher o `config.js`

Abra `config.js` na raiz do projeto e preencha:

```js
window.SUPABASE_URL = 'https://SEU-PROJETO.supabase.co';
window.SUPABASE_ANON_KEY = 'sua-anon-key-aqui';
```

Salve, abra o `index.html` de novo — agora a tela de **Entrar / Criar
conta / Continuar como visitante** deve aparecer.

> **Sobre segurança**: a `anon key` é feita pra ficar exposta no
> navegador (não é senha, não é segredo) — a proteção de verdade vem
> das políticas de **Row Level Security (RLS)** que já estão dentro do
> `schema.sql` (cada usuário só enxerga os próprios dados). Por isso é
> seguro commitar o `config.js` preenchido no seu repositório.

## Passo 5 (opcional) — Confirmação de e-mail

Por padrão, o Supabase pede confirmação de e-mail antes do primeiro
login. Pra testar mais rápido enquanto desenvolve, você pode desativar
isso temporariamente em **Authentication → Providers → Email → Confirm
email** (desligue), ou simplesmente confirmar o e-mail de teste normal
mesmo (chega um link na caixa de entrada).

## Evoluindo o banco (quando quiser)

O `schema.sql` (chave-valor) é ótimo pra começar rápido, mas todo dado
fica guardado como texto/JSON dentro de uma coluna. Quando você quiser
fazer relatórios em SQL de verdade (ex.: "quantas causas raiz foram
confirmadas por setor este mês"), o próximo passo é migrar pro
[`backend/schema-relational.sql`](../backend/schema-relational.sql) —
uma tabela por metodologia, já no mesmo formato que o botão "Arquivar
Análise" do app exporta hoje. Isso pode ser feito bem depois, sem
pressa, e sem quebrar nada do que já está funcionando.

## Dúvidas comuns

**"Mudei o config.js mas continua em modo visitante"**
Confirme que salvou o arquivo e recarregou a página (Ctrl+Shift+R pra
forçar, ignorando cache).

**"Deu erro ao criar conta"**
Abra o Console do navegador (F12) — a mensagem de erro do Supabase
aparece lá com mais detalhes (ex.: senha curta demais, e-mail inválido).

**"Quero trocar pra outro provedor de auth (Google, etc.)"**
O Supabase suporta login social nativamente (Authentication →
Providers). Isso exigiria um pequeno ajuste em `js/storage-adapter.js`
pra adicionar os novos botões — avise quando quiser fazer isso.
