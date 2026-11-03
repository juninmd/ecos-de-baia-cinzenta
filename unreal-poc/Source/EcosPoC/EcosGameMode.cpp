#include "EcosGameMode.h"
#include "EcosCharacter.h"
#include "EcosHUD.h"
#include "EcosWorld.h"

AEcosGameMode::AEcosGameMode()
{
	DefaultPawnClass = AEcosCharacter::StaticClass();
	HUDClass = AEcosHUD::StaticClass();
}

void AEcosGameMode::BeginPlay()
{
	Super::BeginPlay();
	EcosWorld::Build(this);
}

bool AEcosGameMode::IsHidden(const FVector& P) const
{
	for (const FBox& Z : HideZones)
		if (P.X >= Z.Min.X && P.X <= Z.Max.X && P.Y >= Z.Min.Y && P.Y <= Z.Max.Y) return true;
	return false;
}
