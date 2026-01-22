<script setup>
import { ref, onMounted, nextTick, watch } from 'vue'

const props = defineProps({
  isOpen: Boolean
})

const emit = defineEmits(['close'])

const input = ref('')
const output = ref([
  { type: 'system', text: 'Conexão estabelecida...' },
  { type: 'system', text: 'Sistema Operacional Lázaro v4.0.1' },
  { type: 'info', text: 'Digite "help" para ver os comandos disponíveis.' }
])
const inputRef = ref(null)
const terminalBodyRef = ref(null)

const commands = {
  help: () => {
    return [
      { type: 'info', text: 'Comandos Disponíveis:' },
      { type: 'cmd-list', text: '  status       - Exibe status atual da cidade' },
      { type: 'cmd-list', text: '  personagens  - Acessa banco de dados de cidadãos' },
      { type: 'cmd-list', text: '  genesis      - [RESTRICTED] Acessar arquivos do projeto' },
      { type: 'cmd-list', text: '  clear        - Limpar terminal' },
      { type: 'cmd-list', text: '  exit         - Encerrar sessão' }
    ]
  },
  status: () => {
    return [
      { type: 'success', text: '>> ANALISANDO SISTEMAS...' },
      { type: 'text', text: 'Nível da Água: ESTÁVEL (Zona Alta)' },
      { type: 'warning', text: 'Integridade da Cúpula: 87%' },
      { type: 'danger', text: 'Ameaça Biológica: DETECTADA (Setor 4)' },
      { type: 'text', text: 'Dia Atual: 92 pós-dilúvio' }
    ]
  },
  personagens: () => {
    return [
      { type: 'info', text: '>> ACESSANDO ARQUIVOS DA POLÍCIA...' },
      { type: 'text', text: 'MORETTI, GABRIEL [ATIVO] - Detetive Particular' },
      { type: 'danger', text: 'CRUZ, VALÉRIA [ESTASE] - Status Desconhecido' },
      { type: 'text', text: 'ARIA [SISTEMA] - Entidade Digital' },
      { type: 'text', text: 'VILAR, CAPITÃO [ATIVO] - Resistência' },
      { type: 'danger', text: 'MORETTI, MARCO [FALECIDO] - Ex-Prefeito' },
      { type: 'warning', text: 'RANGEL, INSPETOR [ATIVO] - Reintegrado' }
    ]
  },
  genesis: () => {
    return [
      { type: 'danger', text: '>> ALERTA DE SEGURANÇA: ACESSO RESTRITO' },
      { type: 'text', text: 'Descriptografando...' },
      { type: 'system', text: 'O Projeto Genesis não era sobre salvar a cidade.' },
      { type: 'system', text: 'Era sobre transformar a carne em armazenamento.' },
      { type: 'system', text: 'Nós somos o backup.' }
    ]
  },
  bercario: () => {
    return [
      { type: 'success', text: '>> ACESSO CONCEDIDO: NÍVEL 0' },
      { type: 'danger', text: 'AVISO: CONTAMINAÇÃO BIOLÓGICA DETECTADA' },
      { type: 'system', text: 'Localização: Subsolo da Linha Vermelha' },
      { type: 'text', text: 'Status dos Tanques: ATIVOS' },
      { type: 'warning', text: 'Mensagem de Elara Vance: "Eles têm fome."' },
      { type: 'text', text: 'Dica: O silêncio é a chave.' }
    ]
  },
  clear: () => {
    output.value = []
    return []
  },
  exit: () => {
    emit('close')
    return []
  }
}

const handleCommand = () => {
  const cmd = input.value.trim().toLowerCase()

  if (!cmd) return

  // Add user command to history
  output.value.push({ type: 'user', text: `> ${input.value}` })

  // Process command
  if (commands[cmd]) {
    const result = commands[cmd]()
    if (result) {
      output.value.push(...result)
    }
  } else {
    output.value.push({ type: 'error', text: `Comando não reconhecido: ${cmd}` })
  }

  input.value = ''
  scrollToBottom()
}

const scrollToBottom = () => {
  nextTick(() => {
    if (terminalBodyRef.value) {
      terminalBodyRef.value.scrollTop = terminalBodyRef.value.scrollHeight
    }
  })
}

// Auto-focus when opened
watch(() => props.isOpen, (newVal) => {
  if (newVal) {
    nextTick(() => {
      inputRef.value?.focus()
      scrollToBottom()
    })
  }
})
</script>

<template>
  <div v-if="isOpen" class="terminal-overlay" @click.self="emit('close')">
    <div class="terminal-window">
      <div class="terminal-header">
        <span class="terminal-title">TERMINAL DE ACESSO LÁZARO // V4.0.1</span>
        <button class="close-btn" @click="emit('close')">✕</button>
      </div>
      <div class="terminal-body" ref="terminalBodyRef" @click="inputRef?.focus()">
        <div v-for="(line, index) in output" :key="index" :class="['line', line.type]">
          {{ line.text }}
        </div>
        <div class="input-line">
          <span class="prompt">></span>
          <input
            ref="inputRef"
            v-model="input"
            @keyup.enter="handleCommand"
            type="text"
            class="terminal-input"
            autocomplete="off"
            spellcheck="false"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;700&display=swap');

.terminal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.85);
  backdrop-filter: blur(4px);
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.terminal-window {
  width: 100%;
  max-width: 800px;
  height: 80vh;
  background: #0d0d0d;
  border: 1px solid #33ff00;
  box-shadow: 0 0 20px rgba(51, 255, 0, 0.2);
  display: flex;
  flex-direction: column;
  font-family: 'Fira Code', monospace;
  position: relative;
  overflow: hidden;
}

/* Scanline effect */
.terminal-window::before {
  content: " ";
  display: block;
  position: absolute;
  top: 0;
  left: 0;
  bottom: 0;
  right: 0;
  background: linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.25) 50%), linear-gradient(90deg, rgba(255, 0, 0, 0.06), rgba(0, 255, 0, 0.02), rgba(0, 0, 255, 0.06));
  z-index: 2;
  background-size: 100% 2px, 3px 100%;
  pointer-events: none;
}

.terminal-header {
  background: #1a1a1a;
  border-bottom: 1px solid #33ff00;
  padding: 10px 15px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.terminal-title {
  color: #33ff00;
  font-size: 0.9rem;
  font-weight: bold;
  letter-spacing: 1px;
}

.close-btn {
  background: none;
  border: none;
  color: #33ff00;
  cursor: pointer;
  font-size: 1.2rem;
}

.terminal-body {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  color: #33ff00;
  font-size: 1rem;
  line-height: 1.5;
}

.line {
  margin-bottom: 5px;
  text-shadow: 0 0 5px rgba(51, 255, 0, 0.5);
}

.line.user { color: #fff; }
.line.error { color: #ff3333; text-shadow: 0 0 5px rgba(255, 51, 51, 0.5); }
.line.warning { color: #ffcc00; }
.line.system { color: #00ccff; }
.line.danger { color: #ff0000; font-weight: bold; }

.input-line {
  display: flex;
  align-items: center;
  margin-top: 10px;
}

.prompt {
  color: #33ff00;
  margin-right: 10px;
}

.terminal-input {
  background: transparent;
  border: none;
  color: #fff;
  font-family: 'Fira Code', monospace;
  font-size: 1rem;
  flex: 1;
  outline: none;
  caret-color: #33ff00;
}
</style>
