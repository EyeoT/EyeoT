import zmq
from msgpack import loads
import time
import os


class EventDetector:
    """ Detects event based on the pupil

        NOTE:
        Each raw datum received from the pupil is an array.
        The variable name is raw_recv
        The first element is the topic
        The second element is the message
        and the third element depends on the topic and may not exist
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
        gaze_buffer_x = []
        gaze_buffer_y = []
        dispersion_thresh = .25
        fixation_count = 0
        fixations_timeout = 3
        while fixation_count < 4:
            raw_recv = self.sub.recv_multipart()
            if 'gaze' in raw_recv[0]:
                msg = loads(raw_recv[1])
                if msg['confidence'] > .9:
                    gaze_buffer_x.append(msg['base_data'][0]['norm_pos'][0])
                    gaze_buffer_y.append(msg['base_data'][0]['norm_pos'][1])
                    if len(gaze_buffer_x) > 120:
                        gaze_buffer_x.pop(0)
                        gaze_buffer_y.pop(0)

                        dispersion = max(
                            gaze_buffer_x) - min(gaze_buffer_x) + max(gaze_buffer_y) - min(gaze_buffer_y)
                        if dispersion < dispersion_thresh:
                            if fixation_count is 0:
                                first_focus = time.time()
                            elif time.time() - first_focus > fixations_timeout:
                                fixation_count = 0
                                first_focus = time.time()
                            print('Focused {0}'.format(fixation_count))
                            fixation_count += 1
                            gaze_buffer_x = []
                            gaze_buffer_y = []

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
        # TODO: ML project
        stay = True
        while stay:
            raw_recv = self.sub.recv_multipart()
            msg = loads(raw_recv[1])
            print(msg)

    def detect_controls(self):
        stay = True
        while stay:
            raw_recv = self.sub.recv_multipart()
            msg = loads(raw_recv[1])
            print(msg)
        # TODO: Detection for controls

    def grab_frames(self, num_frames=1):
        self.sub.setsockopt(zmq.SUBSCRIBE, 'frame.world')
        start_time_str = '{0}'.format(time.time())
        file_path = 'pupil_frames/{}'.format(start_time_str.split('.')[0])
        if not os.path.exists(file_path):
            os.makedirs(file_path)
        file_name = 'frame{0}.{1}'
        frame_number = 0
        while frame_number < num_frames:
            raw_recv = self.sub.recv_multipart()
            while raw_recv[0] != 'frame.world':
                raw_recv = self.sub.recv_multipart()
            msg = loads(raw_recv[1])
            frame_format = msg['format']
            this_file_name = file_name.format(frame_number, frame_format)
            frame_file = open(os.path.join(file_path, this_file_name), 'w')
            frame_file.write(raw_recv[2])
            frame_number += 1

    def grab_frames_seconds(self, num_secs=1):
        self.sub.setsockopt(zmq.SUBSCRIBE, 'frame.world')
        start_time = time.time()
        start_time_str = '{0}'.format(start_time)
        file_path = 'pupil_frames/{}'.format(start_time_str.split('.')[0])
        if not os.path.exists(file_path):
            os.makedirs(file_path)
        file_name = 'frame{0}.{1}'
        frame_number = 0
        while time.time() - start_time < num_secs:
            raw_recv = self.sub.recv_multipart()
            while raw_recv[0] != 'frame.world':
                raw_recv = self.sub.recv_multipart()
            msg = loads(raw_recv[1])
            frame_format = msg['format']
            this_file_name = file_name.format(frame_number, frame_format)
            frame_file = open(os.path.join(file_path, this_file_name), 'w')
            frame_file.write(raw_recv[2])
            frame_number += 1


if __name__ == '__main__':
    try:
        detector = EventDetector()
    except IOError:
        print('Pupil not connected, failure to create event detector')
        os._exit(1)
    detector.detect_fixation()
