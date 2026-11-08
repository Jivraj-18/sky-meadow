#pragma once

#include "CoreMinimal.h"
#include "Engine/DeveloperSettings.h"
#include "PlatformerAudioSettings.generated.h"

class USoundBase;

UENUM(BlueprintType)
enum class EPlatformerSound : uint8
{
	Jump,
	Coin,
	Stomp,
	Hurt,
	JumpPad,
	Checkpoint,
	LevelComplete,
	GameOver,
};

/** Game sounds and music: Project Settings > Game > Platformer Audio. */
UCLASS(Config = Game, DefaultConfig, meta = (DisplayName = "Platformer Audio"))
class REALWORLDGAME_API UPlatformerAudioSettings : public UDeveloperSettings
{
	GENERATED_BODY()

public:
	virtual FName GetCategoryName() const override { return TEXT("Game"); }

	UPROPERTY(Config, EditAnywhere, Category = "Sound Effects")
	TSoftObjectPtr<USoundBase> Jump;

	UPROPERTY(Config, EditAnywhere, Category = "Sound Effects")
	TSoftObjectPtr<USoundBase> Coin;

	UPROPERTY(Config, EditAnywhere, Category = "Sound Effects")
	TSoftObjectPtr<USoundBase> Stomp;

	UPROPERTY(Config, EditAnywhere, Category = "Sound Effects")
	TSoftObjectPtr<USoundBase> Hurt;

	UPROPERTY(Config, EditAnywhere, Category = "Sound Effects")
	TSoftObjectPtr<USoundBase> JumpPad;

	UPROPERTY(Config, EditAnywhere, Category = "Sound Effects")
	TSoftObjectPtr<USoundBase> Checkpoint;

	UPROPERTY(Config, EditAnywhere, Category = "Sound Effects")
	TSoftObjectPtr<USoundBase> LevelComplete;

	UPROPERTY(Config, EditAnywhere, Category = "Sound Effects")
	TSoftObjectPtr<USoundBase> GameOver;

	UPROPERTY(Config, EditAnywhere, Category = "Sound Effects", meta = (ClampMin = "0.0", ClampMax = "2.0"))
	float EffectsVolume = 1.f;

	/** Loops for the whole level; stops at level complete or game over. */
	UPROPERTY(Config, EditAnywhere, Category = "Music")
	TSoftObjectPtr<USoundBase> LevelMusic;

	UPROPERTY(Config, EditAnywhere, Category = "Music", meta = (ClampMin = "0.0", ClampMax = "2.0"))
	float MusicVolume = 0.55f;

	USoundBase* GetSound(EPlatformerSound Sound) const;
};
