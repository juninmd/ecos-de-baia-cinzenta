import { fileURLToPath } from 'node:url'
import sidebar from './navigation/sidebar'
import { socialMeta } from './social-meta.mjs'
import { prefixCoverPath } from './cover-path.mjs'
import { stripDiagramHints } from './preload-hints.mjs'
﻿import { defineConfig } from 'vitepress'
import { withMermaid } from 'vitepress-plugin-mermaid'

// withMermaid envolve o config para que os blocos ```mermaid de docs/arcos.md
// virem diagramas. Sem ele, o VitePress renderiza tudo como bloco de código.
// O destino informa o prefixo para servir também em /<nome-do-repo>/.
const base = process.env.VITEPRESS_BASE || '/'

export default withMermaid(defineConfig({
  // Dossiês editoriais contêm o desfecho do livro e notas de revisão. Sem esta
  // lista, o VitePress publica todo .md de docs/ e eles viram páginas
  // alcançáveis por URL, mesmo sem link no menu.
  srcExclude: [
    'comparativo_literario.md',
    'parecer_revisao.md',
    'plano_personagens.md',
    'auditoria_repeticao.md',
    'auditoria_tiques.md',
  ],
  buildEnd: ({ outDir }) => stripDiagramHints(outDir),
  transformPageData: (pageData) => {
    const image = pageData.frontmatter.image
    if (typeof image === 'string') pageData.frontmatter.image = prefixCoverPath(image, base)
  },
  base,
  vite: {
    resolve: {
      alias: [
        { find: /^vitepress-plugin-mermaid\/Mermaid\.vue$/, replacement: fileURLToPath(new URL('./theme/MermaidLazy.ts', import.meta.url)) },
      ],
    },
  },
  lang: 'pt-BR',
  title: "Ecos de Baía Cinzenta",
  description: "Um thriller noir cyberpunk em uma cidade onde a chuva nunca para.",
  transformHead: socialMeta,
  head: [
    ['link', { rel: 'preconnect', href: 'https://fonts.googleapis.com' }],
    ['link', { rel: 'preconnect', href: 'https://fonts.gstatic.com', crossorigin: '' }],
    ['link', { href: 'https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500&family=Merriweather:ital,wght@0,300;0,400;0,700;1,300&family=Orbitron:wght@400;500;600;700&family=Playfair+Display:wght@700&family=Rajdhani:wght@400;500;600;700&display=swap', rel: 'stylesheet' }],
    ['meta', { name: 'theme-color', content: '#0a0a0f' }],
    ['meta', { name: 'apple-mobile-web-app-capable', content: 'yes' }],
    ['meta', { name: 'apple-mobile-web-app-status-bar-style', content: 'black-translucent' }],
    ['link', { rel: 'manifest', href: `${base}manifest.json` }],
    ['link', { rel: 'icon', type: 'image/png', sizes: '192x192', href: `${base}icons/icon-192x192.png` }],
    ['link', { rel: 'apple-touch-icon', sizes: '180x180', href: `${base}icons/icon-192x192.png` }],
    ['script', { id: 'register-sw' }, `
      if ('serviceWorker' in navigator) {
        window.addEventListener('load', async () => {
          try {
            await navigator.serviceWorker.register(${JSON.stringify(`${base}sw.js`)});
            console.log('✓ Service Worker registered');
          } catch (err) {
            console.error('✗ SW registration failed:', err);
          }
        });
      }
    `]
  ],
  rewrites: {
    "public/:page.md": ":page.md"
  },
  // 416 ilustrações de capítulo pesam centenas de KB: carregar só o que entra na tela
  markdown: {
    image: { lazyLoading: true }
  },
  themeConfig: {
    nav: [
      { text: 'Home', link: '/' },
      { text: 'Ler Agora', link: '/capitulo-1' },
      { text: 'Cronologia', link: '/cronologia' },
      { text: 'Personagens', link: '/personagens' },
      { text: 'Sobre o Autor', link: '/sobre-o-autor' }
    ],
    sidebar: sidebar,
    docFooter: { prev: 'Capítulo anterior', next: 'Próximo capítulo' },
    outline: { label: 'Nesta página' },
    returnToTopLabel: 'Voltar ao topo',
    sidebarMenuLabel: 'Menu',
    darkModeSwitchLabel: 'Tema',
    lightModeSwitchTitle: 'Mudar para o tema claro',
    darkModeSwitchTitle: 'Mudar para o tema escuro',
    socialLinks: [
    ]
  },
  mermaid: {
    theme: 'dark',
    themeVariables: {
      primaryColor: '#1b2430',
      primaryTextColor: '#e8e6e3',
      lineColor: '#7a8b99',
      fontFamily: 'Rajdhani, sans-serif',
    },
  }
}))
