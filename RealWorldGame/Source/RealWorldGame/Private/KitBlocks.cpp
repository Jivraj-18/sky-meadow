#include "KitBlocks.h"

#include "Components/BoxComponent.h"
#include "Components/SphereComponent.h"
#include "Components/StaticMeshComponent.h"
#include "GameFramework/Character.h"
#include "PlatformerSubsystem.h"

// ---------------------------------------------------------------------------- AMovingPlatform

AMovingPlatform::AMovingPlatform()
{
	PrimaryActorTick.bCanEverTick = true;
	// Tick before characters so riders follow the platform without jitter.
	PrimaryActorTick.TickGroup = TG_PrePhysics;
	Root->SetMobility(EComponentMobility::Movable);
	Mesh->SetMobility(EComponentMobility::Movable);
}

void AMovingPlatform::BeginPlay()
{
	Super::BeginPlay();
	StartLocation = GetActorLocation();
}

void AMovingPlatform::Tick(float DeltaSeconds)
{
	Super::Tick(DeltaSeconds);
	Elapsed += DeltaSeconds;

	// One cycle: travel out, pause, travel back, pause.
	const float Cycle = 2.f * (TravelTime + PauseTime);
	const float T = FMath::Fmod(Elapsed, Cycle);
	float Alpha;
	if (T < TravelTime)
	{
		Alpha = T / TravelTime;
	}
	else if (T < TravelTime + PauseTime)
	{
		Alpha = 1.f;
	}
	else if (T < 2.f * TravelTime + PauseTime)
	{
		Alpha = 1.f - (T - TravelTime - PauseTime) / TravelTime;
	}
	else
	{
		Alpha = 0.f;
	}

	const FVector WorldOffset = GetActorTransform().TransformVectorNoScale(EndOffset);
	SetActorLocation(StartLocation + WorldOffset * FMath::InterpEaseInOut(0.f, 1.f, Alpha, 2.f));
}

// ---------------------------------------------------------------------------- ACoinPickup

ACoinPickup::ACoinPickup()
{
	PrimaryActorTick.bCanEverTick = true;
	Root->SetMobility(EComponentMobility::Movable);
	Mesh->SetMobility(EComponentMobility::Movable);
	Mesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);
	KitScale = 0.25f;

	Trigger = CreateDefaultSubobject<USphereComponent>(TEXT("Trigger"));
	Trigger->SetupAttachment(Root);
	Trigger->SetSphereRadius(45.f);
	Trigger->SetCollisionProfileName(TEXT("OverlapAllDynamic"));
	Trigger->OnComponentBeginOverlap.AddDynamic(this, &ACoinPickup::OnOverlap);
}

void ACoinPickup::BeginPlay()
{
	Super::BeginPlay();
	BaseMeshLocation = Mesh->GetRelativeLocation();
}

void ACoinPickup::Tick(float DeltaSeconds)
{
	Super::Tick(DeltaSeconds);
	Elapsed += DeltaSeconds;
	Mesh->AddRelativeRotation(FRotator(0.f, SpinDegreesPerSecond * DeltaSeconds, 0.f));
	Mesh->SetRelativeLocation(BaseMeshLocation + FVector(0.f, 0.f, BobHeight * FMath::Sin(Elapsed * 3.f)));
}

void ACoinPickup::OnOverlap(UPrimitiveComponent*, AActor* Other, UPrimitiveComponent*, int32, bool, const FHitResult&)
{
	if (!IsPlayerPawn(Other))
	{
		return;
	}
	if (UPlatformerSubsystem* Run = GetWorld()->GetSubsystem<UPlatformerSubsystem>())
	{
		Run->AddCoins(Value);
	}
	UPlatformerSubsystem::SpawnEffect(this, EPlatformerEffect::CoinCollect, Mesh->GetComponentLocation());
	Destroy();
}

// ---------------------------------------------------------------------------- AJumpPad

AJumpPad::AJumpPad()
{
	Trigger = CreateDefaultSubobject<UBoxComponent>(TEXT("Trigger"));
	Trigger->SetupAttachment(Root);
	Trigger->SetBoxExtent(FVector(45.f, 45.f, 30.f));
	Trigger->SetRelativeLocation(FVector(0.f, 0.f, 50.f));
	Trigger->SetCollisionProfileName(TEXT("OverlapAllDynamic"));
	Trigger->OnComponentBeginOverlap.AddDynamic(this, &AJumpPad::OnOverlap);
}

void AJumpPad::OnOverlap(UPrimitiveComponent*, AActor* Other, UPrimitiveComponent*, int32, bool, const FHitResult&)
{
	if (ACharacter* Character = Cast<ACharacter>(Other); Character && IsPlayerPawn(Other))
	{
		Character->LaunchCharacter(FVector(0.f, 0.f, LaunchSpeed), false, true);
		UPlatformerSubsystem::PlaySound(this, EPlatformerSound::JumpPad);
		UPlatformerSubsystem::SpawnEffect(this, EPlatformerEffect::JumpPad, GetActorLocation() + FVector(0.f, 0.f, 30.f));
	}
}

// ---------------------------------------------------------------------------- AGoalFlag

AGoalFlag::AGoalFlag()
{
	Trigger = CreateDefaultSubobject<UBoxComponent>(TEXT("Trigger"));
	Trigger->SetupAttachment(Root);
	Trigger->SetBoxExtent(FVector(80.f, 80.f, 120.f));
	Trigger->SetRelativeLocation(FVector(0.f, 0.f, 120.f));
	Trigger->SetCollisionProfileName(TEXT("OverlapAllDynamic"));
	Trigger->OnComponentBeginOverlap.AddDynamic(this, &AGoalFlag::OnOverlap);
}

void AGoalFlag::OnOverlap(UPrimitiveComponent*, AActor* Other, UPrimitiveComponent*, int32, bool, const FHitResult&)
{
	if (!IsPlayerPawn(Other))
	{
		return;
	}
	if (UPlatformerSubsystem* Run = GetWorld()->GetSubsystem<UPlatformerSubsystem>())
	{
		Run->CompleteLevel();
	}
}

// ---------------------------------------------------------------------------- AKillZone

AKillZone::AKillZone()
{
	Volume = CreateDefaultSubobject<UBoxComponent>(TEXT("Volume"));
	SetRootComponent(Volume);
	Volume->SetBoxExtent(FVector(5000.f, 5000.f, 100.f));
	Volume->SetCollisionProfileName(TEXT("OverlapAllDynamic"));
	Volume->OnComponentBeginOverlap.AddDynamic(this, &AKillZone::OnOverlap);
}

void AKillZone::OnOverlap(UPrimitiveComponent*, AActor* Other, UPrimitiveComponent*, int32, bool, const FHitResult&)
{
	if (APawn* Pawn = Cast<APawn>(Other); Pawn && Pawn->IsPlayerControlled())
	{
		if (UPlatformerSubsystem* Run = GetWorld()->GetSubsystem<UPlatformerSubsystem>())
		{
			// Falling costs a life; if invulnerable from a recent hit, just put them back.
			if (!Run->LoseLife(Pawn) && !Run->IsGameOver())
			{
				Run->RespawnPlayer(Pawn);
			}
		}
	}
}

// ---------------------------------------------------------------------------- ACheckpoint

ACheckpoint::ACheckpoint()
{
	Mesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);

	Trigger = CreateDefaultSubobject<UBoxComponent>(TEXT("Trigger"));
	Trigger->SetupAttachment(Root);
	Trigger->SetBoxExtent(FVector(80.f, 150.f, 120.f));
	Trigger->SetRelativeLocation(FVector(0.f, 0.f, 120.f));
	Trigger->SetCollisionProfileName(TEXT("OverlapAllDynamic"));
	Trigger->OnComponentBeginOverlap.AddDynamic(this, &ACheckpoint::OnOverlap);
}

void ACheckpoint::OnOverlap(UPrimitiveComponent*, AActor* Other, UPrimitiveComponent*, int32, bool, const FHitResult&)
{
	if (bActivated || !IsPlayerPawn(Other))
	{
		return;
	}
	if (UPlatformerSubsystem* Run = GetWorld()->GetSubsystem<UPlatformerSubsystem>())
	{
		bActivated = true;
		Run->SetRespawnLocation(GetActorTransform().TransformPosition(RespawnOffset));
		UPlatformerSubsystem::SpawnEffect(this, EPlatformerEffect::Checkpoint, GetActorLocation() + FVector(0.f, 0.f, 120.f));
		UE_LOG(LogTemp, Log, TEXT("Platformer: checkpoint %s reached"), *GetActorNameOrLabel());
	}
}
