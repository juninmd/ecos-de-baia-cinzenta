# PoC Unreal: Vila da Ferrugem

Prova de conceito 3D do capítulo 1 em **Unreal Engine 5.4** (C++). O mundo é montado por código ao dar Play, então não há assets nem mapa para criar no editor.

> **Status:** escrito sem compilar. Nenhuma engine rodou este código ainda. Espere ajustar um ou outro erro de compilação e a exposição de luz.

## Como rodar

1. Instale o Unreal Engine 5.4 e o Visual Studio 2022 com a carga "Desenvolvimento de jogos com C++" (Windows) ou Xcode (Mac).
2. Clique com o botão direito em `EcosPoC.uproject` e escolha **Generate Visual Studio project files**.
3. Abra o `.sln`, compile `EcosPoCEditor` (Development Editor) e rode, ou dê duplo clique no `.uproject`.
4. Aperte **Play**.

## Controles

`WASD` anda · mouse ou `←` `→` gira a câmera · `E` inspeciona e fala com Silva · `R` recomeça.

## Regras

Cinco pistas e três lembranças. Drones da Aeterna projetam um cone de luz no chão. Dentro dele a barra de vigilância enche, e cheia apaga uma lembrança. Os toldos escuros escondem Gabo. Leve as cinco pistas a Silva, no extremo norte.

## Arquivos (`Source/EcosPoC`)

| Arquivo | Papel |
| --- | --- |
| `EcosGameMode` | Estado da partida, zonas de sombra |
| `EcosWorld` | Gera chão, contêineres, toldos, neon, pistas, drones e Silva |
| `EcosCharacter` | Gabo: câmera, movimento, vigilância, interação |
| `EcosDrone`, `EcosClue` | Inimigo e item |
| `EcosHUD` | Interface via Canvas |

## Próximos passos para chegar ao nível PlayStation

- Gabo e elenco via **MetaHuman**, a partir de `docs/public/personagens/`, e animações (Mixamo ou Control Rig).
- Chuva em **Niagara**, piso molhado com material de reflexo, Lumen e ray tracing ativados.
- Mapa real no editor (Vila da Ferrugem modelada), no lugar de cubos.
- Áudio por personagem (`scripts/daily_telegram/voices.py`) e trilha.
- Migrar o HUD para UMG e a entrada para Enhanced Input.
