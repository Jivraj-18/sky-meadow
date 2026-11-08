#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "KitCharacterAnimator.generated.h"

class ACharacter;
class UAnimSequence;
class USkeletalMesh;

/**
 * Gives the player character the kit's look: swaps its mesh at BeginPlay and plays the right
 * animation for what it is doing (idle, walk, run, jump, air, land, hurt, win, game over).
 * Also plays the jump sound. Add to the player character Blueprint and set the slots below.
 */
UCLASS(ClassGroup = (Platformer), meta = (BlueprintSpawnableComponent))
class REALWORLDGAME_API UKitCharacterAnimator : public UActorComponent
{
	GENERATED_BODY()

public:
	UKitCharacterAnimator();

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Look")
	TObjectPtr<USkeletalMesh> VisualMesh;

	/** Height of the character on screen in cm; the model is scaled to match. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Look")
	float VisualHeight = 165.f;

	/** Turns the model to face the movement direction. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Look")
	float MeshYawOffset = -90.f;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Animations") TObjectPtr<UAnimSequence> Idle;
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Animations") TObjectPtr<UAnimSequence> Walk;
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Animations") TObjectPtr<UAnimSequence> Run;
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Animations") TObjectPtr<UAnimSequence> JumpStart;
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Animations") TObjectPtr<UAnimSequence> InAir;
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Animations") TObjectPtr<UAnimSequence> Land;
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Animations") TObjectPtr<UAnimSequence> Hurt;
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Animations") TObjectPtr<UAnimSequence> Win;
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Animations") TObjectPtr<UAnimSequence> Lose;

	/** Ground speed (cm/s) above which Walk plays, and above which Run plays. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Animations")
	float WalkSpeed = 20.f;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Animations")
	float RunSpeed = 320.f;

	/** Run speed at which the Run animation plays at normal rate (faster runs speed it up). */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Animations")
	float RunAnimSpeed = 600.f;

	/** Play the "Jump" sound from Project Settings > Platformer Audio on every jump. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Sound")
	bool bPlayJumpSound = true;

	/** How quickly the camera catches up with the character (0 = locked on, no smoothing). */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Camera")
	float CameraLagSpeed = 9.f;

	/** Max distance (cm) the camera may trail behind before it is pulled along. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Camera")
	float CameraLagMaxDistance = 150.f;

	/** Name of the animation playing now, for automated playtests. */
	UFUNCTION(BlueprintPure, Category = "Animations")
	FString GetCurrentAnimName() const;

protected:
	virtual void BeginPlay() override;
	virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;

private:
	void Play(UAnimSequence* Anim, bool bLoop, float Rate = 1.f);

	UFUNCTION()
	void HandleLivesChanged(int32 Lives);

	UPROPERTY()
	TObjectPtr<UAnimSequence> Current;

	TWeakObjectPtr<ACharacter> Character;
	int32 LastJumpCount = 0;
	int32 LastLives = -1;
	bool bWasFalling = false;
	float FallSpeed = 0.f;  // fastest downward speed during the current fall
	float OneShotTime = 0.f;  // a one-shot (jump start, land, hurt) is playing for this long
	float SinceJump = 99.f;
};
