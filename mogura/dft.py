import copy
import cupy as cp
import math
import numpy as np
# import threading
import queue
import traceback

xp = cp

DECREASE_RATE = 0.5

class Dft:

    def __init__(self, runtime):
        self.runtime = runtime
        self.frame_queue = queue.Queue()
        self.session_id = 0
        self.enabled = False
        self.level_np = None

    def start(self, sample_rate, frame_size, freq_list):
        self.level_np = None
        self.sample_rate = sample_rate
        self.frame_size = frame_size
        self.freq_list = copy.deepcopy(freq_list)
        self.session_id += 1
        self.frame_queue = queue.Queue()
        self.enabled = True

        self.runtime.thread_pool.submit(self.consume_frame_queue_main, self.session_id)

    def stop(self):
        self.enabled = False
        self.level_np = None

    def stream_callback(self, in_data, frame_count, time_info, status_flags):
        if not self.enabled: return
        # print(f'in_data len: {len(in_data)}')
        # print(f'frame_count: {frame_count}')
        # print(f'frame_size: {self.frame_size}')
        assert(len(in_data) == 2*frame_count)
        assert(frame_count%self.frame_size == 0)
        if self.enabled:
            for i in range(frame_count//self.frame_size):
                self.frame_queue.put(in_data[i*self.frame_size*2:(i+1)*self.frame_size*2])

    def consume_frame_queue_main(self, session_id):
        try:
            self.prepare_xp()
            freq_cnt = len(self.freq_list)
            accum_xp = xp.zeros((freq_cnt,2,1))
            epsilon_xp = xp.nextafter(0,1)
            while True:
                try:
                    assert(accum_xp.shape==(freq_cnt,2,1))
                    if not (self.enabled and session_id == self.session_id and (not self.runtime.exit_done)): break
                    in_data = self.frame_queue.get(timeout=0.2)
                    if not (self.enabled and session_id == self.session_id and (not self.runtime.exit_done)): break
                    assert(len(in_data) == self.frame_size*2)
                    sample_xp = xp.frombuffer(in_data, dtype=xp.int16)
                    sample_xp = sample_xp.astype(xp.float32)
                    # sample_xp = np_to_xp(sample_xp)
                    sample_xp = sample_xp/32768
                    sample_xp = sample_xp * self.decrease_xp
                    mms_xp = xp.matmul(self.ij_xp, sample_xp)
                    mms_xp = mms_xp/self.frame_size
                    mms_xp = mms_xp.reshape((freq_cnt,2,1))
                    accum_xp = xp.matmul(self.rot_xp, accum_xp)
                    # accum_xp = accum_xp * DECREASE_RATE
                    accum_xp = accum_xp + mms_xp
                    accum_xp = mms_xp
                    level_xp = xp.sqrt(xp.sum(xp.square(accum_xp), axis=(1,2)))
                    level_xp = xp.log(level_xp+epsilon_xp)
                    level_np = xp_to_np(level_xp)
                    # print(level_np)
                    with self.runtime.lock:
                        self.level_np = level_np
                except queue.Empty:
                    pass
        except:
            traceback.print_exc()


    def prepare_xp(self):
        frame_size = self.frame_size
        sample_rate = self.sample_rate
        freq_cnt = len(self.freq_list)
        t_np = np.arange(frame_size).reshape((1,frame_size))
        freq_np = np.array(self.freq_list)
        freq_np = freq_np.reshape((freq_cnt,1))
        rad_np = freq_np * t_np * 2 * math.pi / sample_rate
        rad2_np = rad_np.repeat(2,0)
        rad2_np = rad2_np.reshape((freq_cnt,2,frame_size))
        p0_np = np.array([[0],[math.pi/2]])
        rad2_np = rad2_np + p0_np
        ij_np = np.sin(rad2_np)
        rot_np = np.array(self.freq_list)
        rot_np = rot_np*frame_size*math.pi*2*(1)/sample_rate
        rot_sin_np = np.sin(rot_np)
        rot_cos_np = np.cos(rot_np)
        rot_np = np.array(((rot_cos_np, -rot_sin_np), (rot_sin_np, rot_cos_np)))
        rot_np = rot_np.transpose((2,0,1))
        decrease_np = np.arange(frame_size)
        decrease_np = (frame_size-1)-decrease_np
        decrease_np = decrease_np / frame_size
        decrease_np = np.power(DECREASE_RATE, decrease_np)

        self.ij_xp = np_to_xp(ij_np)
        self.rot_xp = np_to_xp(rot_np)
        self.decrease_xp = np_to_xp(decrease_np)

    def get_level_np(self):
        with self.runtime.lock:
            if self.enabled:
                return self.level_np
            else:
                return None

def xp_to_np(xpp):
    if xp == cp:
        return cp.asnumpy(xpp)
    elif xp == np:
        return xpp
    else:
        raise Exception('Unknown xp')

def np_to_xp(npp):
    if xp == cp:
        return cp.array(npp)
    elif xp == np:
        return npp
    else:
        raise Exception('Unknown xp')
