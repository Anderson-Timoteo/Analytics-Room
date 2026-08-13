/**
 * config.js
 * ---------------------------------------------------------------
 * Copie este arquivo para "config.js" (mesmo nome, sem o ".example")
 * e preencha com os dados do SEU projeto Supabase.
 *
 * Onde encontrar esses valores:
 *   Painel do Supabase → seu projeto → Project Settings → API
 *   - Project URL          → SUPABASE_URL
 *   - anon / public key    → SUPABASE_ANON_KEY
 *
 * IMPORTANTE: a "anon key" é feita pra ficar exposta no navegador —
 * não é um segredo. A segurança real vem das políticas de RLS
 * (Row Level Security) definidas em backend/schema.sql. Ainda assim,
 * cada ambiente (dev/produção) pode ter seu próprio config.js.
 *
 * Se você não preencher isso, o app funciona normalmente em modo
 * "visitante" (sem salvar dados), mas as opções de login/cadastro
 * ficam desativadas.
 * ---------------------------------------------------------------
 */
window.SUPABASE_URL = '';        // ex.: 'https://xxxxxxxxxxxx.supabase.co'
window.SUPABASE_ANON_KEY = '';   // ex.: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...'
