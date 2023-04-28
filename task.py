# Simple triggerbox + psychopy test.
# Sends x01 (S  1) on a triangle and
# x02 (S  2) on square.
#
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# !!! MAKE SURE refresh_rate IS SET TO YOUR MONITOR'S REFRESH RATE !!!
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#
# Created........: 28Apr2023 [ollie-d]
# Last Modified..: 28Apr2023 [ollie-d]

from math import atan2, degrees
import psychopy.visual
import psychopy.event
import time
import numpy as np
import random
import serial
import threading

# Global variables
port = None
port_thread = None
connected = True
COM_PORT = 'COM4'
win = None # Global variable for window (Initialized in main)
mrkstream = None # Global variable for LSL marker stream (Initialized in main)
photosensor = None # Global variable for photosensor (Initialized in main)
triangle = None # Global variable for stimulus (Initialized in main)
fixation = None # Global variable for fixation cross (Initialized in main)
bg_color = [-1, -1, -1]
win_w = 1920
win_h = 1080
refresh_rate = 60. # Monitor refresh rate (CRITICAL FOR TIMING)


#========================================================
# High Level Functions
#========================================================
def Paradigm(n):
    for i in range(n):
        # 250ms Black screen
        for frame in range(MsToFrames(250, refresh_rate)):
            win.flip()
            
        # 500ms Shape (triangle or square)
        num_edges = random.randint(3, 4)
        marker = 0x01
        if num_edges == 4:
            marker = 0x02
            
        shape = psychopy.visual.polygon.Polygon(win, edges=num_edges, lineColor=[1, 1, 1], fillColor=[1, 1, 1]) 
        for frame in range(MsToFrames(500, refresh_rate)):
            Send_Marker(marker, frame)
            shape.draw()
            win.flip()

#========================================================
# Low Level Functions
#========================================================
def ReadThread(port):
    while connected:
        if port.inWaiting() > 0:
            print ("0x%X"%ord(port.read(1)))

def Send_Marker(marker, frame):
    ''' This function is trying to be "smart" with sending markers.
        We want to avoid using a thread for timing the pulse width,
        but we still want accurate delay times without blocking our
        stimulus timings.
    '''
    if frame == 0:
        port.write([marker])
    elif frame == 1:
        port.write([0x00])

def MsToFrames(ms, fs):
    dt = 1000 / fs;
    return np.round(ms / dt).astype(int);

if __name__ == "__main__":
    # Initialize port
    port = serial.Serial(COM_PORT)
    port.write([0x00])
    time.sleep(0.01)
    
    # Start read thread of port (unsure how critical this is)
    port_thread = threading.Thread(target=ReadThread, args=(thread_port,))
    port_thread.start()

    # Create PsychoPy window
    win = psychopy.visual.Window(
        screen = 0,
        size=[win_w, win_h],
        units="pix",
        fullscr=True,
        color=bg_color,
        gammaErrorPolicy = "ignore"
    );
    random.seed()
    time.sleep(5)

    # Run through paradigm n times
    Paradigm(n=10)
    
    # Close port and kill thread
    port.write([0xFF])
    time.sleep(0.01)
    connected = False
    thread.join(1.0)
    port.close()
    