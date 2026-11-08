#pragma once

#include "CoreMinimal.h"
#include "Engine/DeveloperSettings.h"
#include "PlatformerEffectsSettings.generated.h"

class AKitEffect;

UENUM(BlueprintType)
enum class EPlatformerEffect : uint8
{
	CoinCollect,
	Stomp,
	Land,
	Checkpoint,
	JumpPad,
	Hurt,
};

/** Burst effects for game events: Project Settings > Game > Platformer Effects. */
UCLASS(Config = Game, DefaultConfig, meta = (DisplayName = "Platformer Effects"))
class REALWORLDGAME_API UPlatformerEffectsSettings : public UDeveloperSettings
{
	GENERATED_BODY()

public:
	virtual FName GetCategoryName() const override { return TEXT("Game"); }

	UPROPERTY(Config, EditAnywhere, Category = "Effects") TSoftClassPtr<AKitEffect> CoinCollect;
	UPROPERTY(Config, EditAnywhere, Category = "Effects") TSoftClassPtr<AKitEffect> Stomp;
	UPROPERTY(Config, EditAnywhere, Category = "Effects") TSoftClassPtr<AKitEffect> Land;
	UPROPERTY(Config, EditAnywhere, Category = "Effects") TSoftClassPtr<AKitEffect> Checkpoint;
	UPROPERTY(Config, EditAnywhere, Category = "Effects") TSoftClassPtr<AKitEffect> JumpPad;
	UPROPERTY(Config, EditAnywhere, Category = "Effects") TSoftClassPtr<AKitEffect> Hurt;

	/** Landings faster than this (cm/s, downward) kick up dust. */
	UPROPERTY(Config, EditAnywhere, Category = "Effects")
	float LandDustSpeed = 550.f;

	TSubclassOf<AKitEffect> GetEffect(EPlatformerEffect Effect) const;
};
