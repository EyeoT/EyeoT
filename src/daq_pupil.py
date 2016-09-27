import zmq
from msgpack import loads
import numpy as np
import time

# Status of DaqPupil
STATUS_STANDBY = 0
STATUS_OPENED = 1
STATUS_RUNNING = 2

# Indexes for theta and phi coordinates
THETA = 0
PHI = 1

# Indexes for left and right eyes
RIGHT = "0"
LEFT = "1"

# Pupil topic
TOPIC_PUPIL = "pupil."

class DaqPupil:
    """Acquisition class for pupil labs eye tracker.

    Like all daq modules, this class has the standard methods
        - OpenDevice
        - StartAcquisition
        - StopAcquisition
        - CloseDevice
        - GetData        

    For now, this class will only return pupil information, not gaze.
    The pupil information is in spherical coordinates

    To overcome camera movements across sessions, there is a Calibrate method    
    that will collect data over a short duration to compute a shift to the average pupil direction    
    """
    def __init__(self, addr="127.0.0.1", port="50020"):
        """ Constructor for daq pupil
        Inputs:
            addr : string
                Address of the pupil publisher
            port : string
                Port for requesting information
        """
        self.addr = addr
        self.req_port = port
        self.context = zmq.Context()        
        self.status = STATUS_STANDBY
        self.offset = {RIGHT: np.array([0,0]), LEFT: np.array([0,0])}

        self.req = []
        self.sub = []
        self.sub_port = []
        self.poller = []

    def open_device(self):
        """ Connects to pupil server
        """
        if self.status is STATUS_STANDBY:
            self.req = self.context.socket(zmq.REQ)
            self.req.connect("tcp://%s:%s" %(self.addr, self.req_port))

            # Request subscriber port
            self.req.send("SUB_PORT")  
            self.sub_port = self.req.recv()          

            # Create zmq socket and connect to subscriber addr:port
            self.sub = self.context.socket(zmq.SUB)
            self.sub.connect("tcp://%s:%s" %(self.addr,self.sub_port))
            self.status = STATUS_OPENED

    def start_acquisition(self):
        """ Starts subscription to the pupil topic
        """
        if self.status is STATUS_OPENED:
            self.sub.subscribe(TOPIC_PUPIL)

            # Create poller to prevent errors when no data exists in msg buffer
            self.poller = zmq.Poller()
            self.poller.register(self.sub, zmq.POLLIN)
            self.status = STATUS_RUNNING

    def get_data(self):
        """ Gets data stored in messaging buffer
        Outputs:
            direction_right : 2d np.array
                n_samples by 2 array with the right pupil normal coordinates (theta and phi)
            direction_left : 2d np.array
                n_samples by 2 array with the left pupil normal coordinates (theta and phi)            
        """
        pupil_direction = {RIGHT: [], LEFT:[]}
        if self.status is STATUS_RUNNING:
            while True:
                # Get sockets that have been polled and have to timeout
                socks = dict(self.poller.poll(0))  
                            
                if (self.sub in socks and socks[self.sub] == zmq.POLLIN): 
                    # Messages are sent in 2 pieces: topic and msg                    
                    topic, msg = self.sub.recv_multipart(zmq.DONTWAIT)
                    msg = loads(msg)   
                    pupil_direction[topic[-1]].append([msg["theta"], msg["phi"]])                    
                else:                    
                    break

        # Trim last sample if uneven
        if len(pupil_direction[RIGHT]) > len(pupil_direction[LEFT]):                                 
            pupil_direction[RIGHT] = pupil_direction[RIGHT][:-1] 
        elif len(pupil_direction[LEFT]) > len(pupil_direction[RIGHT]):  
            pupil_direction[LEFT] = pupil_direction[LEFT][:-1]   

        # Make output at least 2d array                                     
        pupil_direction[RIGHT] = np.atleast_2d(np.array(pupil_direction[RIGHT]).astype(np.float))
        pupil_direction[LEFT] = np.atleast_2d(np.array(pupil_direction[LEFT]).astype(np.float))

        # Make 0's into NaN
        pupil_direction[RIGHT][np.sum(pupil_direction[RIGHT],1)==0, :] = np.nan        
        pupil_direction[LEFT][np.sum(pupil_direction[LEFT],1)==0, :] = np.nan

        # Return empty if size is 0
        if pupil_direction[RIGHT].size == 0:
            return pupil_direction[RIGHT], pupil_direction[LEFT]
        else:
            return pupil_direction[RIGHT]-self.offset[RIGHT], pupil_direction[LEFT]-self.offset[LEFT] 

    def stop_acquisition(self): 
        """ Stops polling and subscription
        """
        if self.status is STATUS_RUNNING:
            self.poller.unregister(self.sub)
            self.sub.unsubscribe(TOPIC_PUPIL)
            self.status = STATUS_OPENED

    def close_device(self):
        """ Closes connection
        """
        if self.status is STATUS_OPENED:
            self.req = []
            self.sub_port = []
            self.sub = []
            self.status = STATUS_STANDBY
    
    def calibrate(self, duration):
        """ Collects data over time to find the average pupil direction to reframe coordinate SystemError
        Input:
            duration : float
                Duration in seconds of calibration
        """
        original_status = self.status

        self.open_device()
        self.start_acquisition()

        time.sleep(duration)
        pupil_right, pupil_left = self.get_data()
        
        self.stop_acquisition()
        self.close_device()

        if pupil_right.size != 0:
            self.offset[RIGHT] = np.mean(pupil_right,0)
            self.offset[LEFT] = np.mean(pupil_left,0)
        
        if original_status >= STATUS_OPENED:
            self.open_device() 

        if original_status is STATUS_RUNNING:
            self.start_acquisition()                                   
        
# Example usage        
if __name__ == "__main__":

    # Instantiate and start collecting data
    pupil = DaqPupil()

    pupil.open_device()
    pupil.start_acquisition()

    # Get data from buffer
    time.sleep(1)
    pupil_right, pupil_left = pupil.get_data()

    print "Number of samples in 1 second: %d" % (pupil_right.size/2)

    time.sleep(1)
    pupil_right, pupil_left = pupil.get_data()

    print "Number of samples in 1 second: %d" % (pupil_right.size/2)

    pupil.stop_acquisition()
    pupil.start_acquisition()

    time.sleep(1)
    pupil_right, pupil_left = pupil.get_data()

    print "Number of samples in 1 second: %d" % (pupil_right.size/2)

    pupil.stop_acquisition()
    pupil.close_device()
    pupil.open_device()
    pupil.start_acquisition()

    time.sleep(1)
    start = time.time()
    pupil_right, pupil_left = pupil.get_data()
    stop = time.time()

    print "Number of samples in 1 second: %d" % (pupil_right.size/2)

    # Close connection
    pupil.stop_acquisition()    
    pupil.close_device()

    # Print data
    for right, left in zip(pupil_right, pupil_left):
        print right, left

    print "Elapsed %f seconds in get_data call " % (stop-start)        
