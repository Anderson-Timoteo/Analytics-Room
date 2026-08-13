# Sala de Análises

Kit de metodologias de melhoria contínua num só lugar: **PDCA · Pareto ·
Ishikawa · 5 Porquês · 5W2H · DMAIC** — tudo interativo, com ponte de
dados entre as ferramentas (ex.: causa marcada no Ishikawa vira ação no
5W2H) e exportação em `.sql` pronta pra qualquer banco.

## Como rodar localmente

Não precisa de build nem de servidor especial — é HTML/CSS/JS puro.

1. Baixe/clone esta pasta inteira.
2. Abra `index.html` num navegador (duplo clique já funciona) **ou**,
   pra evitar bloqueios de CORS em alguns navegadores com o `config.js`,
   rode um servidor local simples:
   ```bash
   npx serve .
   # ou
   python3 -m http.server 8080
   ```
3. Pronto. Sem backend configurado, o app abre direto em **modo
   visitante** — todas as ferramentas funcionam, nada é salvo.

## Estrutura do projeto

```
.
├── index.html                  → o app inteiro (front-end)
├── js/
│   └── storage-adapter.js      → ponte entre o app e o backend (ver abaixo)
├── config.js                   → suas chaves do Supabase (não versionar com chaves reais de produção sensíveis — ver nota em BACKEND.md)
├── config.example.js           → modelo do config.js
├── backend/
│   ├── schema.sql               → schema pra rodar no Supabase (chave-valor, rápido de começar)
│   └── schema-relational.sql    → schema relacional (evolução futura, uma tabela por metodologia)
└── docs/
    ├── BACKEND.md               → como criar e configurar o Supabase
    └── DEPLOY.md                → como colocar isso no ar (GitHub + hospedagem)
```

## Como o backend funciona (resumo)

O `index.html` nunca fala diretamente com o Supabase. Ele só chama
`window.storage.get/set/delete/list(...)` — a mesma interface desde o
início do projeto. Quem decide pra onde esses dados vão é o
`js/storage-adapter.js`:

- **Sem conta / visitante** → fica tudo em memória (perde ao fechar a aba).
- **Com conta** → vai pro Supabase (Postgres), preso ao usuário logado.

Isso significa que **você não precisa mexer no `index.html` pra ligar o
backend** — só preencher o `config.js` e rodar o `backend/schema.sql`
no seu projeto Supabase. Passo a passo completo em
[`docs/BACKEND.md`](docs/BACKEND.md).

## Próximos passos sugeridos

1. Criar o projeto no Supabase e preencher `config.js` → [`docs/BACKEND.md`](docs/BACKEND.md)
2. Subir este repositório pro GitHub
3. Publicar como site (Cloudflare Pages ou GitHub Pages) → [`docs/DEPLOY.md`](docs/DEPLOY.md)

---
Criado por Anderson Timoteo.
