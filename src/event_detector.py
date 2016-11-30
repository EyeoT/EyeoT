import zmq
from msgpack import loads
import time
import os
import cv2
import numpy as np


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

    def reinit(self, addr='127.0.0.1', port='50020'):
        """ Initializes the data stream from the pupil
        """
        self.context = zmq.Context()
        self.req = self.context.socket(zmq.REQ)
        self.req.RCVTIMEO = 1000  # milliseconds
        self.req.connect('tcp://{0}:{1}'.format(addr, port))
        # Ask for the subport
        self.req.send('SUB_PORT')
        sub_port = self.req.recv()
        # Open a sub port to listen to the pupil
        self.sub = self.context.socket(zmq.SUB)
        self.sub.connect('tcp://{0}:{1}'.format(addr, sub_port))
        self.sub.setsockopt(zmq.SUBSCRIBE, '')

    def detect_blink(self, seconds_to_wait=3):
        """ Detects when a blink happens for the specified number of seconds
        """
        self.reinit()
        stay = True
        # While we are still looking for the blink
        while stay:
            raw_recv = self.sub.recv_multipart()
            if 'pupil' in raw_recv[0]:
                msg = loads(raw_recv[1])
                # When the confidence drops below .5, we assume the
                # eyes are closed and a blink has begun
                if msg['confidence'] < .5:
                    conf_queue = [0, 0, 0, 0, 0]  # Reset our confidence queue
                    start_blink = time.time()  # Time when the blink began
                    print start_blink
                    # While the blink has not lasted for specified time
                    while ((time.time() - start_blink) < seconds_to_wait):
                        raw_recv = self.sub.recv_multipart()
                        while 'pupil' not in raw_recv[0]:
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
                            if sum(conf_queue) > 3:
                                stay = True
                                break
                        # If confidence is low, add a 0 to the queue
                        else:
                            conf_queue.append(0)
        return

    def detect_fixation(self, times_to_run=3):
        self.reinit()
        gaze_buffer_x = []
        gaze_buffer_y = []
        dispersion_thresh = .25
        fixation_count = 0
        fixations_timeout = 5
        while fixation_count < times_to_run:
            raw_recv = self.sub.recv_multipart()
            if 'gaze' in raw_recv[0]:
                msg = loads(raw_recv[1])
                if msg['confidence'] > .8:
                    gaze_buffer_x.append(msg['norm_pos'][0])
                    gaze_buffer_y.append(msg['norm_pos'][1])
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
                            if fixation_count <= times_to_run-1:
                                gaze_buffer_x = []
                                gaze_buffer_y = []
        x_fixation_pos = sum(gaze_buffer_x)/float(len(gaze_buffer_x))
        y_fixation_pos = sum(gaze_buffer_y)/float(len(gaze_buffer_y))
        return [x_fixation_pos, y_fixation_pos]

    def detect_controls(self, timeout=5):
        self.reinit()
        start_time = time.time()
        pos_buffer = []
        left_tol = .3
        right_tol = .7
        buffer_len = 20
        while time.time() - start_time < timeout:
            raw_recv = self.sub.recv_multipart()
            if 'gaze' in raw_recv[0]:
                msg = loads(raw_recv[1])
                if msg['confidence'] > .8:
                    pos_buffer.append(msg['norm_pos'][0])
                    if len(pos_buffer) > buffer_len:
                        pos_buffer.pop(0)
                        avg_pos = sum(pos_buffer)/buffer_len
                        if avg_pos < left_tol:
                            print('left')
                            return -1
                        if avg_pos > right_tol:
                            print('right')
                            return 1
        print('straight')
        return 0


    def grab_bgr_frame(self):
        self.reinit()
        self.sub.setsockopt(zmq.SUBSCRIBE, 'frame.world')
        raw_recv = self.sub.recv_multipart()
        while raw_recv[0] != 'frame.world':
            raw_recv = self.sub.recv_multipart()
        msg = loads(raw_recv[1])
        if msg['format'] == 'bgr':
            frame = np.frombuffer(raw_recv[2], dtype=np.uint8).reshape(720, 1280, 3)
        else:
            file_name = 'frame.{0}'.format(msg['format'])
            frame_file = open(file_name, 'w')
            frame_file.write(raw_recv[2])
            frame = cv2.imread(file_name)
        return frame

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
    detector.detect_controls()
