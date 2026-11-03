using UnrealBuildTool;

public class EcosPoCTarget : TargetRules
{
	public EcosPoCTarget(TargetInfo Target) : base(Target)
	{
		Type = TargetType.Game;
		DefaultBuildSettings = BuildSettingsVersion.V5;
		IncludeOrderVersion = EngineIncludeOrderVersion.Latest;
		ExtraModuleNames.Add("EcosPoC");
	}
}
