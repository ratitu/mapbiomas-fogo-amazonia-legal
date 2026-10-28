# Git, remoto e deploy

- Repo git real: `main`, remoto `git@github.com:ratitu/mapbiomas-fogo-amazonia-legal.git`. 4 commits, todos de `ratitu`, mensagens em inglês ("Initial commit: ...", "Add MapLibre Globe version of website", "Deploy website-globe to GitHub Pages", "Move globe version to root for GitHub Pages"). Sem branches de feature, sem PRs.
- README.md e AGENTS.md diziam "não é um repositório git" — corrigido em 28/10/2026 para refletir o repo real (remoto, branch, Pages, trabalho untracked). Se a frase antiga reaparecer em outro arquivo, é resíduo de antes do `git init`.
- Deploy: **só** `.github/workflows/deploy-pages.yml` publica no Pages (`./website-globe`; triggers: push em `website-globe/**` ou no próprio workflow, + `workflow_dispatch`). O antigo `pages.yml` (publicava `./website`) foi removido em 28/10/2026 porque os dois disputavam o mesmo Pages — `website/` agora é local-only. Sobrou uma cópia morta do build do globe na raiz (`index.html`, `assets/`, `favicon.svg`, `icons.svg`, `limites_amazonia_legal.geojson`) com os mesmos hashes de `website-globe/`; sem papel no deploy por Actions.
- `.gitignore` cobre `.omo/`, `.playwright-mcp/`, `session-*.md`, `__pycache__/`, venvs.
- Estado típico: quase todo o trabalho recente (timelapse/, design/, GIFs, MP4s, legendas, GeoJSON do INPE) está **untracked**; só `AGENTS.md`/código antigo é rastreado.

Regra do usuário: **nunca commitar/pushar sem pedido explícito**.