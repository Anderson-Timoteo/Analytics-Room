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
|  **FCA** | Forma mais simplificada de utilizar as metodologias mais a fundo, sendo significado de Fato, Causa, Ação.
|  **VOC** | Voz do cliente, onde tudo começa.

Nenhuma dessas ferramentas é uma ilha. Uma causa marcada como solução no Ishikawa pode virar uma linha no 5W2H com um clique. Uma causa raiz confirmada no 5 Porquês pode virar uma etapa do DMAIC. A ideia é que o trabalho analítico flua de uma tela pra outra, do jeito que você faria numa investigação real.

---

## 🖥️ Como usar

Não tem instalação. Não tem build. É um site.

1. Abra o link do site.
2. Na primeira vez, escolha **entrar com conta**, **criar conta** ou **continuar como visitante** — sem conta, você usa tudo normalmente, só que nada fica salvo entre sessões.
3. Diga seu nome e (se quiser) dê um título pra sua análise.
4. Escolha a metodologia no menu lateral (☰ recolhe/expande) e comece a preencher.
5. Quando terminar, use os botões de exportação — **SQL**,**PDF** (esse último já sai com uma capa automática, tipo um relatório de verdade, com o título da sua análise).

---

## 🏗️ Como foi construído (arquitetura)

Tudo aqui é **HTML, CSS e JavaScript puros** — sem framework, sem processo de build, sem dependência de servidor pra funcionar. Um único `index.html` carrega o app inteiro.


