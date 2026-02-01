# 📱 App Android - Ecos de Baía Cinzenta

Este projeto está configurado como **PWA (Progressive Web App)** e pode ser compilado como **app Android nativo**.

## 🌐 PWA (Progressive Web App)

### O que foi implementado?
- ✅ **Manifest.json**: Permite instalação como app no smartphone
- ✅ **Service Worker**: Cache offline e atualizações em segundo plano
- ✅ **Ícones**: Múltiplos tamanhos para Android/iOS
- ✅ **Offline Page**: Página exibida quando sem conexão

### Como instalar (navegador)?
1. Acesse https://ecos-de-baia-cinzenta.netlify.app no Chrome/Edge mobile
2. Toque no menu (⋮) → "Adicionar à tela inicial"
3. O app será instalado como PWA

### Atualizações em tempo real
- O Service Worker busca atualizações automaticamente
- Quando novo conteúdo é publicado no Netlify, o app atualiza em background
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
GitHub Push → Netlify Deploy → Atualiza site web
                                    ↓
                          App busca do servidor web
```

O app **não empacota** o conteúdo HTML:
- Ele carrega o site do Netlify em um WebView otimizado
- Quando você faz push no GitHub → Netlify atualiza → App já mostra novo conteúdo
- **Zero delay**: Sem necessidade de republicar na Google Play Store

### Configuração (capacitor.config.json)
```json
{
  "server": {
    "url": "https://ecos-de-baia-cinzenta.netlify.app"
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

## 📦 Publicar na Google Play Store

### 1. Criar keystore (certificado)
```bash
cd android
keytool -genkey -v -keystore meu-livro.keystore -alias baia-cinzenta -keyalg RSA -keysize 2048 -validity 10000
```

### 2. Configurar assinatura
Edite `android/app/build.gradle`:
```gradle
android {
    signingConfigs {
        release {
            storeFile file('meu-livro.keystore')
            storePassword 'sua-senha'
            keyAlias 'baia-cinzenta'
            keyPassword 'sua-senha'
        }
    }
    buildTypes {
        release {
            signingConfig signingConfigs.release
        }
    }
}
```

### 3. Build release
```bash
cd android
./gradlew bundleRelease
```

O arquivo `app-release.aab` estará em `android/app/build/outputs/bundle/release/`

### 4. Upload na Play Console
1. Acesse https://play.google.com/console
2. Crie novo app
3. Upload do `.aab`
4. Preencha metadados (descrição, screenshots, etc)
5. Publique!

---

## 🎨 Personalizar ícone do app

### Opção 1: Usar imagem existente
```bash
# Edite scripts/generate_icons.py linha 61:
source = "docs/public/sua-imagem.png"  # Deve ser 512x512

pnpm icons:generate
```

### Opção 2: Criar ícone customizado
1. Crie `docs/public/app-icon-source.png` (512x512 px)
2. Execute `pnpm icons:generate`
3. Ícones gerados em `docs/public/icons/`

---

## 🐛 Troubleshooting

### PWA não aparece "Adicionar à tela"?
- Certifique-se que está em HTTPS (Netlify já usa)
- Limpe cache do navegador
- Verifique console: Service Worker registrado?

### App Android não conecta?
```bash
# Verifique se build está sincronizado
pnpm android:sync

# Logs do app
npx cap run android --livereload
```

### Ícones não aparecem?
```bash
# Regerar ícones
pnpm icons:generate

# Sincronizar com Android
pnpm android:sync
```

---

## 📊 Comparação: PWA vs App Nativo

| Característica | PWA | App Nativo |
|---------------|-----|------------|
| Instalação | Navegador | Google Play Store |
| Aprovação | Não requer | Requer revisão Google |
| Atualizações | Instantâneas | Instantâneas (via web) |
| Tamanho | ~500KB | ~5MB |
| Funciona offline | Sim (cache) | Sim (cache) |
| Notificações push | Sim | Sim |
| Ícone na home | Sim | Sim |

**Recomendação**: Comece com PWA, depois publique app nativo se quiser alcance via Play Store.

---

## 🚀 Deploy automatizado (CI/CD)

Veja `.github/workflows/android-build.yml` para build automático do APK em cada release.
