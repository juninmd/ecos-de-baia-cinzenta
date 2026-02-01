# 🚀 Quick Start: PWA & Android

## ✅ O que já está pronto?

A implementação PWA está completa:
- ✅ Manifest.json configurado
- ✅ Service Worker ativo
- ✅ Ícones gerados (8 tamanhos)
- ✅ Página offline
- ✅ VitePress configurado

## 📱 Testar PWA localmente

```bash
# 1. Build do site
pnpm docs:build

# 2. Preview local
pnpm docs:preview
# Acesse: http://localhost:4173

# 3. Testar no mobile
# Use seu IP local (ex: http://192.168.1.X:4173)
# Chrome mobile → Menu → "Adicionar à tela inicial"
```

## 🌐 Deploy (Já configurado!)

```bash
git add .
git commit -m "feat: add PWA and Android app support"
git push origin main
```

Netlify automaticamente:
1. Faz build do VitePress
2. Publica manifest.json e service worker
3. PWA fica disponível em: https://ecos-de-baia-cinzenta.netlify.app

**Usuários podem instalar imediatamente!**

## 🤖 Compilar app Android (Opcional)

### Primeira vez (setup):
```bash
# Instalar Capacitor
pnpm install

# Adicionar plataforma Android
pnpm android:add
```

### Build regular:
```bash
# Sincronizar web → Android
pnpm android:sync

# Abrir no Android Studio
pnpm android:open

# Ou build direto do APK
cd android && ./gradlew assembleDebug
```

## 🔄 Como as atualizações funcionam?

### PWA (via navegador)
1. Você faz push no GitHub
2. Netlify rebuilda e publica
3. Service Worker detecta nova versão
4. Na próxima visita, usuário vê conteúdo atualizado
5. **ZERO delay!**

### App Android nativo
- Se compilado com `server.url` apontando pro Netlify:
  - Mesma atualização instantânea que PWA
  - Não precisa republicar na Play Store
  
- Se quiser empacotar conteúdo no APK:
  - Mudar `capacitor.config.json` → remover `server.url`
  - Rebuild: `pnpm android:build`

## 📊 Comparação rápida

| Tipo | Setup | Atualização | Instalação |
|------|-------|-------------|------------|
| PWA | ✅ Pronto | Automática | Chrome → Menu |
| APK dev | 5 min | Automática | Transferir .apk |
| Play Store | 2-3 dias | Automática | Google Play |

**Recomendação**: Começar com PWA (já funciona!), depois fazer APK se quiser.

## 🧪 Testar agora

```bash
# Verificar configuração
python tests/test_pwa.py

# Build e visualizar
pnpm docs:build && pnpm docs:preview
```

Abra no Chrome mobile e teste "Adicionar à tela inicial"!

## 📚 Mais detalhes

Ver [ANDROID.md](../ANDROID.md) para:
- Publicação na Google Play Store
- Customizar ícone do app
- Troubleshooting
- Build release assinado
