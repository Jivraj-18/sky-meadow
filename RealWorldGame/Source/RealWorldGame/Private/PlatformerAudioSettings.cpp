#include "PlatformerAudioSettings.h"

#include "Sound/SoundBase.h"

USoundBase* UPlatformerAudioSettings::GetSound(EPlatformerSound Sound) const
{
	const TSoftObjectPtr<USoundBase>* Ref = nullptr;
	switch (Sound)
	{
	case EPlatformerSound::Jump:          Ref = &Jump; break;
	case EPlatformerSound::Coin:          Ref = &Coin; break;
	case EPlatformerSound::Stomp:         Ref = &Stomp; break;
	case EPlatformerSound::Hurt:          Ref = &Hurt; break;
	case EPlatformerSound::JumpPad:       Ref = &JumpPad; break;
	case EPlatformerSound::Checkpoint:    Ref = &Checkpoint; break;
	case EPlatformerSound::LevelComplete: Ref = &LevelComplete; break;
	case EPlatformerSound::GameOver:      Ref = &GameOver; break;
	}
	return Ref ? Ref->LoadSynchronous() : nullptr;
}
