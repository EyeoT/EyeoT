import multiprocessing
import os

from event_detector import EventDetector
# import audio
import color_detection
from BLE_device_control import eyeot_device


def initialize():
    """ Initialize creates all necessary objects for main
    """
    # TODO: start audio - thread?
    # find all EyeoT devices in range
    authorized_devices = eyeot_device.search_for_authorized_eyeot_devices()

    if len(authorized_devices) is 0:  # if no authorized devices are in range or powered on
        print("Error: No Authorized EyeoT devices found in range!")
        # TODO: Audio about no device in range, try again
        return None, None

    else:
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
    blink_proc = multiprocessing.Process(
        target=event_detector.detect_blink, args=(3,))
    blink_proc.start()
    blink_proc.join()
    print('Blink Detected')
    return 'active'


def detect_color_box(event_detector, color_queue):
    """ Detects fixation
        Then finds the lightbox and returns color
    """
    event_detector.detect_fixation()
    frame = event_detector.grab_bgr_frame()
    color = color_detection.get_box_color(frame, [])
    color_queue.put(color)


def active(event_detector):
    """ Process for active state
    """
    print('Active mode')
#   audio.select_device()
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
            print(color_queue.get())
            return 'control'
        if not blink_proc.is_alive():
            box_proc.terminate()
            print('blink first')
            return 'idle'


def control(event_detector):
    """ Processes for control state
    """
    print('control mode')
    control = event_detector.detect_controls()
    print(control)
    return 'active'


def all_systems_good():
    """ Checks that all systems are running properly
    """
    # TODO: Make sure things are working
    return True


def start_state(state, event_detector):
    if state == 'idle':
        return idle(event_detector)
    elif state == 'active':
        return active(event_detector)
    elif state == 'control':
        return control(event_detector)
    else:
        raise ValueError(state)


if __name__ == "__main__":
    try:
        event_detector, eyeot_devices = initialize()
        if event_detector is not None and eyeot_devices is not None:
            next_state = 'idle'
            while True:
                try:
                    next_state = start_state(next_state, event_detector)
                except ValueError as e:
                    print('Bad state given: {0}'.format(e))
                    break

        else:
            print(
                "Error: Problem initializing event_detector or finding an EyeoT device\n")

    except IOError:
        print('Setup failed, quitting program')
        os._exit(1)
