using UnrealBuildTool;

public class RealWorldGameEditorTarget : TargetRules
{
	public RealWorldGameEditorTarget(TargetInfo Target) : base(Target)
	{
		Type = TargetType.Editor;
		DefaultBuildSettings = BuildSettingsVersion.Latest;
		IncludeOrderVersion = EngineIncludeOrderVersion.Latest;
		ExtraModuleNames.Add("RealWorldGame");
	}
}
