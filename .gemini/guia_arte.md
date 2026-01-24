
Este documento estabelece o fluxo de trabalho ("workflow") e os padrões visuais para a geração de imagens do universo de **Baía Cinzenta**.

## Identidade Visual

A estética do projeto é definida por três pilares:

1.  **Neo-Noir**: Sombras profundas, alto contraste (chiaroscuro), chuva constante, ambientes opressivos.
2.  **Cyberpunk Decadente**: Tecnologia avançada misturada com ruína urbana ("High Tech, Low Life"). Cabos expostos, neon refletindo em poças de óleo, ferrugem.
3.  **Realismo Cinematográfico**: Texturas detalhadas (pele, tecido, metal), iluminação dramática, enquadramentos de cinema.

---

## Ferramenta de Geração de Prompts

Para garantir a consistência dos personagens e do estilo, criamos uma ferramenta automatizada localizada em `tools/prompt_generator.py`.

### Como Usar

Execute o script via terminal na raiz do projeto:

```bash
python3 tools/prompt_generator.py --char [NOME] --action "[AÇÃO]" --setting "[CENÁRIO]" --style [ESTILO]
```

**Argumentos:**
*   `--char`: Nome do personagem (ex: `gabo`, `val`, `nise`, `marco`).
*   `--action`: Descrição da ação em inglês (para melhor compatibilidade com modelos de IA).
*   `--setting`: Descrição do ambiente.
*   `--style`: `noir` (padrão), `cyberpunk`, `action`, `portrait`.

### Exemplo Prático (Capítulo 77)

**Cena:** Gabo confrontando o técnico de enfermagem no quarto do hospital.

```bash
python3 tools/prompt_generator.py --char gabo --action "aiming his Glock pistol at a nurse technician" --setting "dimly lit hospital room" --style action
```

**Saída Gerada:**
> 30 years old man, detective, rugged, messy dark hair, full beard with gray patches, deep brown eyes with dark circles, tired expression, wearing a beige trench coat with soot stains over a crumpled white shirt, athletic build but exhausted, noir atmosphere. aiming his Glock pistol at a nurse technician. Located in dimly lit hospital room. Dynamic action shot, motion blur, intense expression, cinematic angle, debris flying, dramatic lighting. Best quality, ultra detailed, 8k, ray tracing.

---

## Workflow Recomendado (Flow)

Para obter os melhores resultados mantendo a identidade visual, recomendamos o uso de modelos baseados em **Flux.1** ou **Midjourney v6**, que possuem alta aderência a prompts complexos.

### Passo a Passo

1.  **Identifique a Cena**: Leia o capítulo e escolha um momento chave.
2.  **Gere o Prompt**: Use o script `tools/prompt_generator.py` para criar a base textual.
3.  **Ajuste Fino (Opcional)**: Adicione detalhes específicos da cena se necessário.
4.  **Configurações de Geração**:
    *   **Proporção (Aspect Ratio)**: 16:9 (Cinematográfico) ou 2:3 (Retrato de Personagem).
    *   **Seed (Semente)**: Se você encontrar uma geração perfeita para um personagem, anote o número da "Seed". Reutilize essa Seed em prompts futuros para manter traços faciais similares (embora mude a pose).
    *   **Image-to-Image (Img2Img)**: Para manter consistência absoluta, use uma imagem aprovada do personagem como referência (Image Prompt) com peso médio (0.5 a 0.8).

### Tokens de Personagens (Referência)

O script já inclui estes tokens automaticamente, mas aqui está a referência para uso manual:

*   **Gabo**: `beige trench coat`, `messy dark hair`, `full beard`, `tired eyes`, `glock`.
*   **Val**: `pixie cut pink and blue hair`, `silver cybernetic eyes`, `LED cheek implants`, `leather jacket`, `cyberdeck`.
*   **Aria**: `holographic girl`, `platinum blonde`, `heterochromatic eyes`, `glowing barcode`.

---

## Exemplos de Prompts (Capítulo 77)

Aqui estão prompts prontos para uso baseados no capítulo recente "Anjos da Morte":

### 1. Gabo em Ação
> 30 years old man, detective, rugged, messy dark hair, full beard with gray patches, deep brown eyes with dark circles, tired expression, wearing a beige trench coat with soot stains over a crumpled white shirt, athletic build but exhausted, noir atmosphere. aiming his Glock pistol at a nurse technician. Located in dimly lit hospital room, sterile environment. Dynamic action shot, motion blur, intense expression, cinematic angle, debris flying, dramatic lighting. Best quality, ultra detailed, 8k, ray tracing.

### 2. Val Hackeando
> 23 years old woman, cyberpunk hacker, small slender build, pixie cut hair with holographic pink and blue tint, silver cybernetic eyes, LED implants on cheekbones, barcode tattoo on neck, wearing leather jacket and cargo pants, holding a futuristic deck, cyberpunk aesthetic. analyzing holographic data on her deck. Located in hospital corridor, cold artificial light. Cyberpunk atmosphere, neon lights (blue and pink), fog, technological debris, holographic advertisements, metallic textures, futuristic, detailed. Best quality, ultra detailed, 8k, ray tracing.

### 3. Dra. Nise no Necrotério
> 65 years old woman, doctor, curved posture, white hair in messy bun, wearing a stained medical lab coat over comfortable clothes, kind wise eyes, underground clinic setting. examining a body with a scanner. Located in morgue, dark and cold. Neo-noir style, heavy shadows, high contrast, dramatic chiaroscuro lighting, rain, wet streets, gloom, cinematic 8k, masterpiece, hyperrealistic texture. Best quality, ultra detailed, 8k, ray tracing.
