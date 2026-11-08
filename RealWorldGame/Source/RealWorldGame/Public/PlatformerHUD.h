#pragma once

#include "CoreMinimal.h"
#include "GameFramework/HUD.h"
#include "PlatformerHUD.generated.h"

class UPlatformerHUDWidget;

/**
 * Puts the platformer HUD widget on screen and handles the global keys (R restart, Esc quit).
 * With -smoketest on the command line it runs a short unattended check of a packaged build:
 * walks forward, saves screenshots and a HUD summary to -smoketestdir, then quits.
 */
UCLASS(Blueprintable)
class REALWORLDGAME_API APlatformerHUD : public AHUD
{
	GENERATED_BODY()

public:
	APlatformerHUD();

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "HUD")
	TSubclassOf<UPlatformerHUDWidget> WidgetClass;

	UFUNCTION(BlueprintPure, Category = "HUD")
	UPlatformerHUDWidget* GetWidget() const { return Widget; }

protected:
	virtual void BeginPlay() override;
	virtual void Tick(float DeltaSeconds) override;

private:
	void TickSmokeTest(float DeltaSeconds);

	UPROPERTY()
	TObjectPtr<UPlatformerHUDWidget> Widget;

	bool bSmokeTest = false;
	FString SmokeTestDir;
	float SmokeTime = 0.f;
	int32 SmokeShots = 0;
	FString SmokePitchLog;  // camera pitch samples, to diagnose startup look input
};
