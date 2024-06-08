FONT_PATH = 'C:\Windows\Fonts\msjh.ttc'
FONT_SIZE = 32
DFT_PITCH_SAMPLE_COUNT = 8

C4_PITCH = 60

DIATONIC_SCALE_LIST = [0, 2, 4, 5, 7, 9, 11]

DIATONIC_PITCH_LIST = []
for i in range(11):
    DIATONIC_PITCH_LIST += list(map(lambda x: x+i*12, DIATONIC_SCALE_LIST))
DIATONIC_PITCH_LIST = filter(lambda x: x>=0 and x<128, DIATONIC_PITCH_LIST)
DIATONIC_PITCH_LIST = sorted(DIATONIC_PITCH_LIST)

C4_INDEX = DIATONIC_PITCH_LIST.index(C4_PITCH)

STAFF_LINE_PITCH_LIST = range(C4_INDEX%2, len(DIATONIC_PITCH_LIST), 2)
STAFF_LINE_PITCH_LIST = map(lambda i: DIATONIC_PITCH_LIST[i], STAFF_LINE_PITCH_LIST)
STAFF_LINE_PITCH_LIST = list(STAFF_LINE_PITCH_LIST)
