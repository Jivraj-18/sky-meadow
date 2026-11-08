#include "KitEnemy.h"

#include "Animation/AnimSequence.h"
#include "Components/BoxComponent.h"
#include "Components/CapsuleComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "GameFramework/Character.h"
#include "PlatformerSubsystem.h"

AKitEnemy::AKitEnemy()
{
	PrimaryActorTick.bCanEverTick = true;

	Root = CreateDefaultSubobject<USceneComponent>(TEXT("Root"));
	Root->SetMobility(EComponentMobility::Movable);
	SetRootComponent(Root);

	Body = CreateDefaultSubobject<UBoxComponent>(TEXT("Body"));
	Body->SetupAttachment(Root);
	Body->SetCollisionProfileName(TEXT("OverlapAllDynamic"));
	Body->OnComponentBeginOverlap.AddDynamic(this, &AKitEnemy::OnOverlap);

	Mesh = CreateDefaultSubobject<USkeletalMeshComponent>(TEXT("Mesh"));
	Mesh->SetupAttachment(Root);
	Mesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);
}

void AKitEnemy::OnConstruction(const FTransform& Transform)
{
	Super::OnConstruction(Transform);
	Mesh->SetSkeletalMesh(MeshAsset);
	Mesh->SetRelativeScale3D(FVector(KitScale));
	Mesh->SetRelativeRotation(FRotator(0.f, MeshYawOffset, 0.f));

	// Origin sits on the ground: the touch box rests on it.
	const FVector Extent = BodyExtent * KitScale * 2.f;
	Body->SetBoxExtent(Extent);
	Body->SetRelativeLocation(FVector(0.f, 0.f, Extent.Z));
}

void AKitEnemy::BeginPlay()
{
	Super::BeginPlay();
	StartLocation = GetActorLocation();
	if (MoveAnim)
	{
		Mesh->PlayAnimation(MoveAnim, true);
	}
}

void AKitEnemy::Tick(float DeltaSeconds)
{
	Super::Tick(DeltaSeconds);

	const float Length = PatrolOffset.Size();
	if (bDead || Length < 1.f || Speed <= 0.f)
	{
		return;
	}

	PatrolAlpha += Direction * Speed * DeltaSeconds / Length;
	if (PatrolAlpha >= 1.f || PatrolAlpha <= 0.f)
	{
		PatrolAlpha = FMath::Clamp(PatrolAlpha, 0.f, 1.f);
		Direction = -Direction;
	}

	SetActorLocation(StartLocation + PatrolOffset * PatrolAlpha);
	const FVector Heading = PatrolOffset.GetSafeNormal() * Direction;
	SetActorRotation(FRotator(0.f, Heading.Rotation().Yaw, 0.f));
}

void AKitEnemy::OnOverlap(UPrimitiveComponent*, AActor* Other, UPrimitiveComponent* OtherComp, int32, bool, const FHitResult&)
{
	ACharacter* Player = Cast<ACharacter>(Other);
	// Only the player's capsule counts; its animated mesh can poke out of the capsule.
	if (bDead || !Player || !Player->IsPlayerControlled() || OtherComp != Player->GetCapsuleComponent())
	{
		return;
	}

	const float Feet = Player->GetActorLocation().Z - Player->GetCapsuleComponent()->GetScaledCapsuleHalfHeight();
	const float Top = Body->GetComponentLocation().Z + Body->GetScaledBoxExtent().Z;
	const float VelocityZ = Player->GetVelocity().Z;
	// Generous, like most platformers: coming down with the body's centre above the enemy's top
	// is a stomp. A fast fall can sink well past the top within one frame before the overlap fires.
	const bool bAbove = Feet >= Top - StompTolerance || Player->GetActorLocation().Z >= Top;
	if (VelocityZ <= 0.f && bAbove)
	{
		Stomp(Player);
	}
	else if (UPlatformerSubsystem* Run = GetWorld()->GetSubsystem<UPlatformerSubsystem>())
	{
		UE_LOG(LogTemp, Log, TEXT("Platformer: hit by %s (feet=%.0f top=%.0f vz=%.0f player=%s enemy=%s)"),
			*GetActorNameOrLabel(), Feet, Top, VelocityZ, *Player->GetActorLocation().ToCompactString(),
			*GetActorLocation().ToCompactString());
		Run->LoseLife(Player);
	}
}

void AKitEnemy::Stomp(ACharacter* By)
{
	bDead = true;
	Body->SetCollisionEnabled(ECollisionEnabled::NoCollision);
	By->LaunchCharacter(FVector(0.f, 0.f, StompBounce), false, true);
	UPlatformerSubsystem::PlaySound(this, EPlatformerSound::Stomp);
	UPlatformerSubsystem::SpawnEffect(this, EPlatformerEffect::Stomp, GetActorLocation() + FVector(0.f, 0.f, 20.f));
	// Cartoon squash: flatten and widen.
	Mesh->SetRelativeScale3D(FVector(KitScale * 1.35f, KitScale * 1.35f, KitScale * 0.35f));
	if (DeathAnim)
	{
		Mesh->PlayAnimation(DeathAnim, false);
	}
	SetLifeSpan(1.2f);
	UE_LOG(LogTemp, Log, TEXT("Platformer: stomped %s"), *GetActorNameOrLabel());
}
