import multiprocessing
import os

from event_detector import EventDetector


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
    # TODO: Bluetooth callback


def wake():
    """ Process for wake state
    """
    # TODO: Device control
    # TODO: DAQ_fixate (n seconds, mu, sigma) Machine Learning
    print('Wake mode')


def all_systems_good():
    """ Checks that all systems are running properly
    """
    # TODO: Make sure things are working
    return True


if __name__ == "__main__":
    try:
        event_detector = initialize()
    except IOError:
        print('Setup failed, quitting program')
        os._exit(1)

    while True:
        idle(event_detector)
        print('Idle finished')
        if not all_systems_good():
            print('Somethings wrong')
            break
        wake()
        print('Wake finished')
