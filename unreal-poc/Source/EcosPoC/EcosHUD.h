#pragma once
#include "CoreMinimal.h"
#include "GameFramework/HUD.h"
#include "EcosHUD.generated.h"

/** HUD simples via Canvas: memoria, pistas, vigilancia, dialogo e fim de jogo. */
UCLASS()
class AEcosHUD : public AHUD
{
	GENERATED_BODY()
public:
	virtual void DrawHUD() override;
};
