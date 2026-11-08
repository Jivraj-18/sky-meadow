#pragma once

#include "CoreMinimal.h"
#include "Blueprint/UserWidget.h"
#include "PlatformerHUDWidget.generated.h"

class UHorizontalBox;
class UImage;
class UTextBlock;
class UTexture2D;
class UVerticalBox;

/**
 * In-game HUD: hearts for lives, coin counter, timer, a level title card, a "Checkpoint!" toast
 * and the Level Complete / Game Over banners. Builds its own layout, so a Blueprint subclass only
 * needs to set the icons and text below.
 */
UCLASS(Blueprintable)
class REALWORLDGAME_API UPlatformerHUDWidget : public UUserWidget
{
	GENERATED_BODY()

public:
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "HUD|Icons")
	TObjectPtr<UTexture2D> HeartFullIcon;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "HUD|Icons")
	TObjectPtr<UTexture2D> HeartEmptyIcon;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "HUD|Icons")
	TObjectPtr<UTexture2D> CoinIcon;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "HUD|Layout")
	float IconSize = 64.f;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "HUD|Layout")
	int32 FontSize = 34;

	/** Title card per level, keyed by map name (e.g. "Lvl_World1_1"). */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "HUD|Text")
	TMap<FString, FText> LevelTitles;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "HUD|Text")
	float TitleCardSeconds = 3.5f;

	/** Shown under the level title at the start. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "HUD|Text", meta = (MultiLine = true))
	FText ControlsHint = NSLOCTEXT("HUD", "Controls", "WASD move   Mouse look   Space jump (x3)   Shift dash\nR restart   Esc quit");

	/** What the HUD currently shows, for automated playtests. */
	UFUNCTION(BlueprintPure, Category = "HUD")
	FString GetDebugSummary() const;

protected:
	virtual TSharedRef<SWidget> RebuildWidget() override;
	virtual void NativeConstruct() override;
	virtual void NativeTick(const FGeometry& MyGeometry, float InDeltaTime) override;

private:
	void BuildLayout();
	UTextBlock* MakeText(int32 Size, const FLinearColor& Color);
	void ShowBanner(const FText& Title, const FText& Subtitle, const FLinearColor& Color);

	UFUNCTION()
	void HandleCheckpoint();

	UPROPERTY() TObjectPtr<UHorizontalBox> HeartsBox;
	UPROPERTY() TArray<TObjectPtr<UImage>> Hearts;
	UPROPERTY() TObjectPtr<UTextBlock> CoinText;
	UPROPERTY() TObjectPtr<UTextBlock> TimeText;
	UPROPERTY() TObjectPtr<UVerticalBox> BannerBox;
	UPROPERTY() TObjectPtr<UTextBlock> BannerTitle;
	UPROPERTY() TObjectPtr<UTextBlock> BannerSubtitle;
	UPROPERTY() TObjectPtr<UTextBlock> ToastText;

	int32 TotalCoins = 0;
	int32 ShownCoins = -1;
	int32 ShownLives = -1;
	float CoinPulse = 0.f;
	float HeartPulse = 0.f;
	float ToastTime = 0.f;
	float TitleTime = 0.f;
	bool bEndShown = false;
};
