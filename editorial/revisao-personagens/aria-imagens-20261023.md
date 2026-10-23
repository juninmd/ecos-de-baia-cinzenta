# Aria: atualização visual de 23/10/2026

Onze imagens selecionadas foram aplicadas a doze destinos: retrato novo,
apresentação, cinco capas e cinco cenas existentes do capítulo 2.
A apresentação e a cena 4 compartilham a mesma arte, como no acervo anterior.
Os capítulos revisados permanecem nas fontes oficiais; seus espelhos são links.

## Origem das cenas

As composições aproveitáveis foram editadas com os pedidos existentes em
[lote.json](aria-agy/lote.json), confrontados com os capítulos oficiais.
O contêiner com criança e a figura verde gigante foram rejeitados porque não
representavam as situações publicadas. As correções usam trechos literais,
intervalos de linhas e hashes das fontes em
[lote-capitulos-20261023.json](aria-agy/lote-capitulos-20261023.json),
com as cláusulas visuais e de continuidade existentes do projeto.
As instruções adicionais corrigem pose, lateralidade e dimensão do módulo;
não acrescentam acontecimentos à história.

| Destino | Situação do capítulo |
| --- | --- |
| Retrato `aria_3.png` | Referência holográfica adulta; apresentação de personagem |
| Apresentação e cena 4 | Ambiente da estreia na enchente, capítulo 2 |
| Capa 2 e cenas 2,5,7 | Cabine telefônica, fone e módulo conectado |
| Cena 10 | Módulo e projeção no painel do Cobalt |
| Capa 59 | Grade de ventilação e complexo de servidores |
| Capa 67 | Avenida alagada, semáforos e conversa com Val |
| Capa 74 | Heliponto, Val ferida e tentativa de extração do módulo |
| Capa 96 | Gabo segura o conector na Árvore-Mãe |

## Identidade e homologação

- O retrato novo preserva a identidade adulta de `aria_2.png`, cabelo platinado,
  heterocromia e jaqueta grafite fechada. Os dois retratos anteriores continuam
  imutáveis, como histórico. A linha do tempo registra a nova âncora.
- Aria aparece como luz translúcida sem contato físico. Na capa 74, está
  representada pelo módulo no terminal, sem acrescentar um avatar ao resgate.
- Gabo e Val usam suas referências oficiais. As capas 67, 74 e 96 foram refeitas
  para corrigir identidade, órteses, lesões, ação e escala do aparelho.
- Houve inspeção visual pelo agente raiz e revisão independente. A arte é
  ilustração da cena, não registro fotográfico literal de cada gesto descrito.
- Todos os doze arquivos passam pelos limites mecânicos de resolução, nitidez,
  contraste e tamanho do projeto. O retrato usa o requisito quadrado próprio.
  O alerta de faixa horizontal no retrato corresponde à malha e aos glitches,
  sem legenda ou título visível.
- A única duplicata detectada é a reutilização prevista da apresentação na
  cena 4. As demais dez imagens são distintas.

## Execução e limites

Foram produzidos dezenove candidatos; onze foram selecionados. O gerador
integrado não encontrou limite de uso. O fallback para Antigravity autorizado
pelo autor não precisou ser acionado. A tentativa antiga com erro 429 permanece
documentada separadamente; não é o resultado desta rodada.

O gerador integrado não expõe parâmetro seed. As seeds solicitadas foram
registradas, mas não aplicadas; não há promessa de reprodução determinística.
Os PNG originais ficam preservados; as cenas foram apenas codificadas como JPEG
para os caminhos já consumidos pelo site, sem recorte ou retoque de pixels.

Hashes dos prompts e arquivos, dimensões e medidas após a codificação estão no
[recibo da promoção](aria-imagens-20261023.json). A medição de todos os candidatos,
incluindo os rejeitados visualmente, está em
[aria-metricas-20261023.json](aria-metricas-20261023.json).

## Entrega

Incluído no [PR #550](https://github.com/juninmd/ecos-de-baia-cinzenta/pull/550).
O PR permanece rascunho enquanto os portões remotos tiverem falhas.
A auditoria Node da primeira execução encontrou 84 vulnerabilidades em
dependências e lockfile que esta revisão não alterou. O smoke também revelou
uma chamada preexistente a `registrar_sem_ancora` sem definição; a correção
reutiliza a fila de homologação e tem regressões para encerramento e deduplicação.
Os resultados finais de testes, lint, build e CI estão no corpo atualizado do PR.
