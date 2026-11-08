#include "WorldBuilderLibrary.h"

#include "Engine/Engine.h"
#include "Engine/StaticMesh.h"
#include "Engine/World.h"
#include "FoliageType_InstancedStaticMesh.h"
#include "InstancedFoliage.h"
#include "InstancedFoliageActor.h"
#include "Landscape.h"
#include "LandscapeInfo.h"
#include "Misc/FileHelper.h"

namespace
{
	UWorld* WorldOf(UObject* WorldContext)
	{
		return GEngine ? GEngine->GetWorldFromContextObject(WorldContext, EGetWorldErrorMode::LogAndReturnNull) : nullptr;
	}
}

ALandscape* UWorldBuilderLibrary::CreateLandscapeFromR16(UObject* WorldContext, const FString& HeightmapPath, int32 Size,
	FVector Location, FVector Scale, UMaterialInterface* Material, const FString& Label)
{
#if WITH_EDITOR
	UWorld* World = WorldOf(WorldContext);
	TArray<uint8> Raw;
	if (!World || !FFileHelper::LoadFileToArray(Raw, *HeightmapPath) || Raw.Num() != Size * Size * 2)
	{
		UE_LOG(LogTemp, Error, TEXT("CreateLandscapeFromR16: can't read %s as %dx%d 16-bit"), *HeightmapPath, Size, Size);
		return nullptr;
	}
	constexpr int32 QuadsPerSection = 63;
	if ((Size - 1) % QuadsPerSection != 0)
	{
		UE_LOG(LogTemp, Error, TEXT("CreateLandscapeFromR16: size %d is not N*63+1"), Size);
		return nullptr;
	}

	TArray<uint16> Heights;
	Heights.SetNumUninitialized(Size * Size);
	FMemory::Memcpy(Heights.GetData(), Raw.GetData(), Raw.Num());

	// Centre the landscape on Location, like the Landscape tool does.
	const FVector Offset = Scale * FVector(-(Size - 1) / 2.0, -(Size - 1) / 2.0, 0.0);
	ALandscape* Landscape = World->SpawnActor<ALandscape>(Location + Offset, FRotator::ZeroRotator);
	Landscape->LandscapeMaterial = Material;
	Landscape->SetActorRelativeScale3D(Scale);

	TMap<FGuid, TArray<uint16>> HeightDataPerLayers;
	HeightDataPerLayers.Add(FGuid(), MoveTemp(Heights));
	TMap<FGuid, TArray<FLandscapeImportLayerInfo>> MaterialLayerDataPerLayers;
	MaterialLayerDataPerLayers.Add(FGuid(), TArray<FLandscapeImportLayerInfo>());

	Landscape->Import(FGuid::NewGuid(), 0, 0, Size - 1, Size - 1, /*NumSubsections=*/1, QuadsPerSection,
		HeightDataPerLayers, *HeightmapPath, MaterialLayerDataPerLayers, ELandscapeImportAlphamapType::Additive,
		TArrayView<const FLandscapeLayer>());
	if (ULandscapeInfo* Info = Landscape->GetLandscapeInfo())
	{
		Info->UpdateLayerInfoMap(Landscape);
	}
	Landscape->SetActorLabel(Label);
	return Landscape;
#else
	return nullptr;
#endif
}

int32 UWorldBuilderLibrary::ScatterFoliage(UObject* WorldContext, UStaticMesh* Mesh, FVector2D Min, FVector2D Max,
	int32 Count, int32 Seed, float ScaleMin, float ScaleMax, float MaxSlopeDegrees, bool bAlignToSlope,
	float CullDistance, bool bCastShadow)
{
#if WITH_EDITOR
	UWorld* World = WorldOf(WorldContext);
	if (!World || !Mesh || Count <= 0)
	{
		return 0;
	}
	AInstancedFoliageActor* IFA = AInstancedFoliageActor::GetInstancedFoliageActorForLevel(World->PersistentLevel, true);

	// Reuse the mesh's foliage type if it's already registered (AddMesh asserts on duplicates).
	FFoliageInfo* Info = nullptr;
	UFoliageType* FoliageType = IFA->GetLocalFoliageTypeForSource(Mesh, &Info);
	if (!FoliageType)
	{
		Info = IFA->AddMesh(Mesh, &FoliageType);
	}
	if (UFoliageType_InstancedStaticMesh* MeshType = Cast<UFoliageType_InstancedStaticMesh>(FoliageType))
	{
		MeshType->CullDistance.Max = static_cast<int32>(CullDistance);
		MeshType->CastShadow = bCastShadow;
		MeshType->AlignToNormal = bAlignToSlope;
		MeshType->Scaling = EFoliageScaling::Uniform;
		MeshType->ScaleX = FFloatInterval(ScaleMin, ScaleMax);
		MeshType->RandomYaw = true;
		MeshType->GroundSlopeAngle = FFloatInterval(0.f, MaxSlopeDegrees);
	}

	FRandomStream Random(Seed);
	const float MinNormalZ = FMath::Cos(FMath::DegreesToRadians(MaxSlopeDegrees));
	FCollisionQueryParams Params(SCENE_QUERY_STAT(WorldBuilderScatter), true);
	TArray<FFoliageInstance> Placed;
	Placed.Reserve(Count);
	for (int32 i = 0; i < Count; ++i)
	{
		const FVector2D P(Random.FRandRange(Min.X, Max.X), Random.FRandRange(Min.Y, Max.Y));
		FHitResult Hit;
		if (!World->LineTraceSingleByChannel(Hit, FVector(P, 100000.0), FVector(P, -100000.0), ECC_Visibility, Params)
			|| Hit.ImpactNormal.Z < MinNormalZ)
		{
			continue;
		}
		FFoliageInstance Instance;
		Instance.Location = Hit.ImpactPoint;
		const FQuat Yaw(FVector::UpVector, Random.FRandRange(0.f, 2.f * PI));
		const FQuat Tilt = bAlignToSlope ? FQuat::FindBetweenNormals(FVector::UpVector, Hit.ImpactNormal) : FQuat::Identity;
		Instance.Rotation = (Tilt * Yaw).Rotator();
		Instance.DrawScale3D = FVector3f(Random.FRandRange(ScaleMin, ScaleMax));
		Instance.BaseComponent = Hit.GetComponent();
		Placed.Add(Instance);
	}

	TArray<const FFoliageInstance*> Pointers;
	for (const FFoliageInstance& Instance : Placed)
	{
		Pointers.Add(&Instance);
	}
	Info->AddInstances(FoliageType, Pointers);
	Info->Refresh(true, true);
	return Placed.Num();
#else
	return 0;
#endif
}

int32 UWorldBuilderLibrary::ClearFoliage(UObject* WorldContext, UStaticMesh* Mesh)
{
#if WITH_EDITOR
	UWorld* World = WorldOf(WorldContext);
	AInstancedFoliageActor* IFA = World ? AInstancedFoliageActor::GetInstancedFoliageActorForLevel(World->PersistentLevel, false) : nullptr;
	if (!IFA || !Mesh)
	{
		return 0;
	}
	int32 Removed = 0;
	IFA->ForEachFoliageInfo([&](UFoliageType* Type, FFoliageInfo& Info)
	{
		if (Type && Type->GetSource() == Mesh)
		{
			TArray<int32> All;
			for (int32 i = 0; i < Info.Instances.Num(); ++i)
			{
				All.Add(i);
			}
			Removed += All.Num();
			Info.RemoveInstances(All, true);
		}
		return true;
	});
	return Removed;
#else
	return 0;
#endif
}
