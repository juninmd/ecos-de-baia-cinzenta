# Correções da auditoria — estado de trabalho

Escopo: A01–A15 e M01–M07, com efeitos sobre continuidade e personagens descritos nos pareceres. O pedido autoriza corrigir a prosa, preservando acontecimentos, identidades, retratos e espelhos relativos.

## Preservação e responsáveis

- Antes de editar, foram arquivados e conferidos por SHA-256 295 arquivos: fontes, fichas, cânone e auditoria anterior.
- Backup local: `C:/Users/jr_ac/AppData/Local/Temp/ecos-correcao-20261023-105558/antes.zip`.
- Baseline dos mesmos arquivos: `baseline.json`, ao lado do backup.
- Raiz: integração, calendário, clínica/recursos, fichas e validação.
- `corrigir_inicio`: começo, plantio, personagens de apoio e contagem do enclave.
- `corrigir_aria`: estado da IA e função das cenas 135–169.
- `corrigir_descida`: função das cenas 198–217 e colosso.
- `corrigir_final`: arquivos, responsabilidade, divulgação e desfecho 218–236.
- Cada editor trabalha em worktree isolado com a versão local copiada; integração somente pela raiz, verificando que a fonte não mudou desde o snapshot.
- Runtime e promoção não aplicáveis; sem geração de mídia, publicação ou mudança de branch da produção.

## Decisões de continuidade

1. Manter o presente em 2056. Reduzir o intervalo 7/8 para três semanas; explicitar 19/03/2056 para as comportas, sem recalcular idades ou deslocar o começo a 2055.
2. Gabo não viu o corpo do pai antes do encontro com o suporte orgânico; a identificação dos restos ocorre em 40. Corrigir a lembrança incompatível em 19.
3. O reboot de Aria limita acesso ao histórico, sem remover sua identidade ou empatia. A destruição do núcleo em 167 permanece definitiva.
4. Enclave: 240 pessoas incluindo Vilar; 27 iniciam a retirada incluindo Peçanha; 26 chegam, incluindo Vilar; 214 mortos incluindo Peçanha.
5. Braga pode ser contido e transferido; Gabo recusa a alternativa e o executa. Corrigir a ficha que alegava impossibilidade de prisão ou necessidade do assassinato.
6. Reforçar plantio com rastros observáveis e teste da hipótese rival, preservando limites de autoria e autenticidade do arquivo.

## Fechamento

Integração e releituras concluídas nos alvos: 61 capítulos, seis fichas e três documentos de cânone/instruções, preservando os demais 177 capítulos. O [fechamento](correcoes-concluidas.md) registra as decisões e os limites; [verificações](correcoes-verificacoes.json) e [hashes finais](correcoes-fontes-sha256.json) identificam a versão corrigida. Testes e lint aprovados; o build foi aprovado com limite de heap de 8 GiB apenas no processo de validação. Não há publicação nem aprovação artística automática.
