# Espelhos relativos dos 238 capítulos

Migração executada em 22/10/2026, sem alterar a fonte oficial para resolver
divergências. A fonte continua em docs/capitulo-N.md; o espelho aponta para
../capitulo-N.md. Incluídos os capítulos intercalares 30.5 e 75.5.

## Antes e depois

| Verificação | Antes | Depois |
| --- | --- | --- |
| Fontes oficiais | 238 | 238 |
| Espelhos em cópias | 186 | 0 |
| Espelhos ausentes | 52 | 0 |
| Symlinks relativos | 0 | 238 |
| Conteúdo divergente da fonte | 10 | 0 |

As diferenças anteriores não foram apagadas sem recibo. Todas as 424 versões
existentes, fontes e espelhos, foram copiadas e conferidas por SHA-256 antes
da migração. As 186 cópias substituídas também têm backup individual e recibo.
Não houve sobrescrita de fonte oficial com conteúdo de espelho.

Backup: C:/Users/jr_ac/AppData/Local/Temp/ecos-revisao-total-tqj068t6.
Originais em originais; cópias da migração em espelhos-migrados.
O recibo fontes-iniciais.json identifica cada versão anterior por hash.

## Divergências preservadas

Capítulos 35, 50, 75.5, 97, 98, 99, 110, 128, 129 e 169 tinham cópias diferentes.
As duas versões de cada capítulo foram preservadas. A comparação editorial
dessas variantes continua pendente; sincronização não significa revisão delas.

## Windows e portabilidade

O primeiro teste falhou com WinError 1314. Depois de o autor ativar o Modo de
Desenvolvedor, a criação de links passou a funcionar. Outro teste mostrou que
o Windows exigia separadores nativos no alvo relativo para conseguir lê-lo.
O migrador converte o caminho ao criar e normaliza ao conferir.

O Git reconheceu o espelho conferido como modo 120000 e alvo ../capitulo-19.md,
com separador portátil. Os 238 links foram reabertos e comparados à fonte.
As mudanças futuras devem ser feitas na fonte, preservando o link. A opção
local core.symlinks foi alterada de false para true e conferida no Git.

## Ferramenta e validação

O script scripts/sincronizar_espelhos.py faz inventário sem mutação por padrão.
Para migrar exige --aplicar e --backup fora do projeto. Testa criação e leitura
antes de substituir cópias, recusa fontes em symlink ou links inesperados,
preserva as versões anteriores e troca cada espelho atomicamente.

Os três testes cobrem falta de privilégio sem remoção de cópias, rejeição de
backup dentro do projeto e migração real com preservação da divergência.
O terceiro passou neste Windows depois da ativação; não é só um teste simulado.
Ruff passou. A validação do site e da revisão aparece no registro da rodada.

A migração cumpre a convenção de espelhos. Não comprova qualidade literária,
correção das variantes preservadas ou revisão dos 238 capítulos.
