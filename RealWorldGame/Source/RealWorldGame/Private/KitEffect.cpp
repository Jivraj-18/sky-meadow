#include "KitEffect.h"

#include "Components/StaticMeshComponent.h"

AKitEffect::AKitEffect()
{
	PrimaryActorTick.bCanEverTick = true;
	SetRootComponent(CreateDefaultSubobject<USceneComponent>(TEXT("Root")));
	RootComponent->SetMobility(EComponentMobility::Movable);
}

void AKitEffect::BeginPlay()
{
	Super::BeginPlay();
	SetLifeSpan(Lifetime + 0.1f);
	if (!PieceMesh)
	{
		return;
	}

	for (int32 i = 0; i < Count; ++i)
	{
		UStaticMeshComponent* Mesh = NewObject<UStaticMeshComponent>(this);
		Mesh->SetMobility(EComponentMobility::Movable);
		Mesh->SetStaticMesh(PieceMesh);
		Mesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);
		Mesh->SetCastShadow(false);
		Mesh->SetupAttachment(RootComponent);
		Mesh->RegisterComponent();
		Mesh->SetRelativeScale3D(FVector(StartScale));
		Mesh->SetRelativeRotation(FRotator(0.f, FMath::FRandRange(0.f, 360.f), 0.f));

		// Evenly spread around the circle with a little jitter, tilted up by UpBias.
		const float Angle = 2.f * PI * (i + FMath::FRandRange(-0.3f, 0.3f)) / Count;
		const FVector Flat(FMath::Cos(Angle), FMath::Sin(Angle), 0.f);
		const FVector Dir = FMath::Lerp(Flat, FVector::UpVector, UpBias).GetSafeNormal();
		const FRotator SpinRate(FMath::FRandRange(-Spin, Spin), FMath::FRandRange(-Spin, Spin), FMath::FRandRange(-Spin, Spin));
		Pieces.Add({Mesh, Dir * FMath::FRandRange(Speed.X, Speed.Y), SpinRate});
	}
}

void AKitEffect::Tick(float DeltaSeconds)
{
	Super::Tick(DeltaSeconds);
	Age += DeltaSeconds;
	const float Alpha = FMath::Clamp(Age / FMath::Max(Lifetime, 0.01f), 0.f, 1.f);
	// Ease-out so pieces pop to full size and stay readable before shrinking away.
	const float Scale = FMath::Lerp(StartScale, EndScale, Alpha * Alpha);

	for (FPiece& Piece : Pieces)
	{
		Piece.Velocity *= FMath::Max(0.f, 1.f - Drag * DeltaSeconds);
		Piece.Velocity.Z -= Gravity * DeltaSeconds;
		Piece.Mesh->AddRelativeLocation(Piece.Velocity * DeltaSeconds);
		Piece.Mesh->AddRelativeRotation(Piece.SpinRate * DeltaSeconds);
		Piece.Mesh->SetRelativeScale3D(FVector(FMath::Max(Scale, 0.001f)));
	}
}
