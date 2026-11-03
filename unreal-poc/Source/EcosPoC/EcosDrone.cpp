#include "EcosDrone.h"
#include "Components/SpotLightComponent.h"
#include "Components/StaticMeshComponent.h"
#include "EcosCharacter.h"
#include "GameFramework/PlayerController.h"

AEcosDrone::AEcosDrone()
{
	PrimaryActorTick.bCanEverTick = true;
	Body = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Body"));
	RootComponent = Body;
	static ConstructorHelpers::FObjectFinder<UStaticMesh> Sph(TEXT("/Engine/BasicShapes/Sphere.Sphere"));
	Body->SetStaticMesh(Sph.Object);
	Body->SetRelativeScale3D(FVector(0.9f, 0.9f, 0.3f));
	Body->SetCollisionEnabled(ECollisionEnabled::NoCollision);

	Spot = CreateDefaultSubobject<USpotLightComponent>(TEXT("Spot"));
	Spot->SetupAttachment(Body);
	Spot->SetRelativeRotation(FRotator(-90.f, 0.f, 0.f));
	Spot->SetInnerConeAngle(18.f);
	Spot->SetOuterConeAngle(FMath::RadiansToDegrees(FMath::Atan(GroundRadius / Height)));
	Spot->SetIntensity(90000.f);
	Spot->SetAttenuationRadius(1600.f);
	Spot->SetLightColor(FLinearColor(0.68f, 0.91f, 1.f));
}

void AEcosDrone::Tick(float Dt)
{
	Super::Tick(Dt);
	T += Dt;
	FVector P;
	if (bLine)
	{
		const float L = LineX1 - LineX0;
		const float U = FMath::Fmod(T * LineSpeed, 2.f * L);
		P = FVector(LineX0 + (U < L ? U : 2.f * L - U), LineZ, Height);
	}
	else
	{
		const float A = T * AngularSpeed + Phase;
		P = FVector(Center.X + FMath::Cos(A) * Radius, Center.Y + FMath::Sin(A) * Radius, Height);
	}
	SetActorLocation(P);

	auto* PC = GetWorld()->GetFirstPlayerController();
	auto* Gabo = PC ? Cast<AEcosCharacter>(PC->GetPawn()) : nullptr;
	if (!Gabo) return;
	if (FVector::Dist2D(P, Gabo->GetActorLocation()) < GroundRadius) Gabo->bSeen = true;
	Spot->SetLightColor(Gabo->Alert > 0.1f ? FLinearColor(1.f, 0.3f, 0.36f) : FLinearColor(0.68f, 0.91f, 1.f));
}
