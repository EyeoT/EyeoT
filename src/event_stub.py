from time import sleep
import random


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

    def detect_gaze(self, num_tries=3, queue=None):
        tries = 0
        while tries < num_tries:
            color = self.get_box_color()
            if color is not None:
                if queue:
                    queue.put(color)
                return color
        if queue:
            queue.put(color)
        return None

    def get_box_color(self):
        sleep(random.random() * 5)
        print('Getting color')
        colors = ['blue', 'green', 'red', None]
        return colors[random.randint(0, 3)]

    def detect_controls(self):
        print('Controls detection')
        return random.randint(0, 1)
