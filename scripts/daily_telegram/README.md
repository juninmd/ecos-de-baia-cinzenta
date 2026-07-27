# 📬 Daily Telegram Chapter

Envia **um capítulo por dia** no Telegram: imagem de capa + texto completo + vídeo narrado.
Custo: **R$ 0,00** — tudo roda em serviços gratuitos.

## Como funciona

| Etapa | Serviço | Custo |
|---|---|---|
| Agendamento diário | GitHub Actions (`cron`) | grátis (repo público = minutos ilimitados) |
| Capa do capítulo | arte já commitada em `docs/public/capitulo_N.jpg`, senão [Pollinations](https://pollinations.ai) | grátis |
| **Cenas com personagens consistentes** | Space `black-forest-labs/FLUX.1-Kontext-Dev` usando os retratos de `docs/public/personagens/` como âncora de identidade | grátis (ZeroGPU) |
| **Movimento real das cenas** | Space `Lightricks/ltx-video-distilled` (image-to-video) | grátis (ZeroGPU) |
| Narração | gTTS (Google Translate TTS) | grátis |
| Montagem | ffmpeg (concat + Ken Burns de fallback), já instalado no runner | grátis |
| Entrega | Telegram Bot API | grátis |

## Modo animado (padrão)

O capítulo é quebrado em 4 cenas. Para cada cena:

1. Detecta os personagens presentes (`docs/personagens.md` + aliases).
2. Se algum tem retrato em `docs/public/personagens/`, a imagem da cena é gerada com
   **FLUX Kontext a partir do retrato** — rosto, cabelo, barba e vestuário se mantêm entre
   capítulos. Sem retrato, cai para texto→imagem com o descritor canônico do personagem.
3. A imagem vira um clipe animado de verdade via LTX-Video (push-in, chuva, neon piscando),
   com movimento diferente por cena.
4. Os clipes são concatenados e a narração é sobreposta.

Cada etapa degrada sozinha: Kontext falhou → gera sem referência; LTX falhou → Ken Burns por
ffmpeg. O vídeo sempre sai.

O estado (`.daily_telegram_state.json`) guarda o último capítulo enviado e é commitado de volta
com `[skip ci]`, então o pipeline retoma exatamente de onde parou. Ao chegar no último capítulo,
recomeça do primeiro.

## Setup (uma vez)

1. **Criar o bot**: fale com [@BotFather](https://t.me/BotFather) → `/newbot` → copie o token.
2. **Descobrir o chat id**: mande qualquer mensagem para o bot e abra
   `https://api.telegram.org/bot<TOKEN>/getUpdates` → campo `message.chat.id`.
3. **Cadastrar os secrets** no repositório (Settings → Secrets and variables → Actions):
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_CHAT_ID`
4. Pronto. O workflow `Daily Telegram Chapter` roda todo dia às **08:00 BRT** (11:00 UTC).

Para disparar manualmente: aba Actions → *Daily Telegram Chapter* → *Run workflow*
(dá para escolher um capítulo específico, pular o vídeo ou rodar em modo `dry-run`).

## Uso local

```bash
pip install requests gtts pillow          # ffmpeg precisa estar no PATH
export TELEGRAM_BOT_TOKEN=...             # PowerShell: $env:TELEGRAM_BOT_TOKEN="..."
export TELEGRAM_CHAT_ID=...

python -m scripts.daily_telegram.main --dry-run            # testa sem enviar
python -m scripts.daily_telegram.main --chapter 42         # envia um capítulo específico
python -m scripts.daily_telegram.main --no-video           # só imagem + texto
```

## Filme da história (`story.py`)

Gera **várias cenas por capítulo**, encadeia tudo e produz um filme contínuo:

```bash
# só a arte, cacheada em docs/public/cenas/capitulo_N/ (nada é regerado)
python -m scripts.daily_telegram.story --from 1 --to 5 --scenes 8 --art-only

# filme animado dos capítulos 1 a 5
python -m scripts.daily_telegram.story --from 1 --to 5 --scenes 8

# usando a GPU local (sem cota, sem fila)
.venv-gpu/Scripts/python -m scripts.daily_telegram.story --from 1 --to 10 --local
```

Cada capítulo entra no filme com uma cartela de título, suas cenas animadas e a narração.
As imagens ficam em `docs/public/cenas/` e são reaproveitadas para sempre — rodar de novo só
preenche o que falta, então dá para construir a história inteira aos poucos.

## Prompt por motor

Modelos diferentes recebem prompts diferentes, porque os limites são diferentes:

| Motor | Prompt | Por quê |
|---|---|---|
| FLUX Kontext (local ou Space) | `Scene.edit_prompt` — identidade + vestuário + cena + descritor canônico completo | aceita prompt longo e usa o retrato como imagem-base |
| SDXL + IP-Adapter | `Scene.compact_prompt` — enquadramento + vestuário + local + ação, ~40 palavras | o CLIP corta em **77 tokens**; com prompt longo só sobrava a identidade e toda cena virava o mesmo close-up frontal |

O peso da âncora de identidade (`Scene.identity_scale`) muda conforme o plano: **0.55** em plano
aberto, **0.9** em close. Com peso fixo alto o IP-Adapter puxa a composição para retrato e todo
plano aberto vira close-up frontal — a cena perde o cenário.

`compact_prompt` também alterna o enquadramento por cena (`wide establishing`, `medium`,
`over-the-shoulder`, `low angle`, `close-up`, `high angle wide`) e prefere frases de narração
a falas — "Ameace com obstrução de justiça" é um prompt visual ruim.

## GPU local (`--local`)

`scripts/daily_telegram/local_gpu.py` usa **SDXL + IP-Adapter**: o retrato do personagem entra
como âncora de identidade (`ip_adapter_image`) e o prompt só define a cena. Sem cota, sem fila.

Setup (uma vez, precisa de Python 3.12 — torch não tem wheel para 3.14):

```bash
uv venv --python 3.12 .venv-gpu
uv pip install --python .venv-gpu/Scripts/python torch torchvision --index-url https://download.pytorch.org/whl/cu124
uv pip install --python .venv-gpu/Scripts/python diffusers transformers accelerate safetensors requests gtts pillow gradio_client
```

## Cota gratuita (o limite real do modo animado)

As Spaces rodam em **ZeroGPU**, que dá alguns minutos de GPU por dia por conta gratuita.
Na prática isso rende **~2 a 4 gerações por dia** (Kontext ~30s + LTX ~120s por clipe).
Quando a cota acaba, o pipeline detecta a mensagem de quota, para de tentar naquele capítulo
e termina o vídeo com Ken Burns — sem falhar e sem gastar tempo em chamadas condenadas.

Para ter mais: gere localmente. A máquina do autor tem uma RTX 4060 Ti, então dá para rodar
FLUX Kontext / LTX offline sem cota nenhuma, commitar o resultado em `docs/public/` e deixar o
pipeline diário só reaproveitar (`find_local_art` já faz isso). Custo continua zero.

## Limites conhecidos

- Vídeo: a narração usa os primeiros 3000 caracteres do capítulo (~4-5 min, ~17 MB).
  O bot do Telegram aceita no máximo 50 MB — arquivos maiores são pulados automaticamente.
- Texto: enviado em blocos de até 4000 caracteres (limite da API).
- Pollinations é grátis mas sem SLA; se falhar após 3 tentativas, o capítulo vai sem imagem nova.
