import multiprocessing
import os
import time

from event_detector import EventDetector
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
        # TODO: Audio about no device in range, try again
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
    # event_detector.detect_blink(3)
    blink_proc = multiprocessing.Process(
        target=event_detector.detect_blink, args=(3,))
    blink_proc.start()
    blink_proc.join()
    print('Blink Detected')
    return 'active', {}


def light_all_eyeot_devices(eyeot_devices):
    color_to_device = {}
    offset = 2
    device_color = ["green", "blue"]
    for i in range(int(len(eyeot_devices))):  # for all devices
        eyeot_devices[i].connect()
        time.sleep(1)
        print ble_consts.commands[i + offset]
        eyeot_devices[i].send_command(i + offset)
        eyeot_devices[i].disconnect()
        color_to_device[device_color[i]] = eyeot_devices[i]
    return color_to_device


def detect_color_box(event_detector, color_queue):
    """ Detects fixation
        Then finds the lightbox and returns color
    """
    fixation = event_detector.detect_fixation()
    frame = event_detector.grab_bgr_frame()
    color = color_detection.get_box_color(frame, fixation)
    color_queue.put(color)


def active(event_detector, eyeot_devices):
    """ Process for active state
    """
    print('Active mode')
#   audio.select_device()
    color_to_device = light_all_eyeot_devices(eyeot_devices)
    color_queue = multiprocessing.Queue()
    blink_proc = multiprocessing.Process(
        target=event_detector.detect_blink, args=(3,))
    box_proc = multiprocessing.Process(
        target=detect_color_box, args=(event_detector, color_queue))
    blink_proc.start()
    box_proc.start()
    while True:
        if not box_proc.is_alive():
            blink_proc.terminate()
            print('box first')
            color = color_queue.get()
            print(color)
            commands = {'color': color, 'color_dict': color_to_device}
            return 'control', commands
        if not blink_proc.is_alive():
            box_proc.terminate()
            print('blink first')
            return 'idle', {}


def control_detection(event_detector, control_queue):
    control = event_detector.detect_controls()
    control_queue.put(control)


def control(event_detector, commands):
    """ Processes for control state
    """
    print('control mode')
    # TODO: No color found
    color = commands['color']
    device = commands['color_dict'][color]
    print(device)
    # TODO: Audio for device and controls
    control_queue = multiprocessing.Queue()
    blink_proc = multiprocessing.Process(
        target=event_detector.detect_blink, args=(3,))
    control_proc = multiprocessing.Process(
        target=control_detection, args=(event_detector, control_queue))
    blink_proc.start()
    control_proc.start()
    while True:
        if not control_proc.is_alive():
            blink_proc.terminate()
            print('control first')
            control = control_queue.get()
            break
        if not blink_proc.is_alive():
            control_proc.terminate()
            print('blink first')
            return 'active', {}
    # TODO: Send device controls
    print(control)
    return 'active', {}


def all_systems_good():
    """ Checks that all systems are running properly
    """
    # TODO: Make sure things are working
    return True


def start_state(state, event_detector, eyeot_devices, commands):
    if state == 'idle':
        audio.system_off()
        return idle(event_detector)
    elif state == 'active':
        audio.system_on()
        return active(event_detector, eyeot_devices)
    elif state == 'control':
        return control(event_detector, commands)
    else:
        raise ValueError(state)


if __name__ == "__main__":
    try:
        event_detector, eyeot_devices = initialize()
        if event_detector is not None and eyeot_devices is not None:
            eyeot_devices[0].connect()
            eyeot_devices[0].send_command(ble_consts.red_light)
            time.sleep(1)
            eyeot_devices[0].send_command(ble_consts.green_light)
            time.sleep(1)
            eyeot_devices[0].send_command(ble_consts.blue_light)
            time.sleep(1)
            eyeot_devices[0].disconnect()
            next_state = 'idle'
            commands = {}
            while True:
                try:
                    next_state, commands = start_state(next_state, event_detector, eyeot_devices, commands)
                except ValueError as e:
                    print('Bad state given: {0}'.format(e))
                    break

        else:
            print(
                "Error: Problem initializing event_detector or finding an EyeoT device\n")

    except IOError:
        print('Setup failed, quitting program')
        os._exit(1)
