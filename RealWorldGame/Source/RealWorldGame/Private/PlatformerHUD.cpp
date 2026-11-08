#include "PlatformerHUD.h"

#include "GameFramework/Pawn.h"
#include "GameFramework/PlayerController.h"
#include "Kismet/GameplayStatics.h"
#include "Kismet/KismetSystemLibrary.h"
#include "Misc/CommandLine.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "PlatformerHUDWidget.h"
#include "UnrealClient.h"

APlatformerHUD::APlatformerHUD()
{
	PrimaryActorTick.bCanEverTick = true;
}

void APlatformerHUD::BeginPlay()
{
	Super::BeginPlay();
	if (WidgetClass && GetOwningPlayerController())
	{
		Widget = CreateWidget<UPlatformerHUDWidget>(GetOwningPlayerController(), WidgetClass);
		Widget->AddToViewport();
	}

	bSmokeTest = FParse::Param(FCommandLine::Get(), TEXT("smoketest"));
	if (bSmokeTest && !FParse::Value(FCommandLine::Get(), TEXT("smoketestdir="), SmokeTestDir))
	{
		SmokeTestDir = FPaths::ProjectSavedDir() / TEXT("SmokeTest");
	}
}

void APlatformerHUD::Tick(float DeltaSeconds)
{
	Super::Tick(DeltaSeconds);
	APlayerController* PC = GetOwningPlayerController();
	if (!PC)
	{
		return;
	}

	if (PC->WasInputKeyJustPressed(EKeys::R))
	{
		UGameplayStatics::OpenLevel(this, FName(*UGameplayStatics::GetCurrentLevelName(this)));
		return;
	}
	if (PC->WasInputKeyJustPressed(EKeys::Escape))
	{
		UKismetSystemLibrary::QuitGame(this, PC, EQuitPreference::Quit, false);
		return;
	}

	if (bSmokeTest)
	{
		TickSmokeTest(DeltaSeconds);
	}
}

void APlatformerHUD::TickSmokeTest(float DeltaSeconds)
{
	SmokeTime += DeltaSeconds;
	if (FParse::Param(FCommandLine::Get(), TEXT("smoketestnolook")))
	{
		GetOwningPlayerController()->SetIgnoreLookInput(true);
	}
	if (FMath::FloorToInt(SmokeTime * 2.f) != FMath::FloorToInt((SmokeTime - DeltaSeconds) * 2.f))
	{
		SmokePitchLog += FString::Printf(TEXT("%.1f:%.0f/%.0f "), SmokeTime,
			GetOwningPlayerController()->GetControlRotation().Pitch, GetOwningPlayerController()->GetControlRotation().Yaw);
	}
	if (APawn* Pawn = GetOwningPawn(); Pawn && SmokeTime > 4.f && SmokeTime < 7.f)
	{
		Pawn->AddMovementInput(FVector::ForwardVector, 1.f);  // run toward the first coins
	}

	// Screenshots: title card, then mid-run.
	const float ShotTimes[] = {1.5f, 6.5f};
	if (SmokeShots < UE_ARRAY_COUNT(ShotTimes) && SmokeTime >= ShotTimes[SmokeShots])
	{
		FScreenshotRequest::RequestScreenshot(SmokeTestDir / FString::Printf(TEXT("smoketest_%d.png"), SmokeShots), true, false);
		++SmokeShots;
	}

	if (SmokeTime >= 9.f)
	{
		const FString Summary = FString::Printf(TEXT("map=%s fps=%.0f %s\npitch/yaw: %s\n"),
			*UGameplayStatics::GetCurrentLevelName(this), 1.f / FMath::Max(DeltaSeconds, 0.001f),
			Widget ? *Widget->GetDebugSummary() : TEXT("no-hud"), *SmokePitchLog);
		FFileHelper::SaveStringToFile(Summary, *(SmokeTestDir / TEXT("smoketest.txt")));
		bSmokeTest = false;
		UKismetSystemLibrary::QuitGame(this, GetOwningPlayerController(), EQuitPreference::Quit, false);
	}
}
