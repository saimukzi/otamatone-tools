import copy
import itertools
#import json
import math
import mido


INF = float('inf')


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
#    end_tick = track_data['noteev_list'][-1]['tick']
#    track_data['bar_list']   = track_to_bar_list(track,end_tick,ticks_per_beat)
#    track_data['bar_set']    = set(track_data['bar_list'])
    track_data['time_signature_list'] = track_to_time_signature_list(track)
    track_data['tempo_list'] = track_to_tempo_list(track,ticks_per_beat)

    max_pitch = track_data['noteev_list']
    max_pitch = map(lambda i:i['pitch'],max_pitch)
    max_pitch = max(max_pitch)
    track_data['max_pitch'] = max_pitch

    min_pitch = track_data['noteev_list']
    min_pitch = map(lambda i:i['pitch'],min_pitch)
    min_pitch = min(min_pitch)
    track_data['min_pitch'] = min_pitch

    tick1 = track_to_end_tick(track)
    if tick1 is None:
        tick1 = last_bar_tick(track_data)
    track_data['tick1'] = tick1

    return track_data


def track_to_noteev_list(track):
    ret_noteev_list = []
    tick = 0
    tempo = 0
    for msg in track:
        tick += msg.time
        if msg.type == 'note_on' and msg.velocity > 0:
            noteev = {
                'tick':tick,
                'type':'on',
                'channel':0,
                'pitch':msg.note,
                'tick0':tick,
            }
            noteev = (tick,1,msg.channel,msg.note,noteev)
            ret_noteev_list.append(noteev)
        elif msg.type == 'note_off' or msg.type == 'note_on':
            noteev = {
                'tick':tick,
                'type':'off',
                'channel':0,
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
            del cp_to_noteev_dict[cp]
    
    return ret_noteev_list


#def track_to_bar_list(track,end_tick,ticks_per_beat):
#    time_signature_list = []
#    time_signature_list.append({
#        'numerator': 4,
#        'denominator': 4,
#        'tick0': 0,
#    })
#    tick = 0
#    for msg in track:
#        tick += msg.time
#        if msg.type != 'time_signature': continue
#        time_signature_list[-1]['tick1'] = tick
#        time_signature_list.append({
#            'numerator': msg.numerator,
#            'denominator': msg.denominator,
#            'tick0': tick,
#        })
#
#    time_signature_list[-1]['tick1'] = end_tick
#
#    ret_bar_list = []
#    for time_signature in time_signature_list:
#        tick = time_signature['tick0']
#        dtick = ticks_per_beat * time_signature['numerator'] * 4 // time_signature['denominator']
#        while tick < time_signature['tick1']:
#            ret_bar_list.append(tick)
#            tick += dtick
#    ret_bar_list.append(tick)
#    ret_bar_list.sort()
#    
#    return ret_bar_list


def track_to_time_signature_list(track):
    time_signature_list = []
    time_signature_list.append({
        'numerator': 4,
        'denominator': 4,
        'tick0': 0,
        'tick1': INF,
        'tick_anchor':0,
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
            'tick1': INF,
            'tick_anchor': tick,
        })

    time_signature_list = list(filter(lambda i:i['tick0']<i['tick1'], time_signature_list))
    time_signature_list[0]['tick0'] = -INF
    
    _check_time_signature_list(time_signature_list)

    return time_signature_list


def track_to_tempo_list(track,ticks_per_beat):
    ret_tempo_list = []
    ret_tempo_list.append({
        'tick0': 0,
        'tempo': 500000,
    })
    tick = 0
    tempo = 0
    for msg in track:
        tick += msg.time
        if msg.type != 'set_tempo': continue
        tempo = msg.tempo
        ret_tempo_list[-1]['tick1'] = tick
        ret_tempo_list.append({
            'tempo': msg.tempo,
            'tick0': tick,
        })

    #print(ret_tempo_list[-1])
    #ret_tempo_list[-1]['tick1'] = max(end_tick,tick)
    ret_tempo_list[-1]['tick1'] = INF
    
    ret_tempo_list = filter(lambda i:i['tick0']<i['tick1'],ret_tempo_list)
    ret_tempo_list = list(ret_tempo_list)
    ret_tempo_list[0]['tick0'] = -INF
    
    _check_tempo_list(ret_tempo_list)
    
    return ret_tempo_list


def tick_to_sec6tpb(tick, tempo_list, time_multiplier):
    #print(f'HGWHMWQKXA tick={tick}, tempo_list={tempo_list}')
    tempo = tempo_list
    tempo = filter(lambda i:i['tick0']<=tick,tempo)
    tempo = filter(lambda i:i['tick1']>tick,tempo)
    tempo = list(tempo)
    if len(tempo) != 1:
        print(f'tick={tick}, tempo={tempo}')
        assert(False)
    tempo = tempo[0]
    return (tick-tempo['tick_anchor'])*tempo['tempo']*time_multiplier+tempo['sec6tpb_anchor']


def sec6tpb_to_tick(sec6tpb, tempo_list, time_multiplier):
    #print(f'IVBIQPSQAA sec6tpb={sec6tpb}, tempo_list={tempo_list}')
    tempo = tempo_list
    tempo = filter(lambda i:i['sec6tpb0']<=sec6tpb,tempo)
    tempo = filter(lambda i:i['sec6tpb1']>sec6tpb,tempo)
    tempo = list(tempo)
    if len(tempo) != 1:
        print(tempo)
        assert(False)
    tempo = tempo[0]
    return (sec6tpb-tempo['sec6tpb_anchor'])/tempo['tempo']/time_multiplier+tempo['tick_anchor']


def track_data_chop_tick(track_data, start_bar_tick, start_note_tick, end_note_tick, end_bar_tick):
    _check_tempo_list(track_data['tempo_list'])

    out_track_data = copy.deepcopy(track_data)
    noteev_list = out_track_data['noteev_list']
    noteev_list = filter(_track_data_chop_time_noteev_filter(start_note_tick, end_note_tick), noteev_list)
    noteev_list = list(noteev_list)
    for noteev in noteev_list:
        noteev['tick0'] = max(noteev['tick0'], start_note_tick)
        noteev['tick1'] = min(noteev['tick1'], end_note_tick)
        noteev['tick'] = noteev['tick0']

    noteev_off_list = map(_on_noteev_to_off_noteev, noteev_list)
    noteev_off_list = list(noteev_off_list)

    noteev_list = noteev_list + noteev_off_list
    noteev_list = sorted(noteev_list, key=_noteev_sort_key)

    out_track_data['noteev_list'] = noteev_list

#    bar_list = out_track_data['bar_list']
#    bar_list = filter(lambda i:i>=start_bar_tick ,bar_list)
#    bar_list = filter(lambda i:i<=end_bar_tick ,bar_list)
#    bar_list = list(bar_list)
#    out_track_data['bar_list'] = bar_list
#    out_track_data['bar_set'] = set(bar_list)

    time_signature_list = out_track_data['time_signature_list']
    time_signature_list = filter(lambda i:i['tick1']>start_bar_tick, time_signature_list)
    time_signature_list = filter(lambda i:i['tick0']<end_bar_tick,   time_signature_list)
    time_signature_list = list(time_signature_list)
    # for time_signature in time_signature_list:
    #     time_signature['tick0'] = max(time_signature['tick0'], start_bar_tick)
    #     time_signature['tick1'] = min(time_signature['tick1'], end_bar_tick)
    time_signature_list[0]['tick0']  = -INF
    time_signature_list[-1]['tick1'] = INF
    _check_time_signature_list(time_signature_list)
    out_track_data['time_signature_list'] = time_signature_list

    tempo_list = out_track_data['tempo_list']
    _check_tempo_list(tempo_list)
    tempo_list = filter(lambda i:i['tick1']> start_bar_tick,tempo_list)
    tempo_list = filter(lambda i:i['tick0']< end_bar_tick  ,tempo_list)
    tempo_list = list(tempo_list)
    #for tempo in tempo_list:
    #    tempo['tick0'] = max(tempo['tick0'], start_bar_tick)
    #    tempo['tick1'] = min(tempo['tick1'], end_bar_tick)
    tempo_list[0]['tick0'] = -INF
    tempo_list[-1]['tick1'] = INF
    _check_tempo_list(tempo_list)
    out_track_data['tempo_list'] = tempo_list

    return out_track_data

def _track_data_chop_time_noteev_filter(start_tick, end_tick):
    def _ret(noteev):
        if noteev['type'] != 'on': return False
        if noteev['tick0'] >= end_tick:   return False
        if noteev['tick1'] <= start_tick: return False
        return True
    return _ret

def _on_noteev_to_off_noteev(noteev):
    #print(f'noteev={noteev}')
    ret_data = {
        'tick':noteev['tick1'],
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
        tempo['tempo'],
    )

def _time_signature_sort_key(ts):
    return (
        ts['tick0'],
        ts['tick1'],
        ts['numerator'],
        ts['denominator'],
    )

def track_data_move_tick(track_data, tick_diff):
    out_track_data = copy.deepcopy(track_data)
    noteev_list = out_track_data['noteev_list']
    for noteev in noteev_list:
        if 'tick' in noteev:  noteev['tick']+=tick_diff
        if 'tick0' in noteev: noteev['tick0']+=tick_diff
        if 'tick1' in noteev: noteev['tick1']+=tick_diff

#    bar_list = out_track_data['bar_list']
#    bar_list = map(lambda i:i+tick_diff, bar_list)
#    bar_list = list(bar_list)
#    out_track_data['bar_list'] = bar_list
#    out_track_data['bar_set'] = set(bar_list)

    time_signature_list = out_track_data['time_signature_list']
    for time_signature in time_signature_list:
        time_signature['tick0'] += tick_diff
        time_signature['tick1'] += tick_diff
        time_signature['tick_anchor'] += tick_diff

    tempo_list = out_track_data['tempo_list']
    for tempo in tempo_list:
        tempo['tick0'] += tick_diff
        tempo['tick1'] += tick_diff

    return out_track_data

# def track_data_move_sec6tpb(track_data, sec6tpb_diff):
#     out_track_data = copy.deepcopy(track_data)
#     noteev_list = out_track_data['noteev_list']
#     for noteev in noteev_list:
#         if 'sec6tpb' in noteev:  noteev['sec6tpb']+=sec6tpb_diff
#         if 'sec6tpb0' in noteev: noteev['sec6tpb0']+=sec6tpb_diff
#         if 'sec6tpb1' in noteev: noteev['sec6tpb1']+=sec6tpb_diff
# 
#     tempo_list = out_track_data['tempo_list']
#     for tempo in tempo_list:
#         tempo['sec6tpb0'] += sec6tpb_diff
#         tempo['sec6tpb1'] += sec6tpb_diff
#     return out_track_data

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

def merge_track_data(src_track_data_list, tick_list):
    assert(len(tick_list)+1 == len(src_track_data_list))

    output_track_data = {}
    output_track_data['name'] = src_track_data_list[0]['name']
    
    tpb = set(map(lambda i:i['ticks_per_beat'],src_track_data_list))
    assert(len(tpb)==1)
    tpb = list(tpb)[0]
    output_track_data['ticks_per_beat'] = tpb

    noteev_list = itertools.chain(*list(map(lambda i:i['noteev_list'],src_track_data_list)))
    noteev_list = sorted(noteev_list, key=_noteev_sort_key)
    on_channel_pitch_set = set()
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

    # bar_list = itertools.chain(*list(map(lambda i:i['bar_list'],src_track_data_list)))
    # bar_list = sorted(list(set(bar_list)))
    # output_track_data['bar_list'] = bar_list
    # output_track_data['bar_set'] = set(output_track_data['bar_list'])
    src_time_signature_list_list = copy.deepcopy(list(map(lambda i:i['time_signature_list'],src_track_data_list)))
    for time_signature_list in src_time_signature_list_list:
        _check_time_signature_list(time_signature_list)
    for i in range(len(tick_list)):
        src_time_signature_list_list[i][-1]['tick1'] = tick_list[i]
        src_time_signature_list_list[i+1][0]['tick0'] = tick_list[i]
    time_signature_list = itertools.chain(*src_time_signature_list_list)
    time_signature_list = list(time_signature_list)
    _check_time_signature_list(time_signature_list)
    #time_signature_list = sorted(time_signature_list, key=_time_signature_sort_key)
    #for i in range(len(time_signature_list)-1):
    #    time_signature0 = time_signature_list[i]
    #    time_signature1 = time_signature_list[i+1]
    #    assert( (time_signature0['tick1'] == INF) or (time_signature0['tick1'] <= time_signature1['tick0']) )
    #    time_signature0['tick1'] = time_signature1['tick0']
    output_track_data['time_signature_list']= time_signature_list

    src_tempo_list_list = copy.deepcopy(list(map(lambda i:i['tempo_list'],src_track_data_list)))
    for src_tempo_list in src_tempo_list_list:
        #print(src_tempo_list)
        _check_tempo_list(src_tempo_list)
    for i in range(len(tick_list)):
        src_tempo_list_list[i][-1]['tick1'] = tick_list[i]
        src_tempo_list_list[i+1][0]['tick0'] = tick_list[i]
    out_tempo_list = itertools.chain(*src_tempo_list_list)
    out_tempo_list = list(out_tempo_list)
    _check_tempo_list(out_tempo_list)
    #src_tempo_list = sorted(src_tempo_list, key=_tempo_sort_key)
    #print(json.dumps(tempo_list,indent=2))
    #for i in range(len(tempo_list)-1):
    #    tempo0 = tempo_list[i]
    #    tempo1 = tempo_list[i+1]
    #    assert(tempo0['tick1']==tempo1['tick0'])
    #    assert(tempo0['sec6tpb1']==tempo1['sec6tpb0'])
    #output_track_data['tempo_list'] = tempo_list
    # print(f'AVYZPMFEOG src_tempo_list={src_tempo_list}')
    # out_tempo_list = []
    # out_tempo_list.append(src_tempo_list[0])
    # for src_tempo in src_tempo_list[1:]:
    #     assert(src_tempo['tick0']>=out_tempo_list[-1]['tick1'])
    #     assert(src_tempo['sec6tpb0']>=out_tempo_list[-1]['sec6tpb1'])
    #     if src_tempo['tick0'] > out_tempo_list[-1]['tick1']:
    #         tick = src_tempo['tick0'] - out_tempo_list[-1]['tick1']
    #         sec6tpb = src_tempo['sec6tpb0'] - out_tempo_list[-1]['sec6tpb1']
    #         tempo = {
    #             'tempo': sec6tpb/tick,
    #             'tick0': out_tempo_list[-1]['tick1'],
    #             'sec6tpb0': out_tempo_list[-1]['sec6tpb1'],
    #             'tick1': src_tempo['tick0'],
    #             'sec6tpb1': src_tempo['sec6tpb0'],
    #         }
    #         out_tempo_list.append(tempo)
    #     out_tempo_list.append(src_tempo)
    #print(f'TVNNIFCPIK out_tempo_list={out_tempo_list}')
    output_track_data['tempo_list'] = out_tempo_list

    output_track_data['max_pitch'] = max(map(lambda i:i['max_pitch'],src_track_data_list))
    output_track_data['min_pitch'] = min(map(lambda i:i['min_pitch'],src_track_data_list))
    
    return output_track_data

# # time_multiplier: >1: slower, <1: faster
# def track_data_time_multiply(track_data, time_multiplier):
#     out_track_data = copy.deepcopy(track_data)
#     # for noteev in out_track_data['noteev_list']:
#     #     if 'sec6tpb'  in noteev: noteev['sec6tpb']  *= time_multiplier
#     #     if 'sec6tpb0' in noteev: noteev['sec6tpb0'] *= time_multiplier
#     #     if 'sec6tpb1' in noteev: noteev['sec6tpb1'] *= time_multiplier
# 
#     for tempo in out_track_data['tempo_list']:
#         tempo['tempo']    *= time_multiplier
#         tempo['sec6tpb0'] *= time_multiplier
#         tempo['sec6tpb1'] *= time_multiplier
# 
#     return out_track_data


def fill_sec6tpb(track_data, time_multiplier):
    track_data['time_multiplier'] = time_multiplier
    tempo_list = track_data['tempo_list']
    _check_tempo_list(tempo_list)
    sec6tpb = 0
    tick = 0
    for tempo in tempo_list:
        tempo['sec6tpb0'] = sec6tpb
        tempo['tick_anchor'] = tick
        tempo['sec6tpb_anchor'] = sec6tpb
        tick_inc = tempo['tick1']-tick
        sec6tpb_inc = tick_inc*tempo['tempo']*time_multiplier
        tick += tick_inc
        sec6tpb += sec6tpb_inc
        tempo['sec6tpb1'] = sec6tpb
    tempo_list[0]['sec6tpb0'] = -INF
    tempo_list[-1]['sec6tpb0'] = INF
    for noteev in track_data['noteev_list']:
        if 'tick'  in noteev: noteev['sec6tpb']  = tick_to_sec6tpb(noteev['tick'],  tempo_list, time_multiplier)
        if 'tick0' in noteev: noteev['sec6tpb0'] = tick_to_sec6tpb(noteev['tick0'], tempo_list, time_multiplier)
        if 'tick1' in noteev: noteev['sec6tpb1'] = tick_to_sec6tpb(noteev['tick1'], tempo_list, time_multiplier)

def track_data_add_woodblock(track_data, start_tick, end_tick):
    out_track_data = copy.deepcopy(track_data)

    tpb = out_track_data['ticks_per_beat']
    # time_signature_list = out_track_data['time_signature_list']
    beat_itr = get_beat_itr(start_tick, tpb)
    bar_itr = get_bar_itr(start_tick, out_track_data)
    bar = next(bar_itr)

    on_noteev_list = []
#    for i in range(out_track_data['bar_list'][0],out_track_data['bar_list'][-1]+1,out_track_data['ticks_per_beat']):
    #start_tick = math.ceil(start_tick/tpb)*tpb
    #print(start_tick,end_tick)
    for i in beat_itr:
        if i >= end_tick: break
        pitch = 84 if i == bar else 60
        tick0 = i
        tick1 = i+tpb//2
        on_noteev_list.append({
            'tick':tick0,
            'tick0':tick0,
            'tick1':tick1,
            'type':'on',
            'pitch':pitch,
            'channel':15,
        })
        if i >= bar: bar=next(bar_itr)
    
    off_noteev_list = list(map(_on_noteev_to_off_noteev,on_noteev_list))
    noteev_list = out_track_data['noteev_list'] + on_noteev_list + off_noteev_list
    noteev_list = sorted(noteev_list, key=_noteev_sort_key)
    out_track_data['noteev_list'] = noteev_list

    return out_track_data

def is_bar(tick, track_data):
    tpb = track_data['ticks_per_beat']
    ts = track_data['time_signature_list']
    ts = list(filter(lambda i:i['tick1']>tick, ts))[0]
    return ((tick-ts['tick0'])*ts['denominator']/tpb/4)%ts['numerator'] == 0

def last_bar_tick(track_data):
    tpb  = track_data['ticks_per_beat']
    tick = track_data['noteev_list']
    tick = list(filter(lambda i:i['type']=='on',tick))[-1]['tick1']
    ts = track_data['time_signature_list'][-1]
    bar_tick = get_bar_tick(ts, tpb)
    assert(tick>=ts['tick0'])
    tick -= ts['tick_anchor']
    tick = math.ceil(tick/bar_tick)
    tick = tick*bar_tick
    assert(tick==math.floor(tick))
    tick = math.floor(tick)
    tick += ts['tick_anchor']
    return tick

def get_bar_itr(tick0, track_data):
    tpb = track_data['ticks_per_beat']
    time_signature_list = track_data['time_signature_list']
    time_signature_list = list(filter(lambda i:i['tick1']>tick0,time_signature_list))
    tsi = 0
    ts = time_signature_list[tsi]
    bar_tick = get_bar_tick(ts, tpb)
    tick = tick0
    tick -= ts['tick_anchor']
    tick = math.ceil(tick/bar_tick)
    tick = tick*bar_tick
    assert(tick==math.floor(tick))
    tick += ts['tick_anchor']
    while True:
        yield(tick)
        tick += bar_tick
        if tick >= ts['tick1']:
            tsi += 1
            # tick = time_signature_list[tsi]['tick0']
            ts = time_signature_list[tsi]
            bar_tick = get_bar_tick(ts, tpb)
            tick -= ts['tick_anchor']
            tick = math.ceil(tick/bar_tick)*bar_tick
            tick += ts['tick_anchor']


def get_bar_tick(ts, tpb):
    return tpb*4*ts['numerator']//ts['denominator']


def get_beat_itr(tick0, tpb):
    tick = tick0
    tick = math.ceil(tick/tpb) * tpb
    while True:
        yield(tick)
        tick += tpb


def track_to_end_tick(track):
    tick = 0
    for msg in track:
        tick += msg.time
        if msg.type != 'cue_marker': continue
        if msg.text != 'smz-end': continue
        return tick
    return None


def _check_time_signature_list(time_signature_list):
    assert(time_signature_list[0]['tick0']==-INF)
    assert(time_signature_list[-1]['tick1']==INF)
    for time_signature in time_signature_list:
        tick = time_signature['tick1']-time_signature['tick0']
    for i in range(len(time_signature_list)-1):
        assert(time_signature_list[i]['tick1']==time_signature_list[i+1]['tick0'])

def _check_tempo_list(tempo_list):
    assert(tempo_list[0]['tick0']==-INF)
    assert(tempo_list[-1]['tick1']==INF)
    for tempo in tempo_list:
        tick = tempo['tick1']-tempo['tick0']
    for i in range(len(tempo_list)-1):
        assert(tempo_list[i]['tick1']==tempo_list[i+1]['tick0'])
