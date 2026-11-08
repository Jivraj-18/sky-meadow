#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "KitEnemy.generated.h"

class UAnimSequence;
class UBoxComponent;
class USkeletalMesh;
class USkeletalMeshComponent;

/**
 * Patrolling enemy. Walks between its start and Patrol Offset (drag the diamond in the viewport).
 * Jump on it to squash it; touching it any other way costs the player a life.
 * Place it with its origin on the ground.
 */
UCLASS(Blueprintable)
class REALWORLDGAME_API AKitEnemy : public AActor
{
	GENERATED_BODY()

public:
	AKitEnemy();

	virtual void OnConstruction(const FTransform& Transform) override;
	virtual void BeginPlay() override;
	virtual void Tick(float DeltaSeconds) override;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Enemy|Look")
	TObjectPtr<USkeletalMesh> MeshAsset;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Enemy|Look")
	TObjectPtr<UAnimSequence> MoveAnim;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Enemy|Look")
	TObjectPtr<UAnimSequence> DeathAnim;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Enemy|Look", meta = (ClampMin = "0.01"))
	float KitScale = 0.5f;

	/** Turns the model to face its walking direction (kit models aren't all authored facing +X). */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Enemy|Look")
	float MeshYawOffset = -90.f;

	/** Half-size of the touch box, before Kit Scale. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Enemy|Look")
	FVector BodyExtent = FVector(45.f, 45.f, 40.f);

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Enemy|Patrol", meta = (MakeEditWidget = true))
	FVector PatrolOffset = FVector(400.f, 0.f, 0.f);

	/** Walking speed in cm/s. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Enemy|Patrol", meta = (ClampMin = "0.0"))
	float Speed = 150.f;

	/** Upward speed given to the player after a stomp. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Enemy|Combat")
	float StompBounce = 900.f;

	/** How far below the enemy's top the player's feet may be and still count as a stomp. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Enemy|Combat")
	float StompTolerance = 35.f;

	UFUNCTION(BlueprintPure, Category = "Enemy")
	bool IsDead() const { return bDead; }

protected:
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Enemy")
	TObjectPtr<USceneComponent> Root;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Enemy")
	TObjectPtr<UBoxComponent> Body;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Enemy")
	TObjectPtr<USkeletalMeshComponent> Mesh;

	UFUNCTION()
	void OnOverlap(UPrimitiveComponent* OverlappedComp, AActor* Other, UPrimitiveComponent* OtherComp,
		int32 OtherBodyIndex, bool bFromSweep, const FHitResult& Sweep);

private:
	void Stomp(class ACharacter* By);

	FVector StartLocation;
	float PatrolAlpha = 0.f;
	float Direction = 1.f;
	bool bDead = false;
};
