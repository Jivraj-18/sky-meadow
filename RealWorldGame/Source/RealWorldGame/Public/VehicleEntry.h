#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "InputCoreTypes.h"
#include "VehicleEntry.generated.h"

class APlayerController;
class UInputMappingContext;

/**
 * Lets the character drive vehicles (BGMI-style): press Interact Key near a vehicle to get in
 * (the character hides and rides along, the player controls the vehicle), press it again to get
 * out beside it. Any pawn with a Chaos vehicle movement component counts as a vehicle.
 */
UCLASS(ClassGroup = (Platformer), meta = (BlueprintSpawnableComponent))
class REALWORLDGAME_API UVehicleEntry : public UActorComponent
{
	GENERATED_BODY()

public:
	UVehicleEntry();

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Vehicle")
	FKey InteractKey = EKeys::E;

	/** How close (cm) the character must be to a vehicle to get in. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Vehicle")
	float Range = 450.f;

	/** Where the character appears when getting out, relative to the vehicle (cm; Y = right). */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Vehicle")
	FVector ExitOffset = FVector(0.f, -260.f, 60.f);

	/** Input used while driving (e.g. the vehicle template's throttle/steer/brake). */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Input")
	TArray<TObjectPtr<UInputMappingContext>> DrivingMappingContexts;

	/** Input used on foot (removed while driving, restored on exit). */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Input")
	TArray<TObjectPtr<UInputMappingContext>> OnFootMappingContexts;

	UFUNCTION(BlueprintPure, Category = "Vehicle")
	bool IsDriving() const { return Vehicle != nullptr; }

	/** Gets into the nearest vehicle in range; returns whether it did. */
	UFUNCTION(BlueprintCallable, Category = "Vehicle")
	bool EnterNearestVehicle();

	UFUNCTION(BlueprintCallable, Category = "Vehicle")
	void ExitVehicle();

protected:
	virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;

private:
	APawn* FindNearestVehicle() const;
	void SwapInput(APlayerController* PC, bool bDriving) const;

	UPROPERTY()
	TObjectPtr<APawn> Vehicle;

	UPROPERTY()
	TObjectPtr<APlayerController> Driver;
};
