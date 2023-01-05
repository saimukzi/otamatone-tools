import argparse
import json
import mido
import mido.messages.specs
import mido.midifiles.meta


def mid_to_data(mid):
    output_data = {}
    output_data['ticks_per_beat'] = mid.ticks_per_beat
    output_data['type'] = mid.type
    output_data['tracks'] = list(map(track_to_data,mid.tracks))
    return output_data


def track_to_data(track):
    track_data = {}
    track_data['name'] = track.name
    track_data['msgs'] = list(map(msg_to_data,track))
    return track_data


def msg_to_data(msg):
    # print(msg)
    # print(msg.hex())
    message_data = {}
    message_data['time']  = msg.time
    message_data['type']  = msg.type
    if msg.type in MSG_TYPE_TO_SPEC_DICT:
        spec = MSG_TYPE_TO_SPEC_DICT[msg.type]
        for value_name in spec['value_names']:
            message_data[value_name] = getattr(msg,value_name)
    if msg.type in MSG_TYPE_TO_METASPEC_DICT:
        spec = MSG_TYPE_TO_METASPEC_DICT[msg.type]
        for attr in spec.attributes:
            message_data[attr] = getattr(msg,attr)
    return message_data


MSG_TYPE_TO_SPEC_DICT = {}
for spec in mido.messages.specs.SPECS:
    MSG_TYPE_TO_SPEC_DICT[spec['type']] = spec

MSG_TYPE_TO_METASPEC_DICT = mido.midifiles.meta._META_SPEC_BY_TYPE

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input_mid_path')
    parser.add_argument('output_json_path')
    args = parser.parse_args()

    mid = mido.MidiFile(args.input_mid_path)
    mid_data = mid_to_data(mid)
    with open(args.output_json_path, mode='w') as fout:
        json.dump(mid_data, fout, sort_keys=True, indent=2)
        fout.write('\n')
