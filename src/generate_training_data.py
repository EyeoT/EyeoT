from event_detector import EventDetector
from msgpack import loads
import time
import os
import zmq
import csv

# Steps taken before running this script
# Open Pupil Capture
# Make sure that the world view and the two eye cameras are working
# In the world view window, scroll up to the top of the settings and open the frame publisher plugin
# Then you can run the script
num_secs = 1

# Instantiating the Event Detector and subscribing to the world frames
detector = EventDetector()
detector.sub.setsockopt(zmq.SUBSCRIBE, 'frame.world')

# Getting the start time
start_time = time.time()

# Creating the output directory for the frames and the CSV
start_time_str = '{0}'.format(start_time)
file_path = 'pupil_frames/{}'.format(start_time_str.split('.')[0])
if not os.path.exists(file_path):
    os.makedirs(file_path)
file_name = 'frame{0}.{1}'
frame_number = 0
csvfile = open(os.path.join(file_path, 'gaze_frame_data.csv'), 'w')
fieldnames = ['timestamp', 'x_norm_pos', 'y_norm_pos', 'confidence', 'frame_file']
writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
writer.writeheader()

while time.time() - start_time < num_secs:
    # Getting the data that's being published
    raw_recv = detector.sub.recv_multipart()

    
    if raw_recv[0] == 'frame.world':
	msg = loads(raw_recv[1])

        # Writing the frame to a file
	frame_format = msg['format']
	this_file_name = file_name.format(frame_number, frame_format)
	frame_file = open(os.path.join(file_path, this_file_name), 'w')
	frame_file.write(raw_recv[2])
	frame_number += 1
    elif ("gaze" in raw_recv[0]) and frame_number >= 1:
	msg = loads(raw_recv[1])
        timestamp =  msg['timestamp']

        # NOTE: you can select a different attribute here by using a different key
        # the base_data is a list which is why you need to iterate over it
        for datum in msg['base_data']:
            print str(datum['timestamp']) + " " + str(datum['norm_pos'][0]) + " " + str(datum['norm_pos'][1]) + " " + this_file_name

            # Writing the sample captured to the csv
            sample = {'timestamp': datum['timestamp'],
                      'x_norm_pos': datum['norm_pos'][0],
                      'y_norm_pos': datum['norm_pos'][1],
                      'confidence': datum['confidence'],
                      'frame_file': this_file_name}
            writer.writerow(sample)
