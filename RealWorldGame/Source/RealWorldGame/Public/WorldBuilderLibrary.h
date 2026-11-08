#pragma once

#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "WorldBuilderLibrary.generated.h"

class ALandscape;
class UMaterialInterface;
class UStaticMesh;

/**
 * Editor-only helpers for building worlds from scripts. Everything they create is ordinary,
 * hand-editable content: a normal Landscape (sculpt/paint brushes) and Foliage-mode instances
 * (paint/erase/select with the Foliage tool).
 */
UCLASS()
class REALWORLDGAME_API UWorldBuilderLibrary : public UBlueprintFunctionLibrary
{
	GENERATED_BODY()

public:
	/**
	 * Creates a Landscape from a raw 16-bit little-endian heightmap (.r16), Size x Size vertices.
	 * Size must be a valid landscape size for 63-quad sections (e.g. 127, 253, 505, 1009).
	 * Height 32768 is Location.Z; one height unit is Scale.Z / 128 cm (Unreal's convention).
	 */
	UFUNCTION(BlueprintCallable, Category = "World Builder", meta = (WorldContext = "WorldContext"))
	static ALandscape* CreateLandscapeFromR16(UObject* WorldContext, const FString& HeightmapPath, int32 Size,
		FVector Location, FVector Scale, UMaterialInterface* Material, const FString& Label);

	/**
	 * Scatters Count instances of Mesh as Foliage over [Min, Max] (XY), snapped to whatever is below
	 * (landscape), skipping ground steeper than MaxSlopeDegrees. Returns the number placed.
	 * Instances land in the level's Instanced Foliage Actor, so the Foliage tool can edit them.
	 */
	UFUNCTION(BlueprintCallable, Category = "World Builder", meta = (WorldContext = "WorldContext"))
	static int32 ScatterFoliage(UObject* WorldContext, UStaticMesh* Mesh, FVector2D Min, FVector2D Max, int32 Count,
		int32 Seed, float ScaleMin, float ScaleMax, float MaxSlopeDegrees, bool bAlignToSlope, float CullDistance,
		bool bCastShadow);

	/** Removes every Foliage instance of Mesh from the current level (to re-run a scatter). */
	UFUNCTION(BlueprintCallable, Category = "World Builder", meta = (WorldContext = "WorldContext"))
	static int32 ClearFoliage(UObject* WorldContext, UStaticMesh* Mesh);
};
