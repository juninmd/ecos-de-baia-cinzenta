#include "EcosCharacter.h"
#include "EcosClue.h"
#include "EcosGameMode.h"
#include "Camera/CameraComponent.h"
#include "Components/CapsuleComponent.h"
#include "Components/InputComponent.h"
#include "Components/StaticMeshComponent.h"
#include "EngineUtils.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/SpringArmComponent.h"
#include "Kismet/GameplayStatics.h"
#include "Materials/MaterialInstanceDynamic.h"

AEcosCharacter::AEcosCharacter()
{
	PrimaryActorTick.bCanEverTick = true;
	bUseControllerRotationYaw = false;
	GetCharacterMovement()->bOrientRotationToMovement = true;
	GetCharacterMovement()->RotationRate = FRotator(0.f, 540.f, 0.f);
	GetCharacterMovement()->MaxWalkSpeed = 460.f; // exoesqueleto: mais lento que o normal
	GetCharacterMovement()->JumpZVelocity = 0.f;

	Boom = CreateDefaultSubobject<USpringArmComponent>(TEXT("Boom"));
	Boom->SetupAttachment(RootComponent);
	Boom->TargetArmLength = 720.f;
	Boom->bUsePawnControlRotation = true;
	Cam = CreateDefaultSubobject<UCameraComponent>(TEXT("Cam"));
	Cam->SetupAttachment(Boom, USpringArmComponent::SocketName);

	static ConstructorHelpers::FObjectFinder<UStaticMesh> Cyl(TEXT("/Engine/BasicShapes/Cylinder.Cylinder"));
	static ConstructorHelpers::FObjectFinder<UStaticMesh> Sph(TEXT("/Engine/BasicShapes/Sphere.Sphere"));
	auto MakePart = [this](const TCHAR* Name, UStaticMesh* Mesh, FVector Loc, FVector Scale) {
		auto* C = CreateDefaultSubobject<UStaticMeshComponent>(Name);
		C->SetupAttachment(RootComponent);
		C->SetStaticMesh(Mesh);
		C->SetRelativeLocation(Loc);
		C->SetRelativeScale3D(Scale);
		C->SetCollisionEnabled(ECollisionEnabled::NoCollision);
		return C;
	};
	Body = MakePart(TEXT("Body"), Cyl.Object, FVector(0, 0, -10), FVector(0.6f, 0.6f, 1.5f));
	Head = MakePart(TEXT("Head"), Sph.Object, FVector(0, 0, 85), FVector(0.3f, 0.3f, 0.3f));
}

void AEcosCharacter::BeginPlay()
{
	Super::BeginPlay();
	SetActorLocation(SpawnPoint);
	if (Controller) Controller->SetControlRotation(FRotator(-28.f, 180.f, 0.f));
	auto Tint = [this](UStaticMeshComponent* C, FLinearColor Col) {
		if (auto* M = C->CreateAndSetMaterialInstanceDynamic(0)) M->SetVectorParameterValue(TEXT("Color"), Col);
	};
	Tint(Body, FLinearColor(0.72f, 0.60f, 0.42f)); // sobretudo bege
	Tint(Head, FLinearColor(0.79f, 0.63f, 0.48f));
	Say(TEXT("Gabo: Cinco pistas. Fique fora da luz dos drones."), 5.f);
}

void AEcosCharacter::Say(const FString& Text, float Seconds)
{
	Message = Text;
	MessageTime = Seconds;
}

void AEcosCharacter::Tick(float Dt)
{
	Super::Tick(Dt);
	auto* GM = GetWorld()->GetAuthGameMode<AEcosGameMode>();
	if (!GM || GM->bOver) return;

	bHidden = GM->IsHidden(GetActorLocation());
	const bool bExposed = bSeen && !bHidden;
	Alert = FMath::Clamp(Alert + (bExposed ? Dt / 0.9f : -Dt * 0.8f), 0.f, 1.f);
	bSeen = false;
	Invuln = FMath::Max(0.f, Invuln - Dt);
	MessageTime -= Dt;
	if (Alert >= 1.f && Invuln <= 0.f) Hurt(GM);

	Prompt.Empty();
	for (TActorIterator<AEcosClue> It(GetWorld()); It; ++It)
		if (FVector::Dist2D(It->GetActorLocation(), GetActorLocation()) < 240.f) Prompt = TEXT("E: inspecionar");
	if (FVector::Dist2D(GM->SilvaLoc, GetActorLocation()) < 320.f) Prompt = TEXT("E: falar com Silva");
}

void AEcosCharacter::Hurt(AEcosGameMode* GM)
{
	Alert = 0.f;
	Invuln = 2.f;
	if (--Memory <= 0)
	{
		GM->bOver = true;
		GM->bWon = false;
		return;
	}
	TeleportTo(SpawnPoint, GetActorRotation());
	Say(TEXT("Alerta: o scanner da Aeterna te pegou. Uma lembranca some."), 4.f);
}

void AEcosCharacter::Interact()
{
	auto* GM = GetWorld()->GetAuthGameMode<AEcosGameMode>();
	if (!GM || GM->bOver) return;
	for (TActorIterator<AEcosClue> It(GetWorld()); It; ++It)
	{
		if (FVector::Dist2D(It->GetActorLocation(), GetActorLocation()) < 240.f)
		{
			++Clues;
			Say(It->Title + TEXT(": ") + It->Text, 7.f);
			It->Destroy();
			return;
		}
	}
	if (FVector::Dist2D(GM->SilvaLoc, GetActorLocation()) < 320.f)
	{
		if (Clues < 5) Say(FString::Printf(TEXT("Silva: So %d pistas, inspetor. Procure o resto."), Clues), 4.f);
		else { GM->bOver = true; GM->bWon = true; }
	}
}

void AEcosCharacter::RestartGame()
{
	UGameplayStatics::OpenLevel(this, FName(*GetWorld()->GetName()));
}

void AEcosCharacter::MoveForward(float V)
{
	if (!Controller || FMath::IsNearlyZero(V)) return;
	const FRotator Yaw(0.f, Controller->GetControlRotation().Yaw, 0.f);
	AddMovementInput(FRotationMatrix(Yaw).GetUnitAxis(EAxis::X), V);
}

void AEcosCharacter::MoveRight(float V)
{
	if (!Controller || FMath::IsNearlyZero(V)) return;
	const FRotator Yaw(0.f, Controller->GetControlRotation().Yaw, 0.f);
	AddMovementInput(FRotationMatrix(Yaw).GetUnitAxis(EAxis::Y), V);
}

void AEcosCharacter::SetupPlayerInputComponent(UInputComponent* Input)
{
	Input->BindAxis("MoveForward", this, &AEcosCharacter::MoveForward);
	Input->BindAxis("MoveRight", this, &AEcosCharacter::MoveRight);
	Input->BindAxis("Turn", this, &APawn::AddControllerYawInput);
	Input->BindAxis("LookUp", this, &APawn::AddControllerPitchInput);
	Input->BindAction("Interact", IE_Pressed, this, &AEcosCharacter::Interact);
	Input->BindAction("Restart", IE_Pressed, this, &AEcosCharacter::RestartGame);
}
