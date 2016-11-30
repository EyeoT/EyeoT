import cv2
import csv
import os
import time
from event_detector import EventDetector
from BLE_device_control import eyeot_device, ble_consts


def initialize():
    """ Initialize creates all necessary objects for main
    """
    # find all EyeoT devices in range
    authorized_devices = eyeot_device.search_for_authorized_eyeot_devices()

    if len(authorized_devices) is 0:  # if no authorized devices are in range or powered on
        print("Error: No Authorized EyeoT devices found in range!")
        # TODO: Audio about no device in range, try again
        return None, None

    if True:
        initialized_devices = list()
        try:
            event_detector = EventDetector()
        except IOError as e:
            print(e)
            raise
        return event_detector, initialized_devices

def get_frame_and_fixation(event_detector):
    frame_set = {}
    frame_set['fixation'] = event_detector.detect_fixation()
    frame_set['frame'] = event_detector.grab_bgr_frame()
    return frame_set


def light_boxes(eyeot_devices):
    color_to_device = {}
    offset = 2
    device_color = ["green", "blue"]
    for i in range(int(len(eyeot_devices))):  # for all devices
        eyeot_devices[i].connect()
        time.sleep(1)
        print ble_consts.commands[i + offset]
        eyeot_devices[i].send_command(i + offset)
        eyeot_devices[i].disconnect()
        color_to_device[device_color[i]] = eyeot_devices[i]
    return color_to_device


def write_frame_sets(frame_sets, file_path):
    if not os.path.exists(file_path):
        os.makedirs(file_path)
    csvfile = open(os.path.join(file_path, 'gaze_frame_data.csv'), 'w')
    fieldnames = ['x_norm_pos', 'y_norm_pos', 'frame_file']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    frame_name = 'frame{0}.jpeg'
    count = 0
    for frame_set in frame_sets:
        curr_frame_name = frame_name.format(count)
        cv2.imwrite(os.path.join(file_path, curr_frame_name), frame_set['frame'])

        # Writing the sample captured to the csv
        sample = {'x_norm_pos': frame_set['fixation'][0],
                  'y_norm_pos': frame_set['fixation'][1],
                  'frame_file': curr_frame_name}
        writer.writerow(sample)

        count += 1


if __name__ == "__main__":
    try:
        event_detector, eyeot_devices = initialize()
        frame_sets = []
        file_path = 'test_data/{0}'.format(time.time())
        if event_detector is not None and eyeot_devices is not None:
            # light_boxes(eyeot_devices)
            for i in range(5):
                frame_sets.append(get_frame_and_fixation(event_detector))
            write_frame_sets(frame_sets, file_path)
    except:
         pass
