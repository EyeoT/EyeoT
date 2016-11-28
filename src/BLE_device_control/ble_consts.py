# coding=utf-8  # encoding declaration (needed)

# defined commands (constant) that the Arduino needs to receive
no_light = 0  # turn off all indicator lights
red_light = 1  # turn indicator lights red
green_light = 2  # turn indicator lights green
blue_light = 3  # turn indicator lights blue
servo_on = 4  # move light switch into on position
servo_off = 5  # move light switch into off position
not_ready = 6  # the Arduino is busy executing a previous command, don't send it new commands
ready = 7  # the Arduino has finished executing previous commands, send it new commands when ready
command_ack = 8  # response acknowledgement from IoT device
command_success = 9  # response from IoT device saying command executed successfully
command_failure = 10  # response from IoT device saying command failed to be properly executed

# dict for printing verbose descriptions
commands = {
    no_light: 'Turn colors off',
    red_light: 'Turn color red',
    green_light: 'Turn color green',
    blue_light: 'Turn color blue',
    servo_on: 'Turn light on',
    servo_off: 'Turn light of'
}

responses = {
    not_ready: 'Arduino is not yet ready for a new command',
    ready: 'Arduino ready for next command',
    command_ack: 'Command acknowledged by IoT device',
    command_success: 'Command successfully carried out by IoT device',
    command_failure: 'Command failed to be carried out by IoT device'
}
