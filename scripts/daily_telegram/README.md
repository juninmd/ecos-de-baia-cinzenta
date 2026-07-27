# 📬 Daily Telegram Chapter

Envia **um capítulo por dia** no Telegram: imagem de capa + texto completo + vídeo narrado.
Custo: **R$ 0,00** — tudo roda em serviços gratuitos.

## Como funciona

| Etapa | Serviço | Custo |
|---|---|---|
| Agendamento diário | GitHub Actions (`cron`) | grátis (repo público = minutos ilimitados) |
| Imagem do capítulo | arte já commitada em `docs/public/capitulo_N.jpg`, senão [Pollinations](https://pollinations.ai) (FLUX, sem API key) | grátis |
| Narração | gTTS (Google Translate TTS) | grátis |
| Vídeo | ffmpeg (Ken Burns sobre a imagem + narração), já instalado no runner | grátis |
| Entrega | Telegram Bot API | grátis |

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

## Limites conhecidos

- Vídeo: a narração usa os primeiros 3000 caracteres do capítulo (~4-5 min, ~17 MB).
  O bot do Telegram aceita no máximo 50 MB — arquivos maiores são pulados automaticamente.
- Texto: enviado em blocos de até 4000 caracteres (limite da API).
- Pollinations é grátis mas sem SLA; se falhar após 3 tentativas, o capítulo vai sem imagem nova.
