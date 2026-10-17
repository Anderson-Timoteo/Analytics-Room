/**
 * storage-adapter.js
 * ---------------------------------------------------------------
 * O Supabase aqui serve SÓ pra autenticação (login/cadastro).
 * Nenhum dado de análise (Ishikawa, 5W2H, PDCA, DMAIC, 5 Porquês,
 * Pareto) é enviado pra nuvem — tudo fica gravado no localStorage
 * do próprio navegador, visitante ou logado, dá no mesmo.
 *
 * O "salvamento de verdade" (portátil, que sobrevive à troca de
 * computador) continua sendo os botões de exportação dentro do app
 * (.sql / .xlsx / .pdf) — não este adaptador.
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

  let mode = null; // 'guest' | 'account' — só controla a TELA/saudação
  let currentUser = null;

  // ---------------- window.storage: local no navegador ----------------
  // A tela promete que no modo visitante "ao fechar a aba, os dados somem".
  // Com localStorage isso era falso: ficava gravado em disco pra sempre e a
  // próxima pessoa na mesma máquina via tudo. Visitante agora usa
  // sessionStorage, que morre junto com a aba — a promessa passou a ser real.
  // Conta continua em localStorage, porque ali persistir é o esperado.
  const LS_PREFIX = 'saladeanalises:';

  function lsKey(key, shared) {
    return `${LS_PREFIX}${shared ? 'shared' : 'p'}:${key}`;
  }

  function store() {
    try {
      return mode === 'guest' ? sessionStorage : localStorage;
    } catch (e) {
      return localStorage;          // navegador com storage bloqueado
    }
  }

  // Uma vez por aba: o que ficou gravado em disco de sessões de visitante
  // anteriores é movido pra sessionStorage e apagado do disco. Sem isso a
  // troca só esconderia os dados antigos, em vez de resolver.
  let migrou = false;
  function migrarVisitante() {
    if (migrou || mode !== 'guest') return;
    migrou = true;
    try {
      const antigas = [];
      for (let i = 0; i < localStorage.length; i++) {
        const k = localStorage.key(i);
        if (k && k.startsWith(LS_PREFIX)) antigas.push(k);
      }
      antigas.forEach(k => {
        if (sessionStorage.getItem(k) === null) {
          sessionStorage.setItem(k, localStorage.getItem(k));
        }
        localStorage.removeItem(k);
      });
    } catch (e) { /* storage bloqueado: segue sem migrar */ }
  }

  window.storage = {
    async get(key, shared) {
      migrarVisitante();
      const raw = store().getItem(lsKey(key, shared));
      if (raw === null) throw new Error('not found');
      return { key, value: raw, shared: !!shared };
    },
    async set(key, value, shared) {
      migrarVisitante();
      store().setItem(lsKey(key, shared), value);
      return { key, value, shared: !!shared };
    },
    async delete(key, shared) {
      migrarVisitante();
      store().removeItem(lsKey(key, shared));
      return { key, deleted: true, shared: !!shared };
    },
    async list(prefix, shared) {
      migrarVisitante();
      const st = store();
      const sharedTag = shared ? 'shared' : 'p';
      const fullPrefix = `${LS_PREFIX}${sharedTag}:${prefix || ''}`;
      const keys = [];
      for (let i = 0; i < st.length; i++) {
        const rawKey = st.key(i);
        if (rawKey && rawKey.startsWith(fullPrefix)) {
          keys.push(rawKey.slice(`${LS_PREFIX}${sharedTag}:`.length));
        }
      }
      return { keys, prefix, shared: !!shared };
    }
  };

  // ---------------- window.authAPI: só login/cadastro (Supabase Auth) ----------------
  const authListeners = [];

  window.authAPI = {
    isBackendConfigured: hasSupabaseConfig,

    continueAsGuest() {
      mode = 'guest';
      currentUser = null;
      authListeners.forEach(fn => fn({ mode: 'guest', user: null }));
    },

    async signUp(email, password) {
      if (!hasSupabaseConfig) throw new Error('Backend não configurado. Veja docs/BACKEND.md.');
      const { data, error } = await supabaseClient.auth.signUp({ email, password });
      if (error) throw error;
      if (data.session) {
        mode = 'account';
        currentUser = data.user;
        authListeners.forEach(fn => fn({ mode: 'account', user: data.user }));
      }
      return data;
    },

    async signIn(email, password) {
      if (!hasSupabaseConfig) throw new Error('Backend não configurado. Veja docs/BACKEND.md.');
      const { data, error } = await supabaseClient.auth.signInWithPassword({ email, password });
      if (error) throw error;
      mode = 'account';
      currentUser = data.user;
      authListeners.forEach(fn => fn({ mode: 'account', user: data.user }));
      return data;
    },

    async signOut() {
      if (hasSupabaseConfig && mode === 'account') {
        await supabaseClient.auth.signOut();
      }
      // NÃO limpamos o localStorage aqui — os dados são do navegador, não da conta.
      mode = null;
      currentUser = null;
      authListeners.forEach(fn => fn({ mode: null, user: null }));
    },

    async getSession() {
      if (!hasSupabaseConfig) return null;
      const { data } = await supabaseClient.auth.getSession();
      if (data && data.session) {
        mode = 'account';
        currentUser = data.session.user;
        return { mode: 'account', user: data.session.user };
      }
      return null;
    },

    onAuthChange(fn) {
      authListeners.push(fn);
    },

    getMode() {
      return mode;
    },

    getUser() {
      return currentUser;
    }
  };
})();