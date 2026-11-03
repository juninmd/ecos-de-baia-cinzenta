using UnrealBuildTool;

public class EcosPoCEditorTarget : TargetRules
{
	public EcosPoCEditorTarget(TargetInfo Target) : base(Target)
	{
		Type = TargetType.Editor;
		DefaultBuildSettings = BuildSettingsVersion.V5;
		IncludeOrderVersion = EngineIncludeOrderVersion.Latest;
		ExtraModuleNames.Add("EcosPoC");
	}
}
