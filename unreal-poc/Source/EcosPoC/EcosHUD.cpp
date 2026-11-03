#include "EcosHUD.h"
#include "Engine/Canvas.h"
#include "Engine/Engine.h"
#include "EcosCharacter.h"
#include "EcosGameMode.h"

void AEcosHUD::DrawHUD()
{
	Super::DrawHUD();
	auto* Gabo = Cast<AEcosCharacter>(GetOwningPawn());
	auto* GM = GetWorld()->GetAuthGameMode<AEcosGameMode>();
	if (!Gabo || !GM || !Canvas) return;

	UFont* F = GEngine->GetMediumFont();
	const FLinearColor Amber(0.94f, 0.65f, 0.23f), Ink(0.84f, 0.88f, 0.86f), Alarm(1.f, 0.3f, 0.36f);
	const float W = Canvas->SizeX, H = Canvas->SizeY;

	DrawText(FString::Printf(TEXT("MEMORIA %d/3     PISTAS %d/5"), Gabo->Memory, Gabo->Clues), Amber, 24, 20, F, 1.4f);
	DrawText(TEXT("VIGILANCIA"), Ink, W - 330, 20, F, 1.0f);
	DrawRect(FLinearColor(0.1f, 0.15f, 0.17f), W - 220, 24, 190, 10);
	DrawRect(Alarm, W - 220, 24, 190 * Gabo->Alert, 10);
	if (Gabo->bHidden) DrawText(TEXT("NA SOMBRA"), FLinearColor(0.25f, 0.82f, 0.79f), W - 330, 44, F, 1.0f);

	if (!Gabo->Prompt.IsEmpty()) DrawText(Gabo->Prompt, Amber, W * 0.5f - 90, H - 150, F, 1.3f);
	if (Gabo->MessageTime > 0.f && !GM->bOver)
	{
		DrawRect(FLinearColor(0.f, 0.f, 0.f, 0.7f), 20, H - 110, W - 40, 80);
		DrawText(Gabo->Message, Ink, 40, H - 90, F, 1.2f);
	}
	if (GM->bOver)
	{
		DrawRect(FLinearColor(0.f, 0.f, 0.f, 0.8f), 0, 0, W, H);
		DrawText(GM->bWon ? TEXT("CASO ABERTO") : TEXT("MEMORIA APAGADA"), Amber, W * 0.5f - 200, H * 0.4f, F, 3.f);
		DrawText(GM->bWon ? TEXT("Silva olha o selo e nao pergunta nada.") : TEXT("O scanner levou as tres lembrancas."),
			Ink, W * 0.5f - 240, H * 0.5f, F, 1.3f);
		DrawText(TEXT("Pressione R para recomecar"), Ink, W * 0.5f - 170, H * 0.58f, F, 1.2f);
	}
}
