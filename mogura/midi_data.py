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
    track_data['name'] = track.name
    track_data['noteev_list'] = track_to_noteev_list(track)
    end_tick = track_data['noteev_list'][-1]['tick']
    track_data['bar_list']   = track_to_bar_list(track,end_tick,ticks_per_beat)
    track_data['tempo_list'] = track_to_tempo_list(track,end_tick,ticks_per_beat)
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
        if noteev['type'] == 'on':
            cp = (noteev['channel'],'pitch')
            cp_to_noteev_dict[cp] = noteev
        elif noteev['type'] == 'off':
            cp = (noteev['channel'],'pitch')
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
