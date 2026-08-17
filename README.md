# 🧭 Sala de Análises

> Metodologias de melhoria contínua reunidas num só lugar — do primeiro sintoma até o plano de ação.

Este projeto nasceu de uma ideia simples: toda empresa conhece PDCA, Ishikawa, 5W2H... mas raramente essas ferramentas *conversam entre si*. Cada uma vive numa planilha separada, num quadro branco, num slide perdido. A Sala de Análises existe pra resolver isso — é um espaço único onde você identifica um problema, investiga a causa raiz, prioriza o que ataca primeiro e sai com um plano de ação real, sem trocar de ferramenta no meio do caminho.

Feito pra rodar direto no navegador, sem instalação, sem curva de aprendizado — e sem mandar seus dados de análise pra lugar nenhum que você não controle.

---

## 🧩 O que tem dentro

| Metodologia | Pra que serve | Se conecta com |
|---|---|---|
| **PDCA** | Ciclo de melhoria contínua (Planejar → Fazer → Verificar → Agir), pra testar e consolidar uma solução | Ponto de partida do fluxo |
| **Pareto** | Regra 80/20 — descobre quais problemas concentram a maior parte do impacto, pra saber o que atacar primeiro | Envia o problema prioritário pro Ishikawa |
| **Ishikawa** | Diagrama espinha de peixe — mapeia todas as causas possíveis de um problema, organizadas por categoria (os 6M) | Alimenta o 5 Porquês e o 5W2H |
| **5 Porquês** | Aprofunda uma causa específica até achar a causa raiz de verdade | Alimenta o 5W2H |
| **5W2H + GUT** | Transforma uma causa em plano de ação (o quê, onde, quando, por quê, quem, como, quanto custa) e prioriza por Gravidade × Urgência × Tendência | Recebe do Ishikawa/5 Porquês |
| **DMAIC** | Framework do Lean Six Sigma pra projetos maiores, baseado em dados (Definir, Medir, Analisar, Melhorar, Controlar) | Importa de Ishikawa e 5W2H |
| **A-M-P-R-E-C** | Metodologia própria do projeto: Analisar o cenário, Medir com números, Procurar a causa, Resolver, Estabilizar e Compartilhar o aprendizado | Importa de Ishikawa, 5 Porquês e 5W2H |

Nenhuma dessas ferramentas é uma ilha. Uma causa marcada como solução no Ishikawa pode virar uma linha no 5W2H com um clique. Uma causa raiz confirmada no 5 Porquês pode virar uma etapa do DMAIC. A ideia é que o trabalho analítico flua de uma tela pra outra, do jeito que você faria numa investigação real.

---

## 🖥️ Como usar

Não tem instalação. Não tem build. É um site.

1. Abra o link do site (ou o `index.html` localmente).
2. Na primeira vez, escolha **entrar com conta**, **criar conta** ou **continuar como visitante** — sem conta, você usa tudo normalmente, só que nada fica salvo entre sessões.
3. Diga seu nome e (se quiser) dê um título pra sua análise.
4. Escolha a metodologia no menu lateral (☰ recolhe/expande) e comece a preencher.
5. Quando terminar, use os botões de exportação — **SQL**, **Excel** ou **PDF** (esse último já sai com uma capa automática, tipo um relatório de verdade, com o título da sua análise).

---

## 🏗️ Como foi construído (arquitetura)

Tudo aqui é **HTML, CSS e JavaScript puros** — sem framework, sem processo de build, sem dependência de servidor pra funcionar. Um único `index.html` carrega o app inteiro.

### Onde os dados ficam

Esse é o ponto que mais vale explicar, porque é uma decisão consciente de design:

- **Os dados das suas análises** (causas, ações, cartões de PDCA, tudo) ficam **só no seu navegador** (`localStorage`) — nunca sobem pra nenhum servidor. Isso significa: zero custo de armazenamento em nuvem, e você é o único dono dos seus dados enquanto trabalha.
- **O login/cadastro de conta** usa [Supabase Auth](https://supabase.com) — mas *só* pra autenticação. Nenhuma tabela de banco guarda o conteúdo das suas análises.
- **O "salvamento de verdade"**, o que sobrevive à troca de computador ou pode ser compartilhado com alguém, são os botões de **exportação** (.sql / .xlsx / .pdf) dentro do app.

Essa ponte entre o app e o backend vive isolada em `js/storage-adapter.js` — o resto do código nem sabe que esse arquivo existe, só chama `window.storage.get/set/delete/list(...)`.

### Estrutura de arquivos

---

## 🔐 Contas e visitantes

- **Visitante**: usa todas as ferramentas, nada é salvo além da sessão do navegador.
- **Conta**: precisa de um projeto Supabase configurado (`config.js` preenchido com `SUPABASE_URL` e `SUPABASE_ANON_KEY`). Sem isso, o app cai automaticamente em modo visitante — nunca trava esperando um backend que não existe.

---

## 🚀 Publicando como site

Como é só HTML/CSS/JS, qualquer hospedagem de site estático serve. Hoje em dia, as opções mais indicadas e gratuitas:

- **Cloudflare Pages** — conecta direto no GitHub, HTTPS automático, banda ilimitada de graça.
- **GitHub Pages** — o mais simples se você já vive no GitHub.

Basta subir este repositório e apontar a hospedagem pra ele. Sem passo de build.

---

## 🗺️ O que vem por aí

O menu lateral já reserva espaço pra novas metodologias — o projeto foi pensado pra crescer sem precisar refazer o que já existe. Ideias em radar: mais pontes de importação entre ferramentas, relatórios comparativos entre análises, e (quem sabe) um agente de IA que ajuda a interpretar os dados direto na tela.

---

## 🙏 Um obrigado

Esse projeto foi crescendo aos poucos, conversa por conversa, ideia por ideia — cada metodologia, cada ajuste de design, cada correção de bug foi pensado com calma pra ficar num jeito que faça sentido usar de verdade, não só bonito de olhar. Se você chegou até aqui lendo o README, provavelmente é porque também acredita que boas ferramentas de análise deveriam ser simples de usar. Espero que essa sala ajude a resolver problemas de verdade.

---

**Criado por Anderson Timoteo.**
