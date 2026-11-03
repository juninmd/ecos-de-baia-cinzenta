#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "EcosDrone.generated.h"

class USpotLightComponent;
class UStaticMeshComponent;

/** Drone da Aeterna: patrulha em circulo ou em linha, projeta um cone de luz no chao. */
UCLASS()
class AEcosDrone : public AActor
{
	GENERATED_BODY()
public:
	AEcosDrone();

	bool bLine = false;
	FVector2D Center = FVector2D::ZeroVector; // circulo
	float Radius = 1000.f, AngularSpeed = 0.35f, Phase = 0.f;
	float LineZ = 0.f, LineX0 = 0.f, LineX1 = 0.f, LineSpeed = 420.f; // linha (eixo Y fixo = LineZ)
	float Height = 700.f;
	float GroundRadius = 350.f;

protected:
	virtual void Tick(float Dt) override;

private:
	UPROPERTY() TObjectPtr<UStaticMeshComponent> Body;
	UPROPERTY() TObjectPtr<USpotLightComponent> Spot;
	float T = 0.f;
};
