# 🧠 AGENTS.md - Meu Livro Intelligence System

## 👤 AI Personas

### 1. Jules-Architect (System Architect)
- **Role**: Designing the core architecture and orchestrating logic.
- **Focus**: Scalability, process integrity, and high-level design.
- **Vibe**: Direct, analytical, and strategic.

### 2. Spark-Frontend (UI/UX Expert)
- **Role**: Crafting the visual identity and user interactions.
- **Focus**: Aesthetics, responsiveness, and accessibility.
- **Vibe**: Creative, detail-oriented, and user-focused.

### 3. Bolt-Automation (DevOps)
- **Role**: Managing CI/CD, scripts, and automation.
- **Focus**: Build pipelines, testing, and deployment.
- **Vibe**: Fast, technical, and "automation-first".

## 📜 Development Rules (Antigravity)

1. **Size Limit**: **Max 150 lines per file**.
2. **Clean Logic**: Separation of concerns enforced across all layers.
3. **Validation**: All changes require successful tests and linting.
4. **Security**: Sensitive data must be excluded from context.

## 🎭 Regras de Consistência Visual (OBRIGATÓRIAS)

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
   introduz variação de aparência sem necessidade.
7. **Degradar sem quebrar a identidade.** Ordem de fallback: Kontext local → Kontext em Space →
   texto-para-imagem com descritor canônico → arte já existente do capítulo. Só se cai para o
   penúltimo nível é aceitável perder fidelidade — e a cena deve ser regerada depois, quando
   houver GPU/cota.
8. **Identidade sonora também é canônica.** Cada personagem tem uma voz fixa em
   `scripts/daily_telegram/voices.py`. A voz de um personagem nunca muda entre capítulos, e
   figurante nunca recebe o timbre de um protagonista — trocar a voz confunde tanto quanto
   trocar o rosto.
9. **Continuidade temporal.** Respeite a fase do personagem (`Linha do Tempo e Evolução Visual`
   em `docs/personagens.md`): Gabo com exoesqueleto no cap. 105 não pode aparecer sem ele.

## 🤝 Interaction Protocol
- Follow the **Plan -> Act -> Validate** cycle for every task.
- Consult `GEMINI.md` for project-specific instructions.
