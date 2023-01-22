import math
import wave

import kivymd.uix.button
import numpy as np
from kivy.config import Config


Config.set('graphics', 'width', '800')
Config.set('graphics', 'height', '600')


from kivy.graphics import Ellipse, Color
from kivy.lang.builder import Builder
from kivymd.app import MDApp
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.screenmanager import MDScreenManager
from kivy.core.window import Window
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

        self.scale = 1.2
        self.size = 300, 300

        with self.canvas.after:
            # Color
            Color(60/255, 63/255, 65/255, 0.7)
            self.background_el = Ellipse(pos=self.pos)
            Color(60/255, 63/255, 65/255, 0.9)
            self.foreground_el = Ellipse(pos=self.pos)

        self.bind(pos=self.config_out_circle)

        self.bind(pos=self.config_in_circle)

    def config_in_circle(self, x, y):
        self.foreground_el.size = (self.size[0]/self.scale, self.size[1]/self.scale)
        dist_x = abs((self.foreground_el.size[0] - self.size[0])/2)
        dist_y = abs((self.foreground_el.size[1] - self.size[1]) / 2)
        self.foreground_el.pos = (self.pos[0] + dist_x, self.pos[1] + dist_y)

    def config_out_circle(self, x, y):
        self.background_el.size = self.size
        self.background_el.pos = self.pos

    def talk(self, btn: kivymd.uix.button.MDRaisedButton):
        if self.IS_MIC_ACTIVE:
            btn.text = "Say Something!"
            btn.md_bg_color = "indigo"
            self.IS_MIC_ACTIVE = False
        else:
            t1 = Thread(target=self.record)
            btn.text = "Listening"
            btn.md_bg_color = "red"
            self.IS_MIC_ACTIVE = True
            t1.start()

    def record(self):
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
            rms = math.sqrt(abs(pow(data, 2).sum()/len(data)))
            print(rms)

        stream.stop_stream()
        stream.close()

        print(sr.recognize_sphinx(speech_recognition.AudioData(d, RATE, 4)))
        # del d

        # debug for myself
        wf = wave.open("test.wav", 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(d)
        wf.close()

        print("Exitting Thread")


    def record2(self):
        r = speech_recognition.Recognizer()
        mic = speech_recognition.Microphone()
        with mic as source:
            while self.IS_MIC_ACTIVE:
                audio = r.listen(source)
                print(audio.frame_data)
                print(r.recognize_sphinx(audio))

        print("Recording over")



class RootWidget(MDScreenManager):
    pass


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