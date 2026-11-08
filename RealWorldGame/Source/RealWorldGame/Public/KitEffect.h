#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "KitEffect.generated.h"

class UStaticMesh;
class UStaticMeshComponent;

/**
 * Lightweight burst effect made of kit meshes (cloud puffs, star sparkles): each piece flies out,
 * spins, falls with gravity and shrinks away. Make a Blueprint per look and set the values below.
 */
UCLASS(Blueprintable)
class REALWORLDGAME_API AKitEffect : public AActor
{
	GENERATED_BODY()

public:
	AKitEffect();

	virtual void BeginPlay() override;
	virtual void Tick(float DeltaSeconds) override;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Effect")
	TObjectPtr<UStaticMesh> PieceMesh;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Effect", meta = (ClampMin = "1", ClampMax = "40"))
	int32 Count = 8;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Effect")
	float Lifetime = 0.6f;

	/** Outward speed range (cm/s). */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Effect")
	FVector2D Speed = FVector2D(150.f, 350.f);

	/** 0 = flat ring along the ground, 1 = straight up. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Effect", meta = (ClampMin = "0.0", ClampMax = "1.0"))
	float UpBias = 0.3f;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Effect")
	float Gravity = 600.f;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Effect")
	float StartScale = 0.12f;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Effect")
	float EndScale = 0.f;

	/** Spin in degrees per second. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Effect")
	float Spin = 360.f;

	/** Slows pieces down over time (0 = no drag). */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Effect")
	float Drag = 2.f;

private:
	struct FPiece
	{
		TObjectPtr<UStaticMeshComponent> Mesh;
		FVector Velocity;
		FRotator SpinRate;
	};
	TArray<FPiece> Pieces;
	float Age = 0.f;
};
