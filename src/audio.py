from os import path
from playsound import playsound

AUDIO_PATH = '../audio/'

# NOTE: Most of the audio files do not yet exist, these are just stubs


def system_on():
    playsound(path.join(AUDIO_PATH, 'system_on.mp3'))


def system_off():
    playsound(path.join(AUDIO_PATH, 'system_off.mp3'))


def select_device():
    playsound(path.join(AUDIO_PATH, 'select_device.mp3'))


def light_selected():
    playsound(path.join(AUDIO_PATH, 'light_selected.mp3'))


def fan_selected():
    playsound(path.join(AUDIO_PATH, 'fan_selected.mp3'))


def binary_control():
    playsound(path.join(AUDIO_PATH, 'binary_control.mp3'))


def incorrect_selection():
    playsound(path.join(AUDIO_PATH, 'incorrect_selection.mp3'))
