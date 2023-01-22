import pyaudio
import wave
import numpy as np
import math

INT16_MAX = 32768  # range is -32768 to 32767


def get_rms(frame: np.ndarray):
    return math.sqrt(abs(pow(frame, 2).sum()/len(frame)))
    # results


CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
RECORD_SECONDS = 5
WAVE_OUTPUT_FILENAME = "voice.wav"

p = pyaudio.PyAudio()

stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

print("* recording")

# The RMS Values seems to be in the range of 0 to 110, I'll just use the values directly without normalizing
# Incase the value is above 100, ill just round it to 100. Less processing (although an if condition is required xd)
for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
    data = stream.read(CHUNK)
    data = np.frombuffer(data, dtype='int16')
    rms_data = get_rms(data)
    print(rms_data)


print("* done recording")

stream.stop_stream()
stream.close()
p.terminate()