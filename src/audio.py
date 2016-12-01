from os import path
import numpy as np
import sounddevice as sd
import soundfile as sf

AUDIO_PATH = '../audio/'


def system_on():
    data, fs = sf.read(path.join(AUDIO_PATH, 'System.wav'), dtype='float32')
    data2, fs = sf.read(path.join(AUDIO_PATH, 'On.wav'), dtype='float32')
    data = np.concatenate((data, data2))
    sd.play(data, fs, blocking=True)


def system_off():
    data, fs = sf.read(path.join(AUDIO_PATH, 'System.wav'), dtype='float32')
    data2, fs = sf.read(path.join(AUDIO_PATH, 'Off.wav'), dtype='float32')
    data = np.concatenate((data, data2))
    sd.play(data, fs, blocking=True)


def system_waking():
    data, fs = sf.read(path.join(AUDIO_PATH, 'System.wav'), dtype='float32')
    data2, fs = sf.read(path.join(AUDIO_PATH, 'Waking.wav'), dtype='float32')
    data = np.concatenate((data, data2))
    sd.play(data, fs, blocking=True)


def system_sleeping():
    data, fs = sf.read(path.join(AUDIO_PATH, 'System.wav'), dtype='float32')
    data2, fs = sf.read(path.join(AUDIO_PATH, 'Sleeping.wav'), dtype='float32')
    data = np.concatenate((data, data2))
    sd.play(data, fs, blocking=True)


def turn_light_on():
    data, fs = sf.read(path.join(AUDIO_PATH, 'To Turn The.wav'), dtype='float32')
    data2, fs = sf.read(path.join(AUDIO_PATH, 'Light.wav'), dtype='float32')
    data3, fs = sf.read(path.join(AUDIO_PATH, 'On.wav'), dtype='float32')
    data4, fs = sf.read(path.join(AUDIO_PATH, 'Look.wav'), dtype='float32')
    data5, fs = sf.read(path.join(AUDIO_PATH, 'Right.wav'), dtype='float32')
    data = np.concatenate((data, data2, data3, data4, data5))
    sd.play(data, fs, blocking=True)


def turn_light_off():
    data, fs = sf.read(path.join(AUDIO_PATH, 'To Turn The.wav'), dtype='float32')
    data2, fs = sf.read(path.join(AUDIO_PATH, 'Light.wav'), dtype='float32')
    data3, fs = sf.read(path.join(AUDIO_PATH, 'Off.wav'), dtype='float32')
    data4, fs = sf.read(path.join(AUDIO_PATH, 'Look.wav'), dtype='float32')
    data5, fs = sf.read(path.join(AUDIO_PATH, 'Left.wav'), dtype='float32')
    data = np.concatenate((data, data2, data3, data4, data5))
    sd.play(data, fs, blocking=True)


def turn_fan_on():
    data, fs = sf.read(path.join(AUDIO_PATH, 'To Turn The.wav'), dtype='float32')
    data2, fs = sf.read(path.join(AUDIO_PATH, 'Fan.wav'), dtype='float32')
    data3, fs = sf.read(path.join(AUDIO_PATH, 'On.wav'), dtype='float32')
    data4, fs = sf.read(path.join(AUDIO_PATH, 'Look.wav'), dtype='float32')
    data5, fs = sf.read(path.join(AUDIO_PATH, 'Right.wav'), dtype='float32')
    data = np.concatenate((data, data2, data3, data4, data5))
    sd.play(data, fs, blocking=True)


def turn_fan_off():
    data, fs = sf.read(path.join(AUDIO_PATH, 'To Turn The.wav'), dtype='float32')
    data2, fs = sf.read(path.join(AUDIO_PATH, 'Fan.wav'), dtype='float32')
    data3, fs = sf.read(path.join(AUDIO_PATH, 'Off.wav'), dtype='float32')
    data4, fs = sf.read(path.join(AUDIO_PATH, 'Look.wav'), dtype='float32')
    data5, fs = sf.read(path.join(AUDIO_PATH, 'Left.wav'), dtype='float32')
    data = np.concatenate((data, data2, data3, data4, data5))
    sd.play(data, fs, blocking=True)


def select_device():
    data, fs = sf.read(path.join(AUDIO_PATH, 'Select Device.wav'), dtype='float32')
    sd.play(data, fs, blocking=True)


def try_again():
    data, fs = sf.read(path.join(AUDIO_PATH, 'Please try again.wav'), dtype='float32')
    sd.play(data, fs, blocking=True)


def light_selected():
    data, fs = sf.read(path.join(AUDIO_PATH, 'Light.wav'), dtype='float32')
    data2, fs = sf.read(path.join(AUDIO_PATH, 'Selected.wav'), dtype='float32')
    data = np.concatenate((data, data2))
    sd.play(data, fs, blocking=True)


def fan_selected():
    data, fs = sf.read(path.join(AUDIO_PATH, 'Fan.wav'), dtype='float32')
    data2, fs = sf.read(path.join(AUDIO_PATH, 'Selected.wav'), dtype='float32')
    data = np.concatenate((data, data2))
    sd.play(data, fs, blocking=True)


def incorrect_selection():
    data, fs = sf.read(path.join(AUDIO_PATH, 'If Incorrect.wav'), dtype='float32')
    sd.play(data, fs, blocking=True)


def not_authenticated():
    data, fs = sf.read(path.join(AUDIO_PATH, 'No Authenticated.wav'), dtype='float32')
    data2, fs = sf.read(path.join(AUDIO_PATH, 'Please try again.wav'), dtype='float32')
    data = np.concatenate((data, data2))
    sd.play(data, fs, blocking=True)

def pip():
    data, fs = sf.read(path.join(AUDIO_PATH, 'Pip.wav'), dtype='float32')
    sd.play(data, fs, blocking=True)


if __name__ == "__main__":
    light_selected()
