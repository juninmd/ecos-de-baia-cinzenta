import { defineAsyncComponent } from 'vue'

// Mermaid só entra quando um bloco de diagrama aparece (arcos.md), fora do app chunk
export default defineAsyncComponent(() => import('../../../node_modules/vitepress-plugin-mermaid/dist/Mermaid.vue'))
