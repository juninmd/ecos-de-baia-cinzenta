module.exports = {
  title: "Ecos de Baía Cinzenta",
  description: "Um thriller noir cyberpunk em uma cidade onde a chuva nunca para.",
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
        ]
      },
      {
        text: 'Parte II: Ruído Branco',
        items: [
          { text: 'Capítulo 4: A Torre de Marfim', link: '/capitulo-4' },
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
