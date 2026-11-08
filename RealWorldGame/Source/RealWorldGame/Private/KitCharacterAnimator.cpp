#include "KitCharacterAnimator.h"

#include "Animation/AnimSequence.h"
#include "Components/CapsuleComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Engine/SkeletalMesh.h"
#include "GameFramework/Character.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/SpringArmComponent.h"
#include "PlatformerSubsystem.h"

UKitCharacterAnimator::UKitCharacterAnimator()
{
	PrimaryComponentTick.bCanEverTick = true;
	PrimaryComponentTick.TickGroup = TG_PostPhysics;
}

void UKitCharacterAnimator::BeginPlay()
{
	Super::BeginPlay();
	Character = Cast<ACharacter>(GetOwner());
	if (!Character.IsValid() || !VisualMesh)
	{
		return;
	}

	// Swap the mannequin for the kit model; animations are driven from here, not an Anim BP.
	USkeletalMeshComponent* Mesh = Character->GetMesh();
	Mesh->SetAnimInstanceClass(nullptr);
	Mesh->SetSkeletalMesh(VisualMesh);
	Mesh->SetAnimationMode(EAnimationMode::AnimationSingleNode);

	const FBox Bounds = VisualMesh->GetImportedBounds().GetBox();
	const float Scale = VisualHeight / FMath::Max(1.f, Bounds.GetSize().Z);
	const float HalfHeight = Character->GetCapsuleComponent()->GetScaledCapsuleHalfHeight();
	Mesh->SetRelativeScale3D(FVector(Scale));
	Mesh->SetRelativeLocation(FVector(0.f, 0.f, -HalfHeight - Bounds.Min.Z * Scale));
	Mesh->SetRelativeRotation(FRotator(0.f, MeshYawOffset, 0.f));

	if (USpringArmComponent* Arm = Character->FindComponentByClass<USpringArmComponent>(); Arm && CameraLagSpeed > 0.f)
	{
		Arm->bEnableCameraLag = true;
		Arm->CameraLagSpeed = CameraLagSpeed;
		Arm->CameraLagMaxDistance = CameraLagMaxDistance;
	}

	if (UPlatformerSubsystem* Game = UPlatformerSubsystem::Get(this))
	{
		LastLives = Game->GetLives();
		Game->OnLivesChanged.AddUniqueDynamic(this, &UKitCharacterAnimator::HandleLivesChanged);
	}
	Play(Idle, true);
}

void UKitCharacterAnimator::Play(UAnimSequence* Anim, bool bLoop, float Rate)
{
	USkeletalMeshComponent* Mesh = Character.IsValid() ? Character->GetMesh() : nullptr;
	if (!Mesh || !Anim)
	{
		return;
	}
	if (Anim != Current)
	{
		Current = Anim;
		Mesh->PlayAnimation(Anim, bLoop);
	}
	Mesh->SetPlayRate(Rate);
}

void UKitCharacterAnimator::HandleLivesChanged(int32 Lives)
{
	if (Lives < LastLives && Character.IsValid())
	{
		UPlatformerSubsystem::SpawnEffect(this, EPlatformerEffect::Hurt, Character->GetActorLocation());
	}
	if (Lives < LastLives && Lives > 0 && Hurt)
	{
		Current = nullptr;  // restart even if already playing
		Play(Hurt, false);
		OneShotTime = 0.45f;
	}
	LastLives = Lives;
}

void UKitCharacterAnimator::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
	Super::TickComponent(DeltaTime, TickType, ThisTickFunction);
	if (!Character.IsValid() || !VisualMesh)
	{
		return;
	}

	const UCharacterMovementComponent* Move = Character->GetCharacterMovement();
	const bool bFalling = Move->IsFalling();
	const float GroundSpeed = Character->GetVelocity().Size2D();
	SinceJump += DeltaTime;

	// Every jump press (double jumps too) bumps the jump count: play the jump sound.
	if (Character->JumpCurrentCount > LastJumpCount)
	{
		if (bPlayJumpSound)
		{
			UPlatformerSubsystem::PlaySound(this, EPlatformerSound::Jump);
		}
		SinceJump = 0.f;
		Current = nullptr;  // restart the jump animation for a double jump
	}
	LastJumpCount = Character->JumpCurrentCount;

	if (const UPlatformerSubsystem* Game = UPlatformerSubsystem::Get(this))
	{
		if (Game->IsLevelComplete() && !bFalling)
		{
			Play(Win, true);
			return;
		}
		if (Game->IsGameOver())
		{
			Play(Lose, false);
			return;
		}
	}

	// A hurt reaction plays out even while dropping back in at the respawn point.
	if (OneShotTime > 0.f && Current == Hurt)
	{
		OneShotTime -= DeltaTime;
		bWasFalling = bFalling;
		return;
	}

	if (bFalling)
	{
		FallSpeed = FMath::Max(FallSpeed, -Character->GetVelocity().Z);
		bWasFalling = true;
		if (SinceJump < 0.3f)
		{
			Play(JumpStart, false);
		}
		else
		{
			Play(InAir, true);
		}
		return;
	}

	if (bWasFalling)
	{
		bWasFalling = false;
		if (FallSpeed > GetDefault<UPlatformerEffectsSettings>()->LandDustSpeed)
		{
			const float HalfHeight = Character->GetCapsuleComponent()->GetScaledCapsuleHalfHeight();
			UPlatformerSubsystem::SpawnEffect(this, EPlatformerEffect::Land,
				Character->GetActorLocation() - FVector(0.f, 0.f, HalfHeight - 10.f));
		}
		FallSpeed = 0.f;
		if (Land && GroundSpeed < RunSpeed)  // skip the landing pose when running on
		{
			Current = nullptr;
			Play(Land, false);
			OneShotTime = 0.25f;
		}
	}
	if (OneShotTime > 0.f)
	{
		OneShotTime -= DeltaTime;
		return;
	}

	if (GroundSpeed > RunSpeed)
	{
		Play(Run, true, FMath::Clamp(GroundSpeed / RunAnimSpeed, 0.6f, 1.8f));
	}
	else if (GroundSpeed > WalkSpeed)
	{
		Play(Walk, true);
	}
	else
	{
		Play(Idle, true);
	}
}

FString UKitCharacterAnimator::GetCurrentAnimName() const
{
	return Current ? Current->GetName() : FString();
}
