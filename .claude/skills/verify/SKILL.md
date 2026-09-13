---
name: verify
description: Build/launch/drive recipe for verifying changes to the Sala de Análises / Metodologias single-page app (index.html).
---

# Verify — Metodologias (Sala de Análises)

Single-page app. Everything lives in `index.html` (HTML + inline `<style>` +
one big inline `<script>`, ~3.9k lines). No build step, no framework, no
package.json. `config.js` holds Supabase Auth keys; `js/storage-adapter.js`
wraps localStorage.

## Launch

```bash
python -m http.server 8765          # from repo root
```
Then open `http://localhost:8765/index.html` in the browser pane
(`navigate`). Opening the `file://` path directly is blocked by the harness —
use the http server.

Server dies with the shell — restart it if the pane 404s / connection-refuses.

## Get past the gate

`config.js` has real Supabase keys, so the **auth gate shows on every load**.
Path in: click **"Continuar como visitante"** → splash screen → **"Iniciar →"**
→ name screen: type any name → **"Iniciar análises →"**.

Guest data persists in localStorage, so on later loads it may jump straight
past the name screen. A returning guest session skips the welcome flow
entirely.

Screenshots frequently time out ("page did not finish rendering" — pane is
hidden/behind another window). Retry once, then fall back to `get_page_text`,
`read_page`, or `javascript_tool` for inspection. `javascript_tool` is the
most reliable way to drive and assert here.

## Data model (globals in page scope, one per methodology)

`state` (Ishikawa), `plan` (5W2H), `pdca`, `fiveWhys`, `dmaic`, `fca`, `voc`,
`pareto` — all keyed by `currentId` (the active analysis). `renderTrilha()`
reads these directly.

## Flows worth driving

- **Theme**: `#btn-theme` in the sidebar footer toggles dark⇄light,
  persists to `localStorage['metodologias:tema']`, and re-renders the
  Pareto/Ishikawa SVG (which read colors via `cssVar()`). Verify persistence
  by reloading. Default (no stored value) = dark.
- **Trilha** (first tab, default view): 8 stage cards with live status
  (`vazia`/`andamento`/`ok`), progress ring `#trilha-progress-num`, next-step
  banner `#trilha-next`. Recomputed on `switchView('trilha')`, `startAppData`,
  `switchAnalysis`, `createNewAnalysis`, and after any handoff — **not** on
  every keystroke in a tool view.
- **Handoffs**: `handoffVocToPareto`, `handoffParetoToIshikawa`,
  `handoffIshikawaToFiveWhys`, `handoffIshikawaSolutionsToPlan`,
  `handoffFiveWhysToPlan`, `handoffFcaToPlan`, `handoffPlanToPdca`,
  `handoffPlanToDmaic`. Each returns `{ok, msg}`, is callable from the Trilha
  card buttons AND the in-view "Importar/Enviar…" buttons. Empty source →
  friendly message, no throw.
- **Regression sweep**: click all 8 sidebar tabs, confirm each renders and
  console stays clean. The handoff refactor touched every tool view's
  import/send button.
- **Export PDF (dossiê)**: "Exportar dados" → "🖨️ PDF". Monta capa + sumário +
  uma metodologia por página (só as com dados, na ordem da trilha — o handler
  **reordena o DOM** e restaura no `afterprint`). `window.print()` trava a
  automação: stube `window.print` e neutralize o fallback (`setTimeout` de
  1500 ms) para o dossiê ficar montado e inspecionável. Para **ver** o layout
  de impressão sem dialog, converta as regras na marra:
  `for(const r of ss.cssRules) if(r.type===4 && /print/.test(r.media.mediaText)) r.media.mediaText='all'`.
  Depois volte para `'print'` e dispare `afterprint` para testar o restore.
- **Export .xlsx**: "Exportar dados" → "📊 Excel (.xlsx)". Lazy-loads ExcelJS
  4.4.0 from cdnjs on first click (needs network), builds a 10-sheet workbook
  (Capa, Painel, uma por metodologia) and downloads it. The pane sandboxes the
  download — measure the blob instead by wrapping `URL.createObjectURL` and
  stubbing `HTMLAnchorElement.prototype.click`. Expect ~25 KB and mime
  `…spreadsheetml.sheet`. To verify the *file* rather than the click, use the
  Node harness in the scratchpad: it slices the `Exportação Excel (.xlsx)`
  block out of `index.html`, runs it against a real `exceljs` with mock data,
  and writes a `.xlsx` you can read back and assert styles on.

## Assert with JS

```js
// status snapshot
[...document.querySelectorAll('.trilha-stage')].map(s =>
  s.querySelector('.trilha-stage-name').textContent + ' | ' + s.dataset.s)
// theme state
({theme: document.documentElement.dataset.theme,
  stored: localStorage.getItem('metodologias:tema')})
// chart colors after toggle
document.querySelector('#pareto-chart polyline').getAttribute('stroke')
```

## Gotchas

- Viewport emulation (`resize_window`) does **not** change `window.innerWidth`
  in this pane — can't truly test the `@media` mobile breakpoints here. The
  CSS uses relative units + `minmax()`, so eyeball the rules instead.
- `drawBones()` (Ishikawa fishbone) runs via `requestAnimationFrame` after
  `switchView` — querying the `#bones` SVG immediately after the click shows
  0 lines; wait a tick.
- The welcome splash still shows the old "ANALYTICS - ROOM" wordmark with
  green/blue accents — that's a separate brand asset, out of scope for the
  reskin.
