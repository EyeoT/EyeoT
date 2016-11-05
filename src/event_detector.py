import zmq
from msgpack import loads
import time
import os


class EventDetector:
    """ Detects event based on the pupil
    """

    def __init__(self, addr='127.0.0.1', port='50020'):
        """ Initializes the data stream from the pupil
        """
        self.context = zmq.Context()
        self.req = self.context.socket(zmq.REQ)
        self.req.RCVTIMEO = 1000  # milliseconds
        try:
            self.req.connect('tcp://{0}:{1}'.format(addr, port))
            # Ask for the subport
            self.req.send('SUB_PORT')
            sub_port = self.req.recv()
            # Open a sub port to listen to the pupil
            self.sub = self.context.socket(zmq.SUB)
            self.sub.connect('tcp://{0}:{1}'.format(addr, sub_port))
            self.sub.setsockopt(zmq.SUBSCRIBE, '')
        except zmq.error.Again:
            print('Trouble with connection, is pupil connected?')
            raise IOError('Pupil not connected')

    def detect_blink(self, seconds_to_wait=3):
        """ Detects when a blink happens for the specified number of seconds
        """
        self.sub.setsockopt(zmq.SUBSCRIBE, 'pupil.')
        stay = True
        # While we are still looking for the blink
        while stay:
            raw_recv = self.sub.recv_multipart()
            msg = loads(raw_recv[1])
            # When the confidence drops below .5, we assume the
            # eyes are closed and a blink has begun
            if msg['confidence'] < .5:
                conf_queue = [0, 0, 0, 0, 0]  # Reset our confidence queue
                start_blink = time.time()  # Time when the blink began
                # While the blink has not lasted for specified time
                while ((time.time() - start_blink) < seconds_to_wait):
                    raw_recv = self.sub.recv_multipart()
                    msg = loads(raw_recv[1])
                    confidence = msg['confidence']
                    stay = False
                    conf_queue.pop(0)  # Take out first item
                    # If confidence is high, add a 1 to queue
                    if confidence > .2:
                        conf_queue.append(1)
                        # When sum of the queue exceeds 2 we determine eyes
                        # have been opened and blink has ended
                        if sum(conf_queue) > 2:
                            stay = True
                            break
                    # If confidence is low, add a 0 to the queue
                    else:
                        conf_queue.append(0)

    def detect_fixation(self):
        stay = True
        while stay:
            raw_recv = self.sub.recv_multipart()
            msg = loads(raw_recv[1])
        # TODO: Detect fixation or blink

    def detect_controls(self):
        stay = True
        while stay:
            raw_recv = self.sub.recv_multipart()
            msg = loads(raw_recv[1])
        # TODO: Detection for controls

if __name__ == '__main__':
    try:
        detector = EventDetector()
    except IOError:
        print('Pupil not connected, failure to create event detector')
        os._exit(1)
    detector.detect_blink(3)
