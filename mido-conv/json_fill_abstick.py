import argparse
import json

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('input_json_path')
    parser.add_argument('output_json_path')
    args = parser.parse_args()

    with open(args.input_json_path) as fin:
        mid_data = json.load(fin)
    for track in mid_data['tracks']:
        tick = 0
        for msg in track['msgs']:
            tick += msg['time']
            msg['abstick'] = tick
    with open(args.output_json_path, mode='w') as fout:
        json.dump(mid_data, fout, sort_keys=True, indent=2)
        fout.write('\n')

if __name__ == '__main__':
    main()
