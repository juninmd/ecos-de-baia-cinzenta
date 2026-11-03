#include "EcosWorld.h"
#include "EcosClue.h"
#include "EcosDrone.h"
#include "EcosGameMode.h"
#include "Components/LightComponent.h"
#include "Components/PointLightComponent.h"
#include "Engine/DirectionalLight.h"
#include "Engine/ExponentialHeightFog.h"
#include "Engine/PointLight.h"
#include "Engine/StaticMeshActor.h"
#include "Components/ExponentialHeightFogComponent.h"
#include "Materials/MaterialInstanceDynamic.h"

namespace
{
	// Coordenadas do mapa em metros (x, z do prototipo web). 1 m = 100 uu.
	const FVector2D Keep[] = { {0, 28}, {0, -28}, {-18, 18}, {15, 12}, {-22, -6}, {20, -12}, {4, -20},
	                           {-12, 8}, {12, 4}, {-4, -14}, {22, -20} };
	const FVector2D CluePos[] = { {-18, 18}, {15, 12}, {-22, -6}, {20, -12}, {4, -20} };
	const FVector2D Canopy[] = { {-12, 8}, {12, 4}, {-4, -14}, {22, -20} };
	struct FClueText { const TCHAR* Title; const TCHAR* Text; };
	const FClueText Texts[] = {
		{ TEXT("O corpo"), TEXT("Dois olhos de vidro encaram o ceu. Troca limpa, feita por quem sabia o que fazia.") },
		{ TEXT("Pegadas na lama"), TEXT("A chuva ja levou metade do chao. Fotografe antes que leve a outra metade.") },
		{ TEXT("A cortina que se mexe"), TEXT("Terceiro conteiner. Alguem viu tudo e escolheu o silencio.") },
		{ TEXT("Cafe frio"), TEXT("Copo com a tampa no lugar. Quem esteve aqui nao ficou para tomar.") },
		{ TEXT("Selo da Aeterna"), TEXT("COMPRE FELICIDADE, COMPRE AETERNA. Gravado por dentro da palpebra de vidro.") } };

	AStaticMeshActor* Shape(UWorld* W, const TCHAR* MeshPath, FVector Loc, FVector Scale, FLinearColor Col)
	{
		auto* A = W->SpawnActor<AStaticMeshActor>(Loc, FRotator::ZeroRotator);
		A->SetMobility(EComponentMobility::Movable);
		auto* C = A->GetStaticMeshComponent();
		C->SetStaticMesh(LoadObject<UStaticMesh>(nullptr, MeshPath));
		A->SetActorScale3D(Scale);
		auto* Base = LoadObject<UMaterialInterface>(nullptr, TEXT("/Engine/BasicShapes/BasicShapeMaterial.BasicShapeMaterial"));
		auto* M = UMaterialInstanceDynamic::Create(Base, A);
		M->SetVectorParameterValue(TEXT("Color"), Col);
		C->SetMaterial(0, M);
		return A;
	}

	AStaticMeshActor* Cube(UWorld* W, FVector Loc, FVector S, FLinearColor C)
	{ return Shape(W, TEXT("/Engine/BasicShapes/Cube.Cube"), Loc, S, C); }

	void Neon(UWorld* W, FVector Loc, FLinearColor Col)
	{
		auto* L = W->SpawnActor<APointLight>(Loc, FRotator::ZeroRotator);
		L->SetMobility(EComponentMobility::Movable);
		if (auto* P = Cast<UPointLightComponent>(L->GetLightComponent()))
		{
			P->SetLightColor(Col);
			P->SetIntensity(60000.f);
			P->SetAttenuationRadius(3000.f);
		}
	}

	bool NearKeep(float X, float Z, float Rx, float Rz)
	{
		for (const FVector2D& K : Keep)
			if (FMath::Abs(X - K.X) < Rx + 4.f && FMath::Abs(Z - K.Y) < Rz + 4.f) return true;
		return false;
	}
}

void EcosWorld::Build(AEcosGameMode* GM)
{
	UWorld* W = GM->GetWorld();

	// Atmosfera: luz de lua fria, neblina e chao molhado escuro.
	auto* Sun = W->SpawnActor<ADirectionalLight>(FVector::ZeroVector, FRotator(-50.f, 30.f, 0.f));
	Sun->SetMobility(EComponentMobility::Movable);
	Sun->GetLightComponent()->SetIntensity(2.f);
	Sun->GetLightComponent()->SetLightColor(FLinearColor(0.35f, 0.5f, 0.7f));
	if (auto* Fog = W->SpawnActor<AExponentialHeightFog>(FVector::ZeroVector, FRotator::ZeroRotator))
		Fog->GetComponent()->SetFogDensity(0.02f);
	Cube(W, FVector(0, 0, -10), FVector(120, 120, 0.2f), FLinearColor(0.02f, 0.03f, 0.04f));

	Neon(W, FVector(-1600, -1000, 500), FLinearColor(0.25f, 0.82f, 0.79f));
	Neon(W, FVector(1800, 600, 500), FLinearColor(1.f, 0.24f, 0.56f));
	Neon(W, FVector(0, -2400, 500), FLinearColor(0.94f, 0.65f, 0.23f));

	// Conteineres enferrujados, posicao sorteada com semente fixa (mesma Vila a cada partida).
	FRandomStream R(11);
	const FLinearColor Rust[] = { {0.54f, 0.29f, 0.18f}, {0.42f, 0.23f, 0.17f}, {0.24f, 0.35f, 0.37f}, {0.35f, 0.29f, 0.23f} };
	TArray<FVector4> Placed;
	for (int32 i = 0; i < 120 && Placed.Num() < 40; ++i)
	{
		const bool bAlong = R.FRand() < 0.5f;
		const float Wd = bAlong ? 6.f : 2.5f, Dp = bAlong ? 2.5f : 6.f;
		const float X = (R.FRand() - 0.5f) * 76.f, Z = (R.FRand() - 0.5f) * 76.f;
		if (NearKeep(X, Z, Wd / 2, Dp / 2)) continue;
		bool bHit = false;
		for (const FVector4& P : Placed)
			if (FMath::Abs(X - P.X) < (Wd + P.Z) / 2 + 1.6f && FMath::Abs(Z - P.Y) < (Dp + P.W) / 2 + 1.6f) bHit = true;
		if (bHit) continue;
		Placed.Add(FVector4(X, Z, Wd, Dp));
		const FLinearColor C = Rust[R.RandRange(0, 3)];
		Cube(W, FVector(X * 100, Z * 100, 130), FVector(Wd, Dp, 2.6f), C);
		if (R.FRand() < 0.3f) Cube(W, FVector(X * 100, Z * 100, 390), FVector(Wd, Dp, 2.6f), C * 0.8f);
	}

	// Skyline distante em anel.
	for (int32 i = 0; i < 26; ++i)
	{
		const float A = i / 26.f * 2.f * PI, H = 24.f + R.FRand() * 34.f;
		Cube(W, FVector(FMath::Cos(A) * 6200, FMath::Sin(A) * 6200, H * 50), FVector(9, 9, H), FLinearColor(0.03f, 0.05f, 0.06f));
	}

	// Toldos: teto, lampada e zona de sombra.
	for (const FVector2D& C : Canopy)
	{
		Cube(W, FVector(C.X * 100, C.Y * 100, 250), FVector(4, 3, 0.15f), FLinearColor(0.11f, 0.16f, 0.18f));
		Neon(W, FVector(C.X * 100, C.Y * 100, 220), FLinearColor(0.94f, 0.65f, 0.23f));
		GM->HideZones.Add(FBox(FVector(C.X * 100 - 200, C.Y * 100 - 150, 0), FVector(C.X * 100 + 200, C.Y * 100 + 150, 300)));
	}

	// Pistas, drones e Silva.
	for (int32 i = 0; i < 5; ++i)
	{
		auto* Clue = W->SpawnActor<AEcosClue>(FVector(CluePos[i].X * 100, CluePos[i].Y * 100, 100), FRotator::ZeroRotator);
		Clue->Title = Texts[i].Title;
		Clue->Text = Texts[i].Text;
	}
	auto* D1 = W->SpawnActor<AEcosDrone>();
	D1->Center = FVector2D(-800, 1000); D1->Radius = 1000.f; D1->AngularSpeed = 0.35f; D1->Phase = PI;
	auto* D2 = W->SpawnActor<AEcosDrone>();
	D2->bLine = true; D2->LineZ = -400.f; D2->LineX0 = -2800.f; D2->LineX1 = 2800.f; D2->LineSpeed = 420.f;
	auto* D3 = W->SpawnActor<AEcosDrone>();
	D3->Center = FVector2D(1200, -1600); D3->Radius = 900.f; D3->AngularSpeed = -0.4f;

	Cube(W, FVector(GM->SilvaLoc.X, GM->SilvaLoc.Y, 80), FVector(0.6f, 0.6f, 1.6f), FLinearColor(0.19f, 0.32f, 0.48f));
	Shape(W, TEXT("/Engine/BasicShapes/Sphere.Sphere"), FVector(GM->SilvaLoc.X, GM->SilvaLoc.Y, 180), FVector(0.3f), FLinearColor(0.79f, 0.63f, 0.48f));
}
