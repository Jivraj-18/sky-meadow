#include "PlatformerEffectsSettings.h"

#include "KitEffect.h"

TSubclassOf<AKitEffect> UPlatformerEffectsSettings::GetEffect(EPlatformerEffect Effect) const
{
	const TSoftClassPtr<AKitEffect>* Ref = nullptr;
	switch (Effect)
	{
	case EPlatformerEffect::CoinCollect: Ref = &CoinCollect; break;
	case EPlatformerEffect::Stomp:       Ref = &Stomp; break;
	case EPlatformerEffect::Land:        Ref = &Land; break;
	case EPlatformerEffect::Checkpoint:  Ref = &Checkpoint; break;
	case EPlatformerEffect::JumpPad:     Ref = &JumpPad; break;
	case EPlatformerEffect::Hurt:        Ref = &Hurt; break;
	}
	return Ref ? Ref->LoadSynchronous() : nullptr;
}
