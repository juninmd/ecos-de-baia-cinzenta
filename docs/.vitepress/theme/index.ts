import DefaultTheme from 'vitepress/theme'
import type { Theme, EnhanceAppContext } from 'vitepress'
import Layout from './Layout.vue'
import CharacterPortraits from './components/CharacterPortraits.vue'
import HomeHero from './components/HomeHero.vue'
import ChapterRiver from './components/ChapterRiver.vue'
import ResumeCard from './components/ResumeCard.vue'
import CastDossier from './components/CastDossier.vue'
import './sodio/tokens.css'
import './sodio/base.css'
import './sodio/doc.css'
import './sodio/home.css'
import './sodio/dock.css'
import './sodio/palette.css'
import './sodio/cast.css'
import mediumZoom from 'medium-zoom'
import { onMounted, watch, nextTick } from 'vue'
import { useRoute } from 'vitepress'

export default {
  extends: DefaultTheme,
  Layout,
  enhanceApp({ app }: EnhanceAppContext) {
    app.component('CharacterPortraits', CharacterPortraits)
    app.component('HomeHero', HomeHero)
    app.component('ChapterRiver', ChapterRiver)
    app.component('ResumeCard', ResumeCard)
    app.component('CastDossier', CastDossier)
  },
  setup() {
    const route = useRoute()
    // Zoom só nas imagens do texto; retratos do dossiê e do hero têm o próprio comportamento.
    const initZoom = () => mediumZoom('.vp-doc img:not(.hh-bg):not(.cast-card img)', { background: 'var(--sd-ink)' })
    onMounted(initZoom)
    watch(() => route.path, () => nextTick(initZoom))
  }
} satisfies Theme
