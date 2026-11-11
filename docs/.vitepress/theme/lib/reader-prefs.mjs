// Preferências de leitura: limites e valores válidos num lugar só, testável sem navegador.
export const SKINS = ['auto', 'noite', 'sepia', 'papel']
export const FACES = ['serifa', 'condensada']
export const DEFAULTS = { size: 100, lineHeight: 1.78, skin: 'auto', face: 'serifa' }
export const SIZE = { min: 70, max: 150, step: 10 }
export const LINE = { min: 1.4, max: 2.2 }

const clamp = (v, min, max) => Math.min(max, Math.max(min, v))

export function normalizePrefs(raw) {
  const p = { ...DEFAULTS, ...(raw && typeof raw === 'object' ? raw : {}) }
  const size = Math.round(Number(p.size) / SIZE.step) * SIZE.step
  const line = Number(p.lineHeight)
  return {
    size: Number.isFinite(size) ? clamp(size, SIZE.min, SIZE.max) : DEFAULTS.size,
    lineHeight: Number.isFinite(line) ? Math.round(clamp(line, LINE.min, LINE.max) * 100) / 100 : DEFAULTS.lineHeight,
    skin: SKINS.includes(p.skin) ? p.skin : DEFAULTS.skin,
    face: FACES.includes(p.face) ? p.face : DEFAULTS.face,
  }
}

export function stepSize(size, dir) {
  return dir === 0 ? DEFAULTS.size : clamp(size + dir * SIZE.step, SIZE.min, SIZE.max)
}
