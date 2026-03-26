import DefaultTheme from 'vitepress/theme'
import Layout from './Layout.vue'
import './style.css'
import mediumZoom from 'medium-zoom'
import { onMounted, watch, nextTick } from 'vue'
import { useRoute } from 'vitepress'
import type { Theme } from 'vitepress'

const theme: Theme = {
  ...DefaultTheme,
  Layout,
  enhanceApp({ app }) {
    // Custom app enhancements can go here
  },
  setup() {
    const route = useRoute()
    const initZoom = () => {
      // Select images in the document content
      mediumZoom('.vp-doc img', { background: 'var(--vp-c-bg)' })
    }
    onMounted(() => {
      initZoom()
    })
    watch(
      () => route.path,
      () => nextTick(() => initZoom())
    )
  }
}

export default theme
