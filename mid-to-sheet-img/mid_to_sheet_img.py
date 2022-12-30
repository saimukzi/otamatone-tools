import argparse
import math
import mido
import sys
from collections import deque
from PIL import Image, ImageDraw

# midi clock = 24, https://en.wikipedia.org/wiki/MIDI_beat_clock
MIDI_CLOCK = 24
TIME_UNIT = MIDI_CLOCK*8

PITCH_A4 = 69
LINE_PITCH_CNT = 4
LINE_PITCH_CNT3 = LINE_PITCH_CNT*3

PX_UNIT = 32
X_OFFSET = PX_UNIT//8
Y_OFFSET = PX_UNIT*3//8
BUFFER_Y_OFFSET = PX_UNIT * 2
PHI = (1+5**0.5)/2 
PX_UNIT_PHII2 = math.ceil(PX_UNIT/PHI/2)

parser = argparse.ArgumentParser()
parser.add_argument('input_mid_path')
parser.add_argument('output_img_path')
args = parser.parse_args()

mid = mido.MidiFile(args.input_mid_path)

for ti,track in enumerate(mid.tracks):
    print(f'[track {ti}, {track.name}]')
    for msg in track:
        print(msg)
        #print(msg.type)

cp_to_note_deque = {}
note_list = []
for ti,track in enumerate(mid.tracks):
    t = 0
    for msg in track:
        t += msg.time
        if msg.is_meta: continue
        elif msg.type == 'note_on':
            note = {
                'channel': msg.channel,
                'pitch': msg.note,
                'start': t
            }
            cp = (msg.channel, msg.note)
            if cp not in cp_to_note_deque:
                cp_to_note_deque[cp] = deque()
            cp_to_note_deque[cp].append(note)
            note_list.append(note)
        elif msg.type == 'note_off':
            cp = (msg.channel, msg.note)
            if cp not in cp_to_note_deque:
                print(f'err-XRBOLKQWAY: msg={msg}| channel-note not found', file=sys.stderr)
                exit(1)
            note_deque = cp_to_note_deque[cp]
            if len(note_deque) <= 0:
                print(f'err-OULBGQXBDA: msg={msg}| channel-note queue size zero', file=sys.stderr)
                exit(1)
            note = note_deque.popleft()
            note['end'] = t
        else:
            print(f'err-RVIXOVZSVX: msg={msg}| unhandled note found', file=sys.stderr)

for note in note_list:
    print(note)

time_min = note_list
time_min = map(lambda i:i['start'], time_min)
time_min = min(time_min)
print(f'time_min={time_min}')

time_max = note_list
time_max = map(lambda i:i['end'], time_max)
time_max = max(time_max)
print(f'time_max={time_max}')

pitch_min = note_list
pitch_min = map(lambda i:i['pitch'], pitch_min)
pitch_min = min(pitch_min)
print(f'pitch_min={pitch_min}')

pitch_max = note_list
pitch_max = map(lambda i:i['pitch'], pitch_max)
pitch_max = max(pitch_max)
print(f'pitch_max={pitch_max}')

#buffer_sheet_l_pitch = math.ceil((pitch_max+1-PITCH_A4)/LINE_PITCH_CNT)*LINE_PITCH_CNT+PITCH_A4
#print(f'buffer_sheet_l_pitch={buffer_sheet_l_pitch}')
buffer_sheet_l_pitch = pitch_max + 4

#buffer_sheet_r_pitch = math.floor((pitch_min-1-PITCH_A4)/LINE_PITCH_CNT)*LINE_PITCH_CNT+PITCH_A4
#print(f'buffer_sheet_r_pitch={buffer_sheet_r_pitch}')
buffer_sheet_r_pitch = pitch_min - 8

img_w = PX_UNIT * (buffer_sheet_l_pitch-buffer_sheet_r_pitch) // LINE_PITCH_CNT
img_h = PX_UNIT * (time_max-time_min) // TIME_UNIT + BUFFER_Y_OFFSET*2

print(f'img_w={img_w}, img_h={img_h}')

img = Image.new('RGBA', (img_w,img_h), (255,255,255,255) )

draw = ImageDraw.Draw(img)

# draw color bg
y0,y1 = 0,img_h
for pitch in range(buffer_sheet_r_pitch, buffer_sheet_l_pitch+1):
    p12 = ( pitch - PITCH_A4 + 300 ) % (LINE_PITCH_CNT3)
    if p12 % LINE_PITCH_CNT != 0: continue
    x0 = (buffer_sheet_l_pitch-pitch-LINE_PITCH_CNT) * PX_UNIT / LINE_PITCH_CNT
    x1 = (buffer_sheet_l_pitch-pitch) * PX_UNIT / LINE_PITCH_CNT
    color = (255,246,246,255) if p12 == 0 else \
            (246,255,246,255) if p12 == LINE_PITCH_CNT else \
            (246,246,255,255)
    draw.rectangle((x0,y0,x1,y1), fill=color)

# draw vertical line
for pitch in range(buffer_sheet_r_pitch, buffer_sheet_l_pitch+1):
    p = ( pitch - PITCH_A4 + 300 ) % (LINE_PITCH_CNT3)
    if p % LINE_PITCH_CNT != 0: continue
    x = (buffer_sheet_l_pitch-pitch) * PX_UNIT / LINE_PITCH_CNT
    y0,y1 = 0,img_h
    w = 2 if p % LINE_PITCH_CNT3 == 0 else 1
    print((x,y0,x,y1))
    draw.line((x,y0,x,y1),fill=(0,0,0,255),width=w)

# draw note
for note in note_list:
    pitch = note['pitch']
    start = note['start']
    p4 = ( pitch - PITCH_A4 + 300 ) % (LINE_PITCH_CNT)
    if p4 == 0:
        x = (buffer_sheet_l_pitch-pitch) * PX_UNIT / LINE_PITCH_CNT
        y = (start-time_min) * PX_UNIT // TIME_UNIT + BUFFER_Y_OFFSET
        draw.line((x-PX_UNIT_PHII2,y-PX_UNIT_PHII2,x+PX_UNIT_PHII2,y+PX_UNIT_PHII2),fill=(0,0,0,255),width=1)
        draw.line((x-PX_UNIT_PHII2,y+PX_UNIT_PHII2,x+PX_UNIT_PHII2,y-PX_UNIT_PHII2),fill=(0,0,0,255),width=1)
    elif p4 == 1:
        x = (buffer_sheet_l_pitch-pitch+1) * PX_UNIT / LINE_PITCH_CNT
        y = (start-time_min) * PX_UNIT // TIME_UNIT + BUFFER_Y_OFFSET
        p0 = (x,y)
        p1 = (x-PX_UNIT_PHII2*2,y-PX_UNIT_PHII2)
        p2 = (x-PX_UNIT_PHII2*2,y+PX_UNIT_PHII2)
        draw.line((p0,p1,p2,p0),fill=(0,0,0,255),width=1)
    elif p4 == 2:
        x = (buffer_sheet_l_pitch-pitch) * PX_UNIT / LINE_PITCH_CNT
        y = (start-time_min) * PX_UNIT // TIME_UNIT + BUFFER_Y_OFFSET
        draw.ellipse((x-PX_UNIT_PHII2,y-PX_UNIT_PHII2,x+PX_UNIT_PHII2,y+PX_UNIT_PHII2),outline=(0,0,0,255),width=1)
    elif p4 == 3:
        x = (buffer_sheet_l_pitch-pitch-1) * PX_UNIT / LINE_PITCH_CNT
        y = (start-time_min) * PX_UNIT // TIME_UNIT + BUFFER_Y_OFFSET
        p0 = (x,y)
        p1 = (x+PX_UNIT_PHII2*2,y-PX_UNIT_PHII2)
        p2 = (x+PX_UNIT_PHII2*2,y+PX_UNIT_PHII2)
        draw.line((p0,p1,p2,p0),fill=(0,0,0,255),width=1)

img.save(args.output_img_path)

