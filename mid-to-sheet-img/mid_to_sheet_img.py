import argparse
import math
import mido
import sys
from collections import deque
from PIL import Image, ImageDraw

PHI = (1+5**0.5)/2 

# midi clock = 24, https://en.wikipedia.org/wiki/MIDI_beat_clock
#MIDI_CLOCK = 24
#TIME_UNIT = MIDI_CLOCK*8

PITCH_C4 = 72
LINE_PITCH_CNT = 4
LINE_PITCH_CNT3 = LINE_PITCH_CNT*3

PX_UNIT = 64
X_OFFSET = math.floor(PX_UNIT/PHI)
Y_OFFSET = math.floor(PX_UNIT/PHI)
BUFFER_Y_OFFSET = PX_UNIT * 2
PX_UNIT_PHII = math.ceil(PX_UNIT/PHI)
PX_UNIT_PHII2 = math.ceil(PX_UNIT/PHI/2)

VLINE_SIZE_LIST = [4,1]
HLINE_SIZE = [4,1]
NOTE_LINE_SIZE = 4+1

parser = argparse.ArgumentParser()
parser.add_argument('input_mid_path')
parser.add_argument('output_img_path')
parser.add_argument('--beat-padding', type=int)
args = parser.parse_args()

mid = mido.MidiFile(args.input_mid_path)
#print(f'ticks_per_beat={mid.ticks_per_beat}')
ticks_per_beat = mid.ticks_per_beat

for ti,track in enumerate(mid.tracks):
    print(f'[track {ti}, {track.name}]')
    for msg in track:
        print(msg)
        #print(msg.type)

cp_to_note_deque = {}
note_list = []
time_signature_list = []
time_signature_list.append({
    'numerator': 4,
    'denominator': 4,
    'start': 0,
})
page_break_list = []
page_break_list.append(0)
line_break_list = []
line_break_list.append(0)
track = mid.tracks[0]
t = 0
for msg in track:
    t += msg.time
    if msg.type == 'time_signature':
        #print(f'numerator={msg.numerator}, denominator={msg.denominator}')
        time_signature_list[-1]['end'] = t
        time_signature_list.append({
            'numerator': msg.numerator,
            'denominator': msg.denominator,
            'start': t,
        })
    elif msg.type == 'cue_marker' and msg.text=='smz-page-break':
        page_break_list.append(t)
        line_break_list.append(t)
    elif msg.type == 'cue_marker' and msg.text=='smz-line-break':
        line_break_list.append(t)
    elif msg.is_meta: pass
    elif msg.type == 'note_on' and msg.velocity > 0:
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
    elif msg.type == 'note_off' or msg.type == 'note_on':
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

time_signature_list[-1]['end'] = t

if args.beat_padding:
    p = args.beat_padding
    pp = lambda i:(i*p+(ticks_per_beat//2))//ticks_per_beat*ticks_per_beat//p
    for note in note_list:
        note['start'] = pp(note['start'])
        note['end']   = pp(note['end'])
    line_break_list = list(map(pp,line_break_list))
    page_break_list = list(map(pp,page_break_list))

for note in note_list:
    print(note)

time_min = note_list
time_min = map(lambda i:i['start'], time_min)
time_min = min(time_min)
#time_min = 0
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

#buffer_sheet_l_pitch = math.ceil((pitch_max+1-PITCH_C4)/LINE_PITCH_CNT)*LINE_PITCH_CNT+PITCH_C4
#print(f'buffer_sheet_l_pitch={buffer_sheet_l_pitch}')
buffer_sheet_l_pitch = pitch_max + 8

#buffer_sheet_r_pitch = math.floor((pitch_min-1-PITCH_C4)/LINE_PITCH_CNT)*LINE_PITCH_CNT+PITCH_C4
#print(f'buffer_sheet_r_pitch={buffer_sheet_r_pitch}')
buffer_sheet_r_pitch = pitch_min - 8

img_w = PX_UNIT * (buffer_sheet_l_pitch-buffer_sheet_r_pitch) // LINE_PITCH_CNT
img_h = PX_UNIT * (time_max-time_min) // ticks_per_beat + BUFFER_Y_OFFSET*2

print(f'img_w={img_w}, img_h={img_h}')

img = Image.new('RGBA', (img_w,img_h), (255,255,255,255) )

draw = ImageDraw.Draw(img)

# draw color bg
y0,y1 = 0,img_h
for pitch in range(buffer_sheet_r_pitch, buffer_sheet_l_pitch+1):
    p12 = ( pitch - PITCH_C4 + 300 ) % (LINE_PITCH_CNT3)
    if p12 % LINE_PITCH_CNT != 0: continue
    x0 = (buffer_sheet_l_pitch-pitch-LINE_PITCH_CNT) * PX_UNIT / LINE_PITCH_CNT
    x1 = (buffer_sheet_l_pitch-pitch) * PX_UNIT / LINE_PITCH_CNT
    color = (255,246,246,255) if p12 == 0 else \
            (246,255,246,255) if p12 == LINE_PITCH_CNT else \
            (246,246,255,255)
    draw.rectangle((x0,y0,x1,y1), fill=color)

# draw note len
C = 0xdd
for note in note_list:
    pitch = note['pitch']
    start = note['start']
    end   = note['end']
    p4 = ( pitch - PITCH_C4 + 300 ) % (LINE_PITCH_CNT)
    x = (buffer_sheet_l_pitch-pitch) * PX_UNIT / LINE_PITCH_CNT
    x0 = x-PX_UNIT//4
    x1 = x+PX_UNIT//4
    y0 = (start-time_min) * PX_UNIT // ticks_per_beat + BUFFER_Y_OFFSET
    y1 = (end-time_min) * PX_UNIT // ticks_per_beat + BUFFER_Y_OFFSET
    draw.rectangle((x0,y0,x1,y1), fill=(C,C,C,255))

# draw white time line
x0,x1=(0,img_w)
for t in range(0,math.ceil((time_max+1)/ticks_per_beat)*ticks_per_beat,ticks_per_beat):
    y = (t-time_min) * PX_UNIT // ticks_per_beat + BUFFER_Y_OFFSET
    draw.line((x0,y,x1,y),fill=(255,255,255,255),width=2)

# draw vertical line
C0 = 128
C1 = 192
for pitch in range(buffer_sheet_r_pitch, buffer_sheet_l_pitch+1):
    p = ( pitch - PITCH_C4 + 300 ) % (LINE_PITCH_CNT3)
    if p % LINE_PITCH_CNT != 0: continue
    x = (buffer_sheet_l_pitch-pitch) * PX_UNIT / LINE_PITCH_CNT
    y0,y1 = 0,img_h
    w = VLINE_SIZE_LIST[0] if p % LINE_PITCH_CNT3 == 0 else VLINE_SIZE_LIST[1]
    c = C0 if p % LINE_PITCH_CNT3 == 0 else C1
    print((x,y0,x,y1))
    draw.line((x,y0,x,y1),fill=(c,c,c,255),width=w)

# draw horizontal line
C = 128
x0,x1 = (0,img_w)
for time_signature in time_signature_list:
    dt = ticks_per_beat*time_signature['numerator']*4//time_signature['denominator']
    for t in range(time_signature['start'],time_signature['end']+1,dt):
        y = (t-time_min) * PX_UNIT // ticks_per_beat + BUFFER_Y_OFFSET
        draw.line((x0,y,x1,y),fill=(C,C,C,255),width=HLINE_SIZE[0])

# draw note
C = (0,0,0,255)
for note in note_list:
    pitch = note['pitch']
    start = note['start']
    p4 = ( pitch - PITCH_C4 + 300 ) % (LINE_PITCH_CNT)
    if p4 == 0:
        x = (buffer_sheet_l_pitch-pitch) * PX_UNIT / LINE_PITCH_CNT
        y = (start-time_min) * PX_UNIT // ticks_per_beat + BUFFER_Y_OFFSET
        p0 = x-PX_UNIT_PHII2,y-PX_UNIT_PHII2
        p1 = x+PX_UNIT_PHII2,y+PX_UNIT_PHII2
        p2 = x-PX_UNIT_PHII2,y+PX_UNIT_PHII2
        p3 = x+PX_UNIT_PHII2,y-PX_UNIT_PHII2
#        draw.line((x-PX_UNIT_PHII2,y-PX_UNIT_PHII2,x+PX_UNIT_PHII2,y+PX_UNIT_PHII2),fill=(0,0,0,255),width=NOTE_LINE_SIZE)
        # width+1 to draw fine, reason unknown
        draw.line(p0+p1,fill=(0,0,0,255),width=NOTE_LINE_SIZE+1)
        draw.line(p2+p3,fill=(0,0,0,255),width=NOTE_LINE_SIZE+1)
        l = NOTE_LINE_SIZE//2
        draw.ellipse((p0[0]-l,p0[1]-l,p0[0]+l,p0[1]+l),fill=C)
        draw.ellipse((p1[0]-l,p1[1]-l,p1[0]+l,p1[1]+l),fill=C)
        draw.ellipse((p2[0]-l,p2[1]-l,p2[0]+l,p2[1]+l),fill=C)
        draw.ellipse((p3[0]-l,p3[1]-l,p3[0]+l,p3[1]+l),fill=C)
    elif p4 == 1:
        x = (buffer_sheet_l_pitch-pitch+1) * PX_UNIT / LINE_PITCH_CNT
        y = (start-time_min) * PX_UNIT // ticks_per_beat + BUFFER_Y_OFFSET
        p0 = (x,y)
        p1 = (x-PX_UNIT_PHII2*2,y-PX_UNIT_PHII2)
        p2 = (x-PX_UNIT_PHII2*2,y+PX_UNIT_PHII2)
        draw.line((p0,p1,p2,p0),fill=(0,0,0,255),width=NOTE_LINE_SIZE)
        l = NOTE_LINE_SIZE//2
        draw.ellipse((p0[0]-l,p0[1]-l,p0[0]+l,p0[1]+l),fill=C)
        draw.ellipse((p1[0]-l,p1[1]-l,p1[0]+l,p1[1]+l),fill=C)
        draw.ellipse((p2[0]-l,p2[1]-l,p2[0]+l,p2[1]+l),fill=C)
    elif p4 == 2:
        x = (buffer_sheet_l_pitch-pitch) * PX_UNIT / LINE_PITCH_CNT
        y = (start-time_min) * PX_UNIT // ticks_per_beat + BUFFER_Y_OFFSET
        draw.ellipse((x-PX_UNIT_PHII2,y-PX_UNIT_PHII2,x+PX_UNIT_PHII2,y+PX_UNIT_PHII2),outline=(0,0,0,255),width=NOTE_LINE_SIZE)
    elif p4 == 3:
        x = (buffer_sheet_l_pitch-pitch-1) * PX_UNIT / LINE_PITCH_CNT
        y = (start-time_min) * PX_UNIT // ticks_per_beat + BUFFER_Y_OFFSET
        p0 = (x,y)
        p1 = (x+PX_UNIT_PHII2*2,y-PX_UNIT_PHII2)
        p2 = (x+PX_UNIT_PHII2*2,y+PX_UNIT_PHII2)
        draw.line((p0,p1,p2,p0),fill=(0,0,0,255),width=NOTE_LINE_SIZE)
        l = NOTE_LINE_SIZE//2
        draw.ellipse((p0[0]-l,p0[1]-l,p0[0]+l,p0[1]+l),fill=C)
        draw.ellipse((p1[0]-l,p1[1]-l,p1[0]+l,p1[1]+l),fill=C)
        draw.ellipse((p2[0]-l,p2[1]-l,p2[0]+l,p2[1]+l),fill=C)

img.save(f'{args.output_img_path}-debug.png')

page_break_list.append(time_max)
page_break_list.append(time_min)
line_break_list.append(time_max)
line_break_list.append(time_min)
page_break_list.sort()
line_break_list.sort()

print(f'line_break_list={line_break_list}')

page_data_list = []
for i in range(len(page_break_list)-1):
    page_data_list.append({
        't0':page_break_list[i],
        't1':page_break_list[i+1],
    })

page_data_list = list(filter(lambda i:i['t0']<i['t1'],page_data_list))

page_id = 0
for page_data in page_data_list:

    print(f'page_id={page_id}')
    print(f'page_data={page_data}')

    line_break_0_list = line_break_list
    line_break_0_list = filter(lambda i:i>=page_data['t0'],line_break_0_list)
    line_break_0_list = filter(lambda i:i<=page_data['t1'],line_break_0_list)
    line_break_0_list = list(line_break_0_list)

    print(f'line_break_0_list={line_break_0_list}')

    clip_rect_list = []
    for i in range(len(line_break_0_list)-1):
        clip_rect_list.append({
            't0':line_break_0_list[i],
            't1':line_break_0_list[i+1],
        })
    
    clip_rect_list = list(filter(lambda i:i['t0']<i['t1'],clip_rect_list))

    print(f'clip_rect_list={clip_rect_list}')
    
    for clip_rect in clip_rect_list:
        pitch_list = note_list
        pitch_list = filter(lambda i:i['end']>clip_rect['t0'],pitch_list)
        pitch_list = filter(lambda i:i['start']<clip_rect['t1'],pitch_list)
        pitch_list = list(pitch_list)
        clip_rect['remain'] = len(pitch_list)
    
    clip_rect_list = list(filter(lambda i:i['remain']>0,clip_rect_list))

    print(f'clip_rect_list={clip_rect_list}')
    
    for clip_rect in clip_rect_list:
        pitch_list = note_list
        pitch_list = filter(lambda i:i['end']>=clip_rect['t0'],pitch_list)
        pitch_list = filter(lambda i:i['start']<=clip_rect['t1'],pitch_list)
        pitch_list = map(lambda i:i['pitch'],pitch_list)
        pitch_list = list(pitch_list)
        clip_rect['p0'] = min(pitch_list)
        clip_rect['p1'] = max(pitch_list)
    
    clip_rect_list = filter(lambda i:'p0'in i,clip_rect_list)
    clip_rect_list = filter(lambda i:'p1'in i,clip_rect_list)
    clip_rect_list = list(clip_rect_list)
    
    print(f'clip_rect_list={clip_rect_list}')

    if len(clip_rect_list) <= 0:
        continue
    
    for clip_rect in clip_rect_list:
        clip_rect['y0'] = (clip_rect['t0']-time_min) * PX_UNIT // ticks_per_beat + BUFFER_Y_OFFSET - Y_OFFSET
        clip_rect['y1'] = (clip_rect['t1']-time_min) * PX_UNIT // ticks_per_beat + BUFFER_Y_OFFSET + Y_OFFSET
        clip_rect['x0'] = (buffer_sheet_l_pitch-clip_rect['p1']) * PX_UNIT // LINE_PITCH_CNT - X_OFFSET
        clip_rect['x1'] = (buffer_sheet_l_pitch-clip_rect['p0']) * PX_UNIT // LINE_PITCH_CNT + X_OFFSET
    
    #for clip_rect in clip_rect_list:
    #    x0,x1 = clip_rect['x0'],clip_rect['x1']
    #    y0,y1 = clip_rect['y0'],clip_rect['y1']
    #    draw.rectangle((x0,y0,x1,y1),outline=(0xff,0,0,255),width=1)
    #    #draw.line((x0,y1,x1,y1),fill=(0xff,0,0,255),width=1)
    
    #img.save(args.output_img_path)
    
    output_h = clip_rect_list
    output_h = map(lambda i:i['y1']-i['y0'], output_h)
    output_h = max(output_h)
    
    output_w = clip_rect_list
    output_w = map(lambda i:i['x1']-i['x0'], output_w)
    output_w = sum(output_w)
    output_w += (len(clip_rect_list)-1)*PX_UNIT_PHII
    
    out_img = Image.new('RGBA', (output_w,output_h), (255,255,255,255) )
    #out_draw = ImageDraw.Draw(out_img)
    
    x = output_w
    for clip_rect in clip_rect_list:
        x0,x1 = clip_rect['x0'],clip_rect['x1']
        y0,y1 = clip_rect['y0'],clip_rect['y1']
        region = img.crop((x0,y0,x1,y1))
        x -= (x1-x0)
        out_img.paste(region,(x,0))
        x -= PX_UNIT_PHII
    
    out_img.save(f'{args.output_img_path}-{page_id}.png')
    
    page_id += 1
