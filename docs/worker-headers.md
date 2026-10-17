# Headers de segurança no Cloudflare Worker

O site hoje responde sem nenhum header de segurança:

```
Content-Type: text/html
Cache-Control: public, max-age=0, must-revalidate
Server: cloudflare
```

Faltam `Content-Security-Policy`, `X-Frame-Options`, `X-Content-Type-Options`,
`Referrer-Policy` e `Strict-Transport-Security`. Sem os dois primeiros, qualquer
site pode embutir o app num iframe invisível e capturar cliques (*clickjacking*).

Isto é configuração do Worker — não muda nada no `index.html`.

## O trecho

Envolva a resposta que o Worker já devolve. Se ele hoje faz algo como
`return new Response(html, { headers: { 'Content-Type': 'text/html' } })`,
passe a resposta por `comSeguranca()`:

```js
const CSP = [
  "default-src 'self'",
  // o app tem CSS e JS embutidos no index.html, por isso os 'unsafe-inline'
  "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com",
  "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
  "font-src 'self' https://fonts.gstatic.com",
  // o Supabase Auth: troque pelo seu projeto se mudar
  "connect-src 'self' https://noplasgmzevfxkfvdkxv.supabase.co",
  "img-src 'self' data:",
  "frame-ancestors 'none'",        // ninguém pode embutir o site num iframe
  "base-uri 'self'",
  "form-action 'self'",
  "object-src 'none'"
].join('; ');

function comSeguranca(res) {
  const h = new Headers(res.headers);
  h.set('Content-Security-Policy', CSP);
  h.set('X-Content-Type-Options', 'nosniff');
  h.set('Referrer-Policy', 'strict-origin-when-cross-origin');
  h.set('Permissions-Policy', 'geolocation=(), microphone=(), camera=()');
  h.set('Strict-Transport-Security', 'max-age=31536000; includeSubDomains');
  // frame-ancestors já cobre navegador moderno; X-Frame-Options é o fallback
  h.set('X-Frame-Options', 'DENY');
  return new Response(res.body, { status: res.status, headers: h });
}

export default {
  async fetch(request, env, ctx) {
    const res = /* o que o Worker já devolvia */;
    return comSeguranca(res);
  }
};
```

## Por que os `'unsafe-inline'`

O app é um `index.html` único, com `<style>` e `<script>` embutidos. Uma CSP sem
`'unsafe-inline'` bloquearia o próprio app. Para apertar isso seria preciso
separar CSS e JS em arquivos — decisão que já foi avaliada e adiada.

Mesmo com esse afrouxamento, a CSP ainda vale muito: `frame-ancestors 'none'`
mata clickjacking, e o `script-src` com lista fixa impede que um script de
origem desconhecida rode, que é o cenário de CDN comprometido.

## Depois de publicar, confira

```bash
curl -sI https://analytics-room.anderson-timoteo.workers.dev/ | grep -iE "content-security|x-frame|x-content-type|referrer|strict-transport"
```

Devem aparecer os cinco. E abra o app no navegador olhando o console: se algum
recurso for bloqueado pela CSP, o erro aparece lá, dizendo qual diretiva faltou.
