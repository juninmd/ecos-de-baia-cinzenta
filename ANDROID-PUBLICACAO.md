# Publicação e manutenção do app Android

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
- Certifique-se que está em HTTPS (GitHub Pages já usa)
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
| Atualizações | Após publicação | Após publicação (via web) |
| Tamanho | ~500KB | ~5MB |
| Funciona offline | Sim (cache) | Sim (cache) |
| Notificações push | Sim | Sim |
| Ícone na home | Sim | Sim |

**Recomendação**: Comece com PWA, depois publique app nativo se quiser alcance via Play Store.

---

## 🚀 Deploy automatizado (CI/CD)

Veja `.github/workflows/android-build.yml` para build automático do APK em cada release.
