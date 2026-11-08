#include "PlatformerHUDWidget.h"

#include "Blueprint/WidgetTree.h"
#include "Components/CanvasPanel.h"
#include "Components/CanvasPanelSlot.h"
#include "Components/HorizontalBox.h"
#include "Components/HorizontalBoxSlot.h"
#include "Components/Image.h"
#include "Components/TextBlock.h"
#include "Components/VerticalBox.h"
#include "Components/VerticalBoxSlot.h"
#include "EngineUtils.h"
#include "KitBlocks.h"
#include "Kismet/GameplayStatics.h"
#include "PlatformerSubsystem.h"

namespace
{
	const FLinearColor White(1.f, 1.f, 1.f);
	const FLinearColor Gold(1.f, 0.78f, 0.2f);
	const FLinearColor Green(0.45f, 1.f, 0.35f);
	const FLinearColor Red(1.f, 0.25f, 0.25f);

	FText FormatTime(float Seconds)
	{
		const int32 Total = FMath::FloorToInt(Seconds);
		return FText::FromString(FString::Printf(TEXT("%d:%02d"), Total / 60, Total % 60));
	}

	UCanvasPanelSlot* Place(UCanvasPanelSlot* Slot, FVector2D Anchor, FVector2D Offset)
	{
		Slot->SetAnchors(FAnchors(Anchor.X, Anchor.Y));
		Slot->SetAlignment(Anchor);
		Slot->SetPosition(Offset);
		Slot->SetAutoSize(true);
		return Slot;
	}
}

TSharedRef<SWidget> UPlatformerHUDWidget::RebuildWidget()
{
	if (WidgetTree && !WidgetTree->RootWidget)
	{
		BuildLayout();
	}
	return Super::RebuildWidget();
}

UTextBlock* UPlatformerHUDWidget::MakeText(int32 Size, const FLinearColor& Color)
{
	UTextBlock* Text = WidgetTree->ConstructWidget<UTextBlock>();
	FSlateFontInfo Font = Text->GetFont();
	Font.Size = Size;
	Font.TypefaceFontName = TEXT("Bold");
	Font.OutlineSettings.OutlineSize = FMath::Max(2, Size / 10);
	Font.OutlineSettings.OutlineColor = FLinearColor(0.08f, 0.05f, 0.04f);
	Text->SetFont(Font);
	Text->SetColorAndOpacity(FSlateColor(Color));
	Text->SetShadowOffset(FVector2D(0.f, 3.f));
	Text->SetShadowColorAndOpacity(FLinearColor(0.f, 0.f, 0.f, 0.45f));
	return Text;
}

void UPlatformerHUDWidget::BuildLayout()
{
	UCanvasPanel* Root = WidgetTree->ConstructWidget<UCanvasPanel>();
	WidgetTree->RootWidget = Root;

	// Top left: hearts, then coins underneath.
	UVerticalBox* Stats = WidgetTree->ConstructWidget<UVerticalBox>();
	Place(Root->AddChildToCanvas(Stats), FVector2D(0.f, 0.f), FVector2D(36.f, 28.f));

	HeartsBox = WidgetTree->ConstructWidget<UHorizontalBox>();
	Stats->AddChildToVerticalBox(HeartsBox);
	for (int32 i = 0; i < UPlatformerSubsystem::StartingLives; ++i)
	{
		UImage* Heart = WidgetTree->ConstructWidget<UImage>();
		Heart->SetDesiredSizeOverride(FVector2D(IconSize));
		UHorizontalBoxSlot* HeartSlot = HeartsBox->AddChildToHorizontalBox(Heart);
		HeartSlot->SetPadding(FMargin(0.f, 0.f, 6.f, 0.f));
		HeartSlot->SetVerticalAlignment(VAlign_Center);
		Hearts.Add(Heart);
	}

	UHorizontalBox* CoinRow = WidgetTree->ConstructWidget<UHorizontalBox>();
	Stats->AddChildToVerticalBox(CoinRow)->SetPadding(FMargin(0.f, 8.f, 0.f, 0.f));
	UImage* Coin = WidgetTree->ConstructWidget<UImage>();
	Coin->SetDesiredSizeOverride(FVector2D(IconSize * 0.9f));
	if (CoinIcon)
	{
		Coin->SetBrushFromTexture(CoinIcon);
	}
	// Centre, don't fill: a filled slot stretches the icon to the text height (oval coin).
	CoinRow->AddChildToHorizontalBox(Coin)->SetVerticalAlignment(VAlign_Center);
	CoinText = MakeText(FontSize, White);
	UHorizontalBoxSlot* CoinTextSlot = CoinRow->AddChildToHorizontalBox(CoinText);
	CoinTextSlot->SetVerticalAlignment(VAlign_Center);
	CoinTextSlot->SetPadding(FMargin(10.f, 0.f, 0.f, 0.f));

	// Top right: timer.
	TimeText = MakeText(FontSize, White);
	Place(Root->AddChildToCanvas(TimeText), FVector2D(1.f, 0.f), FVector2D(-40.f, 34.f));

	// Upper middle: short toasts ("Checkpoint!").
	ToastText = MakeText(FontSize + 8, Green);
	ToastText->SetJustification(ETextJustify::Center);
	ToastText->SetVisibility(ESlateVisibility::Hidden);
	Place(Root->AddChildToCanvas(ToastText), FVector2D(0.5f, 0.22f), FVector2D::ZeroVector);

	// Centre: title card and end-of-level banners.
	BannerBox = WidgetTree->ConstructWidget<UVerticalBox>();
	Place(Root->AddChildToCanvas(BannerBox), FVector2D(0.5f, 0.42f), FVector2D::ZeroVector);
	BannerTitle = MakeText(FontSize * 2 + 8, Gold);
	BannerTitle->SetJustification(ETextJustify::Center);
	BannerBox->AddChildToVerticalBox(BannerTitle)->SetHorizontalAlignment(HAlign_Center);
	BannerSubtitle = MakeText(FontSize, White);
	BannerSubtitle->SetJustification(ETextJustify::Center);
	BannerBox->AddChildToVerticalBox(BannerSubtitle)->SetHorizontalAlignment(HAlign_Center);
	BannerBox->SetVisibility(ESlateVisibility::Hidden);
}

void UPlatformerHUDWidget::NativeConstruct()
{
	Super::NativeConstruct();

	for (TActorIterator<ACoinPickup> It(GetWorld()); It; ++It)
	{
		++TotalCoins;
	}

	if (UPlatformerSubsystem* Run = UPlatformerSubsystem::Get(this))
	{
		Run->OnCheckpointReached.AddUniqueDynamic(this, &UPlatformerHUDWidget::HandleCheckpoint);
	}

	const FString MapName = UGameplayStatics::GetCurrentLevelName(this);
	if (const FText* Title = LevelTitles.Find(MapName))
	{
		ShowBanner(*Title, ControlsHint, Gold);
		TitleTime = TitleCardSeconds;
	}
}

void UPlatformerHUDWidget::ShowBanner(const FText& Title, const FText& Subtitle, const FLinearColor& Color)
{
	BannerTitle->SetText(Title);
	BannerTitle->SetColorAndOpacity(FSlateColor(Color));
	BannerSubtitle->SetText(Subtitle);
	BannerSubtitle->SetVisibility(Subtitle.IsEmpty() ? ESlateVisibility::Collapsed : ESlateVisibility::HitTestInvisible);
	BannerBox->SetRenderOpacity(1.f);
	BannerBox->SetVisibility(ESlateVisibility::HitTestInvisible);
}

void UPlatformerHUDWidget::HandleCheckpoint()
{
	ToastText->SetText(NSLOCTEXT("HUD", "Checkpoint", "Checkpoint!"));
	ToastText->SetVisibility(ESlateVisibility::HitTestInvisible);
	ToastTime = 1.6f;
}

void UPlatformerHUDWidget::NativeTick(const FGeometry& MyGeometry, float InDeltaTime)
{
	Super::NativeTick(MyGeometry, InDeltaTime);
	const UPlatformerSubsystem* Run = UPlatformerSubsystem::Get(this);
	if (!Run)
	{
		return;
	}

	// Hearts: full for each life left; pulse when one is lost.
	if (Run->GetLives() != ShownLives)
	{
		if (ShownLives > Run->GetLives())
		{
			HeartPulse = 1.f;
		}
		ShownLives = Run->GetLives();
		for (int32 i = 0; i < Hearts.Num(); ++i)
		{
			if (UTexture2D* Icon = i < ShownLives ? HeartFullIcon : HeartEmptyIcon)
			{
				Hearts[i]->SetBrushFromTexture(Icon);
				Hearts[i]->SetDesiredSizeOverride(FVector2D(IconSize));
			}
		}
	}
	HeartPulse = FMath::Max(0.f, HeartPulse - InDeltaTime * 2.5f);
	HeartsBox->SetRenderScale(FVector2D(1.f + 0.25f * HeartPulse));

	// Coins: count with a little pop when one is collected.
	if (Run->GetCoins() != ShownCoins)
	{
		CoinPulse = ShownCoins >= 0 ? 1.f : 0.f;
		ShownCoins = Run->GetCoins();
		CoinText->SetText(FText::FromString(FString::Printf(TEXT("x %d"), ShownCoins)));
	}
	CoinPulse = FMath::Max(0.f, CoinPulse - InDeltaTime * 4.f);
	CoinText->SetRenderScale(FVector2D(1.f + 0.35f * CoinPulse));

	TimeText->SetText(FText::Format(NSLOCTEXT("HUD", "Time", "TIME {0}"), FormatTime(Run->GetElapsedTime())));

	if (ToastTime > 0.f)
	{
		ToastTime -= InDeltaTime;
		ToastText->SetRenderOpacity(FMath::Clamp(ToastTime / 0.4f, 0.f, 1.f));
		if (ToastTime <= 0.f)
		{
			ToastText->SetVisibility(ESlateVisibility::Hidden);
		}
	}

	if (!bEndShown && Run->IsLevelComplete())
	{
		bEndShown = true;
		ShowBanner(NSLOCTEXT("HUD", "Complete", "LEVEL COMPLETE!"),
			FText::Format(NSLOCTEXT("HUD", "CompleteStats", "Coins {0} / {1}     Time {2}\nPress R to play again"),
				FText::AsNumber(Run->GetCoins()), FText::AsNumber(TotalCoins), FormatTime(Run->GetElapsedTime())),
			Gold);
	}
	else if (!bEndShown && Run->IsGameOver())
	{
		bEndShown = true;
		ShowBanner(NSLOCTEXT("HUD", "GameOver", "GAME OVER"), NSLOCTEXT("HUD", "Retry", "Try again!"), Red);
	}
	else if (!bEndShown && TitleTime > 0.f)
	{
		TitleTime -= InDeltaTime;
		BannerBox->SetRenderOpacity(FMath::Clamp(TitleTime / 0.6f, 0.f, 1.f));
		if (TitleTime <= 0.f)
		{
			BannerBox->SetVisibility(ESlateVisibility::Hidden);
		}
	}
}

FString UPlatformerHUDWidget::GetDebugSummary() const
{
	const bool bBanner = BannerBox && BannerBox->GetVisibility() != ESlateVisibility::Hidden;
	const bool bToast = ToastText && ToastText->GetVisibility() != ESlateVisibility::Hidden;
	return FString::Printf(TEXT("hearts=%d coins='%s' time='%s' total_coins=%d banner='%s|%s' toast='%s'"),
		ShownLives, CoinText ? *CoinText->GetText().ToString() : TEXT(""),
		TimeText ? *TimeText->GetText().ToString() : TEXT(""), TotalCoins,
		bBanner ? *BannerTitle->GetText().ToString() : TEXT(""),
		bBanner ? *BannerSubtitle->GetText().ToString() : TEXT(""),
		bToast ? *ToastText->GetText().ToString() : TEXT(""));
}
