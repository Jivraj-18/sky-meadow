#include "KitBlock.h"

#include "Components/StaticMeshComponent.h"
#include "GameFramework/Pawn.h"

AKitBlock::AKitBlock()
{
	PrimaryActorTick.bCanEverTick = false;

	Root = CreateDefaultSubobject<USceneComponent>(TEXT("Root"));
	SetRootComponent(Root);

	Mesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Mesh"));
	Mesh->SetupAttachment(Root);
	Mesh->SetCollisionProfileName(TEXT("BlockAll"));
}

void AKitBlock::OnConstruction(const FTransform& Transform)
{
	Super::OnConstruction(Transform);
	Mesh->SetStaticMesh(MeshAsset);
	Mesh->SetRelativeScale3D(FVector(KitScale));
}

bool AKitBlock::IsPlayerPawn(const AActor* Actor)
{
	const APawn* Pawn = Cast<APawn>(Actor);
	return Pawn && Pawn->IsPlayerControlled();
}
