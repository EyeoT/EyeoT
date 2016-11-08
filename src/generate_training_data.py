from event_detector import EventDetector
from msgpack import loads
import time
import os
import zmq
import ipdb

num_secs = 1
detector = EventDetector()
detector.sub.setsockopt(zmq.SUBSCRIBE, 'frame.world')
start_time = time.time()
start_time_str = '{0}'.format(start_time)
file_path = 'pupil_frames/{}'.format(start_time_str.split('.')[0])
if not os.path.exists(file_path):
    os.makedirs(file_path)
file_name = 'frame{0}.{1}'
frame_number = 0
while time.time() - start_time < num_secs:
    raw_recv = detector.sub.recv_multipart()
    if raw_recv[0] == 'frame.world':
	msg = loads(raw_recv[1])
	frame_format = msg['format']
	this_file_name = file_name.format(frame_number, frame_format)
	frame_file = open(os.path.join(file_path, this_file_name), 'w')
	frame_file.write(raw_recv[2])
	frame_number += 1
    elif ("gaze" in raw_recv[0]) and frame_number >= 1:
	msg = loads(raw_recv[1])
        timestamp =  msg['timestamp']
        for datum in msg['base_data']:
            print str(datum['timestamp']) + " " + str(datum['norm_pos'][0]) + " " + str(datum['norm_pos'][1]) + " " + this_file_name
