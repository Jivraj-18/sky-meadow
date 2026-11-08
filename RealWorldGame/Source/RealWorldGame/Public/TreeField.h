#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "TreeField.generated.h"

class UInstancedSkinnedMeshComponent;
class USkinnedAsset;

/**
 * Plants a grid of one tree model as GPU instances (one draw batch, wind still works).
 * Set Tree, Rows and Columns in the Details panel; each tree gets a seeded random offset,
 * rotation and size so the grid reads as a forest.
 */
UCLASS(Blueprintable)
class REALWORLDGAME_API ATreeField : public AActor
{
	GENERATED_BODY()

public:
	ATreeField();

	virtual void OnConstruction(const FTransform& Transform) override;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Tree Field")
	TObjectPtr<USkinnedAsset> Tree;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Tree Field", meta = (ClampMin = "0", ClampMax = "1000"))
	int32 Rows = 1;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Tree Field", meta = (ClampMin = "0", ClampMax = "1000"))
	int32 Columns = 1;

	/** Distance between grid cells in cm. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Tree Field", meta = (ClampMin = "10"))
	float Spacing = 600.f;

	/** Random offset within a cell, as a fraction of Spacing (0 = perfect grid). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Tree Field", meta = (ClampMin = "0", ClampMax = "0.5"))
	float Jitter = 0.35f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Tree Field")
	FVector2D ScaleRange = FVector2D(0.8f, 1.2f);

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Tree Field")
	int32 Seed = 1;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Tree Field")
	bool bCastShadows = true;

	/** Rebuilds the instances (also happens automatically when a property changes in the editor). */
	UFUNCTION(BlueprintCallable, CallInEditor, Category = "Tree Field")
	void Rebuild();

	UFUNCTION(BlueprintPure, Category = "Tree Field")
	int32 GetTreeCount() const { return Rows * Columns; }

protected:
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Tree Field")
	TObjectPtr<UInstancedSkinnedMeshComponent> Instances;
};
