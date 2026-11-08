#pragma once

#include "CoreMinimal.h"
#include "KitBlock.h"
#include "KitBlocks.generated.h"

class UBoxComponent;
class USphereComponent;

/** Platform that glides between its start and End Offset (drag the diamond in the viewport). */
UCLASS(Blueprintable)
class REALWORLDGAME_API AMovingPlatform : public AKitBlock
{
	GENERATED_BODY()

public:
	AMovingPlatform();

	virtual void BeginPlay() override;
	virtual void Tick(float DeltaSeconds) override;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Moving Platform", meta = (MakeEditWidget = true))
	FVector EndOffset = FVector(0.f, 400.f, 0.f);

	/** Seconds to travel one way. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Moving Platform", meta = (ClampMin = "0.1"))
	float TravelTime = 2.5f;

	/** Seconds to wait at each end. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Moving Platform", meta = (ClampMin = "0.0"))
	float PauseTime = 0.75f;

private:
	FVector StartLocation;
	float Elapsed = 0.f;
};

/** Spinning collectible worth Value coins. */
UCLASS(Blueprintable)
class REALWORLDGAME_API ACoinPickup : public AKitBlock
{
	GENERATED_BODY()

public:
	ACoinPickup();

	virtual void BeginPlay() override;
	virtual void Tick(float DeltaSeconds) override;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Coin", meta = (ClampMin = "1"))
	int32 Value = 1;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Coin")
	float SpinDegreesPerSecond = 180.f;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Coin")
	float BobHeight = 10.f;

protected:
	UPROPERTY(VisibleAnywhere, Category = "Coin")
	TObjectPtr<USphereComponent> Trigger;

	UFUNCTION()
	void OnOverlap(UPrimitiveComponent* OverlappedComp, AActor* Other, UPrimitiveComponent* OtherComp,
		int32 OtherBodyIndex, bool bFromSweep, const FHitResult& Sweep);

private:
	FVector BaseMeshLocation;
	float Elapsed = 0.f;
};

/** Launches the player upward on touch. */
UCLASS(Blueprintable)
class REALWORLDGAME_API AJumpPad : public AKitBlock
{
	GENERATED_BODY()

public:
	AJumpPad();

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Jump Pad")
	float LaunchSpeed = 1400.f;

protected:
	UPROPERTY(VisibleAnywhere, Category = "Jump Pad")
	TObjectPtr<UBoxComponent> Trigger;

	UFUNCTION()
	void OnOverlap(UPrimitiveComponent* OverlappedComp, AActor* Other, UPrimitiveComponent* OtherComp,
		int32 OtherBodyIndex, bool bFromSweep, const FHitResult& Sweep);
};

/** Reaching this completes the level. */
UCLASS(Blueprintable)
class REALWORLDGAME_API AGoalFlag : public AKitBlock
{
	GENERATED_BODY()

public:
	AGoalFlag();

protected:
	UPROPERTY(VisibleAnywhere, Category = "Goal")
	TObjectPtr<UBoxComponent> Trigger;

	UFUNCTION()
	void OnOverlap(UPrimitiveComponent* OverlappedComp, AActor* Other, UPrimitiveComponent* OtherComp,
		int32 OtherBodyIndex, bool bFromSweep, const FHitResult& Sweep);
};

/** Invisible volume (place below the course) that respawns a player who falls in. */
UCLASS(Blueprintable)
class REALWORLDGAME_API AKillZone : public AActor
{
	GENERATED_BODY()

public:
	AKillZone();

protected:
	UPROPERTY(VisibleAnywhere, Category = "Kill Zone")
	TObjectPtr<UBoxComponent> Volume;

	UFUNCTION()
	void OnOverlap(UPrimitiveComponent* OverlappedComp, AActor* Other, UPrimitiveComponent* OtherComp,
		int32 OtherBodyIndex, bool bFromSweep, const FHitResult& Sweep);
};

/** Touch to make this the respawn point. */
UCLASS(Blueprintable)
class REALWORLDGAME_API ACheckpoint : public AKitBlock
{
	GENERATED_BODY()

public:
	ACheckpoint();

	UFUNCTION(BlueprintPure, Category = "Checkpoint")
	bool IsActivated() const { return bActivated; }

protected:
	UPROPERTY(VisibleAnywhere, Category = "Checkpoint")
	TObjectPtr<UBoxComponent> Trigger;

	/** Where the player reappears, relative to the checkpoint. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Checkpoint", meta = (MakeEditWidget = true))
	FVector RespawnOffset = FVector(0.f, 0.f, 100.f);

	UFUNCTION()
	void OnOverlap(UPrimitiveComponent* OverlappedComp, AActor* Other, UPrimitiveComponent* OtherComp,
		int32 OtherBodyIndex, bool bFromSweep, const FHitResult& Sweep);

private:
	bool bActivated = false;
};
