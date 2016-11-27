import zmq
from msgpack import loads
import time
import ipdb
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
        #while stay:
        #TODO Change this to 3 seconds
        seconds_to_wait = 3
        right_eye_sum = 0.0
        left_eye_sum = 0.0
        count = 0
        conf_tol = 0.5
        means = []
        start_detection = time.time()  # Time when the detection started
    #    while ((time.time() - start_detection) < seconds_to_wait):
        while stay:
            raw_recv = self.sub.recv_multipart()
            if "gaze" in raw_recv[0]:
              msg = loads(raw_recv[1])
              if msg['confidence'] > conf_tol:
                msg = loads(raw_recv[1])
                base_data = msg['base_data']
                for idx, datum in enumerate(base_data):
                    x_pos = float(datum['norm_pos'][0])
                    count += 1.0

                    if idx % 2 == 0:
                        right_eye_sum += x_pos
                    elif idx % 2 == 1:
                        right_eye_sum += x_pos
                    
                    if count == 8:
                        right_mean = right_eye_sum / count
                        left_mean = right_eye_sum / count
                        means.append([left_mean, right_mean])
                        right_eye_sum = 0.0
                        left_eye_sum = 0.0
                        count = 0

            if len(means) > 30:
                length = len(means)
                len_diff = length - 30
                tmp_means = means
                means = tmp_means[len_diff:]

            vote = 0
            for idx, mean in enumerate(means):
                left_diff = mean[0] - means[idx-1][0]
                right_diff = mean[1] - means[idx-1][1]

                if left_diff > 0 and right_diff > 0:
                    vote += 1
                elif left_diff > 0 and right_diff < 0:
                    vote += 0
                elif left_diff < 0 and right_diff > 0:
                    vote += 0
                elif left_diff < 0 and right_diff < 0:
                    vote -= 1

                
                print float(vote/len(means))
                    



    #        print right_eye_deltas
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


    def test_gaze(self):
        while True:
            raw_recv = self.sub.recv_multipart()
            msg = loads(raw_recv[1])
            print(raw_recv[0])
            import pdb; pdb.set_trace()



if __name__ == '__main__':
    try:
        detector = EventDetector()
    except IOError:
        print('Pupil not connected, failure to create event detector')
        os._exit(1)
    #detector.grab_frames()
    #detector.grab_frames_seconds()
    #detector.detect_controls()
    detector.test_gaze()
