// Data loader do VitePress: estatística de todos os capítulos, lida dos arquivos-fonte no build.
import { readFileSync } from 'node:fs'
import { chapterStats } from './lib/chapter-stats.mjs'

export default {
  watch: ['../../capitulo-*.md'],
  load(files) {
    return files
      .map((file) => chapterStats(file, readFileSync(file, 'utf8')))
      .filter(Boolean)
      .sort((a, b) => a.n - b.n)
  },
}
