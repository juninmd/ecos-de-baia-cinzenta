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
      { text: 'Personagens', link: '/personagens' },
      { text: 'Sobre o Autor', link: '/sobre-o-autor' }
    ],
    sidebar: [
      {
        text: 'Parte I: A Chuva',
        items: [
          { text: 'Capítulo 1: Olhos de Vidro', link: '/capitulo-1' },
          { text: 'Capítulo 2: Náufragos de Concreto', link: '/capitulo-2' },
          { text: 'Capítulo 3: Teatro de Carne', link: '/capitulo-3' },
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
        text: 'Parte IV: O Jogo',
        items: [
          { text: 'Capítulo 14: Caçada ao Invisível', link: '/capitulo-14' },
          { text: 'Capítulo 15: Protocolo de Extermínio', link: '/capitulo-15' },
          { text: 'Capítulo 16: Zona Morta', link: '/capitulo-16' },
        ]
      },
      {
        text: 'Parte V: Ecos',
        items: [
          { text: 'Capítulo 17: O Ultimato', link: '/capitulo-17' },
          { text: 'Capítulo 18: A Queda', link: '/capitulo-18' },
          { text: 'Capítulo 19: O Código Morto', link: '/capitulo-19' },
          { text: 'Capítulo 20: Profanação', link: '/capitulo-20' },
          { text: 'Capítulo 21: Lar, Doce Inferno', link: '/capitulo-21' },
        ]
      },
      {
        text: 'Parte VI: A Torre',
        items: [
          { text: 'Capítulo 22: O Mapa da Alma', link: '/capitulo-22' },
          { text: 'Capítulo 23: Ratos e Reis', link: '/capitulo-23' },
          { text: 'Capítulo 24: A Galeria dos Deformados', link: '/capitulo-24' },
          { text: 'Capítulo 25: Elevador para o Inferno', link: '/capitulo-25' },
          { text: 'Capítulo 26: A Sala dos Espelhos', link: '/capitulo-26' },
          { text: 'Capítulo 27: O Pai, O Filho e a Máquina', link: '/capitulo-27' },
        ]
      },
      {
        text: 'Parte VII: O Apagão',
        items: [
          { text: 'Capítulo 28: A Voz na Caixa', link: '/capitulo-28' },
          { text: 'Capítulo 29: O Código de Lázaro', link: '/capitulo-29' },
          { text: 'Capítulo 30: Sacrifício de Sangue', link: '/capitulo-30' },
          { text: 'Capítulo 31: Ruptura Total', link: '/capitulo-31' },
          { text: 'Capítulo 32: Queda Livre', link: '/capitulo-32' },
          { text: 'Capítulo 33: Noite Eterna', link: '/capitulo-33' },
          { text: 'Capítulo 34: O Julgamento da Rua', link: '/capitulo-34' },
          { text: 'Capítulo 35: Calibre 12', link: '/capitulo-35' },
        ]
      },
      {
        text: 'Parte VIII: Cinzas',
        items: [
          { text: 'Capítulo 36: O Ninho da Serpente', link: '/capitulo-36' },
          { text: 'Capítulo 37: A Última Bala', link: '/capitulo-37' },
          { text: 'Capítulo 38: A Manhã Seguinte', link: '/capitulo-38' },
          { text: 'Capítulo 39: Dossiê Vance', link: '/capitulo-39' },
          { text: 'Capítulo 40: Traidores e Túmulos', link: '/capitulo-40' },
          { text: 'Capítulo 41: O Preço da Justiça', link: '/capitulo-41' },
          { text: 'Capítulo 42: Fantasmas da Cidade', link: '/capitulo-42' },
          { text: 'Capítulo 43: O Novo Departamento', link: '/capitulo-43' },
          { text: 'Capítulo 44: Ecos', link: '/capitulo-44' },
          { text: 'Capítulo 45: O Despertar', link: '/capitulo-45' },
        ]
      },
      {
        text: 'Parte IX: Dilúvio',
        items: [
          { text: 'Capítulo 46: A Maré Montante', link: '/capitulo-46' },
        ]
      },
      {
        text: 'Arquivos',
        items: [
          { text: 'Dossiê de Personagens', link: '/personagens' },
          { text: 'Lore do Livro', link: '/lore-do-livro' },
          { text: 'Sobre o Autor', link: '/sobre-o-autor' }
        ]
      }
    ],
    socialLinks: [
    ]
  }
}
