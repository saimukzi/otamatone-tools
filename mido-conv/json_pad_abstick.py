import argparse
import json

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('input_json_path')
    parser.add_argument('output_json_path')
    parser.add_argument('tick', type=int)
    args = parser.parse_args()

    half_tick = args.tick // 2

    with open(args.input_json_path) as fin:
        mid_data = json.load(fin)
    for track in mid_data['tracks']:
        for msg in track['msgs']:
            t = msg['abstick']
            if is_off(msg): t += 1
            t += half_tick
            t //= args.tick
            t *= args.tick
            if is_off(msg): t -= 1
            msg['abstick'] = t
        track['msgs']=sorted(track['msgs'],key=lambda i:i['abstick'])
    with open(args.output_json_path, mode='w') as fout:
        json.dump(mid_data, fout, sort_keys=True, indent=2)
        fout.write('\n')

def is_off(msg):
    if msg['type']=='note_off': return True
    if msg['type']!='note_on': return False
    return msg['velocity'] == 0

if __name__ == '__main__':
    main()
