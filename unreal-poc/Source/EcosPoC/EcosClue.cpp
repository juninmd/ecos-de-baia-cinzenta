#include "EcosClue.h"
#include "Components/PointLightComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Materials/MaterialInstanceDynamic.h"

AEcosClue::AEcosClue()
{
	PrimaryActorTick.bCanEverTick = true;
	Gem = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Gem"));
	RootComponent = Gem;
	static ConstructorHelpers::FObjectFinder<UStaticMesh> Cube(TEXT("/Engine/BasicShapes/Cube.Cube"));
	Gem->SetStaticMesh(Cube.Object);
	Gem->SetRelativeScale3D(FVector(0.35f));
	Gem->SetCollisionEnabled(ECollisionEnabled::NoCollision);

	Glow = CreateDefaultSubobject<UPointLightComponent>(TEXT("Glow"));
	Glow->SetupAttachment(Gem);
	Glow->SetLightColor(FLinearColor(0.94f, 0.65f, 0.23f));
	Glow->SetIntensity(6000.f);
	Glow->SetAttenuationRadius(450.f);
}

void AEcosClue::BeginPlay()
{
	Super::BeginPlay();
	if (auto* M = Gem->CreateAndSetMaterialInstanceDynamic(0))
		M->SetVectorParameterValue(TEXT("Color"), FLinearColor(1.f, 0.55f, 0.1f));
}

void AEcosClue::Tick(float Dt)
{
	Super::Tick(Dt);
	T += Dt;
	AddActorWorldRotation(FRotator(0.f, 120.f * Dt, 0.f));
	Gem->SetRelativeLocation(FVector(0.f, 0.f, 12.f * FMath::Sin(T * 3.f)));
}
