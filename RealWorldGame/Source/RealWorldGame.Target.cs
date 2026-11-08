using UnrealBuildTool;

public class RealWorldGameTarget : TargetRules
{
	public RealWorldGameTarget(TargetInfo Target) : base(Target)
	{
		Type = TargetType.Game;
		DefaultBuildSettings = BuildSettingsVersion.Latest;
		IncludeOrderVersion = EngineIncludeOrderVersion.Latest;
		ExtraModuleNames.Add("RealWorldGame");
	}
}
