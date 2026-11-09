#include "VehicleEntry.h"

#include "ChaosVehicleMovementComponent.h"
#include "Components/CapsuleComponent.h"
#include "EngineUtils.h"
#include "EnhancedInputSubsystems.h"
#include "GameFramework/Character.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/PlayerController.h"
#include "InputMappingContext.h"

UVehicleEntry::UVehicleEntry()
{
	PrimaryComponentTick.bCanEverTick = true;
}

APawn* UVehicleEntry::FindNearestVehicle() const
{
	const FVector Here = GetOwner()->GetActorLocation();
	APawn* Best = nullptr;
	double BestDist = Range;
	for (TActorIterator<APawn> It(GetWorld()); It; ++It)
	{
		if (*It != GetOwner() && It->FindComponentByClass<UChaosVehicleMovementComponent>())
		{
			const double Dist = FVector::Dist(Here, It->GetActorLocation());
			if (Dist < BestDist)
			{
				BestDist = Dist;
				Best = *It;
			}
		}
	}
	return Best;
}

void UVehicleEntry::SwapInput(APlayerController* PC, bool bDriving) const
{
	const ULocalPlayer* Player = PC ? PC->GetLocalPlayer() : nullptr;
	UEnhancedInputLocalPlayerSubsystem* Input = Player ? Player->GetSubsystem<UEnhancedInputLocalPlayerSubsystem>() : nullptr;
	if (!Input)
	{
		return;
	}
	for (const UInputMappingContext* Context : bDriving ? OnFootMappingContexts : DrivingMappingContexts)
	{
		if (Context)
		{
			Input->RemoveMappingContext(Context);
		}
	}
	for (const UInputMappingContext* Context : bDriving ? DrivingMappingContexts : OnFootMappingContexts)
	{
		if (Context && !Input->HasMappingContext(Context))
		{
			Input->AddMappingContext(Context, 0);
		}
	}
}

bool UVehicleEntry::EnterNearestVehicle()
{
	ACharacter* Character = Cast<ACharacter>(GetOwner());
	APlayerController* PC = Character ? Cast<APlayerController>(Character->GetController()) : nullptr;
	APawn* Car = PC ? FindNearestVehicle() : nullptr;
	if (!Car || Car->IsPlayerControlled())
	{
		return false;
	}

	// Ride along hidden inside the vehicle.
	Character->GetCharacterMovement()->StopMovementImmediately();
	Character->GetCharacterMovement()->DisableMovement();
	Character->GetCapsuleComponent()->SetCollisionEnabled(ECollisionEnabled::NoCollision);
	Character->SetActorHiddenInGame(true);
	Character->AttachToActor(Car, FAttachmentTransformRules::SnapToTargetNotIncludingScale);

	if (UChaosVehicleMovementComponent* Move = Car->FindComponentByClass<UChaosVehicleMovementComponent>())
	{
		Move->SetHandbrakeInput(false);  // released again (getting out pulls it)
	}

	Driver = PC;
	Vehicle = Car;
	PC->Possess(Car);
	SwapInput(PC, true);
	UE_LOG(LogTemp, Log, TEXT("Platformer: entered vehicle %s"), *Car->GetName());
	return true;
}

void UVehicleEntry::ExitVehicle()
{
	ACharacter* Character = Cast<ACharacter>(GetOwner());
	if (!Character || !Vehicle || !Driver)
	{
		return;
	}
	if (UChaosVehicleMovementComponent* Move = Vehicle->FindComponentByClass<UChaosVehicleMovementComponent>())
	{
		Move->SetThrottleInput(0.f);
		Move->SetHandbrakeInput(true);  // don't roll away
	}

	Character->DetachFromActor(FDetachmentTransformRules::KeepWorldTransform);
	const FVector Out = Vehicle->GetActorTransform().TransformPosition(ExitOffset);
	Character->TeleportTo(Out, FRotator(0.f, Vehicle->GetActorRotation().Yaw, 0.f));
	Character->GetCapsuleComponent()->SetCollisionEnabled(ECollisionEnabled::QueryAndPhysics);
	Character->SetActorHiddenInGame(false);
	Character->GetCharacterMovement()->SetMovementMode(MOVE_Falling);

	SwapInput(Driver, false);
	Driver->Possess(Character);
	UE_LOG(LogTemp, Log, TEXT("Platformer: exited vehicle %s"), *Vehicle->GetName());
	Vehicle = nullptr;
	Driver = nullptr;
}

void UVehicleEntry::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
	Super::TickComponent(DeltaTime, TickType, ThisTickFunction);
	// While driving, the controller belongs to the vehicle, so keep a handle to it for the key.
	const APawn* Owner = Cast<APawn>(GetOwner());
	APlayerController* PC = Vehicle ? Driver.Get() : (Owner ? Cast<APlayerController>(Owner->GetController()) : nullptr);
	if (PC && PC->WasInputKeyJustPressed(InteractKey))
	{
		if (Vehicle)
		{
			ExitVehicle();
		}
		else
		{
			EnterNearestVehicle();
		}
	}
}
