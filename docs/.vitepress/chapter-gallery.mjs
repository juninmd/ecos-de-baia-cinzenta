// Imagens de um capítulo para o carrossel do cabeçalho: capa + cenas aprovadas.
import { existsSync, readdirSync, readFileSync } from 'node:fs'
import { join } from 'node:path'
import { prefixCoverPath } from './cover-path.mjs'

const CHAPTER_FILE = /^capitulo-(\d+)\.md$/
const SCENE_FILE = /^cena_(\d+)\.(jpe?g|png|webp)$/i

// regerar.txt lista as cenas reprovadas na homologação: refugo não ocupa lugar de cena.
function rejectedScenes(scenesDir) {
  const file = join(scenesDir, 'regerar.txt')
  if (!existsSync(file)) return new Set()
  const lines = readFileSync(file, 'utf-8').split(/\r?\n/).map((l) => l.trim())
  // O arquivo grava o caminho do repositório (docs/public/cenas/capitulo_N/cena_K.jpg).
  return new Set(lines.filter((l) => l && !l.startsWith('#')).map((l) => l.replace(/^.*\/cenas\//, '')))
}

export function chapterImages({ publicDir, relativePath, cover, base = '/' }) {
  const match = CHAPTER_FILE.exec(relativePath ?? '')
  if (!match) return []
  const folder = `capitulo_${match[1]}`
  const scenesDir = join(publicDir, 'cenas')
  const dir = join(scenesDir, folder)
  const rejected = rejectedScenes(scenesDir)
  // Só arquivos da pasta do capítulo: local/ e qwen_edit/ são comparativos, não cenas publicadas.
  const scenes = existsSync(dir)
    ? readdirSync(dir, { withFileTypes: true })
        .filter((e) => e.isFile() && SCENE_FILE.test(e.name) && !rejected.has(`${folder}/${e.name}`))
        .map((e) => e.name)
        .sort((a, b) => Number(SCENE_FILE.exec(a)[1]) - Number(SCENE_FILE.exec(b)[1]))
    : []
  const images = scenes.map((name) => prefixCoverPath(`/cenas/${folder}/${name}`, base))
  return typeof cover === 'string' && cover ? [prefixCoverPath(cover, base), ...images] : images
}
