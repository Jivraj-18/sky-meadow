using UnrealBuildTool;

public class RealWorldGame : ModuleRules
{
	public RealWorldGame(ReadOnlyTargetRules Target) : base(Target)
	{
		PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;
		PublicDependencyModuleNames.AddRange(new[] { "Core", "CoreUObject", "Engine", "InputCore", "UMG", "Slate", "SlateCore", "DeveloperSettings", "Landscape", "Foliage", "EnhancedInput", "ChaosVehicles" });
	}
}
