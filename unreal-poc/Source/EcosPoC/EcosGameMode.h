#pragma once
#include "CoreMinimal.h"
#include "GameFramework/GameModeBase.h"
#include "EcosGameMode.generated.h"

/** Regras da PoC: monta a Vila da Ferrugem por codigo e guarda o estado da partida. */
UCLASS()
class AEcosGameMode : public AGameModeBase
{
	GENERATED_BODY()
public:
	AEcosGameMode();

	TArray<FBox> HideZones; // toldos: area onde o scanner nao ve Gabo
	FVector SilvaLoc = FVector(0.f, -2800.f, 0.f);
	bool bOver = false;
	bool bWon = false;

	bool IsHidden(const FVector& P) const;

protected:
	virtual void BeginPlay() override;
};
