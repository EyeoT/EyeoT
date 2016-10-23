from device import Device


class Light(Device):

    def __init__(self, name):
        Device.__init__(self, name)
        self.is_on = False

    def turn_off(self):
        pass

    def turn_on(self):
        pass
