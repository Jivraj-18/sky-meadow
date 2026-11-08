#include "PlatformerSubsystem.h"

#include "Engine/Engine.h"
#include "EngineUtils.h"
#include "GameFramework/Character.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/PlayerStart.h"
#include "Components/AudioComponent.h"
#include "KitEffect.h"
#include "Kismet/GameplayStatics.h"
#include "Sound/SoundBase.h"
#include "TimerManager.h"

UPlatformerSubsystem* UPlatformerSubsystem::Get(const UObject* WorldContext)
{
	const UWorld* World = GEngine ? GEngine->GetWorldFromContextObject(WorldContext, EGetWorldErrorMode::ReturnNull) : nullptr;
	return World ? World->GetSubsystem<UPlatformerSubsystem>() : nullptr;
}

void UPlatformerSubsystem::OnWorldBeginPlay(UWorld& InWorld)
{
	Super::OnWorldBeginPlay(InWorld);
	StartTime = InWorld.GetTimeSeconds();

	const UPlatformerAudioSettings* Audio = GetDefault<UPlatformerAudioSettings>();
	if (USoundBase* Track = Audio->LevelMusic.LoadSynchronous())
	{
		Music = UGameplayStatics::SpawnSound2D(this, Track, Audio->MusicVolume, 1.f, 0.f, nullptr, false, false);
		UE_LOG(LogTemp, Log, TEXT("Platformer: music %s"), *Track->GetName());
	}
}

void UPlatformerSubsystem::PlaySound(const UObject* WorldContext, EPlatformerSound Sound)
{
	const UPlatformerAudioSettings* Audio = GetDefault<UPlatformerAudioSettings>();
	if (USoundBase* Asset = Audio->GetSound(Sound))
	{
		UGameplayStatics::PlaySound2D(WorldContext, Asset, Audio->EffectsVolume);
		UE_LOG(LogTemp, Log, TEXT("Platformer: sound %s"), *UEnum::GetValueAsString(Sound));
	}
}

void UPlatformerSubsystem::SpawnEffect(const UObject* WorldContext, EPlatformerEffect Effect, FVector Location)
{
	UWorld* World = GEngine ? GEngine->GetWorldFromContextObject(WorldContext, EGetWorldErrorMode::ReturnNull) : nullptr;
	if (TSubclassOf<AKitEffect> Class = GetDefault<UPlatformerEffectsSettings>()->GetEffect(Effect); World && Class)
	{
		World->SpawnActor<AKitEffect>(Class, Location, FRotator::ZeroRotator);
	}
}

void UPlatformerSubsystem::StopMusic()
{
	if (Music)
	{
		Music->FadeOut(0.3f, 0.f);
		Music = nullptr;
	}
}

void UPlatformerSubsystem::SetRespawnLocation(const FVector& Location)
{
	RespawnLocation = Location;
	bHasRespawnLocation = true;
	PlaySound(this, EPlatformerSound::Checkpoint);
	OnCheckpointReached.Broadcast();
}

float UPlatformerSubsystem::GetElapsedTime() const
{
	const double Now = EndTime >= 0.0 ? EndTime : GetWorld()->GetTimeSeconds();
	return static_cast<float>(Now - StartTime);
}

void UPlatformerSubsystem::AddCoins(int32 Amount)
{
	Coins += Amount;
	PlaySound(this, EPlatformerSound::Coin);
	UE_LOG(LogTemp, Log, TEXT("Platformer: coins=%d"), Coins);
	OnCoinsChanged.Broadcast(Coins);
}

bool UPlatformerSubsystem::IsInvulnerable() const
{
	return GetWorld()->GetTimeSeconds() < InvulnerableUntil;
}

bool UPlatformerSubsystem::LoseLife(APawn* Pawn)
{
	if (!Pawn || bGameOver || bLevelComplete || IsInvulnerable())
	{
		return false;
	}

	Lives = FMath::Max(0, Lives - 1);
	UE_LOG(LogTemp, Log, TEXT("Platformer: lost a life, lives=%d"), Lives);
	OnLivesChanged.Broadcast(Lives);

	if (Lives == 0)
	{
		bGameOver = true;
		EndTime = GetWorld()->GetTimeSeconds();
		StopMusic();
		PlaySound(this, EPlatformerSound::GameOver);
		UE_LOG(LogTemp, Log, TEXT("Platformer: GAME OVER coins=%d"), Coins);
		OnGameOver.Broadcast();
		Pawn->DisableInput(nullptr);
		GetWorld()->GetTimerManager().SetTimer(RestartTimer, this, &UPlatformerSubsystem::RestartLevel,
			RestartDelaySeconds);
		return true;
	}

	PlaySound(this, EPlatformerSound::Hurt);
	InvulnerableUntil = GetWorld()->GetTimeSeconds() + InvulnerableSeconds;
	RespawnPlayer(Pawn);
	return true;
}

void UPlatformerSubsystem::RestartLevel()
{
	UE_LOG(LogTemp, Log, TEXT("Platformer: restarting level"));
	UGameplayStatics::OpenLevel(this, FName(*UGameplayStatics::GetCurrentLevelName(this)));
}

void UPlatformerSubsystem::RespawnPlayer(APawn* Pawn)
{
	if (!Pawn)
	{
		return;
	}

	FVector Location = RespawnLocation;
	FRotator Rotation = Pawn->GetActorRotation();
	if (!bHasRespawnLocation)
	{
		for (TActorIterator<APlayerStart> It(GetWorld()); It; ++It)
		{
			Location = It->GetActorLocation();
			Rotation = It->GetActorRotation();
			break;
		}
	}

	if (ACharacter* Character = Cast<ACharacter>(Pawn))
	{
		Character->GetCharacterMovement()->StopMovementImmediately();
	}
	Pawn->TeleportTo(Location, Rotation);
	++RespawnCount;
	UE_LOG(LogTemp, Log, TEXT("Platformer: respawn #%d at %s"), RespawnCount, *Location.ToString());
}

void UPlatformerSubsystem::CompleteLevel()
{
	if (bLevelComplete)
	{
		return;
	}
	bLevelComplete = true;
	EndTime = GetWorld()->GetTimeSeconds();
	StopMusic();
	PlaySound(this, EPlatformerSound::LevelComplete);
	UE_LOG(LogTemp, Log, TEXT("Platformer: LEVEL COMPLETE coins=%d"), Coins);
	OnLevelComplete.Broadcast();
}
