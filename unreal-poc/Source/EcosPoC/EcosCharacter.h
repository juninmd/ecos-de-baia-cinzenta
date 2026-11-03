#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "EcosCharacter.generated.h"

class AEcosGameMode;
class UCameraComponent;
class USpringArmComponent;
class UStaticMeshComponent;

/** Gabo: terceira pessoa, 3 lembrancas, barra de vigilancia. */
UCLASS()
class AEcosCharacter : public ACharacter
{
	GENERATED_BODY()
public:
	AEcosCharacter();

	int32 Memory = 3;
	int32 Clues = 0;
	float Alert = 0.f;
	bool bSeen = false;   // drones marcam a cada frame
	bool bHidden = false; // sob um toldo
	FString Prompt;
	FString Message;
	float MessageTime = 0.f;
	FVector SpawnPoint = FVector(0.f, 2800.f, 110.f);

	void Say(const FString& Text, float Seconds = 5.f);

protected:
	virtual void BeginPlay() override;
	virtual void Tick(float Dt) override;
	virtual void SetupPlayerInputComponent(UInputComponent* Input) override;

private:
	UPROPERTY() TObjectPtr<USpringArmComponent> Boom;
	UPROPERTY() TObjectPtr<UCameraComponent> Cam;
	UPROPERTY() TObjectPtr<UStaticMeshComponent> Body;
	UPROPERTY() TObjectPtr<UStaticMeshComponent> Head;
	float Invuln = 0.f;

	void MoveForward(float V);
	void MoveRight(float V);
	void Interact();
	void RestartGame();
	void Hurt(AEcosGameMode* GM);
};
