import time

class TimerPool:

    def __init__(self):
        self.running = None
        self.timer_list = []

    def add_timer(self, timer):
        self.timer_list.append(timer)

    def run(self):
        self.running = True

        while self.running:
            now_sec = time.time()

            active_timer_sec_idx_timer_list = []
            for i,timer in enumerate(self.timer_list):
                next_sec = timer.next_sec()
                if next_sec is None: continue
                if next_sec > now_sec: continue
                active_timer_sec_idx_timer_list.append((next_sec,i,timer))
            active_timer_sec_idx_timer_list.sort()

            for _,_,timer in active_timer_sec_idx_timer_list:
                timer.run(now_sec)
                timer.update_next_sec(now_sec)

            next_sec = self.timer_list
            next_sec = map(lambda i:i.next_sec(),next_sec)
            next_sec = filter(lambda i:i!=None,next_sec)
            next_sec = min(next_sec)

            now_sec = time.time()
            time.sleep(max(next_sec-now_sec,0))

    def stop(self):
        self.running = False
