-- ============================================================
-- Sala de Análises — schema principal (Supabase / Postgres)
-- ============================================================
-- Rode isso no painel do Supabase: SQL Editor → New query → Run.
--
-- Essa é a versão "chave-valor": uma tabela só, onde cada linha é
-- um pedacinho de dado do app (uma análise, um diagrama, um plano
-- 5W2H etc.), igual ao jeito que o app já salva as coisas hoje.
-- É a opção mais rápida pra sair do zero SEM precisar mexer no
-- index.html. Quando quiser uma estrutura relacional "de verdade"
-- (uma tabela por metodologia, JOINs, relatórios em SQL), veja
-- backend/schema-relational.sql — é o próximo passo natural.
-- ============================================================

create extension if not exists "pgcrypto";

create table if not exists kv_store (
  id          uuid primary key default gen_random_uuid(),
  user_id     uuid not null references auth.users(id) on delete cascade,
  key         text not null,
  shared      boolean not null default false,
  value       text,
  updated_at  timestamptz not null default now(),
  unique (user_id, key, shared)
);

create index if not exists kv_store_user_id_idx on kv_store (user_id);
create index if not exists kv_store_key_idx on kv_store (user_id, key);

-- Row Level Security: cada usuário só enxerga e mexe nos próprios dados.
alter table kv_store enable row level security;

drop policy if exists "kv_store_select_own" on kv_store;
create policy "kv_store_select_own"
  on kv_store for select
  using (auth.uid() = user_id);

drop policy if exists "kv_store_insert_own" on kv_store;
create policy "kv_store_insert_own"
  on kv_store for insert
  with check (auth.uid() = user_id);

drop policy if exists "kv_store_update_own" on kv_store;
create policy "kv_store_update_own"
  on kv_store for update
  using (auth.uid() = user_id)
  with check (auth.uid() = user_id);

drop policy if exists "kv_store_delete_own" on kv_store;
create policy "kv_store_delete_own"
  on kv_store for delete
  using (auth.uid() = user_id);

-- Mantém updated_at sempre atual em cada alteração.
create or replace function kv_store_set_updated_at()
returns trigger as $$
begin
  new.updated_at = now();
  return new;
end;
$$ language plpgsql;

drop trigger if exists kv_store_touch on kv_store;
create trigger kv_store_touch
  before update on kv_store
  for each row execute function kv_store_set_updated_at();
