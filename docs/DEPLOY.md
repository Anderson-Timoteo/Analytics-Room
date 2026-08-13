# Deploy — colocando no ar como um site

## Passo 1 — Subir pro GitHub

```bash
cd sala-de-analises      # esta pasta
git init
git add .
git commit -m "Primeira versão da Sala de Análises"
git branch -M main
git remote add origin https://github.com/SEU-USUARIO/SEU-REPOSITORIO.git
git push -u origin main
```

(Se preferir sem terminal: crie o repositório vazio no GitHub e arraste
os arquivos pela interface web em "Add file → Upload files".)

## Passo 2 — Escolher a hospedagem (grátis)

Recomendação atual: **Cloudflare Pages** — banda ilimitada de graça,
HTTPS automático, e é só conectar o repositório do GitHub direto pelo
painel. É hoje a opção mais indicada pra sites estáticos gratuitos.

1. Crie uma conta em **https://pages.cloudflare.com**.
2. **Create a project → Connect to Git** → escolha o repositório.
3. Configuração de build:
   - **Build command**: (deixe em branco — não tem build, é HTML puro)
   - **Build output directory**: `/` (raiz)
4. **Save and Deploy**. Em ~1 minuto o site está no ar, com uma URL
   tipo `sala-de-analises.pages.dev`.

Alternativas igualmente válidas:
- **GitHub Pages**: mais simples se você já vive no GitHub — em
  **Settings → Pages** do repositório, escolha a branch `main` e a
  pasta raiz. Fica no ar em `SEU-USUARIO.github.io/SEU-REPOSITORIO`.
- **Netlify**: bom se quiser recursos extras depois (funções serverless,
  formulários prontos), mas hoje cobra por "créditos" de uso — vale
  comparar se o seu uso vai crescer bastante.

## Passo 3 (opcional) — Domínio próprio

Depois de publicado em qualquer uma dessas plataformas, você pode
conectar um domínio comprado separadamente (Registro.br, GoDaddy,
Namecheap etc.) direto no painel de "Custom domains" — todas oferecem
certificado HTTPS gratuito automático nesse processo.

## Antes de publicar de verdade: configure o backend

Se o `config.js` estiver vazio, o site publicado funciona, mas só em
modo visitante (ninguém consegue criar conta nem salvar nada entre
visitas). Configure o Supabase primeiro — veja
[`docs/BACKEND.md`](BACKEND.md) — e faça commit do `config.js`
preenchido antes do deploy final.

## Cada vez que você editar algo

Qualquer novo `git push` pra branch `main` já dispara um novo deploy
automático — tanto no Cloudflare Pages quanto no GitHub Pages/Netlify.
Não precisa repetir a configuração.
