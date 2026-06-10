# Ecos de Baía Cinzenta

<img width="1365" height="768" alt="image" src="https://github.com/user-attachments/assets/9a99341a-9473-49bc-a1d8-75641ec84085" />

> *Um thriller noir cyberpunk sobre memórias roubadas, chuva ácida e a busca pela verdade em uma cidade que nunca dorme.*

🔴 **[ACESSE O LIVRO ONLINE AQUI](https://ecos-de-baia-cinzenta.netlify.app/)** 🔴

![Banner do Projeto](/public/banner_placeholder.jpg)
*(Nota: Adicionar banner conceitual aqui)*

## 📖 Sobre o Projeto

**Ecos de Baía Cinzenta** é um livro interativo sendo desenvolvido como um site estático usando [VitePress](https://vitepress.dev/). A narrativa combina elementos clássicos de *Film Noir* com a estética e temáticas *Cyberpunk*.

Você pode ler a versão mais recente online em: **[ecos-de-baia-cinzenta.netlify.app](https://ecos-de-baia-cinzenta.netlify.app/)**

A história acompanha **Gabriel "Gabo" Moretti**, um detetive da Divisão de Casos Esquecidos, em uma investigação que começa no noir policial e escala para uma guerra pela alma de Baía Cinzenta — entre megacorporações, colapso tecnológico, cultos biológicos e uma nova ordem autoritária.

Para um panorama completo dos arcos e eventos principais, consulte a [Cronologia da Ópera](docs/cronologia.md).

## 🤖 O Experimento

Este projeto é um laboratório vivo para medir a capacidade criativa de Inteligência Artificial.

*   **O Processo:** Diariamente, o agente **Jules** abre um Pull Request com um novo capítulo para a história.
*   **A Supervisão:** Todo o conteúdo é revisado e supervisionado por **Antonio Carlos**.
*   **O Objetivo:** Avaliar se uma IA consegue manter consistência de lore, progressão de personagens e tensão dramática em uma saga de longa duração, capítulo após capítulo.

## 🎧 Funcionalidades de Leitura Imersiva

Para melhorar a acessibilidade e a imersão, o projeto conta com um **Player de Áudio (TTS)** personalizado:

*   **Leitura Contínua:** Ao ativar o player, o sistema narra o capítulo atual e avança automaticamente para o próximo após uma breve pausa.
*   **Navegação por Parágrafo:** Cada parágrafo possui um marcador oculto (visível ao passar o mouse ou clicar) que permite iniciar a leitura a partir daquele ponto exato.
*   **Acompanhamento Visual:**
    *   **Barra de Progresso:** Indica quanto do capítulo já foi narrado.
    *   **Destaque de Leitura:** O parágrafo que está sendo lido é destacado visualmente para facilitar o acompanhamento.
*   **Controles:** Pausa, Play, Stop, ajuste de velocidade (0.8x a 1.5x) e seleção de vozes (pt-BR).

## 📱 App Android & PWA

O livro está disponível como **Progressive Web App (PWA)** e pode ser instalado em smartphones:

*   **Instalação rápida:** Acesse o site no Chrome/Edge mobile → Menu → "Adicionar à tela inicial"
*   **Funciona offline:** Service Worker mantém cache para leitura sem internet
*   **Atualizações automáticas:** Novo conteúdo aparece automaticamente quando publicado
*   **App nativo:** Pode ser compilado como APK Android via Capacitor

📖 **[Ver guia completo de instalação](ANDROID.md)**

## 💻 Terminal do Sistema

Pressione **`Ctrl + K`** ou clique no botão flutuante `_>` para acessar o **Terminal Lázaro**, uma interface CLI que permite explorar segredos do universo, verificar status de personagens e acessar arquivos confidenciais.

Comandos disponíveis:
- `status`: Exibe o status do sistema.
- `personagens`: Lista o dossiê dos envolvidos.
- `genesis`: [ACESSO RESTRITO]
- `bercario`: [ACESSO RESTRITO - PERIGO BIOLÓGICO]

## 🏙️ O Universo

O cenário é **Baía Cinzenta**, uma metrópole costeira assolada por chuva perpétua e desigualdade extrema.
*   **Aeterna Corp:** A empresa que controla tudo, da energia à saúde.
*   **Droga Lázaro:** O escapismo definitivo que custa a alma do usuário.
*   **O Taxidermista:** Um serial killer que transforma vítimas em "arte".
*   **O Vazio (Parte XIV):** A nova realidade da cidade, onde o silêncio reina e a tecnologia falha.

Para mais detalhes sobre as regras do mundo, consulte a [Constituição do Universo (Lore)](docs/lore-do-livro.md).

## 🚀 Como Executar Localmente

Este projeto utiliza Node.js e VitePress.

### Pré-requisitos
*   Node.js (versão 18 ou superior)
*   npm

### Instalação

1.  Clone o repositório:
    ```bash
    git clone https://github.com/seu-usuario/ecos-baia-cinzenta.git
    cd ecos-baia-cinzenta
    ```

2.  Instale as dependências:
    ```bash
    npm install
    ```

3.  Inicie o servidor de desenvolvimento:
    ```bash
    npm run docs:dev
    ```
    O site estará acessível em `http://localhost:5173`.

### Build para Produção

Para gerar os arquivos estáticos para deploy:

```bash
npm run docs:build
```
Os arquivos serão gerados na pasta `docs/.vitepress/dist`.

## 🎬 Video Generation

Este projeto inclui um pipeline automatizado de geração de vídeos cinematográficos para cada capítulo usando ferramentas 100% open source.

### Stack Tecnológico
- **gTTS + pydub**: Narração em PT-BR
- **FFmpeg**: Composição e efeitos visuais
- **Wan2.2 (HF Inference)**: Geração text-to-video
- **Modo image2video local**: Vídeo curto com zoom cinematográfico a partir da capa do capítulo

### Geração Automática
Vídeos são gerados automaticamente via GitHub Actions quando novos capítulos são adicionados ao repositório. Os vídeos finalizados são salvos em `docs/public/videos/`.

### Teste Local

### Alternativas para manter aparência dos personagens
Quando a consistência visual cair entre capítulos, priorize estes fluxos:
- **SDXL img2img com referência do personagem** (`scripts/local_art_gen.py`): usa foto base + prompt para preservar traços.
- **LoRA/DreamBooth por personagem principal**: melhora identidade em cenas novas.
- **IP-Adapter/ControlNet Reference** no Automatic1111/ComfyUI: preserva rosto e silhueta com mais controle.
- **Pós-processo de face swap leve** (apenas ajuste fino), mantendo iluminação original.

#### Pré-requisitos
- Python 3.12+
- ffmpeg (para encoding de vídeo)

#### Setup
```bash
# Instalar uv (gerenciador de pacotes Python)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Instalar dependências
uv pip install -r requirements-dev.txt
uv pip install -r requirements-art.txt

# Configurar ambiente
python scripts/setup_assets.py
```

#### Gerar Vídeo
```bash
# Gerar vídeo para um capítulo específico
python -m scripts.video_gen.main --chapter 1 --mode auto

# Forçar text-to-video (Wan2.2)
python -m scripts.video_gen.main --chapter 1 --mode text2video

# Gerar vídeo curto da imagem de capa (image2video)
python -m scripts.video_gen.main --chapter 1 --mode image2video

# Processar todos os capítulos
python -m scripts.video_gen.main --all --mode auto

# Output: docs/public/videos/capitulo_*.mp4
```

#### Testes
```bash
# Executar testes unitários
pytest tests/test_video_gen.py -v
```

## 📂 Estrutura do Projeto

*   `docs/`: Contém todos os arquivos Markdown (capítulos e lore).
*   `docs/.vitepress/`: Configurações do tema e do site.
*   `docs/public/`: Imagens e ativos estáticos.

## ✍️ Autores

*   **Antonio Carlos (J.R.A.C.N)** - Autor Original e Supervisor do Projeto
*   **Jules** - Co-autor e Arquiteto de Software (AI Agent)
