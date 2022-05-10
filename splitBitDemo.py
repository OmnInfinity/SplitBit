import os
import time
import pickle

import numpy as np

import nanovnacmd as nv



from concurrent import futures




def readValues(self, value): # -> List[str]:
    # logger.debug("VNA reading %s", value)
    result = list(self.exec_command(value, 0.0))
            # logger.debug("VNA done reading %s (%d values)",
            # value, len(result))
    print("REPLACE")
    return result




DC = 1 # 0 [Hz]

vna = nv.connect()
freq = np.linspace(130e3, 135e3, 5 + DC)
# vna.datapoints = 11
vna.datapoints = 5
vna.setSweep(freq[1], freq[-1])
# vna.datapoints = 5 + DC

# vna.timeout = 0.005 # time sleep now biggest?
# 0.05 rn??
# vna.__class__.__mro__[1].readValues = readValues # for freq Val for vna.measure

if (not (os.path.isfile("db.pkl"))):
    db = open("db.pkl", "ab")
    calibration = nv.calibrate1port(vna)
    pickle.dump(calibration, db)
else:
    db = open("db.pkl", "rb")
    calibration = pickle.load(db)
db.close()





from tkinter import *
import time

root = Tk()
root.title("SplitBit")
root.config(bg = "black")

width = 500 # 400
height = 240 # 200

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

width = screen_width
height = screen_height

x = (screen_width / 2) - (width / 2)
y = (screen_height / 2) - (height / 2)

root.geometry("%dx%d+%d+%d" % (width, height, x, y))

millisec = 000
sec = 00
min = 00
lapa = 1 # 01
start = time.time()
current = time.time()
process = None
buffer = [] # ""
# total = 000
totalMs = 0
totalSec = 0
totalMin = 0

def lap():
    global width, height, lapa, buffer
    global process, timer, millisec, sec, min
    
    global totalMs, totalSec, totalMin

    height += 12 + 2 * 4 # 5?

    x = (screen_width / 2) - (width / 2)
    y = (screen_height / 2) - (height / 2) # anchor?

    if len(buffer) > 0:
        buffer.pop() # -1
    # buffer += f"Lap {lapa:02}: {min:02}:{sec:02}:{millisec:03}\n"
    buffer.append(f"Lap {lapa:02}: {min:02}:{sec:02}:{millisec:03}")

    totalMs += millisec # sep? # first
    totalSec += sec
    totalMin += min

    buffer.append(f"Total: {totalMin:02}:{totalSec:02}:{totalMs:03}")
    # laps.config(text = buffer)
    laps.config(text = "\n".join(buffer))
    lapa += 1

    reset()
    tick()

    lapper.config(text = f"Lap {lapa:02}")

    root.geometry("%dx%d+%d+%d" % (width, height, x, y))

def tick():
    global process, timer, millisec, sec, min, current, start

    # millisec += 1
    millisec += int((current - start) * 1000)
    # millisec  # 03?
    # millisecond
    
    start = current
    current = time.time()

    if millisec >= 1000: # mod
        # print(sec, millisec)
        # millisec = 0
        millisec = millisec % 1000
        sec += 1
    if sec >= 60:
        sec = 0
        min += 1

    timer.config(text = f"{min:02}:{sec:02}:{millisec:03}")

    process = timer.after(1, tick)

def pause():
    global process, timer

    timer.after_cancel(process)

def reset():
    global process, timer, millisec, sec, min, start

    start = time.time()

    millisec = 00
    sec = 00
    min = 00

    timer.config(text = f"{min:02}:{sec:02}:{millisec:03}")

    if process: # missing id otherwise
        timer.after_cancel(process)

def exit():
    root.destroy()

from tkinter import ttk
style = ttk.Style()
# style.configure("TButton", padding=0, background="#ffffff", borderwidth=0)

Top = Frame(root, width=400, bg="black")
Top.pack(side=TOP, padx = 5, pady = 5)


Center = Frame(root, width=400, bg="black")
Center.pack(padx = 5, pady = 5)
Center.place(relx = 0.5, rely = 0.5, anchor = CENTER) # ack(side=CENTER, padx = 5, pady = 5)

Bottom = Frame(root, width=500, bg="black")
Bottom.pack(side = BOTTOM, padx = 5, pady = 5)


Title = Label(Top, text="SplitBit Lapper", font=("arial 24 bold"),
              fg="white", bg="black")
Title.pack(fill=X)



laps = Label(Top, font = ("arial", 12), fg = "gray",
              bg = "black")
laps.pack(fill=X)
laps.config(text = f"")

lapper = Label(Center, font = ("arial", 72), fg = "white",
              bg = "black")
lapper.pack(fill=X)
lapper.config(text = f"Lap {lapa:02}")

timer = Label(Center, font=("arial", 144), fg="white",
              bg="black")
timer.pack(fill=X) # , expand=NO, pady=0)
timer.config(text = f"{min:02}:{sec:02}:{millisec:03}")


def start():
    global start
    start = time.time() # continue instead of ghost timer
    tick()
Startt = Button(Bottom, text='START', font=("arial 16 bold"),
        fg="gray", bg = "black", width=0, command=start)
Startt.pack(side=LEFT,padx=5, pady=5)
Stopp = Button(Bottom, text='STOP', font=("arial 16 bold"),
               fg="gray", bg = "black", width=6, command=pause)
Stopp.pack(side=LEFT,padx=5, pady=5)
Resett = Button(Bottom, text='RESET', font=("arial 16 bold"),
                fg="gray", bg = "black", width=6, command=reset)
Resett.pack(side=LEFT,padx=5, pady=5)
# Exitt = Button(Bottom, text='CLOSE', font=("arial 16 bold"),
#                fg="gray", bg = "black", width = 6, command=exit)
# Exitt.pack(side=LEFT,padx=5, pady=5)

Lap = Button(Bottom, text='LAP', font=("arial 16 bold"),
               fg="gray", bg = "black", width = 6, command=lap)
Lap.pack(side=LEFT,padx=5, pady=5)





# Not async but fine
rolling_avg = [0 for _ in range(5)] # nv.measure(vna, calibration) # 10

"""
Full = Frame(root, width=width, height = height, bg="black")
Full.pack(side=TOP, padx = 0, pady = 0)
Full.place(x = 0, y = 0)
loading = Label(Full, font = ("arial", 12), fg = "gray", # center
              bg = "black")
loading.pack(fill=X)
loading.config(text = f"Loading...") # laps
"""


done = False
toggle = False
direction = -1 # positive = away

initial = True
counts = 0

def sweep():
    global done, toggle, rolling_avg, direction, initial, counts, start # forgot start

    while True:
        (f, s11, s21) = nv.measure(vna, calibration) # slow
        rolling_avg.pop(0)
        val = np.absolute(np.average(s11)) # lpf
        rolling_avg.append(val)
        # print(rolling_avg, val) # np.avg alone
        # print((val - np.average(rolling_avg)) / 0.001) # d/dt

        deriv = (val - np.average(rolling_avg)) / 0.001 # d/dt
        # print(s11) # slow

        # print(deriv)

        # if (deriv > 0.004 and done): # lin interp?
        if (abs(deriv) > 1 and done and initial):
            direction = -1 if deriv >= 0 else 1 # val?
            # print("START", direction)
            initial = False

            toggle = True if direction == 1 else False # True down if dip
            # direction = -direction # forgot

            start = time.time()

            tick()
            # print(toggle)


            counts +=1


        elif (deriv / direction > 1 and done): # lin interp? # reset 0 first?, pemdas # -deriv?
            # print("LAP!")
            toggle = not toggle
            direction = -direction # forgot

            if counts % 2 == 0:
            # if counts % 2 == 1: # off to on
                lap()

            counts += 1

            # print(toggle) # on true ==> lap?

            # rolling_avg = [deriv for _ in range(10)] # prevent spam, unless edge triggers debounce?
            # rolling_avg = [val for _ in range(10)] # prevent spam, unless edge triggers debounce?
            # use avg of avgs?

        if (not(any(avg == 0 for avg in rolling_avg)) and not done):
            print("[Calibration] Complete")
            # Full.pack_forget()
            # Full.destroy() # reuse? otherwise, or just hide
            done = True # rebind

            # initial = True

        # if toggle == True: # down
            # abs or rel

        # root.after(1, sweep)
        # root.after(1, lambda: thread_pool_executor.submit(sweep)) # max speed?

        # avg then find peak interpolate?

# faster on hardware?

# def load():

print("[Calibration] Start")
# sweep()
thread_pool_executor = futures.ThreadPoolExecutor(max_workers=1)
thread_pool_executor.submit(sweep) # kill?
root.mainloop()

