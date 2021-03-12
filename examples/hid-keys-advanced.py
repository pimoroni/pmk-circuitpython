# SPDX-FileCopyrightText: 2021 Sandy Macdonald
#
# SPDX-License-Identifier: MIT

# An advanced example of how to set up a HID keyboard.

# There are three layers, selected by pressing and holding key 0 (bottom left), 
# then tapping one of the coloured layer selector keys above it to switch layer.

# The layer colours are as follows:

#  * layer 1: pink: numpad-style keys, 0-9, delete, and enter.
#  * layer 2: blue: sends strings on each key press
#  * layer 3: media controls, rev, play/pause, fwd on row one, vol. down, mute,
#             vol. up on row two

# You'll need to connect Keybow 2040 to a computer, as you would with a regular
# USB keyboard.

# Drop the keybow2040.py file into your `lib` folder on your `CIRCUITPY` drive.

# NOTE! Requires the adafruit_hid CircuitPython library also!

import board
import time
from keybow2040 import Keybow2040

import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
from adafruit_hid.keycode import Keycode

from adafruit_hid.consumer_control import ConsumerControl
from adafruit_hid.consumer_control_code import ConsumerControlCode

# Set up Keybow
i2c = board.I2C()
keybow = Keybow2040(i2c)
keys = keybow.keys

# Set up the keyboard and layout
keyboard = Keyboard(usb_hid.devices)
layout = KeyboardLayoutUS(keyboard)

# Set up consumer control (used to send media key presses)
consumer_control = ConsumerControl(usb_hid.devices)

# Our layers. The key of item in the layer dictionary is the key number on
# Keybow to map to, and the value is the key press to send.

# Note that keys 0-3 are reserved as the modifier and layer selector keys 
# respectively.

layer_1 =     {4: Keycode.ZERO,
               5: Keycode.ONE,
               6: Keycode.FOUR,
               7: Keycode.SEVEN,
               8: Keycode.DELETE,
               9: Keycode.TWO,
               10: Keycode.FIVE,
               11: Keycode.EIGHT,
               12: Keycode.ENTER,
               13: Keycode.THREE,
               14: Keycode.SIX,
               15: Keycode.NINE}

layer_2 =     {7: "pack ",
               11: "my ",
               15: "box ",
               6: "with ",
               10: "five ",
               14: "dozen ",
               5: "liquor ",
               9: "jugs "}

layer_3 =     {6: ConsumerControlCode.VOLUME_DECREMENT,
               7: ConsumerControlCode.SCAN_PREVIOUS_TRACK,
               10: ConsumerControlCode.MUTE,
               11: ConsumerControlCode.PLAY_PAUSE,
               14: ConsumerControlCode.VOLUME_INCREMENT,
               15: ConsumerControlCode.SCAN_NEXT_TRACK}

layers =      {1: layer_1,
               2: layer_2,
               3: layer_3}

# Define the modifier key and layer selector keys
modifier = keys[0]

selectors =   {1: keys[1],
               2: keys[2],
               3: keys[3]}

# Start on layer 1
current_layer = 1

# The colours for each layer
colours = {1: (255, 0, 255),
           2: (0, 255, 255),
           3: (255, 255, 0)}

layer_keys = range(4, 16)

# Set the LEDs for each key in the current layer
for k in layers[current_layer].keys():
    keys[k].set_led(*colours[current_layer])

# To prevent the strings (as opposed to single key presses) that are sent from 
# refiring on a single key press, the debounce time for the strings has to be 
# longer.
short_debounce = 0.03
long_debounce = 0.15
debounce = 0.03
fired = False

while True:
    # Always remember to call keybow.update()!
    keybow.update()

    # This handles the modifier and layer selector behaviour
    if modifier.held:
        # Give some visual feedback for the modifier key
        keys[0].led_off()

        # If the modifier key is held, light up the layer selector keys
        for layer in layers.keys():
            keys[layer].set_led(*colours[layer])

            # Change layer if layer key is pressed
            if current_layer != layer:
                if selectors[layer].pressed:
                    current_layer = layer

                    # Set the key LEDs first to off, then to their layer colour
                    for k in layer_keys:
                        keys[k].set_led(0, 0, 0)

                    for k in layers[layer].keys():
                        keys[k].set_led(*colours[layer])

    # Turn off the layer selector LEDs if the modifier isn't held
    else:
        for layer in layers.keys():
            keys[layer].led_off()

        # Give some visual feedback for the modifier key
        keys[0].set_led(0, 255, 25)

    # Loop through all of the keys in the layer and if they're pressed, get the
    # key code from the layer's key map
    for k in layers[current_layer].keys():
        if keys[k].pressed:
            key_press = layers[current_layer][k]

            # If the key hasn't just fired (prevents refiring)
            if not fired:
                fired = True

                # Send the right sort of key press and set debounce for each
                # layer accordingly (layer 2 needs a long debounce)
                if current_layer == 1:
                    debounce = short_debounce
                    keyboard.send(key_press)
                elif current_layer == 2:
                    debounce = long_debounce
                    layout.write(key_press)
                elif current_layer == 3:
                    debounce = short_debounce
                    consumer_control.send(key_press)

    # If enough time has passed, reset the fired variable
    if fired and time.monotonic() - keybow.time_of_last_press > debounce:
        fired = False