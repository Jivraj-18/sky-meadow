#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "KitBlock.generated.h"

class UStaticMeshComponent;

/**
 * Base for every level building block. Pick the look with Mesh Asset and Kit Scale in the
 * Details panel; subclasses add behaviour (moving, collecting, launching...).
 */
UCLASS(Blueprintable)
class REALWORLDGAME_API AKitBlock : public AActor
{
	GENERATED_BODY()

public:
	AKitBlock();

	virtual void OnConstruction(const FTransform& Transform) override;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Block")
	TObjectPtr<UStaticMesh> MeshAsset;

	/** Quaternius kit models are authored ~2x Unreal scale; 0.5 makes a cube 1 m. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Block", meta = (ClampMin = "0.01"))
	float KitScale = 0.5f;

protected:
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Block")
	TObjectPtr<USceneComponent> Root;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Block")
	TObjectPtr<UStaticMeshComponent> Mesh;

	/** True when the overlapping actor is a pawn controlled by a human player. */
	static bool IsPlayerPawn(const AActor* Actor);
};
