import multiprocessing
import os

from event_stub import EventDetector


def initialize():
    """ Initialize creates all necessary objects for main
    """
    # TODO: start audio - thread?
    # TODO: start ble - get list of nearby shit
    try:
        event_detector = EventDetector()
    except IOError as e:
        print(e)
        raise
    return event_detector


def idle(event_detector):
    """ Processes for idle state
    """
    blink_proc = multiprocessing.Process(
        target=event_detector.detect_blink, args=(3,))
    blink_proc.start()
    blink_proc.join()
    print('Blink Detected')
    return 'active'


def active():
    """ Process for active state
    """
    # TODO: Device control
    # TODO: DAQ_fixate (n seconds, mu, sigma) Machine Learning
    print('Active mode')
    return 'idle'


def control():
    """ Processes for control state
    """
    print('control mode')
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
        return active()
    elif state == 'control':
        return control()
    else:
        print('AHHHHH')


if __name__ == "__main__":
    try:
        event_detector = initialize()
    except IOError:
        print('Setup failed, quitting program')
        os._exit(1)

    next_state = 'idle'
    while True:
        next_state = start_state(next_state, event_detector)


"""
        idle(event_detector)
        print('Idle finished')
        if not all_systems_good():
            print('Somethings wrong')
            break
        next_state = active(event_detector)
        print('Active mode finished')
        if next_state == 'control':
            control(event_detector)
            """
