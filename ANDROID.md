# 📱 App Android - Ecos de Baía Cinzenta

Este projeto está configurado como **PWA (Progressive Web App)** e pode ser compilado como **app Android nativo**.

## 🌐 PWA (Progressive Web App)

### O que foi implementado?
- ✅ **Manifest.json**: Permite instalação como app no smartphone
- ✅ **Service Worker**: Cache offline e atualizações em segundo plano
- ✅ **Ícones**: Múltiplos tamanhos para Android/iOS
- ✅ **Offline Page**: Página exibida quando sem conexão

### Como instalar (navegador)?
1. Acesse https://juninmd.github.io/ecos-de-baia-cinzenta/ no Chrome/Edge mobile
2. Toque no menu (⋮) → "Adicionar à tela inicial"
3. O app será instalado como PWA

### Atualizações em tempo real
- O Service Worker busca atualizações automaticamente
- Quando novo conteúdo é publicado no GitHub Pages, o app atualiza em background
- Usuário recebe novo conteúdo na próxima navegação

---

## 🤖 App Android Nativo (Capacitor)

### Pré-requisitos
- Android Studio instalado
- Java JDK 17+
- Node.js e pnpm

### Setup inicial

```bash
# 1. Instalar dependências do Capacitor
pnpm install

# 2. Gerar ícones do app
pnpm icons:generate

# 3. Adicionar plataforma Android (primeira vez)
pnpm android:add
```

### Build do app

```bash
# Sincronizar código web com projeto Android
pnpm android:sync

# Abrir no Android Studio
pnpm android:open

# Build APK direto (sem Android Studio)
pnpm android:build
```

O APK será gerado em: `android/app/build/outputs/apk/debug/app-debug.apk`

### Testar no dispositivo

```bash
# Conecte celular via USB com depuração ativada
pnpm android:run
```

---

## 🔄 Como funciona a atualização em tempo real?

### Arquitetura Híbrida
```
GitHub Push → GitHub Pages → Atualiza site web
                                    ↓
                          App busca do servidor web
```

O app **não empacota** o conteúdo HTML:
- Ele carrega o site do GitHub Pages em um WebView otimizado
- Quando a publicação no GitHub Pages termina, o app pode carregar o novo conteúdo
- O aplicativo remoto recebe o conteúdo publicado sem republicação na Google Play Store; a atualização depende do cache e do carregamento.

### Configuração (capacitor.config.json)
```json
{
  "server": {
    "url": "https://juninmd.github.io/ecos-de-baia-cinzenta/"
  }
}
```

Para development local, mude para:
```json
{
  "server": {
    "url": "http://192.168.1.X:5173",  // Seu IP local
    "cleartext": true
  }
}
```

---

Para publicação, ícones e solução de problemas, consulte [ANDROID-PUBLICACAO.md](ANDROID-PUBLICACAO.md).
