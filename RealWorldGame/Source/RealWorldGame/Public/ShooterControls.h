#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "InputCoreTypes.h"
#include "ShooterControls.generated.h"

class UInputMappingContext;

/**
 * Turns the platforming character into a grounded third-person shooter character (BGMI-style):
 * over-the-shoulder camera, one jump, normal gravity, run + hold-to-sprint, and the platformer's
 * input (dash) swapped for plain move/look/jump. Add to a character Blueprint; tune in Details.
 */
UCLASS(ClassGroup = (Platformer), meta = (BlueprintSpawnableComponent))
class REALWORLDGAME_API UShooterControls : public UActorComponent
{
	GENERATED_BODY()

public:
	UShooterControls();

	// ---- Camera --------------------------------------------------------------------------------
	/** Distance of the camera behind the character (cm). */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Camera")
	float ArmLength = 260.f;

	/** Shoulder offset: Y = to the right, Z = up (cm). */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Camera")
	FVector ShoulderOffset = FVector(0.f, 55.f, 70.f);

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Camera")
	float FieldOfView = 85.f;

	/** How quickly the camera follows (0 = rigid). */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Camera")
	float CameraLagSpeed = 14.f;

	// ---- Movement ------------------------------------------------------------------------------
	/** Normal (jog) speed, cm/s. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Movement")
	float RunSpeed = 420.f;

	/** Speed while the sprint key is held, cm/s. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Movement")
	float SprintSpeed = 650.f;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Movement")
	FKey SprintKey = EKeys::LeftShift;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Movement", meta = (ClampMin = "1"))
	int32 MaxJumps = 1;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Movement")
	float JumpVelocity = 450.f;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Movement")
	float GravityScale = 1.f;

	/** 0 = no steering in the air, 1 = full. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Movement", meta = (ClampMin = "0", ClampMax = "1"))
	float AirControl = 0.2f;

	// ---- Input ---------------------------------------------------------------------------------
	/** Mapping contexts to remove from the player (e.g. the platformer's, which has dash). */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Input")
	TArray<TObjectPtr<UInputMappingContext>> RemoveMappingContexts;

	/** Mapping contexts to add instead (e.g. plain move/look/jump). */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Input")
	TArray<TObjectPtr<UInputMappingContext>> AddMappingContexts;

	UFUNCTION(BlueprintPure, Category = "Movement")
	bool IsSprinting() const { return bSprinting; }

protected:
	virtual void BeginPlay() override;
	virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;

private:
	void ApplySettings();
	void ApplyInput();

	bool bInputApplied = false;
	bool bSprinting = false;
};
