import copy
import itertools
#import json
import mido


def path_to_data(file_path):
    return mid_to_data(mido.MidiFile(file_path))


def mid_to_data(mid):
    output_data = {}
    output_data['ticks_per_beat'] = mid.ticks_per_beat
    output_data['track_list'] = list(map(lambda i:track_to_data(i,mid.ticks_per_beat),mid.tracks))
    return output_data


def track_to_data(track,ticks_per_beat):
    track_data = {}
    track_data['ticks_per_beat'] = ticks_per_beat
    track_data['name'] = track.name
    track_data['noteev_list'] = track_to_noteev_list(track)
    end_tick = track_data['noteev_list'][-1]['tick']
    track_data['bar_list']   = track_to_bar_list(track,end_tick,ticks_per_beat)
    track_data['bar_set']    = set(track_data['bar_list'])
    track_data['tempo_list'] = track_to_tempo_list(track,end_tick,ticks_per_beat)

    max_pitch = track_data['noteev_list']
    max_pitch = map(lambda i:i['pitch'],max_pitch)
    max_pitch = max(max_pitch)
    track_data['max_pitch'] = max_pitch

    min_pitch = track_data['noteev_list']
    min_pitch = map(lambda i:i['pitch'],min_pitch)
    min_pitch = min(min_pitch)
    track_data['min_pitch'] = min_pitch

    return track_data


def track_to_noteev_list(track):
    ret_noteev_list = []
    tick = 0
    tempo = 0
    sec6tpb = 0
    for msg in track:
        tick += msg.time
        sec6tpb += msg.time * tempo
        if msg.type == 'note_on' and msg.velocity > 0:
            noteev = {
                'tick':tick,
                'sec6tpb':sec6tpb,
                'type':'on',
                'channel':msg.channel,
                'pitch':msg.note,
                'tick0':tick,
                'sec6tpb0':sec6tpb,
            }
            noteev = (tick,1,msg.channel,msg.note,noteev)
            ret_noteev_list.append(noteev)
        elif msg.type == 'note_off' or msg.type == 'note_on':
            noteev = {
                'tick':tick,
                'sec6tpb':sec6tpb,
                'type':'off',
                'channel':msg.channel,
                'pitch':msg.note,
            }
            noteev = (tick,0,msg.channel,msg.note,noteev)
            ret_noteev_list.append(noteev)
        elif msg.type == 'set_tempo':
            tempo = msg.tempo
    ret_noteev_list.sort()
    ret_noteev_list = map(lambda i:i[4],ret_noteev_list)
    ret_noteev_list = list(ret_noteev_list)
    
    cp_to_noteev_dict = {}
    for noteev in ret_noteev_list:
        #print(noteev)
        if noteev['type'] == 'on':
            cp = (noteev['channel'],noteev['pitch'])
            cp_to_noteev_dict[cp] = noteev
        elif noteev['type'] == 'off':
            cp = (noteev['channel'],noteev['pitch'])
            noteev0 = cp_to_noteev_dict[cp]
            noteev0['tick1'] = noteev['tick']
            noteev0['sec6tpb1'] = noteev['sec6tpb']
            del cp_to_noteev_dict[cp]
    
    return ret_noteev_list


def track_to_bar_list(track,end_tick,ticks_per_beat):
    time_signature_list = []
    time_signature_list.append({
        'numerator': 4,
        'denominator': 4,
        'tick0': 0,
    })
    tick = 0
    for msg in track:
        tick += msg.time
        if msg.type != 'time_signature': continue
        time_signature_list[-1]['tick1'] = tick
        time_signature_list.append({
            'numerator': msg.numerator,
            'denominator': msg.denominator,
            'tick0': tick,
        })

    time_signature_list[-1]['tick1'] = end_tick

    ret_bar_list = []
    for time_signature in time_signature_list:
        tick = time_signature['tick0']
        dtick = ticks_per_beat * time_signature['numerator'] * 4 // time_signature['denominator']
        while tick < time_signature['tick1']:
            ret_bar_list.append(tick)
            tick += dtick
    ret_bar_list.append(tick)
    ret_bar_list.sort()
    
    return ret_bar_list

def track_to_tempo_list(track,end_tick,ticks_per_beat):
    ret_tempo_list = []
    ret_tempo_list.append({
        'tick0': 0,
        'sec6tpb0': 0,
    })
    tick = 0
    tempo = 0
    sec6tpb = 0
    for msg in track:
        tick += msg.time
        sec6tpb += msg.time * tempo
        if msg.type != 'set_tempo': continue
        tempo = msg.tempo
        ret_tempo_list[-1]['tick1'] = tick
        ret_tempo_list[-1]['sec6tpb1'] = sec6tpb
        ret_tempo_list.append({
            'tempo': msg.tempo,
            'tick0': tick,
            'sec6tpb0': sec6tpb,
        })

    ret_tempo_list[-1]['tick1'] = end_tick
    ret_tempo_list[-1]['sec6tpb1'] = (end_tick-ret_tempo_list[-1]['tick0'])*tempo
    
    ret_tempo_list = filter(lambda i:i['tick0']<i['tick1'],ret_tempo_list)
    ret_tempo_list = filter(lambda i:i['sec6tpb0']<i['sec6tpb1'],ret_tempo_list)
    ret_tempo_list = list(ret_tempo_list)
    
    return ret_tempo_list


def tick_to_sec6tpb(tick, tempo_list):
    #print(f'HGWHMWQKXA tick={tick}, tempo_list={tempo_list}')
    if tick < tempo_list[0]['tick1']:
        tempo = tempo_list[0]
    elif tick >= tempo_list[-1]['tick0']:
        tempo = tempo_list[-1]
    else:
        tempo = tempo_list
        tempo = filter(lambda i:i['tick0']<=tick,tempo)
        tempo = filter(lambda i:i['tick1']>tick,tempo)
        assert(len(tempo))
        tempo = tempo[0]
    return (tick-tempo['tick0'])*tempo['tempo']+tempo['sec6tpb0']


def sec6tpb_to_tick(sec6tpb, tempo_list):
    #print(f'IVBIQPSQAA sec6tpb={sec6tpb}, tempo_list={tempo_list}')
    if sec6tpb <= 0:
        tempo = tempo_list[0]
    if sec6tpb >= tempo_list[-1]['sec6tpb0']:
        tempo = tempo_list[-1]
    else:
        tempo = tempo_list
        tempo = filter(lambda i:i['sec6tpb0']<=sec6tpb,tempo)
        tempo = filter(lambda i:i['sec6tpb1']>sec6tpb,tempo)
        tempo = list(tempo)
        #print(f'DWKUYTSJIC sec6tpb={sec6tpb}, tempo={tempo}')
        assert(len(tempo)==1)
        tempo = tempo[0]
    return (sec6tpb-tempo['sec6tpb0'])/tempo['tempo']+tempo['tick0']


def track_data_chop_tick(track_data, start_bar_tick, start_note_tick, end_note_tick, end_bar_tick):
    start_bar_sec6tpb  = tick_to_sec6tpb(start_bar_tick,  track_data['tempo_list'])
    start_note_sec6tpb = tick_to_sec6tpb(start_note_tick, track_data['tempo_list'])
    end_note_sec6tpb   = tick_to_sec6tpb(end_note_tick,   track_data['tempo_list'])
    end_bar_sec6tpb    = tick_to_sec6tpb(end_bar_tick,    track_data['tempo_list'])

    out_track_data = copy.deepcopy(track_data)
    noteev_list = out_track_data['noteev_list']
    noteev_list = filter(_track_data_chop_time_noteev_filter(start_note_tick, end_note_tick), noteev_list)
    noteev_list = list(noteev_list)
    for noteev in noteev_list:
        noteev['tick0'] = max(noteev['tick0'], start_note_tick)
        noteev['tick1'] = min(noteev['tick1'], end_note_tick)
        noteev['tick'] = noteev['tick0']
        noteev['sec6tpb0'] = max(noteev['sec6tpb0'], start_note_sec6tpb)
        noteev['sec6tpb1'] = min(noteev['sec6tpb1'], end_note_sec6tpb)
        noteev['sec6tpb'] = noteev['sec6tpb0']

    noteev_off_list = map(_on_noteev_to_off_noteev, noteev_list)
    noteev_off_list = list(noteev_off_list)

    noteev_list = noteev_list + noteev_off_list
    noteev_list = sorted(noteev_list, key=_noteev_sort_key)

    out_track_data['noteev_list'] = noteev_list

    bar_list = out_track_data['bar_list']
    bar_list = filter(lambda i:i>=start_bar_tick ,bar_list)
    bar_list = filter(lambda i:i<=end_bar_tick ,bar_list)
    bar_list = list(bar_list)
    out_track_data['bar_list'] = bar_list

    out_track_data['bar_set'] = set(bar_list)

    tempo_list = out_track_data['tempo_list']
    tempo_list = filter(lambda i:i['tick1']> start_bar_tick,tempo_list)
    tempo_list = filter(lambda i:i['tick0']< end_bar_tick  ,tempo_list)
    tempo_list = list(tempo_list)
    for tempo in tempo_list:
        tempo['tick0'] = max(tempo['tick0'], start_bar_tick)
        tempo['tick1'] = min(tempo['tick1'], end_bar_tick)
        tempo['sec6tpb0'] = max(tempo['sec6tpb0'], start_bar_sec6tpb)
        tempo['sec6tpb1'] = min(tempo['sec6tpb1'], end_bar_sec6tpb)
    out_track_data['tempo_list'] = tempo_list
    return out_track_data

def _track_data_chop_time_noteev_filter(start_tick, end_tick):
    def _ret(noteev):
        if noteev['type'] != 'on': return False
        if noteev['tick0'] >= end_tick:   return False
        if noteev['tick1'] <  start_tick: return False
        return True
    return _ret

def _on_noteev_to_off_noteev(noteev):
    ret_data = {
        'tick':noteev['tick1'],
        'sec6tpb':noteev['sec6tpb1'],
        'type':'off',
        'channel':noteev['channel'],
        'pitch':noteev['pitch'],
    }
    return ret_data

def _noteev_sort_key(noteev):
    TYPE_TO_IDX={'off':0,'on':1}
    return (
        noteev['tick'],
        TYPE_TO_IDX[noteev['type']],
        noteev['channel'],
        noteev['pitch'],
    )

def _tempo_sort_key(tempo):
    return (
        tempo['tick0'],
        tempo['tick1'],
        tempo['sec6tpb0'],
        tempo['sec6tpb1'],
        tempo['tempo'],
    )

def track_data_move_tick(track_data, tick_diff):
    out_track_data = copy.deepcopy(track_data)
    noteev_list = out_track_data['noteev_list']
    for noteev in noteev_list:
        if 'tick' in noteev:  noteev['tick']+=tick_diff
        if 'tick0' in noteev: noteev['tick0']+=tick_diff
        if 'tick1' in noteev: noteev['tick1']+=tick_diff

    bar_list = out_track_data['bar_list']
    bar_list = map(lambda i:i+tick_diff, bar_list)
    bar_list = list(bar_list)
    out_track_data['bar_list'] = bar_list

    tempo_list = out_track_data['tempo_list']
    for tempo in tempo_list:
        tempo['tick0'] += tick_diff
        tempo['tick1'] += tick_diff
    return out_track_data

def track_data_move_sec6tpb(track_data, sec6tpb_diff):
    out_track_data = copy.deepcopy(track_data)
    noteev_list = out_track_data['noteev_list']
    for noteev in noteev_list:
        if 'sec6tpb' in noteev:  noteev['sec6tpb']+=sec6tpb_diff
        if 'sec6tpb0' in noteev: noteev['sec6tpb0']+=sec6tpb_diff
        if 'sec6tpb1' in noteev: noteev['sec6tpb1']+=sec6tpb_diff

    tempo_list = out_track_data['tempo_list']
    for tempo in tempo_list:
        tempo['sec6tpb0'] += sec6tpb_diff
        tempo['sec6tpb1'] += sec6tpb_diff
    return out_track_data

# def merge_track_data(track_data_list):
#     output_data = {}
#     
#     ticks_per_beat = map(lambda i:i['ticks_per_beat'],m_data_list)
#     ticks_per_beat = set(ticks_per_beat)
#     assert(len(ticks_per_beat)==1)
#     ticks_per_beat = list(ticks_per_beat)[0]
#     output_data['ticks_per_beat'] = ticks_per_beat
# 
#     track_cnt = map(lambda i:len(i['track_list']),m_data_list)
#     track_cnt = max(track_cnt)
#     output_data['track_list'] = []
#     for track_id in range(track_cnt):
#         src_track_data_list = filter(lambda i:len(i['track_list'])>track_id, m_data_list)
#         src_track_data_list = list(map(lambda i:i['track_list'][track_id], m_data_list))
#         
#         output_track_data = _merge_track_data(src_track_data_list)
#         output_data['track_list'].append(output_track_data)
# 
#     return output_data

def merge_track_data(src_track_data_list):
    output_track_data = {}
    output_track_data['name'] = src_track_data_list[0]['name']

    noteev_list = itertools.chain(*list(map(lambda i:i['noteev_list'],src_track_data_list)))
    noteev_list = sorted(noteev_list, key=_noteev_sort_key)
    on_channel_pitch_set = set()
    #print(noteev_list)
    #print(json.dumps(noteev_list,indent=2))
    for noteev in noteev_list:
        #print(f'BYFKBGRYBS noteev={noteev}')
        channel_pitch = (noteev['channel'], noteev['pitch'])
        if noteev['type'] == 'on':
            if channel_pitch in on_channel_pitch_set:
                assert(False)
            on_channel_pitch_set.add(channel_pitch)
        elif noteev['type'] == 'off':
            assert(channel_pitch in on_channel_pitch_set)
            on_channel_pitch_set.remove(channel_pitch)
        else:
            assert(False)
    output_track_data['noteev_list'] = noteev_list

    bar_list = itertools.chain(*list(map(lambda i:i['bar_list'],src_track_data_list)))
    bar_list = sorted(list(set(bar_list)))
    output_track_data['bar_list'] = bar_list

    output_track_data['bar_set'] = set(output_track_data['bar_list'])

    src_tempo_list = itertools.chain(*list(map(lambda i:i['tempo_list'],src_track_data_list)))
    src_tempo_list = sorted(src_tempo_list, key=_tempo_sort_key)
    #print(json.dumps(tempo_list,indent=2))
    #for i in range(len(tempo_list)-1):
    #    tempo0 = tempo_list[i]
    #    tempo1 = tempo_list[i+1]
    #    assert(tempo0['tick1']==tempo1['tick0'])
    #    assert(tempo0['sec6tpb1']==tempo1['sec6tpb0'])
    #output_track_data['tempo_list'] = tempo_list
    #print(f'AVYZPMFEOG src_tempo_list={src_tempo_list}')
    out_tempo_list = []
    out_tempo_list.append(src_tempo_list[0])
    for src_tempo in src_tempo_list[1:]:
        assert(src_tempo['tick0']>=out_tempo_list[-1]['tick1'])
        assert(src_tempo['sec6tpb0']>=out_tempo_list[-1]['sec6tpb1'])
        if src_tempo['tick0'] > out_tempo_list[-1]['tick1']:
            tick = src_tempo['tick0'] - out_tempo_list[-1]['tick1']
            sec6tpb = src_tempo['sec6tpb0'] - out_tempo_list[-1]['sec6tpb1']
            tempo = {
                'tempo': sec6tpb/tick,
                'tick0': out_tempo_list[-1]['tick1'],
                'sec6tpb0': out_tempo_list[-1]['sec6tpb1'],
                'tick1': src_tempo['tick0'],
                'sec6tpb1': src_tempo['sec6tpb0'],
            }
            out_tempo_list.append(tempo)
        out_tempo_list.append(src_tempo)
    #print(f'TVNNIFCPIK out_tempo_list={out_tempo_list}')
    output_track_data['tempo_list'] = out_tempo_list

    output_track_data['max_pitch'] = max(map(lambda i:i['max_pitch'],src_track_data_list))
    output_track_data['min_pitch'] = min(map(lambda i:i['min_pitch'],src_track_data_list))
    
    return output_track_data

# speed_factor: >1: slower, <1: faster
def track_data_change_speed(track_data, speed_factor):
    out_track_data = copy.deepcopy(track_data)
    for noteev in out_track_data['noteev_list']:
        if 'sec6tpb'  in noteev: noteev['sec6tpb']  *= speed_factor
        if 'sec6tpb0' in noteev: noteev['sec6tpb0'] *= speed_factor
        if 'sec6tpb1' in noteev: noteev['sec6tpb1'] *= speed_factor

    for tempo in out_track_data['tempo_list']:
        tempo['tempo']    *= speed_factor
        tempo['sec6tpb0'] *= speed_factor
        tempo['sec6tpb1'] *= speed_factor

    return out_track_data
