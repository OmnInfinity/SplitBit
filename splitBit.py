import os
import time
import pickle
from concurrent import futures

import numpy as np

import nanovnacmd as nv

from tkinter import *
from tkinter import ttk



DC = 1 # 0 [Hz]
SWEEP = 10

vna = nv.connect()
freq = np.linspace(125e3, 135e3, SWEEP + DC)
vna.datapoints = SWEEP
vna.setSweep(freq[1], freq[-1])

if (not (os.path.isfile("db.pkl"))):
    db = open("db.pkl", "ab")
    calibration = nv.calibrate1port(vna)
    pickle.dump(calibration, db)
else:
    db = open("db.pkl", "rb")
    calibration = pickle.load(db)
db.close()



class Stopwatch():
    NEAR = True
    FAR = False

    CLOSER = -1
    FURTHER = 1

    INITIAL_WIDTH = 480
    INITIAL_HEIGHT = 240
    
    def __init__(self, freq):
        self.freq = freq # Target RFID for future resonant frequency biasing

        self.root = Tk()
        self.root.title(f"SplitBit @ {freq} [Hz]") # [Idea] "[Hz]" to "[kHz]"
        self.root.config(bg = "black")

        self.width = self.INITIAL_WIDTH
        self.height = self.INITIAL_HEIGHT

        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()

        self.x = (self.screen_width / 2) - (self.width / 2)
        self.y = (self.screen_height / 2) - (self.height / 2)

        self.root.geometry("%dx%d+%d+%d" % (self.width, self.height, self.x, self.y))

        self.msec = 0
        self.sec = 0
        self.min = 0
        
        self.total_msec = 0
        self.total_sec = 0
        self.total_min = 0
        
        self.laps = 1

        self.start_time = time.time()
        self.current_time = time.time()

        self.process = None
        self.buffer = []

        self.rolling_avg = [0 for _ in range(5)]
        self.is_lpf_calibration_done = False
        self.location = self.FAR
        self.direction = self.CLOSER
        self.initial = True
        self.counts = 0

        # self.style = ttk.Style()

        """ Containers/Layout """
        self.top = Frame(self.root, width = 400, bg = "black")
        self.top.pack(side = TOP, padx = 5, pady = 5)

        self.center = Frame(self.root, width = 400, bg = "black")
        self.center.pack(padx = 5, pady = 5)
        self.center.place(relx = 0.5, rely = 0.5, anchor = CENTER)

        self.bottom = Frame(self.root, width = 500, bg = "black")
        self.bottom.pack(side = BOTTOM, padx = 5, pady = 5)

        """ Inputs """
        self.start_button = Button(self.bottom, text = "START", font = ("arial 16 bold"), fg = "gray", bg = "black", width = 6, \
                command = self.start
        )
        self.start_button.pack(side = LEFT, padx = 5, pady = 5)

        self.stop_button = Button(self.bottom, text = "STOP", font = ("arial 16 bold"), fg = "gray", bg = "black", width = 6, \
                command = self.pause
        )
        self.stop_button.pack(side = LEFT, padx = 5, pady = 5)

        self.reset_button = Button(self.bottom, text = "RESET", font = ("arial 16 bold"), fg = "gray", bg = "black", width = 6, \
                command = self.reset
        )
        self.reset_button.pack(side = LEFT, padx = 5, pady = 5)

        self.lap_button = Button(self.bottom, text = "LAP", font = ("arial 16 bold"), fg = "gray", bg = "black", width = 6, \
                command = self.lap
        )
        self.lap_button.pack(side = LEFT, padx = 5, pady = 5)

        """ Outputs """
        self.title = Label(self.top, text = "SplitBit Lapper", font = ("arial 24 bold"), fg = "white", bg = "black")
        self.title.pack(fill = X)

        self.laps_history = Label(self.center, font = ("arial", 12), fg = "gray", bg = "black")
        self.laps_history.pack(fill = X)
        self.laps_history.config(text = f"")

        self.lapper = Label(self.center, font = ("arial", 18), fg = "white", bg = "black")
        self.lapper.pack(fill = X)
        self.lapper.config(text = f"Lap {self.laps:02}")

        self.timer = Label(self.center, font = ("arial", 36), fg = "white", bg = "black")
        self.timer.pack(fill = X)
        self.timer.config(text = f"{self.min:02}:{self.sec:02}:{self.msec:03}")

    def lap(self):
        self.height += 12 + 2 * 4

        self.x = (self.screen_width / 2) - (self.width / 2)
        self.y = (self.screen_height / 2) - (self.height / 2)

        if len(self.buffer) > 0:
            self.buffer.pop()
        self.buffer.append(f"Lap {self.laps:02}: {self.min:02}:{self.sec:02}:{self.msec:03}")

        self.total_msec += self.msec
        self.total_sec += self.sec
        self.total_min += self.min

        self.buffer.append(f"Total: {self.total_min:02}:{self.total_sec:02}:{self.total_msec:03}")
        self.laps_history.config(text = "\n".join(self.buffer))
        self.laps += 1

        self.zero()
        self.tick()

        self.lapper.config(text = f"Lap {self.laps:02}")

        self.root.geometry("%dx%d+%d+%d" % (self.width, self.height, self.x, self.y))

    def tick(self):
        # self.msec += 1
        self.msec += int((self.current_time - self.start_time) * 1000)
        
        self.start_time = self.current_time
        self.current_time = time.time()

        if (self.msec >= 1000):
            self.msec = self.msec % 1000
            self.sec += 1
        if (self.sec >= 60):
            self.sec = 0
            self.min += 1

        self.timer.config(text = f"{self.min:02}:{self.sec:02}:{self.msec:03}")

        self.process = self.timer.after(1, self.tick)

    def start(self):
        self.start_time = time.time() # Continue from now instead of preserving a "ghost timer"
        self.tick()

    def pause(self):
        self.timer.after_cancel(self.process)

    def zero(self):
        self.start_time = time.time()

        self.msec = 0
        self.sec = 0
        self.min = 0

        self.timer.config(text = f"{self.min:02}:{self.sec:02}:{self.msec:03}")

        if (self.process is not None):
            self.timer.after_cancel(self.process)

    def reset(self):
        self.zero()

        self.buffer = []
        self.laps_history.config(text = "\n".join(self.buffer))
        
        self.laps = 1
        self.lapper.config(text = f"Lap {self.laps:02}")
        
        self.width = self.INITIAL_WIDTH
        self.height = self.INITIAL_HEIGHT
        self.root.geometry("%dx%d+%d+%d" % (self.width, self.height, self.x, self.y))

    def exit(self):
        self.root.destroy()

    def sweep(self):
        while (True):
            (f, s11, s21) = nv.measure(vna, calibration)
            self.rolling_avg.pop(0)
            val = np.absolute(np.average(s11)) # LPF
            self.rolling_avg.append(val)

            deriv = (val - np.average(self.rolling_avg)) / 0.001
            
            if (abs(deriv) > 1 and self.is_lpf_calibration_done and self.initial):
                self.direction = self.CLOSER if deriv >= 0 else self.FURTHER
                self.initial = False

                self.location = self.NEAR if self.direction == self.FURTHER else self.FAR

                self.start_time = time.time()

                self.tick()

                self.counts += 1

            elif ((deriv / self.direction > 1) and (self.is_lpf_calibration_done)):
                self.location = not self.location
                self.direction = -self.direction

                if (self.counts % 2 == 0):
                    self.lap()

                self.counts += 1

            if ((not(any(avg == 0 for avg in self.rolling_avg))) and (not self.is_lpf_calibration_done)):
                print("[Calibration] Complete")
                self.is_lpf_calibration_done = True

print("[Calibration] Start")
app = Stopwatch(130e3)
thread_pool_executor = futures.ThreadPoolExecutor(max_workers = 1)
thread_pool_executor.submit(app.sweep) # [Todo] Kill threads on clean-up?
app.root.mainloop()

