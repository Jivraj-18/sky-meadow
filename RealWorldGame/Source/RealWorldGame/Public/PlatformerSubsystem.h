#pragma once

#include "CoreMinimal.h"
#include "PlatformerAudioSettings.h"
#include "PlatformerEffectsSettings.h"
#include "Subsystems/WorldSubsystem.h"
#include "PlatformerSubsystem.generated.h"

DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnCoinsChanged, int32, Coins);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnLivesChanged, int32, Lives);
DECLARE_DYNAMIC_MULTICAST_DELEGATE(FOnLevelComplete);
DECLARE_DYNAMIC_MULTICAST_DELEGATE(FOnGameOver);
DECLARE_DYNAMIC_MULTICAST_DELEGATE(FOnCheckpointReached);

/** Per-level run state: coins, lives, respawn point, level completion and game over. */
UCLASS()
class REALWORLDGAME_API UPlatformerSubsystem : public UWorldSubsystem
{
	GENERATED_BODY()

public:
	static constexpr int32 StartingLives = 3;
	/** Seconds the player can't be hurt again after losing a life. */
	static constexpr float InvulnerableSeconds = 1.5f;
	/** Seconds between game over and the level restarting. */
	static constexpr float RestartDelaySeconds = 2.5f;

	/** Convenience accessor for Blueprints and editor Python (unreal.PlatformerSubsystem.get(world)). */
	UFUNCTION(BlueprintPure, Category = "Platformer", meta = (WorldContext = "WorldContext"))
	static UPlatformerSubsystem* Get(const UObject* WorldContext);

	/** Plays a game sound from Project Settings > Platformer Audio (2D, effects volume). */
	UFUNCTION(BlueprintCallable, Category = "Platformer", meta = (WorldContext = "WorldContext"))
	static void PlaySound(const UObject* WorldContext, EPlatformerSound Sound);

	/** Spawns a burst effect from Project Settings > Platformer Effects. */
	UFUNCTION(BlueprintCallable, Category = "Platformer", meta = (WorldContext = "WorldContext"))
	static void SpawnEffect(const UObject* WorldContext, EPlatformerEffect Effect, FVector Location);

	UFUNCTION(BlueprintCallable, Category = "Platformer")
	void AddCoins(int32 Amount);

	UFUNCTION(BlueprintPure, Category = "Platformer")
	int32 GetCoins() const { return Coins; }

	virtual void OnWorldBeginPlay(UWorld& InWorld) override;

	/** Called by checkpoints: future respawns happen here. */
	UFUNCTION(BlueprintCallable, Category = "Platformer")
	void SetRespawnLocation(const FVector& Location);

	/** Seconds since the level started; stops counting at level complete or game over. */
	UFUNCTION(BlueprintPure, Category = "Platformer")
	float GetElapsedTime() const;

	/**
	 * Costs the player a life (fall, enemy, hazard) and respawns them, or ends the game on the last
	 * life. Ignored while invulnerable; returns whether a life was lost.
	 */
	UFUNCTION(BlueprintCallable, Category = "Platformer")
	bool LoseLife(APawn* Pawn);

	/** Teleports the pawn to the last checkpoint, or the PlayerStart if none was reached. */
	UFUNCTION(BlueprintCallable, Category = "Platformer")
	void RespawnPlayer(APawn* Pawn);

	UFUNCTION(BlueprintCallable, Category = "Platformer")
	void CompleteLevel();

	UFUNCTION(BlueprintPure, Category = "Platformer")
	bool IsLevelComplete() const { return bLevelComplete; }

	UFUNCTION(BlueprintPure, Category = "Platformer")
	int32 GetLives() const { return Lives; }

	UFUNCTION(BlueprintPure, Category = "Platformer")
	bool IsGameOver() const { return bGameOver; }

	UFUNCTION(BlueprintPure, Category = "Platformer")
	bool IsInvulnerable() const;

	UFUNCTION(BlueprintPure, Category = "Platformer")
	int32 GetRespawnCount() const { return RespawnCount; }

	UPROPERTY(BlueprintAssignable, Category = "Platformer")
	FOnCoinsChanged OnCoinsChanged;

	UPROPERTY(BlueprintAssignable, Category = "Platformer")
	FOnLivesChanged OnLivesChanged;

	UPROPERTY(BlueprintAssignable, Category = "Platformer")
	FOnLevelComplete OnLevelComplete;

	UPROPERTY(BlueprintAssignable, Category = "Platformer")
	FOnGameOver OnGameOver;

	UPROPERTY(BlueprintAssignable, Category = "Platformer")
	FOnCheckpointReached OnCheckpointReached;

private:
	void RestartLevel();
	void StopMusic();

	UPROPERTY()
	TObjectPtr<class UAudioComponent> Music;

	int32 Coins = 0;
	int32 Lives = StartingLives;
	int32 RespawnCount = 0;
	bool bLevelComplete = false;
	bool bGameOver = false;
	bool bHasRespawnLocation = false;
	double InvulnerableUntil = 0.0;
	double StartTime = 0.0;
	double EndTime = -1.0;
	FVector RespawnLocation = FVector::ZeroVector;
	FTimerHandle RestartTimer;
};
