# constant values from Arduino 101 boards
mac_addresses = ['98:4F:EE:0F:7B:A2', '98:4F:EE:0F:89:69']  # MAC addresses of authorized Arduino 101 BLE boards
service_uuid = '19B10000-E8F2-537E-4F6C-D104768A1214'  # static UUID of Arduino 101 BLE service
tx_command = '19B10001-E8F2-537E-4F6C-D104768A1214'  # static UUID of Arduino 101 BLE characteristic
rx_response = '19B10002-E8F2-537E-4F6C-D104768A1214'  # static UUID of Arduino 101 BLE characteristic
command_handle = 0x0b  # static characteristic handle to write commands to device
response_handle = 0x0d  # static characteristic handle to read state from device
state_handle = 0x0f  # static characteristic handle to read state from device
name = 'EyeoT_BLE'  # name all Arduino boards should broadcast
light = mac_addresses[0]
fan = mac_addresses[1]
