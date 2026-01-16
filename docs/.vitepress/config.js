module.exports = {
  title: "Ecos de Baía Cinzenta",
  description: "Um thriller noir cyberpunk em uma cidade onde a chuva nunca para.",
  head: [
    ['link', { rel: 'preconnect', href: 'https://fonts.googleapis.com' }],
    ['link', { rel: 'preconnect', href: 'https://fonts.gstatic.com', crossorigin: '' }],
    ['link', { href: 'https://fonts.googleapis.com/css2?family=Merriweather:ital,wght@0,300;0,400;0,700;1,300&family=Playfair+Display:wght@700&display=swap', rel: 'stylesheet' }]
  ],
  themeConfig: {
    nav: [
      { text: 'Home', link: '/' },
      { text: 'Ler Agora', link: '/capitulo-1' },
      { text: 'Personagens', link: '/personagens' }
    ],
    sidebar: [
      {
        text: 'Parte I: A Chuva',
        items: [
          { text: 'Capítulo 1: Olhos de Vidro', link: '/capitulo-1' },
          { text: 'Capítulo 2: Náufragos de Concreto', link: '/capitulo-2' },
          { text: 'Capítulo 3: O Fantasma da Máquina', link: '/capitulo-3' },
          { text: 'Capítulo 4: A Torre de Marfim', link: '/capitulo-4' },
        ]
      },
      {
        text: 'Parte II: Ruído Branco',
        items: [
          { text: 'Capítulo 5: A Capela dos Esquecidos', link: '/capitulo-5' },
          { text: 'Capítulo 6: O Coração da Tempestade', link: '/capitulo-6' },
          { text: 'Capítulo 7: O Fim do Silêncio', link: '/capitulo-7' },
        ]
      },
      {
        text: 'Parte III: A Rede',
        items: [
          { text: 'Capítulo 8: Ressaca Digital', link: '/capitulo-8' },
          { text: 'Capítulo 9: Feed Infinito', link: '/capitulo-9' },
          { text: 'Capítulo 10: A Fábrica de Sorrisos', link: '/capitulo-10' },
          { text: 'Capítulo 11: Filtros de Realidade', link: '/capitulo-11' },
          { text: 'Capítulo 12: Cancelamento', link: '/capitulo-12' },
          { text: 'Capítulo 13: Shadowban', link: '/capitulo-13' },
        ]
      },
      {
        text: 'Arquivos',
        items: [
          { text: 'Dossiê de Personagens', link: '/personagens' }
        ]
      }
    ],
    socialLinks: [
    ]
  }
}
