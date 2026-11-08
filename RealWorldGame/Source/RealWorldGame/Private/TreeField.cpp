#include "TreeField.h"

// InstancedSkinnedMeshComponent is tagged UE_EXPERIMENTAL; with our build settings that becomes a
// [[deprecated]] attribute clang rejects in this position. Accept the experimental API here.
#undef UE_EXPERIMENTAL
#define UE_EXPERIMENTAL(Version, Message)
#include "Components/InstancedSkinnedMeshComponent.h"
#include "Engine/SkinnedAsset.h"

ATreeField::ATreeField()
{
	Instances = CreateDefaultSubobject<UInstancedSkinnedMeshComponent>(TEXT("Instances"));
	SetRootComponent(Instances);
}

void ATreeField::OnConstruction(const FTransform& Transform)
{
	Super::OnConstruction(Transform);
	Rebuild();
}

void ATreeField::Rebuild()
{
	Instances->ClearInstances();
	Instances->SetSkinnedAssetAndUpdate(Tree);
	Instances->SetCastShadow(bCastShadows);
	if (!Tree || Rows <= 0 || Columns <= 0)
	{
		return;
	}

	FRandomStream Random(Seed);
	TArray<FTransform> Transforms;
	TArray<int32> AnimationIndices;
	Transforms.Reserve(Rows * Columns);
	// Centre the grid on the actor.
	const FVector2D Origin(-(Columns - 1) * Spacing * 0.5f, -(Rows - 1) * Spacing * 0.5f);
	for (int32 Row = 0; Row < Rows; ++Row)
	{
		for (int32 Col = 0; Col < Columns; ++Col)
		{
			const FVector Location(
				Origin.X + Col * Spacing + Random.FRandRange(-Jitter, Jitter) * Spacing,
				Origin.Y + Row * Spacing + Random.FRandRange(-Jitter, Jitter) * Spacing,
				0.f);
			const FRotator Rotation(0.f, Random.FRandRange(0.f, 360.f), 0.f);
			const float Scale = Random.FRandRange(ScaleRange.X, ScaleRange.Y);
			Transforms.Emplace(Rotation, Location, FVector(Scale));
			AnimationIndices.Add(INDEX_NONE);  // no animation clip; wind drives the motion
		}
	}
	Instances->AddInstances(Transforms, AnimationIndices, /*bShouldReturnIds=*/false, /*bWorldSpace=*/false);
}
