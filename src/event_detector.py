import zmq
from msgpack import loads


class EventDetector:
    """ Detects event based on the pupil
    """

    def __init__(self, addr='127.0.0.1', port='50020'):
        """ Initializes the data stream from the pupil
        """
        self.context = zmq.Context()
        self.req = self.context.socket(zmq.REQ)
        self.req.connect('tcp://{0}:{1}'.format(addr, port))
        # Ask for the subport
        self.req.send('SUB_PORT')
        sub_port = self.req.recv()
        # Open a sub port to listen to the pupil
        self.sub = self.context.socket(zmq.SUB)
        self.sub.connect('tcp://{0}:{1}'.format(addr, sub_port))
        self.sub.setsockopt(zmq.SUBSCRIBE, '')

    def detect_blink(self):
        self.sub.setsockopt(zmq.SUBSCRIBE, 'pupil.')
        stay = True
        while stay:
            topic, msg = self.sub.recv_multipart()
            msg = loads(msg)
            if msg['confidence'] == 0:
                print('Blink')
                stay = False
        # TODO: Detect blink

    def detect_fixation(self):
        stay = True
        while stay:
            topic, msg = self.sub.recv_multipart()
        # TODO: Detect fixation or blink

    def detect_controls(self):
        stay = True
        while stay:
            topic, msg = self.sub.recv_multipart()
        # TODO: Detection for controls
    
if __name__ == '__main__':
    detector = EventDetector()
    detector.detect_blink()
