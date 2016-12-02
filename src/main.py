import os
import time

from event_detector2 import EventDetector
import audio
import color_detection
from BLE_device_control import eyeot_device, ble_consts


def initialize():
    """ Initialize creates all necessary objects for main
    """
    # find all EyeoT devices in range
    authorized_devices = eyeot_device.search_for_authorized_eyeot_devices()

    if len(authorized_devices) is 0:  # if no authorized devices are in range or powered on
        print("Error: No Authorized EyeoT devices found in range!")
        audio.not_authenticated()
        return None, None

    if True:
        initialized_devices = list()
        for address in authorized_devices:  # for each valid EyeoT device
            initialized_devices.append(eyeot_device.determine_device_type(
                address))  # initialize light or fan
        try:
            event_detector = EventDetector()
        except IOError as e:
            print(e)
            raise
        return event_detector, initialized_devices


def idle(event_detector):
    """ Processes for idle state
    """
    print('Idle state')
    event_detector.detect_blink(2.25)
    print('Blink Detected')
    return 'active', {}


def light_all_eyeot_devices(eyeot_devices):
    color_to_device = {}
    offset = 2
    device_color = ["green", "blue"]
    for i in range(int(len(eyeot_devices))):  # for all devices
        print(ble_consts.commands[i + offset])
        eyeot_devices[i].send_command(i + offset)
        color_to_device[device_color[i]] = eyeot_devices[i]
    return color_to_device


def active(event_detector, eyeot_devices):
    """ Process for active state
    """
    color = None
    while color is None:
        print('Active mode')
        audio.select_device()
        color_to_device = light_all_eyeot_devices(eyeot_devices)
        detection = event_detector.detect_fixation()
        if detection[0] == 'blink':
            print('blink first')
            return 'idle', {}
        print('box first')
        fixation = detection[1]
        frame = event_detector.grab_bgr_frame()
        color = color_detection.get_box_color(frame, fixation)
        if color == 'red':
            color = None
    commands = {'color': color, 'color_dict': color_to_device}
    return 'control', commands


def control(event_detector, commands):
    """ Processes for control state
    """
    print('control mode')
    time.sleep(3)
    color = commands['color']
    if color is None:
        audio.try_again()
        return 'active', {}
    device = commands['color_dict'][color]
    print(device)
    audio.device_instructions(device.device_name, device.device_state)
    detection = event_detector.detect_controls()
    if detection[0] == 'blink':
        return 'active', {}
    control = detection[1]
    if control == 1:  # User looked right
        device.turn_on()  # command right
        print("Turning device on")
    elif control == -1:  # User looked left
        device.turn_off()  # command left
        print("Turning device off")
    elif control == 0:  # User looked straight ahead
        print "Looked Straight, didn't send command yet"
        return 'control', commands
    print(control)
    print "Returning to idle because command was successful"
    time.sleep(5)
    return 'idle', {}


def all_systems_good():
    """ Checks that all systems are running properly
    """
    # TODO: Make sure things are working
    return True


def start_state(state, event_detector, eyeot_devices, commands):
    if state == 'idle':
        audio.system_sleeping()
        time.sleep(2)
        return idle(event_detector)
    elif state == 'active':
        audio.system_waking()
        return active(event_detector, eyeot_devices)
    elif state == 'control':
        return control(event_detector, commands)
    else:
        raise ValueError(state)


if __name__ == "__main__":
    try:
        event_detector, eyeot_devices = initialize()
        if event_detector is not None and eyeot_devices is not None:
            audio.power_on()
            next_state = 'idle'
            commands = {}
            while True:
                try:
                    next_state, commands = start_state(
                        next_state, event_detector, eyeot_devices, commands)
                except ValueError as e:
                    print('Bad state given: {0}'.format(e))
                    break
                except RuntimeError as e:
                    print(e)
                    break

        else:
            print(
                "Error: Problem initializing event_detector or finding an EyeoT device\n")

    except IOError:
        print('Setup failed, quitting program')
        os._exit(1)
