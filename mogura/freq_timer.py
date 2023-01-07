import time

class FreqTimer:

    def __init__(self, runtime, start, freq, func):
        self.runtime = runtime
        self.start    = start
        self.freq     = freq
        self.func     = func
        self.tick_cnt = 1

    def next_sec(self):
        return self.start + self.tick_cnt / self.freq

    def update_next_sec(self, sec):
        next_tick_cnt = sec
        next_tick_cnt += 0.01 / self.freq
        next_tick_cnt -= self.start
        next_tick_cnt *= self.freq
        next_tick_cnt += 1
        self.tick_cnt = next_tick_cnt

    def run(self, sec):
        self.func(sec)
