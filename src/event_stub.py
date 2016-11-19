from time import sleep


class EventDetector:
    """ THIS CLASS IS FOR TESTING ONLY
        Replace imports of event_detector with event_stub to test
        code without pupil
    """

    def __init__(self):
        self.context = 'context'

    def detect_blink(self, seconds_to_wait=3):
        sleep(seconds_to_wait)
        print('Blinked')

    def grab_frames(self, num_frames=1):
        print('Frame grabbed')

    def detect_gaze(self):
        print('Gaze detected')

    def detect_controls(self):
        print('Controls detection')
        return 0
