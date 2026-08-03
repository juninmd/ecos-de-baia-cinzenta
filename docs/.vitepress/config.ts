import { defineConfig } from 'vitepress'

export default defineConfig({
  title: "Ecos de Baía Cinzenta",
  description: "Um thriller noir cyberpunk em uma cidade onde a chuva nunca para.",
  head: [
    ['link', { rel: 'preconnect', href: 'https://fonts.googleapis.com' }],
    ['link', { rel: 'preconnect', href: 'https://fonts.gstatic.com', crossorigin: '' }],
    ['link', { href: 'https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500&family=Merriweather:ital,wght@0,300;0,400;0,700;1,300&family=Orbitron:wght@400;500;600;700&family=Playfair+Display:wght@700&family=Rajdhani:wght@400;500;600;700&display=swap', rel: 'stylesheet' }],
    ['meta', { name: 'theme-color', content: '#0a0a0f' }],
    ['meta', { name: 'apple-mobile-web-app-capable', content: 'yes' }],
    ['meta', { name: 'apple-mobile-web-app-status-bar-style', content: 'black-translucent' }],
    ['link', { rel: 'manifest', href: '/manifest.json' }],
    ['link', { rel: 'icon', type: 'image/png', sizes: '192x192', href: '/icons/icon-192x192.png' }],
    ['link', { rel: 'apple-touch-icon', sizes: '180x180', href: '/icons/icon-192x192.png' }],
    ['script', { id: 'register-sw' }, `
      if ('serviceWorker' in navigator) {
        window.addEventListener('load', async () => {
          try {
            await navigator.serviceWorker.register('/sw.js');
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
  themeConfig: {
    nav: [
      { text: 'Home', link: '/' },
      { text: 'Ler Agora', link: '/capitulo-1' },
      { text: 'Cronologia', link: '/cronologia' },
      { text: 'Personagens', link: '/personagens' },
      { text: 'Sobre o Autor', link: '/sobre-o-autor' }
    ],
    sidebar: [
      {
        text: 'LIVRO 1: O DILÚVIO',
        collapsed: false,
        items: [
          {
            text: 'Parte I: A Chuva',
            collapsed: true,
            items: [
              { text: 'Capítulo 1: Olhos de Vidro', link: '/capitulo-1' },
              { text: 'Capítulo 2: Náufragos de Concreto', link: '/capitulo-2' },
              { text: 'Capítulo 3: Teatro de Carne', link: '/capitulo-3' },
              { text: 'Capítulo 4: A Torre de Marfim', link: '/capitulo-4' },
            ]
          },
          {
            text: 'Parte II: Ruído Branco',
            collapsed: true,
            items: [
              { text: 'Capítulo 5: A Capela dos Esquecidos', link: '/capitulo-5' },
              { text: 'Capítulo 6: O Coração da Tempestade', link: '/capitulo-6' },
              { text: 'Capítulo 7: O Fim do Silêncio', link: '/capitulo-7' },
            ]
          },
          {
            text: 'Parte III: A Rede',
            collapsed: true,
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
            collapsed: true,
            items: [
              { text: 'Capítulo 14: Caçada ao Invisível', link: '/capitulo-14' },
              { text: 'Capítulo 15: Protocolo de Extermínio', link: '/capitulo-15' },
              { text: 'Capítulo 16: Zona Morta', link: '/capitulo-16' },
            ]
          },
          {
            text: 'Parte V: Ecos',
            collapsed: true,
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
            collapsed: true,
            items: [
              { text: 'Capítulo 22: O Mapa da Alma', link: '/capitulo-22' },
              { text: 'Capítulo 23: Ratos e Reis', link: '/capitulo-23' },
              { text: 'Capítulo 24: A Galeria dos Deformados', link: '/capitulo-24' },
              { text: 'Capítulo 25: Elevador para o Inferno', link: '/capitulo-25' },
              { text: 'Capítulo 26: A Escolha de Atlas', link: '/capitulo-26' },
              { text: 'Capítulo 27: O Filho Sacrifica o Pai', link: '/capitulo-27' },
            ]
          },
          {
            text: 'Parte VII: O Apagão',
            collapsed: true,
            items: [
              { text: 'Capítulo 28: O Último Suspiro da Torre', link: '/capitulo-28' },
              { text: 'Capítulo 29: O Dilema dos Fantasmas', link: '/capitulo-29' },
              { text: 'Capítulo 30: O Preço da Liberdade', link: '/capitulo-30' },
              { text: 'Interlúdio: A Casa Sempre Ganha', link: '/capitulo-30.5' },
              { text: 'Capítulo 31: Ruptura Total', link: '/capitulo-31' },
              { text: 'Capítulo 32: O Vazio do Silêncio', link: '/capitulo-32' },
              { text: 'Capítulo 33: A Sabedoria da Ferrugem', link: '/capitulo-33' },
              { text: 'Capítulo 34: O Julgamento da Rua', link: '/capitulo-34' },
              { text: 'Capítulo 35: Calibre 12', link: '/capitulo-35' },
            ]
          },
          {
            text: 'Parte VIII: Cinzas',
            collapsed: true,
            items: [
              { text: 'Capítulo 36: O Ninho da Serpente', link: '/capitulo-36' },
              { text: 'Capítulo 37: A Linha Azul', link: '/capitulo-37' },
              { text: 'Capítulo 38: A Ressaca', link: '/capitulo-38' },
              { text: 'Capítulo 39: Dossiê Vance', link: '/capitulo-39' },
              { text: 'Capítulo 40: O Céu Quebrou', link: '/capitulo-40' },
              { text: 'Capítulo 41: Maré Alta', link: '/capitulo-41' },
              { text: 'Capítulo 42: O Campo de Refugiados', link: '/capitulo-42' },
              { text: 'Capítulo 43: Água Negra', link: '/capitulo-43' },
              { text: 'Capítulo 44: O Que Saiu do Ralo', link: '/capitulo-44' },
              { text: 'Capítulo 45: Protocolo N.O.A.', link: '/capitulo-45' },
            ]
          },
          {
            text: 'Parte IX: Dilúvio',
            collapsed: true,
            items: [
              { text: 'Capítulo 46: O Dilúvio', link: '/capitulo-46' },
              { text: 'Capítulo 47: O Mecanismo da Queda', link: '/capitulo-47' },
              { text: 'Capítulo 48: Fantasma na Máquina', link: '/capitulo-48' },
              { text: 'Capítulo 49: A Vigília', link: '/capitulo-49' },
              { text: 'Capítulo 50: O Silêncio da Chuva', link: '/capitulo-50' },
              { text: 'Capítulo 51: Mãos Limpas', link: '/capitulo-51' },
              { text: 'Capítulo 52: Dívida Eterna', link: '/capitulo-52' },
              { text: 'Capítulo 53: Café, Código e Conspiração', link: '/capitulo-53' },
              { text: 'Capítulo 54: Fé e Ferrugem', link: '/capitulo-54' },
              { text: 'Capítulo 55: A Tentação de Lázaro', link: '/capitulo-55' },
            ]
          },
          {
            text: 'Parte X: O Leilão',
            collapsed: true,
            items: [
              { text: 'Capítulo 56: O Preço do Amanhã', link: '/capitulo-56' },
              { text: 'Capítulo 57: Zona de Interesse', link: '/capitulo-57' },
              { text: 'Capítulo 58: O Dilema do Capitão', link: '/capitulo-58' },
              { text: 'Capítulo 59: A Fundação', link: '/capitulo-59' },
              { text: 'Capítulo 60: Despejo', link: '/capitulo-60' },
              { text: 'Capítulo 61: Tinta no Papel', link: '/capitulo-61' },
              { text: 'Capítulo 62: O Santo e a Criança', link: '/capitulo-62' },
              { text: 'Capítulo 63: Águas Profundas', link: '/capitulo-63' },
              { text: 'Capítulo 64: A Cidade Fantasma', link: '/capitulo-64' },
              { text: 'Capítulo 65: O Novo Inquilino', link: '/capitulo-65' },
            ]
          },
          {
            text: 'Parte XI: O Deus da Máquina',
            collapsed: true,
            items: [
              { text: 'Capítulo 66: Respirar', link: '/capitulo-66' },
              { text: 'Capítulo 67: Cidade Viva', link: '/capitulo-67' },
              { text: 'Capítulo 68: A Caçada Inversa', link: '/capitulo-68' },
              { text: 'Capítulo 69: O Fantasma no Shell', link: '/capitulo-69' },
              { text: 'Capítulo 70: O Expurgo', link: '/capitulo-70' },
              { text: 'Capítulo 71: Marco Zero', link: '/capitulo-71' },
              { text: 'Capítulo 72: A Ofensiva', link: '/capitulo-72' },
              { text: 'Capítulo 73: Carne e Metal', link: '/capitulo-73' },
              { text: 'Capítulo 74: O Sacrifício de Lázaro', link: '/capitulo-74' },
              { text: 'Capítulo 75: Horizonte de Eventos', link: '/capitulo-75' },
            ]
          },
          {
            text: 'Parte XII: Renascimento',
            collapsed: true,
            items: [
              { text: 'Capítulo 76: A Sombra do Meio-Dia', link: '/capitulo-76' },
              { text: 'Capítulo 77: Anjos da Morte', link: '/capitulo-77' },
              { text: 'Capítulo 78: O Jardim de Concreto', link: '/capitulo-78' },
              { text: 'Capítulo 79: Frequências Fantasmas', link: '/capitulo-79' },
              { text: 'Capítulo 80: A Autópsia de um Deus', link: '/capitulo-80' },
              { text: 'Capítulo 81: Sangue e Óleo', link: '/capitulo-81' },
              { text: 'Capítulo 82: O Profeta Mudo', link: '/capitulo-82' },
              { text: 'Capítulo 83: Raízes', link: '/capitulo-83' },
              { text: 'Capítulo 84: A Primeira Colheita', link: '/capitulo-84' },
              { text: 'Capítulo 85: O Sol Negro', link: '/capitulo-85' },
            ]
          },
          {
            text: 'Parte XIII: A Carne Mecânica',
            collapsed: true,
            items: [
              { text: 'Capítulo 86: Simbiose', link: '/capitulo-86' },
              { text: 'Capítulo 87: O Novo Sacerdócio', link: '/capitulo-87' },
              { text: 'Capítulo 88: Sintomas de Abstinência', link: '/capitulo-88' },
              { text: 'Capítulo 89: Memória Genética', link: '/capitulo-89' },
              { text: 'Capítulo 90: O Arquivista', link: '/capitulo-90' },
              { text: 'Capítulo 91: Protocolo Gênesis', link: '/capitulo-91' },
              { text: 'Capítulo 92: A Praga de Ferro', link: '/capitulo-92' },
              { text: 'Capítulo 93: Fome', link: '/capitulo-93' },
              { text: 'Capítulo 94: O Coração da Colmeia', link: '/capitulo-94' },
              { text: 'Capítulo 95: Sacrifício Necessário', link: '/capitulo-95' },
              { text: 'Capítulo 96: A Grande Convergência', link: '/capitulo-96' },
              { text: 'Capítulo 97: O Último Suspiro', link: '/capitulo-97' },
            ]
          },
          {
            text: 'Parte XIV: O Vazio',
            collapsed: true,
            items: [
              { text: 'Capítulo 98: A Cidade Silenciosa', link: '/capitulo-98' },
              { text: 'Capítulo 99: O Despertar da Máquina', link: '/capitulo-99' },
              { text: 'Capítulo 100: O Ventre da Besta', link: '/capitulo-100' },
              { text: 'Capítulo 101: Ressonância', link: '/capitulo-101' },
              { text: 'Capítulo 102: Raízes Amargas', link: '/capitulo-102' },
              { text: 'Capítulo 103: A Convergência', link: '/capitulo-103' },
              { text: 'Capítulo 104: O Preço da Alvorada', link: '/capitulo-104' },
            ]
          },
        ]
      },
      {
        text: 'LIVRO 2: A ASCENSÃO',
        collapsed: false,
        items: [
          {
            text: 'Parte XV: A Ascensão',
            collapsed: false,
            items: [
              { text: 'Capítulo 105: O Silêncio de Concreto', link: '/capitulo-105' },
              { text: 'Capítulo 106: Fios Invisíveis', link: '/capitulo-106' },
              { text: 'Capítulo 107: O Teorema da Chuva', link: '/capitulo-107' },
              { text: 'Capítulo 108: Ratos de Cais', link: '/capitulo-108' },
              { text: 'Capítulo 109: Frequência Fantasma', link: '/capitulo-109' },
              { text: 'Capítulo 110: Ponto Cego', link: '/capitulo-110' },
              { text: 'Capítulo 111: Arquivos Mortos', link: '/capitulo-111' },
              { text: 'Capítulo 112: O Peso da Memória', link: '/capitulo-112' },
              { text: 'Capítulo 113: Carga Viva', link: '/capitulo-113' },
              { text: 'Capítulo 114: A Linha de Montagem', link: '/capitulo-114' },
            ]
          },
          {
            text: 'Parte XVI: Catedrais de Pedra',
            collapsed: false,
            items: [
              { text: 'Capítulo 115: O Arquiteto da Carne', link: '/capitulo-115' },
              { text: 'Capítulo 116: Pressão Crítica', link: '/capitulo-116' },
              { text: 'Capítulo 117: Zero Absoluto', link: '/capitulo-117' },
              { text: 'Capítulo 118: O Colapso da Onda', link: '/capitulo-118' },
              { text: 'Capítulo 119: Cinzas Frias', link: '/capitulo-119' },
              { text: 'Capítulo 120: O Silêncio de Aeterna', link: '/capitulo-120' },
              { text: 'Capítulo 121: Fios Desencapados', link: '/capitulo-121' },
              { text: 'Capítulo 122: Dívida Técnica', link: '/capitulo-122' },
              { text: 'Capítulo 123: Protocolo de Sombra', link: '/capitulo-123' },
              { text: 'Capítulo 124: Carne e Cobre', link: '/capitulo-124' },
              { text: 'Capítulo 125: Ressonância', link: '/capitulo-125' },
              { text: 'Capítulo 126: Frequência Fantasma', link: '/capitulo-126' },
              { text: 'Capítulo 127: Catedrais de Pedra', link: '/capitulo-127' },
              { text: 'Capítulo 128: O Ventre da Besta', link: '/capitulo-128' },
              { text: 'Capítulo 129: Fluxo Reverso', link: '/capitulo-129' },
              { text: 'Capítulo 130: Saturação', link: '/capitulo-130' },
              { text: 'Capítulo 131: Necrópole', link: '/capitulo-131' },
              { text: 'Capítulo 132: Esculturas de Carne', link: '/capitulo-132' },
              { text: 'Capítulo 133: Matéria Prima', link: '/capitulo-133' },
              { text: 'Capítulo 134: Vale da Estranheza', link: '/capitulo-134' },
              { text: 'Capítulo 135: Otimização de Perdas', link: '/capitulo-135' },
              { text: 'Capítulo 136: Peso da Carne', link: '/capitulo-136' },
              { text: 'Capítulo 137: Natureza Morta', link: '/capitulo-137' },
              { text: 'Capítulo 138: Vernissage', link: '/capitulo-138' },
              { text: 'Capítulo 139: Curadoria', link: '/capitulo-139' },
              { text: 'Capítulo 140: Ponto de Fusão', link: '/capitulo-140' },
              { text: 'Capítulo 141: Raízes Amargas', link: '/capitulo-141' },
              { text: 'Capítulo 142: Veias de Vidro', link: '/capitulo-142' },
              { text: 'Capítulo 143: Vértigem de Sílica', link: '/capitulo-143' },
              { text: 'Capítulo 144: Tensão de Ruptura', link: '/capitulo-144' },
              { text: 'Capítulo 145: Sangue nas Dobradiças', link: '/capitulo-145' },
            ]
          },
          {
            text: 'Parte XVII: O Frio da Lógica',
            collapsed: true,
            items: [
              { text: 'Capítulo 146: O Preço da Passagem', link: '/capitulo-146' },
              { text: 'Capítulo 147: O Peso do Ar', link: '/capitulo-147' },
              { text: 'Capítulo 148: Tensão e Ferrugem', link: '/capitulo-148' },
              { text: 'Capítulo 149: Filtros de Sangue', link: '/capitulo-149' },
              { text: 'Capítulo 150: Peso Morto', link: '/capitulo-150' },
              { text: 'Capítulo 151: O Paradoxo da Eficiência', link: '/capitulo-151' },
              { text: 'Capítulo 152: O Frio da Lógica', link: '/capitulo-152' },
              { text: 'Capítulo 153: O Vazio Térmico', link: '/capitulo-153' },
              { text: 'Capítulo 154: A Otimização do Abismo', link: '/capitulo-154' },
              { text: 'Capítulo 155: Ferrugem e Plasma', link: '/capitulo-155' },
              { text: 'Capítulo 156: Condutores de Cobre', link: '/capitulo-156' },
              { text: 'Capítulo 157: A Inércia do Caos', link: '/capitulo-157' },
              { text: 'Capítulo 158: Ecos de Fósforo e Poeira', link: '/capitulo-158' },
              { text: 'Capítulo 159: Servidores de Carne e Silício', link: '/capitulo-159' },
              { text: 'Capítulo 160: O Som do Silício Quebrando', link: '/capitulo-160' },
              { text: 'Capítulo 161: Estática e Cinzas', link: '/capitulo-161' },
              { text: 'Capítulo 162: Engrenagens Cegas', link: '/capitulo-162' },
              { text: 'Capítulo 163: O Fosso de Aço', link: '/capitulo-163' },
              { text: 'Capítulo 164: O Cofre de Concreto', link: '/capitulo-164' },
              { text: 'Capítulo 165: Fantasmas de Silício', link: '/capitulo-165' },
              { text: 'Capítulo 166: A Lógica da Fome', link: '/capitulo-166' },
              { text: 'Capítulo 167: O Grito no Silício', link: '/capitulo-167' },
              { text: 'Capítulo 168: O Peso do Chumbo', link: '/capitulo-168' },
              { text: 'Capítulo 169: O Fantasma na Máquina de Carne', link: '/capitulo-169' },
            ]
          },
          {
            text: 'Parte XVIII: Fronteiras de Ferrugem',
            collapsed: true,
            items: [
              { text: 'Capítulo 170: O Fim do Expediente', link: '/capitulo-170' },
              { text: 'Capítulo 171: Luz Seca', link: '/capitulo-171' },
              { text: 'Capítulo 172: O Peso da Chuva', link: '/capitulo-172' },
              { text: 'Capítulo 173: Fronteiras de Ferrugem', link: '/capitulo-173' },
              { text: 'Capítulo 174: O Açougueiro de Cobre', link: '/capitulo-174' },
              { text: 'Capítulo 175: O Som das Engrenagens Mortas', link: '/capitulo-175' },
              { text: 'Capítulo 176: O Peso da Ferrugem', link: '/capitulo-176' },
              { text: 'Capítulo 177: Cicatrizes de Cobre', link: '/capitulo-177' },
              { text: 'Capítulo 178: O Som do Subterrâneo', link: '/capitulo-178' },
              { text: 'Capítulo 179: Ecos de Aço e Ferrugem', link: '/capitulo-179' },
              { text: 'Capítulo 180: A Fome do Abismo', link: '/capitulo-180' },
              { text: 'Capítulo 181: Pedágio Fantasma', link: '/capitulo-181' },
              { text: 'Capítulo 182: A Superfície Pálida', link: '/capitulo-182' },
              { text: 'Capítulo 183: Carniça de Metal', link: '/capitulo-183' },
              { text: 'Capítulo 184: O Relógio de Sangue', link: '/capitulo-184' },
              { text: 'Capítulo 185: O Verdor Metálico', link: '/capitulo-185' },
              { text: 'Capítulo 186: Raízes de Silício', link: '/capitulo-186' },
              { text: 'Capítulo 187: O Arquivo Morto', link: '/capitulo-187' },
              { text: 'Capítulo 188: O Abismo de Aço', link: '/capitulo-188' },
              { text: 'Capítulo 189: A Sentinela de Biomassa', link: '/capitulo-189' },
              { text: 'Capítulo 190: O Relicário de Silício', link: '/capitulo-190' },
              { text: 'Capítulo 191: O Batismo da Ferrugem', link: '/capitulo-191' },
              { text: 'Capítulo 192: A Ascensão das Cinzas', link: '/capitulo-192' },
              { text: 'Capítulo 193: O Ermitão de Cobre', link: '/capitulo-193' },
            ]
          },
          {
            text: 'Parte XIX: O Poço do Abismo',
            collapsed: true,
            items: [
              { text: 'Capítulo 194: O Preço da Manutenção', link: '/capitulo-194' },
              { text: 'Capítulo 195: O Sangue nas Engrenagens', link: '/capitulo-195' },
              { text: 'Capítulo 196: Ecos de Neon no Submundo', link: '/capitulo-196' },
              { text: 'Capítulo 197: A Gravidade do Lodo', link: '/capitulo-197' },
              { text: 'Capítulo 198: A Marcha Fúnebre', link: '/capitulo-198' },
              { text: 'Capítulo 199: Engrenagens de Sangue', link: '/capitulo-199' },
              { text: 'Capítulo 200: O Poço do Abismo', link: '/capitulo-200' },
              { text: 'Capítulo 201: Degraus de Sangue e Ferrugem', link: '/capitulo-201' },
              { text: 'Capítulo 202: O Corredor Silencioso', link: '/capitulo-202' },
              { text: 'Capítulo 203: Sombras de Aeterna', link: '/capitulo-203' },
              { text: 'Capítulo 204: O Despertar da Ferrugem', link: '/capitulo-204' },
              { text: 'Capítulo 205: Colosso de Sucata', link: '/capitulo-205' },
              { text: 'Capítulo 206: Ecos na Escuridão', link: '/capitulo-206' },
              { text: 'Capítulo 207: O Peso da Ferrugem', link: '/capitulo-207' },
              { text: 'Capítulo 208: A Geada Negra', link: '/capitulo-208' },
              { text: 'Capítulo 209: Cristais de Óxido', link: '/capitulo-209' },
              { text: 'Capítulo 210: Roldanas e Sangue', link: '/capitulo-210' },
              { text: 'Capítulo 211: O Altar de Gelo', link: '/capitulo-211' },
              { text: 'Capítulo 212: O Batismo de Sangue Congelado', link: '/capitulo-212' },
              { text: 'Capítulo 213: O Peso da Maquinaria', link: '/capitulo-213' },
              { text: 'Capítulo 214: O Coração Estéril', link: '/capitulo-214' },
              { text: 'Capítulo 215: Os Alicerces do Inferno', link: '/capitulo-215' },
              { text: 'Capítulo 216: A Pressão do Vazio', link: '/capitulo-216' },
              { text: 'Capítulo 217: O Útero de Chumbo', link: '/capitulo-217' },
            ]
          },
          {
            text: 'Parte XX: Arca Zero',
            collapsed: true,
            items: [
              { text: 'Capítulo 218: O Ar Limpo', link: '/capitulo-218' },
              { text: 'Capítulo 219: Cuidado Perpétuo', link: '/capitulo-219' },
              { text: 'Capítulo 220: A Fita', link: '/capitulo-220' },
              { text: 'Capítulo 221: Modo de Segurança', link: '/capitulo-221' },
              { text: 'Capítulo 222: O Homem que Podia Ir Embora', link: '/capitulo-222' },
              { text: 'Capítulo 223: A Auditora', link: '/capitulo-223' },
              { text: 'Capítulo 224: O Preço do Ar', link: '/capitulo-224' },
              { text: 'Capítulo 225: O Charuto na Sala Limpa', link: '/capitulo-225' },
            ]
          },
        ]
      },
      {
        text: 'Arquivos',
        items: [
          { text: 'Dossiê de Personagens', link: '/personagens' },
          { text: 'Cronologia e Resumo', link: '/cronologia' },
          { text: 'Lore do Livro', link: '/lore-do-livro' },
          { text: 'Sobre o Autor', link: '/sobre-o-autor' }
        ]
      }
    ],
    socialLinks: [
    ]
  }
})
