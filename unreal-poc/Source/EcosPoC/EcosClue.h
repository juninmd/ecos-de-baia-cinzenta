#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "EcosClue.generated.h"

class UPointLightComponent;
class UStaticMeshComponent;

/** Pista: losango ambar que gira e brilha. Gabo coleta com E. */
UCLASS()
class AEcosClue : public AActor
{
	GENERATED_BODY()
public:
	AEcosClue();
	FString Title;
	FString Text;

protected:
	virtual void BeginPlay() override;
	virtual void Tick(float Dt) override;

private:
	UPROPERTY() TObjectPtr<UStaticMeshComponent> Gem;
	UPROPERTY() TObjectPtr<UPointLightComponent> Glow;
	float T = 0.f;
};
