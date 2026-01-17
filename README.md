# Ecos de Baía Cinzenta

> *Um thriller noir cyberpunk sobre memórias roubadas, chuva ácida e a busca pela verdade em uma cidade que nunca dorme.*

![Banner do Projeto](/public/banner_placeholder.jpg)
*(Nota: Adicionar banner conceitual aqui)*

## 📖 Sobre o Projeto

**Ecos de Baía Cinzenta** é um livro interativo sendo desenvolvido como um site estático usando [VitePress](https://vitepress.dev/). A narrativa combina elementos clássicos de *Film Noir* com a estética e temáticas *Cyberpunk*.

A história acompanha **Gabriel "Gabo" Moretti**, um detetive da Divisão de Casos Esquecidos, enquanto ele desvenda uma conspiração que envolve megacorporações, drogas de realidade virtual e serial killers teatrais.

## 🏙️ O Universo

O cenário é **Baía Cinzenta**, uma metrópole costeira assolada por chuva perpétua e desigualdade extrema.
*   **Aeterna Corp:** A empresa que controla tudo, da energia à saúde.
*   **Droga Lázaro:** O escapismo definitivo que custa a alma do usuário.
*   **O Taxidermista:** Um serial killer que transforma vítimas em "arte".

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

## 📂 Estrutura do Projeto

*   `docs/`: Contém todos os arquivos Markdown (capítulos e lore).
*   `docs/.vitepress/`: Configurações do tema e do site.
*   `docs/public/`: Imagens e ativos estáticos.

## ✍️ Autores

*   **J.R.A.C.N** - Autor Original
*   **Jules** - Co-autor e Arquiteto de Software (AI Agent)

## 📄 Licença

Todos os direitos reservados ao autor original.
