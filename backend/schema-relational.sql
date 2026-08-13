-- ============================================================
-- Sala de Análises — schema relacional (evolução futura)
-- ============================================================
-- NÃO precisa rodar isso agora. É o mesmo formato que o botão
-- "Arquivar Análise" já exporta em .sql dentro do app — uma
-- tabela por metodologia, com relações de verdade (JOIN, filtros,
-- relatórios). Fica aqui documentado como o próximo passo natural
-- quando o modelo chave-valor (schema.sql) não for mais suficiente.
--
-- Migração sugerida, quando chegar a hora:
--   1. Rode este schema no Supabase.
--   2. Escreva uma função que lê o JSON de cada chave do kv_store
--      e faz o INSERT nas tabelas abaixo (é basicamente o que o
--      buildSqlExport() do app já faz em JavaScript — dá pra portar
--      direto a mesma lógica).
-- ============================================================

create table if not exists analises (
  id            text primary key,
  user_id       uuid not null references auth.users(id) on delete cascade,
  nome          text not null,
  criado_em     timestamptz default now(),
  arquivado_em  timestamptz
);

create table if not exists ishikawa_problemas (
  analise_id  text primary key references analises(id) on delete cascade,
  problema    text
);

create table if not exists ishikawa_categorias (
  id          text primary key,
  analise_id  text not null references analises(id) on delete cascade,
  nome        text not null,
  ordem       integer
);

create table if not exists ishikawa_causas (
  id            text primary key,
  categoria_id  text not null references ishikawa_categorias(id) on delete cascade,
  analise_id    text not null references analises(id) on delete cascade,
  texto         text not null
);

create table if not exists ishikawa_subcausas (
  id           text primary key,
  causa_id     text not null references ishikawa_causas(id) on delete cascade,
  analise_id   text not null references analises(id) on delete cascade,
  texto        text not null,
  eh_solucao   boolean default false
);

create table if not exists cinco_porques (
  id                       text primary key,
  analise_id               text not null references analises(id) on delete cascade,
  problema_investigado     text,
  por_que_1 text, por_que_2 text, por_que_3 text, por_que_4 text, por_que_5 text,
  causa_raiz_confirmada    boolean default false
);

create table if not exists acoes_5w2h (
  id             text primary key,
  analise_id     text not null references analises(id) on delete cascade,
  o_que          text,
  onde           text,
  quando         text,
  por_que        text,
  quem           text,
  como           text,
  quanto_custa   text,
  gravidade      integer,
  urgencia       integer,
  tendencia      integer,
  score_gut      integer,
  concluida      boolean default false
);

create table if not exists pdca_itens (
  id          text primary key,
  analise_id  text not null references analises(id) on delete cascade,
  texto       text,
  etapa       text
);

create table if not exists dmaic_itens (
  id          text primary key,
  analise_id  text not null references analises(id) on delete cascade,
  texto       text,
  etapa       text
);

create table if not exists pareto_itens (
  id                     text primary key,
  analise_id             text not null references analises(id) on delete cascade,
  problema               text not null,
  valor                  numeric,
  ordem                  integer,
  percentual_acumulado   numeric,
  poucos_vitais          boolean default false
);

-- RLS: repita o padrão abaixo pra cada tabela (exemplo com "analises").
alter table analises enable row level security;
create policy "analises_own" on analises for all
  using (auth.uid() = user_id) with check (auth.uid() = user_id);
-- As tabelas filhas (causas, ações etc.) podem checar posse via
-- JOIN com "analises" numa policy, ou simplesmente confiar no
-- "on delete cascade" + nunca expor essas tabelas sem passar pela
-- análise dona. Ajuste conforme a necessidade quando for usar.
