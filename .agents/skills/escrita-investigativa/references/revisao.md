# Revisão e entrega editorial

## Ordem de trabalho

1. Delimite o pedido: diagnóstico, revisão pontual, reescrita ou capítulo novo.
2. Registre os problemas com passagem, efeito no leitor e reparo proposto.
3. Resolva causalidade, investigação, tecnologia e continuidade.
4. Ajuste a função das cenas, o custo, o subtexto e o fluxo da informação.
5. Revise voz, clareza, repetição, pontuação e imagens. Leia diálogos em sequência.
6. Releia o final, o capítulo anterior e o seguinte quando existir. Verifique
   inventário, ferimentos e conhecimento depois da alteração.

Se a revisão for apenas diagnóstica, entregue os reparos propostos sem aplicá-los.
Em revisão localizada, preserve as escolhas que funcionam; não uniformize a voz
do livro inteiro para acomodar uma preferência de frase.

## Portões duros: conferir os cinco lendo

| Portão do projeto | Evidência necessária |
| --- | --- |
| D1 — Extensão | Pelo menos 600 palavras de narrativa; alvo 1.100–1.600 |
| D2 — Título | Um H1, número/formato corretos e título idêntico ao menu em `config.ts` |
| D3 — Metadados | Localização e Personagens Presentes declarados e compatíveis com a cena |
| D4 — Cânone | Nenhuma violação demonstrada; fase corporal, identidade e sobrevivência conferidas |
| D5 — Fechamento | Última linha produz imagem, decisão ou ameaça; não recapitula o capítulo |

Cada falha reprova sozinha. Não use uma média para compensar um portão quebrado.
Registre dúvida relevante como pendência, não como evidência de aprovação.

## Notas editoriais: 0, 1 ou 2

Reproduza a régua do `AGENTS.md` e justifique cada eixo com passagem ou cena:

| Eixo | 0 | 1 | 2 |
| --- | --- | --- | --- |
| Atmosfera noir | Só descrição visual | Dois sentidos | Três ou mais e ambiente com posição dramática |
| Custo | Ninguém perde nada | Perda reversível | Perda permanente de corpo, pessoa, crença ou opção |
| Voz e personagem | Todos falam igual | Protagonista tem voz | Cada voz se distingue; um silêncio importa |
| Ritmo | Exposição em bloco | Alterna diálogo e ação | Informação chega por conflito |
| Consequência | Episódio isolado | Referencia o anterior | Muda a compreensão do que já foi lido |

9–10: faixa chamada obra-prima pela régua; 7–8: publicável; 5–6: revisar;
até 4: reescrever. Uma nota é juízo editorial fundamentado, não garantia artística.
A permanência pode ser sentida num capítulo de consequência; não crie outra morte
para repetir o efeito da perda anterior.

## Auditoria de mistério e cyberpunk

Estes critérios complementam a nota, sem inventar um segundo placar:

- **Cadeia lógica:** cada inferência decisiva tem fonte, alternativa e teste?
  Qual observação exclui a hipótese rival mais forte?
- **Jogo limpo:** o leitor recebeu as condições necessárias antes da solução?
  O personagem usou um fato que só aparece depois? Há informação sonegada pelo ponto de vista?
- **Plantio:** cada virada aponta para capítulo e passagem já publicados?
  Um plano de plantio futuro não vale como preparação passada.
- **Prova:** depoimentos são independentes? Há origem, custódia, autenticidade e
  diferença entre saber o que aconteceu e poder demonstrá-lo?
- **Tecnologia:** capacidade, limite, acesso e custo foram estabelecidos? O dado
  obtido é confiável? A tecnologia foi usada para escapar da lógica da cena?
- **Agência:** o avanço vem de uma ação e escolha, ou de coincidência salvadora?
  O antagonista e as testemunhas têm objetivos enquanto Gabo investiga?
- **Serialização:** a pergunta local avança e as perguntas maiores permanecem
  legíveis? A revelação muda decisões em vez de apenas acrescentar outro nome?

Uma resposta negativa que invalide a solução ou sua compreensão impede chamar
o capítulo de pronto, mesmo quando a triagem automática lhe dá 10.

## O que o script comprova

`scripts/quality_gate.py` é triagem lexical. `avalia(Path(...))` não grava relatório;
`main()` percorre a obra e grava `docs/qualidade_capitulos.md`, retornando falha
quando encontra portões automatizados reprovados em qualquer capítulo.

O contador de palavras ainda pode incluir título e outros elementos fora da
prosa. Confira a narrativa separadamente. O script não compara o H1 com o menu,
não exige toda a localização, não detecta todas as violações de cânone e não
avalia D5. As notas baseadas em travessões e palavras de dor são aproximações.

Antes de editar, registre a triagem do alvo para distinguir problemas existentes.
Depois, execute os testes do repositório e o lint apropriado; se mudar navegação
ou componentes, execute também `pnpm docs:build`. Não execute testes exploratórios
de GPU em `scripts/` por rotina: alguns carregam modelos, criam arte ou preparam
envio externo. Leia os efeitos antes de ampliar o conjunto de testes.

Um teste que verifica links não comprova fidelidade de personagem. Um build
completo não avalia subtexto. Reporte cada resultado no nível que ele verifica.

## Modelo de parecer

```text
Alvo e escopo da revisão:
Estado de entrada e de saída; fontes de continuidade:
Problemas corrigidos: passagem -> defeito -> mudança e efeito:
Pistas: ID -> capítulo/passagem de plantio -> teste -> retorno:
Hipóteses ainda abertas e limites de prova:
D1 / D2 / D3 / D4 / D5: resultado e evidência de cada um:
Atmosfera / custo / voz / ritmo / consequência: nota e justificativa:
Auditoria de investigação e tecnologia: falhas ou evidências:
Comandos executados e resultados; problemas prévios separados:
Pendências:
Veredito: pronto / revisar / reescrever / aguardando decisão específica:
```

Mantenha spoilers e notas de construção no parecer ou dossiê editorial, fora da
prosa e do menu de leitura. Entregue apenas os artefatos pedidos. Criar um texto
não autoriza gerar mídia, enviar Telegram ou publicar uma nova versão do site.
