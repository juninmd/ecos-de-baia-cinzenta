#!/usr/bin/env node
import { spawnSync } from 'node:child_process'

// O reusable-validate roda `pnpm test` antes de instalar Python/uv.
// No CI, o pytest é executado na etapa Python do próprio Validate; aqui
// apenas saímos com sucesso para não derrubar o job antes dessa etapa.
if (process.env.CI) {
  console.log('pytest roda na etapa Python do Validate; etapa Node ignorada.')
  process.exit(0)
}

const probe = spawnSync('uv', ['--version'], { stdio: 'ignore' })

if (probe.error || probe.status !== 0) {
  console.error('uv não encontrado. Use: uv run --no-sync python -m pytest tests/')
  process.exit(1)
}

const run = spawnSync(
  'uv',
  ['run', '--no-sync', 'python', '-m', 'pytest', 'tests/'],
  { stdio: 'inherit' },
)

process.exit(run.status ?? 1)
