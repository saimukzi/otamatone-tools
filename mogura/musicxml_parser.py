import xml.etree.ElementTree as ET
import midi_data

DEFAULT_TICKS_PER_BEAT = 480

def path_to_data(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    midi_data = {}
    midi_data['ticks_per_beat'] = DEFAULT_TICKS_PER_BEAT
    midi_data['track_list'] = []
    midi_data['audio_data'] = None

    for part in root.findall('part'):
        track_data = part_to_track_data(part)
        midi_data['track_list'].append(track_data)

    for track in midi_data['track_list']:
        for tempo in track['tempo_list']:
            tempo['orisec0'] = tempo['temposec0']
            tempo['orisec1'] = tempo['temposec1']

    return midi_data

def part_to_track_data(part):
    track_data = {}
    track_data['ticks_per_beat'] = DEFAULT_TICKS_PER_BEAT
    track_data['name'] = f'Part {part.attrib["id"]}'
    track_data['noteev_list'] = part_to_noteev_list(part)
    # track_data['time_signature_list'] = part_to_time_signature_list(part)
    # track_data['tempo_list'] = part_to_tempo_list(part)
    track_data['time_signature_list'],track_data['tempo_list'],track_data['key_signature_list'], end_tick \
        = part_to_time_signature_list_tempo_list_key_signature_list_end_tick(part)

    opitch1 = track_data['noteev_list']
    opitch1 = map(lambda i:i['opitch'],opitch1)
    opitch1 = max(opitch1)
    track_data['opitch1'] = opitch1

    opitch0 = track_data['noteev_list']
    opitch0 = map(lambda i:i['opitch'],opitch0)
    opitch0 = min(opitch0)
    track_data['opitch0'] = opitch0

    notetick0 = track_data['noteev_list']
    notetick0 = filter(lambda i:i['type']=='on',notetick0)
    notetick0 = map(lambda i:i['tick0'],notetick0)
    notetick0 = min(notetick0)
    track_data['notetick0'] = notetick0

    notetick1 = track_data['noteev_list']
    notetick1 = filter(lambda i:i['type']=='on',notetick1)
    notetick1 = map(lambda i:i['tick1'],notetick1)
    notetick1 = max(notetick1)
    track_data['notetick1'] = notetick1

    # tick1 = part_to_end_tick(part)
    # if tick1 is None:
    #     tick1 = midi_data.last_bar_tick(track_data)
    track_data['tick1'] = end_tick

    return track_data

def part_to_noteev_list(part):
    ret_noteev_list = []
    tick = 0
    divisions = None
    slur_level = 0
    for ele in part.findall('.//'):
        if ele.tag == 'divisions':
            divisions = int(ele.text)
        if ele.tag == 'note':
            dtick = int(ele.find('duration').text) * DEFAULT_TICKS_PER_BEAT / divisions
            tick0 = tick
            tick1 = tick+dtick
            pitch_ele = ele.find('pitch')
            if pitch_ele is not None:
                slur_ele = ele.find('notations/slur')
                if slur_ele is not None:
                    if slur_ele.attrib['type'] == 'start':
                        slur_level += 1
                    if slur_ele.attrib['type'] == 'stop':
                        slur_level -= 1
                tie_ele_list = ele.findall('tie')
                for tie_ele in tie_ele_list:
                    if tie_ele.attrib['type'] == 'start':
                        slur_level += 1
                    if tie_ele.attrib['type'] == 'stop':
                        slur_level -= 1
                pitch = parse_pitch(pitch_ele)
                noteev = {
                    'usage': 'OTM',
                    'tick': tick0,
                    'type': 'on',
                    'channel': 0,
                    'opitch': pitch,
                    'tick0': tick0,
                    'tick1': tick1,
                    'slur': slur_level>0,
                }
                ret_noteev_list.append(noteev)
            tick = tick1

    assert(slur_level == 0)

    ret_noteev_list = midi_data.noteev_list_process_slur(ret_noteev_list)

    return ret_noteev_list

STEP_TO_PITCH = {
    'C': 0,
    'D': 2,
    'E': 4,
    'F': 5,
    'G': 7,
    'A': 9,
    'B': 11
}
def parse_pitch(pitch):
    step = pitch.find('step').text
    octave = int(pitch.find('octave').text)
    alter = 0
    if pitch.find('alter') is not None:
        alter = int(pitch.find('alter').text)
    return 12 + 12 * octave + STEP_TO_PITCH[step] + alter

FIFTHS_TO_KEY_DICT = {
    0: 'C',
    1: 'G',
    2: 'D',
    3: 'A',
    4: 'E',
    5: 'B',
    6: 'F#',
    -1: 'F',
    -2: 'Bb',
    -3: 'Eb',
    -4: 'Ab',
    -5: 'Db',
    -6: 'Gb',
}

def part_to_time_signature_list_tempo_list_key_signature_list_end_tick(part):
    time_signature_list = []
    ret_tempo_list = []
    ret_tempo_list.append({
        'tick0': 0,
        'tempo': 500000,
    })
    key_signature_list = []
    key_signature_list.append({
        'key': None,
        'tick0': 0,
    })

    tick = 0
    time_signature = None
    divisions = 0
    tick_per_measure = 0
    for ele in part.findall('.//'):
        print(ele.tag)
        if ele.tag == 'measure':
            tick += tick_per_measure
        if ele.tag == 'attributes':
            time_ele = ele.find('time')
            if time_ele is not None:
                if len(time_signature_list) > 0:
                    time_signature_list[-1]['tick1'] = tick
                time_signature = {
                    'numerator': int(time_ele.find('beats').text),
                    'denominator': int(time_ele.find('beat-type').text),
                    'tick0': tick,
                    'tick_anchor': tick,
                }
                time_signature_list.append(time_signature)
            divisions_ele = ele.find('divisions')
            if divisions_ele is not None:
                divisions = int(divisions_ele.text)
            tick_per_measure = time_signature['numerator'] * DEFAULT_TICKS_PER_BEAT * 4 / time_signature['denominator']
        if ele.tag == 'sound':
            tempo = int(ele.attrib['tempo'])
            ret_tempo_list[-1]['tick1'] = tick
            ret_tempo_list.append({
                'tempo': 60*1000000/tempo,
                'tick0': tick,
            })
        if ele.tag == 'key':
            fifths = ele.find('fifths').text
            key = FIFTHS_TO_KEY_DICT[int(fifths)]
            pitch = midi_data.SIGNATURE_KEY_NAME_TO_DO_PITCH_DICT[key]
            key_signature_list[-1]['tick1'] = tick
            key_signature_list.append({
                'key': pitch,
                'tick0': tick,
            })

    time_signature_list[-1]['tick1'] = tick
    midi_data._check_time_signature_list(time_signature_list)

    ret_tempo_list[-1]['tick1'] = tick
    ret_tempo_list = filter(lambda i:i['tick0']<i['tick1'],ret_tempo_list)
    ret_tempo_list = list(ret_tempo_list)

    temposec = 0
    for tempo in ret_tempo_list:
        tempo['temposec0'] = temposec
        tick = tempo['tick1']-tempo['tick0']
        temposec += tick*tempo['tempo']/1000000/DEFAULT_TICKS_PER_BEAT
        tempo['temposec1'] = temposec
    
    midi_data._check_tempo_list(ret_tempo_list)

    key_signature_list[-1]['tick1'] = tick
    key_signature_list = list(filter(lambda i:i['tick0']<i['tick1'], key_signature_list))

    midi_data._check_key_signature_list(key_signature_list)

    print(time_signature_list)

    return time_signature_list, ret_tempo_list, key_signature_list, tick
