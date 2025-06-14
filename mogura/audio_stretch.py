import copy
import hashlib
import pyrubberband as pyrb
import weakref

# audiodatamd5_tm_to_audionp_wvdict = weakref.WeakValueDictionary()
# audiodatamd5_tm_to_audionp_wvdict = {}

def stretch_audio(audio_data, time_multiplier):
    if audio_data is None: return None

    ret_audio_data = {
        'SAMPLE_RATE': audio_data['SAMPLE_RATE'],
    }

    key = f'_stretch_audio_np_{time_multiplier}'
    audio_np = audio_data.get(key, None)
    if audio_np is None:
        audio_np = pyrb.time_stretch(audio_data['audio_np'], audio_data['SAMPLE_RATE'], 1/time_multiplier)
        audio_data[key] = audio_np

    ret_audio_data['audio_np'] = audio_np
    return ret_audio_data
