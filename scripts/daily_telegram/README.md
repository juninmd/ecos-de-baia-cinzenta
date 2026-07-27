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
