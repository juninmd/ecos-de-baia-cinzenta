# AGENTS.md

Ecos de Baía Cinzenta: cyberpunk noir novel in 256 chapters (pt-BR), published as a VitePress site, plus Python tooling for art, audio and video. Story text is pt-BR; code, identifiers, comments and commits are English.

## Stack

- Site: VitePress on Node, pnpm 10.30.3 (`packageManager`). Docker: `node:22-alpine` build, `nginx-unprivileged` serve.
- Tooling: Python >=3.11 (CI runs 3.12), managed with uv (`pyproject.toml`, `uv.lock`). `requirements-dev.txt` is the pip-compatible list.
- Tests: `node --test` (`tests/*.test.mjs`, `scripts/*.test.mjs`) and pytest (`tests/`).
- Mobile: Capacitor, with a pnpm patch for `@capacitor/cli` 6.2.2 (`patches/`).

## Commands

```bash
pnpm install --frozen-lockfile   # pnpm only; CI and Docker use the frozen lockfile
pnpm docs:dev                    # dev server, localhost:5173
pnpm docs:build                  # runs build:sw (tsc -p docs/tsconfig.sw.json) first
pnpm test                        # dependency metadata check + scripts/npm_test.mjs
pnpm test:docs && pnpm test:sw   # docs unit tests + service-worker cache test
node --test tests/chapter_cover_build.test.mjs   # run by github-pages.yml after docs:build
uv venv && uv pip install -r requirements-dev.txt  # Python env
pytest                           # Python tests in tests/
python scripts/quality_gate.py   # chapter quality gate, writes docs/qualidade_capitulos.md
pnpm android:build               # Android debug build (needs Android SDK)
```

Lint: none configured in the repo (no linter config at the root). Typecheck: only `tsc` via `build:sw`.

## Structure

- `docs/`: VitePress site and source. `capitulo-N.md` is the official chapter source; `personagens/` is the character canon; `.vitepress/` holds theme and navigation.
- `docs/public/`: static assets. `personagens/` (portraits), `cenas/capitulo_N/` (committed scene art), `vozes/` (voice audio), `videos/`. `public/capitulo-N.md` are symlinks.
- `editorial/`: revision notes and audits. Working records, not product source.
- `scripts/`: `art_gen/` (portraits, continuity, fidelity), `daily_telegram/` (voices, cache, animation), quality and homologation scripts.
- `tests/`: pytest and node tests.
- `.github/workflows/`: `validate` (reusable from `juninmd/base-actions`), `github-pages`, `deploy`, `docker-pr`, `sast`, `security`, `daily-telegram`, `arte-cenas`, `send-full-story`, `release-drafter`.
- `.agents/skills/escrita-investigativa/`: skill for planning, writing and reviewing chapters.
- `.agent/workflows/`: chapter review workflow.

## Conventions

- Default branch: `master`. The `validate` workflow runs on `main` and `master`; `github-pages` deploys from `master`.
- PR template: `.github/pull_request_template.md` (Summary, Quality Checklist, Verification).
- Agent personas (roles for review, not code owners): Jules-Architect (scalability, architecture, high-level design), Spark-Frontend (UI/UX, visual identity, responsiveness), Bolt-Automation (CI/CD, build pipelines, scripts).

### Development Rules

1. **Size Limit**: **Max 150 lines per file**.
2. **Clean Logic**: Separation of concerns enforced across all layers.
3. **Validation**: All changes require successful tests and linting.
4. **Security**: Sensitive data must be excluded from context.

### GitHub Actions (mandatory @main)

<!-- base-actions-main-policy -->
- Reference internal actions by branch, never by SHA:
  - `uses: juninmd/base-actions/<action>@main`
  - `uses: juninmd/base-actions/.github/workflows/<file>.yml@main`
- Do not pin `@<sha>` on `juninmd/base-actions`: updates are centralized on `main` and apply on the next run.
- PRs whose checks do not start due to billing/spending limit are merged by the central bot `juninmd/base-actions/.github/workflows/auto-merge-billing-blocked.yml`. To block that automatic merge of a PR, apply the label `do-not-merge`.

### Interaction Protocol

- Follow the Plan -> Act -> Validate cycle for every task.
- Consult `GEMINI.md` for project-specific instructions.
- To plan, write or review chapters, use the [escrita-investigativa skill](.agents/skills/escrita-investigativa/SKILL.md).
- Chapter source: `docs/capitulo-N.md`. The mirror `docs/public/capitulo-N.md` must be a relative symlink to `../capitulo-N.md`. Migration is complete (238 mirrors are links). Edit only the source; never replace a link with a copy.

### Visual Consistency Rules (mandatory)

> **Regra Zero: a fisionomia e a aparência dos personagens NUNCA mudam.**
> Um personagem gerado hoje tem que ser reconhecível como o mesmo de 200 capítulos atrás.
> Qualquer geração de imagem ou vídeo que viole isso deve ser descartada, não publicada.

1. **Âncora de imagem antes de texto.** Se o personagem tem retrato em
   `docs/public/personagens/`, a cena **tem** que ser gerada a partir dele (image-to-image /
   FLUX Kontext), nunca só por descrição textual. Texto sozinho reinventa o rosto a cada geração.
   O peso da âncora se ajusta ao plano (alto em close, baixo em plano aberto): peso fixo alto
   trava a identidade mas transforma toda cena em retrato frontal.
2. **`docs/personagens.md` é a fonte da verdade.** Vestuário, cabelo, olhos, porte e marcas
   distintivas vão sempre no prompt, com **vestuário primeiro** — é o traço que os modelos mais
   trocam por conta própria.
   - **Todo personagem tem retrato.** Perfil novo entra com `![Nome](/personagens/slug.png)` e
     um campo `**Prompt Visual:**` — a descrição física traduzida para inglês, porque o CLIP é
     treinado em inglês e ignora metade do português. Depois é só rodar
     `python -m scripts.art_gen.portraits`, que gera só o que falta, com seed determinística.
   - **O `Prompt Visual` tem que caber em 77 tokens.** É onde os dois encoders do SDXL cortam;
     acima disso os últimos traços somem em silêncio. O gerador avisa quando estoura.
   - `tests/test_personagens_dossie.py` trava as duas coisas: perfil sem retrato no disco ou
     sem campo visual obrigatório quebra a build.
3. **Retrato de referência é imutável.** Nunca sobrescreva um arquivo de
   `docs/public/personagens/`. Novo visual canônico = arquivo novo com sufixo
   (`elena_2.png`) + registro na "Linha do Tempo e Evolução Visual" do personagem.
4. **Seed determinística.** Mesma cena de mesmo capítulo tem que produzir a mesma imagem:
   `seed = numero_do_capitulo * 100 + indice_da_cena`. Nada de seed aleatória.
5. **Uma âncora por cena.** Escolha o personagem com mais menções reais no trecho e trave a
   identidade nele. Ignore aliases com menos de 4 caracteres — "O" de "O Taxidermista" casa com
   todo artigo em português e sequestra o ranking.
6. **Arte é cache, não descartável.** Toda cena gerada é commitada em
   `docs/public/cenas/capitulo_N/`. Regerar uma cena que já existe é proibido: gasta cota e
   introduz variação de aparência sem necessidade. A única exceção é a cena reprovada na
   homologação — refugo não é arte aprovada e não ocupa lugar de cena.
7. **Dois modelos locais, escolhidos pelo tipo de plano.** A rota local não é um modelo só:
   - **Cena de ambiente** (sem âncora de identidade, `identity_scale == 0`, todo plano `wide`):
     **ZavyChromaXL v8** (`misri/zavychromaxl_v80`) + SDXL, ~40 s por imagem. O establishing
     shot do Gemini também não tem personagem — forçar âncora aqui era o que transformava toda
     cena em retrato 3x4.
   - **Cena com personagem**: **Qwen-Image-Edit-2511** em GGUF Q2_K
     (`unsloth/Qwen-Image-Edit-2511-GGUF`), ~4 min por imagem. Exige
     **diffusers >= 0.40**: na 0.39 o modelo carrega mas o processo morre na geracao.
     A versao 2509 foi testada antes e reprovada — em 5 cenas so 1 saiu boa, o resto
     veio lavado e com o adereco da foto de referencia (o copo de cafe do Gabo)
     colado em toda cena. A 2511 acertou as 4 cenas de teste e troca o adereco
     conforme a cena. Recebe o retrato de referência
     como imagem de entrada e edita o mundo em volta, em vez de injetar um vetor de rosto na
     difusão. É o que preserva rosto **e** vestuário canônico — o IP-Adapter troca a roupa.
   - O prompt do Edit tem que **separar o que preserva do que muda**. Só pedir "mantenha o rosto"
     faz o modelo recortar a referência e trocar só o fundo: mesma pose, mesmos adereços, dez
     cenas do capítulo viram dez retratos iguais. É preciso afirmar que é uma fotografia nova,
     com pose e ação diferentes, **e** cravar o enquadramento na mesma instrução — uma sem a
     outra derruba o resultado.
   - Adereço que aparece no retrato de referência (o copo de café do Gabo) vaza para a cena
     gerada. Se a cena não comporta o objeto, ele entra no prompt negativo.
   - **Rota de volume, só Qwen-Edit** (`scripts/gerar_cenas_qwen_edit.py`): vinte cenas por
     capítulo em `capitulo_N/qwen_edit/`, todas pelo Qwen-Image-Edit-2511, inclusive as de
     ambiente — o ZavyChromaXL não entra. Não substitui a rota de duas vias acima; é uma
     terceira pasta, para comparar. A cena sem personagem citado herda a âncora do capítulo,
     porque o Edit não gera nada sem imagem de entrada. Em plano aberto a instrução **não**
     pode pedir "upper body large in the frame": isso devolve retrato 3x4 no lugar da cena.

   Ordem de fallback quando a rota local falha: Kontext em Space → texto-para-imagem com
   descritor canônico → arte existente. Modelos reprovados: SDXL base 1.0, RealVisXL V5,
   DreamShaper XL, Juggernaut XL v9, FLUX.1-dev (estoura VRAM) e Qwen-Image sem âncora.
8. **Identidade sonora também é canônica.** Cada personagem tem uma voz fixa em
   `scripts/daily_telegram/voices.py`. A voz de um personagem nunca muda entre capítulos, e
   figurante nunca recebe o timbre de um protagonista — trocar a voz confunde tanto quanto
   trocar o rosto.
9. **Continuidade temporal.** Respeite a fase do personagem (`Linha do Tempo e Evolução Visual`
   em `docs/personagens.md`): Gabo com exoesqueleto no cap. 107 não pode aparecer sem ele.
   `scripts/art_gen/continuidade.py` lê essa linha do tempo e injeta a fase correta no prompt;
   o vestuário com fases declaradas (Dante) é escolhido pelo capítulo, nunca mandado inteiro.
10. **Dez cenas por capítulo.** O alvo da obra é `CENAS_POR_CAPITULO = 10` em
    `scripts/build_scene_manifest.py` — 2.350 imagens. Três imagens não cobrem um capítulo de
    1.100 palavras e faziam o livro inteiro repetir o mesmo trio de planos.
11. **Nenhuma imagem entra sem homologação.** `python scripts/homologar_cenas.py --realimentar`
    mede resolução, nitidez, contraste, arquivo chapado, texto queimado e cena repetida, escreve
    `docs/qualidade_imagens.md` e devolve as reprovadas para `docs/public/cenas/regerar.txt`.
    Fidelidade de rosto é auditada com visão (`--visao N`). O ciclo completo está em
    `docs/pipeline_imagens.md`.
12. **Bases de Referência Oficiais e Benchmark Gabo (OBRIGATÓRIO).** Gabo, Bio-Dante, Enzo e
    Sofia **NUNCA** podem ser gerados/recriados sem suas imagens de referência oficiais:
    - Gabo: base mandatória em `docs/public/personagens/gabo.jpg`.
    - Bio-Dante: base fisionômica mandatória em `docs/public/personagens/dante.jpg` (biohost rejuvenescido).
    - Enzo e Sofia: base fisionômica mandatória em `docs/public/personagens/enzo_sofia.png`.

    A imagem `docs/public/personagens/gabo.jpg` é o **padrão ouro mandatório de qualidade visual,
    textura cinematográfica realista (35mm film still, granulação suja, iluminação de rua)** para
    todas as demais imagens do universo.

### Chapter Quality Standard (mandatory)

> Todo capítulo é avaliado nesta régua antes de ser considerado pronto.
> `python scripts/quality_gate.py` mede o que é mensurável e gera
> `docs/qualidade_capitulos.md`. O que a máquina não mede, o revisor lê.

Hard gates (each one rejects alone):

| # | Gate | Limit |
| --- | --- | --- |
| D1 | **Extensão** | ≥ 600 palavras (reprova abaixo disso: é cena, não capítulo). **Alvo: 1.100–1.600.** A mediana histórica da obra é 900, e capítulo curto é a causa número um de arco que não respira. |
| D2 | **Título** | Exatamente um H1, no formato `# Capítulo N: Título`, idêntico ao menu. |
| D3 | **Elenco declarado** | Bloco de metadados com Localização e Personagens Presentes. |
| D4 | **Traços canônicos** | Zero violações: Gabo nunca fuma; morto não age; fase física correta (exoesqueleto, braço fraturado/órtese, tipóia). |
| D5 | **Fechamento** | A última linha vira a página — imagem, decisão ou ameaça. Nunca resumo do que acabou de acontecer. |

Quality scale (0 to 2 per axis, max 10):

| Eixo | 0 | 1 | 2 |
| --- | --- | --- | --- |
| **Atmosfera noir** | Só descrição visual | Dois sentidos | **Três ou mais sentidos**, e o ambiente tem opinião sobre os personagens |
| **Custo** | Ninguém perde nada | Perda reversível | **Perda permanente**: corpo, pessoa, crença ou opção |
| **Voz e personagem** | Todos falam igual | Protagonista tem voz | **Cada personagem fala do jeito dele** e o silêncio de alguém significa algo |
| **Ritmo** | Bloco único de exposição | Alterna diálogo e ação | **A informação chega por conflito**, nunca por alguém explicando |
| **Consequência** | Episódio isolado | Referencia o anterior | **Muda o que o leitor entende** de algo que já leu |

**Cut notes:** 9–10 obra-prima · 7–8 publicável · 5–6 revisar · ≤4 reescrever.

Writing rules the scale enforces:

1. **Sem solução fácil.** Se o problema se resolve por competência sem preço, o capítulo está errado. Gabo ganha quebrado ou não ganha.
2. **Exposição é conflito.** Ninguém explica lore para quem já sabe. Se dois personagens conversam sobre algo que ambos conhecem, é para o leitor — e isso se corta.
3. **Nada de segunda cena de travessia.** Descer túnel, atravessar duto e subir escada só valem quando terminam em porta que muda o gênero da história. Duas seguidas viram rotina.
4. **A dor tem contabilidade.** Ferimento aberto num capítulo aparece no próximo. Personagem não se cura entre cenas.
5. **Revelação precisa de plantio.** Toda reviravolta tem que se sustentar em material já publicado. Cite o capítulo de plantio no dossiê.

## Gotchas

- Env var and secret names (never commit values; `.env*` is gitignored): `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`, `HF_TOKEN`, `GEMINI_API_KEY`, `NANO_BANANA_API_KEY` (and `_IMAGE`/`_TEXT` variants), `POLLINATIONS_TOKEN`. Keystores and keys (`*.jks`, `*.keystore`, `*.pem`, `*.key`) are gitignored.
- `docs/public/capitulo-N.md` must stay a relative symlink. Replacing it with a copy forks the chapter.
- Local art routes need a GPU and the `art` extra (torch, diffusers). `.venv-qwen/` is gitignored (~3 GB). Tests under `scripts/` are excluded from the default pytest gate.
- Generated files, regenerate instead of editing: `docs/qualidade_capitulos.md` (`scripts/quality_gate.py`), `docs/qualidade_imagens.md` (`scripts/homologar_cenas.py`).
- `pnpm-lock.yaml` is the only lockfile (`package-lock.json` and `yarn.lock` are gitignored). Never hand-edit it.
- `android/`, `.capacitor/` and `docs/.vitepress/dist` are generated and gitignored.
- `.github/copilot-instructions.md` is outdated: `pnpm test` runs node tests, not pytest. This file and `package.json` are the source of truth.
