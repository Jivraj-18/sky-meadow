#include "ShooterControls.h"

#include "Camera/CameraComponent.h"
#include "EnhancedInputSubsystems.h"
#include "GameFramework/Character.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/PlayerController.h"
#include "GameFramework/SpringArmComponent.h"
#include "InputMappingContext.h"

UShooterControls::UShooterControls()
{
	PrimaryComponentTick.bCanEverTick = true;
}

void UShooterControls::BeginPlay()
{
	Super::BeginPlay();
	ApplySettings();
}

void UShooterControls::ApplySettings()
{
	ACharacter* Character = Cast<ACharacter>(GetOwner());
	if (!Character)
	{
		return;
	}

	if (USpringArmComponent* Arm = Character->FindComponentByClass<USpringArmComponent>())
	{
		Arm->TargetArmLength = ArmLength;
		Arm->SocketOffset = ShoulderOffset;
		Arm->bEnableCameraLag = CameraLagSpeed > 0.f;
		Arm->CameraLagSpeed = CameraLagSpeed;
	}
	if (UCameraComponent* Camera = Character->FindComponentByClass<UCameraComponent>())
	{
		Camera->SetFieldOfView(FieldOfView);
	}

	Character->JumpMaxCount = MaxJumps;
	UCharacterMovementComponent* Move = Character->GetCharacterMovement();
	Move->MaxWalkSpeed = RunSpeed;
	Move->JumpZVelocity = JumpVelocity;
	Move->GravityScale = GravityScale;
	Move->AirControl = AirControl;
}

void UShooterControls::ApplyInput()
{
	const APawn* Pawn = Cast<APawn>(GetOwner());
	const APlayerController* PC = Pawn ? Cast<APlayerController>(Pawn->GetController()) : nullptr;
	const ULocalPlayer* Player = PC ? PC->GetLocalPlayer() : nullptr;
	UEnhancedInputLocalPlayerSubsystem* Input = Player ? Player->GetSubsystem<UEnhancedInputLocalPlayerSubsystem>() : nullptr;
	if (!Input)
	{
		return;
	}
	for (const UInputMappingContext* Context : RemoveMappingContexts)
	{
		if (Context)
		{
			Input->RemoveMappingContext(Context);
		}
	}
	for (const UInputMappingContext* Context : AddMappingContexts)
	{
		if (Context && !Input->HasMappingContext(Context))
		{
			Input->AddMappingContext(Context, 0);
		}
	}
	bInputApplied = true;
}

void UShooterControls::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
	Super::TickComponent(DeltaTime, TickType, ThisTickFunction);
	ACharacter* Character = Cast<ACharacter>(GetOwner());
	if (!Character)
	{
		return;
	}

	// The player controller adds its own mapping contexts after the pawn begins play, so swap
	// them once the pawn is possessed.
	if (!bInputApplied)
	{
		// The character Blueprint's BeginPlay runs after ours and can set its own jump count or
		// gravity: apply again once everything has started.
		ApplySettings();
		ApplyInput();
	}

	const APlayerController* PC = Cast<APlayerController>(Character->GetController());
	bSprinting = PC && PC->IsInputKeyDown(SprintKey) && !Character->GetCharacterMovement()->IsFalling();
	Character->GetCharacterMovement()->MaxWalkSpeed = bSprinting ? SprintSpeed : RunSpeed;
}
