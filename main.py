"""
Project started on 19th of January 2023
"""

import math
import wave

import kivymd.uix.button
import numpy as np
from kivy.clock import mainthread
from kivy.config import Config

import pyttsx3

engine = pyttsx3.init()
voices = engine.getProperty('voices')

MALE = 0
FEMALE = 1

engine.setProperty('voice', FEMALE)

Config.set('graphics', 'width', '800')
Config.set('graphics', 'height', '600')

from kivy.graphics import Ellipse, Color
from kivy.lang.builder import Builder
from kivymd.app import MDApp
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.toast import toast
from kivy.properties import NumericProperty

from threading import Thread
import speech_recognition
import pyaudio

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100

p = pyaudio.PyAudio()

sr = speech_recognition.Recognizer()


class AIFx(MDGridLayout):
    IS_MIC_ACTIVE = False

    def __init__(self, *args, **kwargs):
        super(AIFx, self).__init__(*args, **kwargs)

        self.apply_property(scale=NumericProperty(1.2))
        self.size = 300, 300

        with self.canvas.after:
            # Color
            self.oc = Color(99 / 255, 233 / 255, 203 / 255, 0.7)
            self.background_el = Ellipse(pos=self.pos)
            self.ic = Color(29 / 255, 120 / 255, 115 / 255, 0.9)
            self.foreground_el = Ellipse(pos=self.pos)

        self.bind(pos=self.config_out_circle)
        self.bind(pos=self.config_in_circle)
        self.bind(scale=self.config_in_circle)
        # To update the vertex instructions based on voice (which affects scale)
        # refer to self.record for details

    def config_in_circle(self, *args):
        """
        Positions the Circles appropriately by calculating the distance between their centers and offsetting their pos
        by the distance
        Author: Kushal Sai
        :param args:
        :return:
        """
        self.foreground_el.size = (self.size[0] / self.scale, self.size[1] / self.scale)
        dist_x = abs((self.foreground_el.size[0] - self.size[0]) / 2)
        dist_y = abs((self.foreground_el.size[1] - self.size[1]) / 2)
        self.foreground_el.pos = (self.pos[0] + dist_x, self.pos[1] + dist_y)

    def config_out_circle(self, *args):
        self.background_el.size = self.size
        self.background_el.pos = self.pos

    def talk(self, btn: kivymd.uix.button.MDRaisedButton):
        if self.IS_MIC_ACTIVE:
            btn.text = "Say Something!"
            btn.md_bg_color = "#219ebc"
            self.IS_MIC_ACTIVE = False
        else:
            t1 = Thread(target=self.record)
            btn.text = "Listening"
            btn.md_bg_color = "red"
            self.IS_MIC_ACTIVE = True
            t1.start()

    def record(self):
        """
        Opens an audio stream using Mic as Input.
        This function doesn't run in the main thread, so you must be careful when working with main thread resources
        This function is also responsible for Updating the diameter of the cool circle you see xD
        Author: Kushal Sai
        :return:
        """
        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)
        d = b""
        while self.IS_MIC_ACTIVE:
            data = stream.read(CHUNK)

            d += data
            data = np.frombuffer(data, dtype="int16")
            # print(len(data))
            rms = math.sqrt(abs(pow(data, 2).sum() / len(data)))
            norm_rms = (rms / 100) + 2  # offsetting normalized rms by 2 for visual reasons
            # print(rms, norm_rms)
            self.updater(norm_rms)

        stream.stop_stream()
        stream.close()
        self.reset_cirle()

        text = sr.recognize_sphinx(speech_recognition.AudioData(d, RATE, 4))
        self.change_voice_line(text)
        engine.say(text)
        engine.runAndWait()  # Fortunately this code was ran in a different thread so it doesn't freeze the whole prog

        del d

        # d is a huge object, better to free it as soon as possible since i might add a command after this
        # for doing some work

        """
        debug for myself - AUDIO TEST
        wf = wave.open("test.wav", 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(d)
        wf.close()
        """

        print("Exitting Thread")

    @mainthread
    def updater(self, norm_rms):  # Since Kivy requires you to update graphics Context in its main thread we need this
        self.scale = norm_rms  # Decorator

    @mainthread
    def change_voice_line(self, text):
        self.voice_line.text = text

    @mainthread
    def reset_cirle(self):
        self.scale = 1.2


class RootWidget(MDScreenManager):
    def set_voice(self, gender: MALE | FEMALE):
        print(f"Voice changed to: {gender}")
        toast(f"Voice set to {'MALE' if not gender else 'FEMALE'}")
        engine.setProperty('voice', voices[gender].id)


class PersonaAI(MDApp):
    def build(self):
        return RootWidget()

    def on_stop(self):
        p.terminate()
        super(PersonaAI, self).on_stop()


if __name__ == '__main__':
    Builder.load_file("core.kv")
    myapp = PersonaAI()
    myapp.run()
