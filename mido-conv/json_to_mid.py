import argparse
import json
import mido
import mido.messages.specs
import mido.midifiles.meta

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('input_json_path')
    parser.add_argument('output_mid_path')
    args = parser.parse_args()

    with open(args.input_json_path) as fin:
        mid_data = json.load(fin)
    mid = data_to_mid(mid_data)
    mid.save(args.output_mid_path)


def data_to_mid(data):
    ret_mid = mido.MidiFile(
        type = data.get('type', 1),
        ticks_per_beat = data.get('ticks_per_beat', 480),
        tracks = list(map(data_to_track,data['tracks'])) if ('tracks' in data) else None,
    )
    return ret_mid


def data_to_track(data):
    ret_track = mido.MidiTrack()
    if 'name' in data:
        ret_track.name = data['name']
    if 'msgs' in data:
        msg_itr = map(data_to_msg,data['msgs'])
        ret_track.extend(msg_itr)
    return ret_track


def data_to_msg(data):
    if data['type'] in MSG_TYPE_TO_SPEC_DICT:
        d = {
            'type': data['type'],
            'time': data['time'],
        }
        spec = MSG_TYPE_TO_SPEC_DICT[data['type']]
        for value_name in spec['value_names']:
            d[value_name] = data[value_name]
        return mido.Message(**d)
    elif data['type'] in MSG_TYPE_TO_METASPEC_DICT:
        d = {
            'type': data['type'],
            'time': data['time'],
        }
        spec = MSG_TYPE_TO_METASPEC_DICT[data['type']]
        for attr in spec.attributes:
            d[attr] = data[attr]
        return mido.MetaMessage(**d)
    else:
        raise Exception(f'Err[HAMHVNFEPA]: Unexpected data_type={data_type}, data={data}')


MSG_TYPE_TO_SPEC_DICT = {}
for spec in mido.messages.specs.SPECS:
    MSG_TYPE_TO_SPEC_DICT[spec['type']] = spec

MSG_TYPE_TO_METASPEC_DICT = mido.midifiles.meta._META_SPEC_BY_TYPE


if __name__ == '__main__':
    main()
