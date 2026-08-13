/**
 * storage-adapter.js
 * ---------------------------------------------------------------
 * Implementa `window.storage` com a MESMA assinatura que o app já
 * usa (get/set/delete/list), então o index.html não precisa de
 * NENHUMA alteração no seu código de persistência.
 *
 * Dois modos:
 *  - Visitante (guest): tudo fica só em memória. Fecha a aba, perde.
 *    Não faz nenhuma chamada de rede.
 *  - Conta (account): dados ficam no Supabase (Postgres), presos ao
 *    usuário logado, sincronizados entre dispositivos.
 *
 * Também expõe `window.authAPI` com os métodos que a tela de
 * login/cadastro usa: signUp, signIn, signOut, continueAsGuest,
 * getSession, onAuthChange.
 *
 * Pré-requisito: o SDK do Supabase (via CDN) e config.js precisam
 * ser carregados ANTES deste arquivo. Veja index.html <head>.
 * ---------------------------------------------------------------
 */
(function () {
  'use strict';

  const hasSupabaseConfig =
    typeof window.SUPABASE_URL === 'string' &&
    window.SUPABASE_URL.length > 0 &&
    typeof window.SUPABASE_ANON_KEY === 'string' &&
    window.SUPABASE_ANON_KEY.length > 0 &&
    typeof window.supabase !== 'undefined';

  const supabaseClient = hasSupabaseConfig
    ? window.supabase.createClient(window.SUPABASE_URL, window.SUPABASE_ANON_KEY)
    : null;

  // Modo atual: começa indefinido até o usuário escolher (login/cadastro/visitante)
  let mode = null; // 'guest' | 'account'
  let currentUserId = null;

  // ---------------- Armazenamento em memória (modo visitante) ----------------
  const memoryStore = new Map(); // chave: `${shared?1:0}:${key}` -> value (string)

  function memKey(key, shared) {
    return `${shared ? 1 : 0}:${key}`;
  }

  const guestStorage = {
    async get(key, shared) {
      const k = memKey(key, shared);
      if (!memoryStore.has(k)) throw new Error('not found');
      return { key, value: memoryStore.get(k), shared: !!shared };
    },
    async set(key, value, shared) {
      memoryStore.set(memKey(key, shared), value);
      return { key, value, shared: !!shared };
    },
    async delete(key, shared) {
      memoryStore.delete(memKey(key, shared));
      return { key, deleted: true, shared: !!shared };
    },
    async list(prefix, shared) {
      const sharedFlag = shared ? 1 : 0;
      const keys = [];
      for (const k of memoryStore.keys()) {
        const [s, ...rest] = k.split(':');
        const realKey = rest.join(':');
        if (Number(s) === sharedFlag && (!prefix || realKey.startsWith(prefix))) {
          keys.push(realKey);
        }
      }
      return { keys, prefix, shared: !!sharedFlag };
    }
  };

  // ---------------- Armazenamento via Supabase (modo conta) ----------------
  // Tabela esperada: kv_store (user_id, key, shared, value) — veja backend/schema.sql
  const accountStorage = {
    async get(key, shared) {
      const sharedFlag = !!shared;
      const { data, error } = await supabaseClient
        .from('kv_store')
        .select('value')
        .eq('user_id', currentUserId)
        .eq('key', key)
        .eq('shared', sharedFlag)
        .maybeSingle();
      if (error) throw error;
      if (!data) throw new Error('not found');
      return { key, value: data.value, shared: sharedFlag };
    },
    async set(key, value, shared) {
      const sharedFlag = !!shared;
      const { error } = await supabaseClient
        .from('kv_store')
        .upsert(
          { user_id: currentUserId, key, shared: sharedFlag, value, updated_at: new Date().toISOString() },
          { onConflict: 'user_id,key,shared' }
        );
      if (error) throw error;
      return { key, value, shared: sharedFlag };
    },
    async delete(key, shared) {
      const sharedFlag = !!shared;
      const { error } = await supabaseClient
        .from('kv_store')
        .delete()
        .eq('user_id', currentUserId)
        .eq('key', key)
        .eq('shared', sharedFlag);
      if (error) throw error;
      return { key, deleted: true, shared: sharedFlag };
    },
    async list(prefix, shared) {
      const sharedFlag = !!shared;
      let query = supabaseClient
        .from('kv_store')
        .select('key')
        .eq('user_id', currentUserId)
        .eq('shared', sharedFlag);
      if (prefix) query = query.like('key', `${prefix}%`);
      const { data, error } = await query;
      if (error) throw error;
      return { keys: (data || []).map(r => r.key), prefix, shared: sharedFlag };
    }
  };

  // `window.storage` sempre delega pro backend ativo no momento da chamada.
  window.storage = {
    get: (key, shared) => (mode === 'account' ? accountStorage : guestStorage).get(key, shared),
    set: (key, value, shared) => (mode === 'account' ? accountStorage : guestStorage).set(key, value, shared),
    delete: (key, shared) => (mode === 'account' ? accountStorage : guestStorage).delete(key, shared),
    list: (prefix, shared) => (mode === 'account' ? accountStorage : guestStorage).list(prefix, shared)
  };

  // ---------------- API de autenticação usada pela tela de login ----------------
  const authListeners = [];

  window.authAPI = {
    isBackendConfigured: hasSupabaseConfig,

    continueAsGuest() {
      mode = 'guest';
      currentUserId = null;
      authListeners.forEach(fn => fn({ mode: 'guest', user: null }));
    },

    async signUp(email, password) {
      if (!hasSupabaseConfig) throw new Error('Backend não configurado. Veja docs/BACKEND.md.');
      const { data, error } = await supabaseClient.auth.signUp({ email, password });
      if (error) throw error;
      // Se a confirmação de e-mail estiver ativada no projeto Supabase,
      // data.session pode vir nulo até o usuário confirmar o e-mail.
      if (data.session) {
        mode = 'account';
        currentUserId = data.user.id;
        authListeners.forEach(fn => fn({ mode: 'account', user: data.user }));
      }
      return data;
    },

    async signIn(email, password) {
      if (!hasSupabaseConfig) throw new Error('Backend não configurado. Veja docs/BACKEND.md.');
      const { data, error } = await supabaseClient.auth.signInWithPassword({ email, password });
      if (error) throw error;
      mode = 'account';
      currentUserId = data.user.id;
      authListeners.forEach(fn => fn({ mode: 'account', user: data.user }));
      return data;
    },

    async signOut() {
      if (hasSupabaseConfig && mode === 'account') {
        await supabaseClient.auth.signOut();
      }
      mode = null;
      currentUserId = null;
      memoryStore.clear();
      authListeners.forEach(fn => fn({ mode: null, user: null }));
    },

    async getSession() {
      if (!hasSupabaseConfig) return null;
      const { data } = await supabaseClient.auth.getSession();
      if (data && data.session) {
        mode = 'account';
        currentUserId = data.session.user.id;
        return { mode: 'account', user: data.session.user };
      }
      return null;
    },

    onAuthChange(fn) {
      authListeners.push(fn);
    },

    getMode() {
      return mode;
    }
  };
})();
