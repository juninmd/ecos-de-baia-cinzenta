import { readdir, readFile, writeFile } from 'node:fs/promises'
import { join } from 'node:path'

// Os chunks de diagramas entram no preload de toda página pelo app chunk, e só
// arcos.md os usa. O import dinâmico do mermaid os carrega quando o diagrama aparece.
export const DIAGRAM_HINT_RE = /<link rel="(?:modulepreload|prefetch)" href="[^"]*(?:diagram|definition|mermaid|cytoscape|cose-bilkent|dagre|katex|swimlane)[^"]*">/gi

export async function stripDiagramHints(dir) {
  for (const entry of await readdir(dir, { withFileTypes: true })) {
    const path = join(dir, entry.name)
    if (entry.isDirectory()) {
      await stripDiagramHints(path)
    } else if (entry.name.endsWith('.html')) {
      const html = await readFile(path, 'utf8')
      const stripped = html.replace(DIAGRAM_HINT_RE, '')
      if (stripped !== html) await writeFile(path, stripped)
    }
  }
}
