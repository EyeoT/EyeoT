from eventdetector import eventdetector
import unittest
import zmq

class EventDetectorTestCase(unittest.TestCase):

  def test_instantiation(self):
    import ipdb; ipdb.set_trace()
    event_detector = eventdetector.EventDetector()
    assert isinstance(event_detector.context, zmq.sugar.context.Context)
    assert isinstance(event_detector.req, zmq.sugar.socket.Socket)


if __name__ == '__main__':
  unittest.main()
