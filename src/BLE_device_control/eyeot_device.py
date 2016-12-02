from bluetooth.ble import DiscoveryService, GATTRequester

import arduino
import ble_consts
import pc
from time import sleep


class EyeoTDevice(object):
    """EyeoTDevice represents a single EyeoT IoT (Arduino 101) BLE device, initialized by one of several authorized MAC
    addresses.

    Input: MAC address of the EyeoT device to control

    Initialization result: Initialized EyeoT device containing the proper MAC address, service UUID, tx_command and
    rx_response characteristic UUIDs, tx_handle, and GATTRequester
    """

    def __init__(self, address):
        self.address = address
        self.response = "Undefined"
        self.device_state = "Undefined"
        self.req = "Undefined"

    def connect(self):
        print("Connecting...\n")
        self.req = GATTRequester(self.address, True)  # initialize req and connect
        print("Connection Successful! \n")

    def disconnect(self):
        print("Disconnecting...\n")
        self.req.disconnect()
        del self.req
        self.req = "Undefined"
        print("Disconnection Successful! \n")

    def send_command(self, command):
        self.req.write_by_handle(arduino.command_handle, str(command))
        print("Sent '{0}' command\n".format(ble_consts.commands[command]))

    def receive_response(self):
        response = int(self.req.read_by_handle(arduino.response_handle)[0].encode('hex')[:2], 16)
        print("Response '{0}' received!\n".format(ble_consts.responses[response]))
        return response


class BinaryStateDevice(EyeoTDevice):
    def __init__(self, address, name):
        EyeoTDevice.__init__(self, address)
        self.device_name = name
        self.connect()
        #self.response = self.receive_response()
        self.device_state = ble_consts.states[self.read_state()]
        #self.disconnect()

    def read_state(self):
        state = int(self.req.read_by_handle(arduino.state_handle)[0].encode('hex')[:2], 16)
        print ("Device functional state '{0}' received!\n".format(ble_consts.states[state]))
        return state

    def turn_on(self):
        self.send_command(ble_consts.servo_on)

    def turn_off(self):
        self.send_command(ble_consts.servo_off)


def search_for_authorized_eyeot_devices():
    """This function performs a BLE scan, finding all possible devices in range. It compares each device's name and MAC
    address against those already white listed. It returns a list of any authorized devices.

    Input: authorized_devices, a list containing the current MAC addresses of valid EyeoT devices in range

    Output: authorized_devices, a list containing the current MAC addresses of valid EyeoT devices in range
    """
    auth_devices = list()  # initialize empty
    service = DiscoveryService(pc.hci_num)  # make sure to use the proper hci BLE radio, be it integrated or a dongle
    devices = service.discover(2)  # find all possible nearby BLE devices

    for address, name in devices.items():  # for all devices
        # if a discovered device's name and MAC address are pre-approved
        if address in arduino.mac_addresses:
            print("Authorized EyeoT device: {} at MAC address: {}".format(name, address))
            auth_devices.append(address)
        else:
            print("Rejected Device: {} at MAC address: {}".format(name, address))
    return auth_devices


def determine_device_type(address):
    if address == arduino.light:
        return BinaryStateDevice(address, "light")
    elif address == arduino.fan:
        return BinaryStateDevice(address, "fan")
