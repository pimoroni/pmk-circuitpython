
# SPDX-FileCopyrightText: 2021 Philip Howard
#
# SPDX-License-Identifier: MIT

# This example gives you eight toggle and eight "mutex" key bindings for OBS studio
#
# MUTEX
# Use the top eight buttons (nearest the USB connector) to bind your scenes.
# The light on these is mutually exclusive- the one you last pressed should light up,
# and this is the scene you should be broadcasting.
#
# TOGGLE
# The bottom eight buttons will toggle on/off, emitting a slightly different keycode
# for each state. This means they will *always* indicate the toggle state.
# Bind these to Mute/Unmute audio by pressing the key once in Mute and once again in Unmute.
#
# Keep OBS focussed when using these... to avoid weirdness!

# Drop the `pmk` folder
# into your `lib` folder on your `CIRCUITPY` drive.

import math
from pmk import PMK, number_to_xy, hsv_to_rgb
from pmk.platform.keybow2040 import Keybow2040 as Hardware          # for Keybow 2040
# from pmk.platform.rgbkeypadbase import RGBKeypadBase as Hardware  # for Pico RGB Keypad Base

import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
from adafruit_hid.keycode import Keycode

# Pick your keycodes here, these are chosen to - mostly - stay out of the way
# and use Numpad and regular numbers.
# Toggle keybinds (indicated by a Tuple with True) will send:
# * CONTROL + SHIFT + KEYCODE - when toggled on
# * CONTROL + ALT + KEYCODE - when toggled off
keycodes = [
    (Keycode.KEYPAD_FIVE, True),       # Bottom 1
    (Keycode.KEYPAD_ONE, True),        # Bottom 1
    Keycode.FIVE,
    Keycode.ONE,
    (Keycode.KEYPAD_SIX, True),        # Bottom 2
    (Keycode.KEYPAD_TWO, True),        # Bottom 2
    Keycode.SIX,
    Keycode.TWO,
    (Keycode.KEYPAD_SEVEN, True),      # Bottom 3
    (Keycode.KEYPAD_THREE, True),      # Bottom 3
    Keycode.SEVEN,
    Keycode.THREE,
    (Keycode.KEYPAD_EIGHT, True),      # Bottom 4
    (Keycode.KEYPAD_FOUR, True),       # Bottom 4
    Keycode.EIGHT,
    Keycode.FOUR
]

# Set up the keyboard and layout
keyboard = Keyboard(usb_hid.devices)
layout = KeyboardLayoutUS(keyboard)

# Set up Keybow
keybow = PMK(Hardware())
keys = keybow.keys

states = [False for _ in keys]

# Increment step to shift animation across keys.
step = 0
active = -1

for key in keys:
    @keybow.on_press(key)
    def press_handler(key):
        global active
        print("{} pressed".format(key.number))
        binding = keycodes[key.number]
        if binding is None:
            return
        if type(binding) is tuple:
            binding, _ = binding
            states[key.number] = not states[key.number]
            if states[key.number]:
                keyboard.press(Keycode.LEFT_CONTROL, Keycode.LEFT_SHIFT, binding)
            else:
                keyboard.press(Keycode.LEFT_CONTROL, Keycode.LEFT_SHIFT, Keycode.LEFT_ALT, binding)
        else:
            keyboard.press(Keycode.LEFT_CONTROL, Keycode.LEFT_SHIFT, binding)
            active = key.number

    @keybow.on_release(key)
    def release_handler(key):
        global active
        print("{} released".format(key.number))
        binding = keycodes[key.number]
        if binding is None:
            return
        if type(binding) is tuple:
            binding, _ = binding
            if states[key.number]:
                keyboard.release(Keycode.LEFT_CONTROL, Keycode.LEFT_SHIFT, binding)
            else:
                keyboard.release(Keycode.LEFT_CONTROL, Keycode.LEFT_SHIFT, Keycode.LEFT_ALT, binding)
        else:
            keyboard.release(Keycode.LEFT_CONTROL, Keycode.LEFT_SHIFT, binding)

    @keybow.on_hold(key)
    def hold_handler(key):
        pass


while True:
    # Always remember to call keybow.update() on every iteration of your loop!
    keybow.update()

    step += 1

    for i in range(16):
        # Convert the key number to an x/y coordinate to calculate the hue
        # in a matrix style-y.
        x, y = number_to_xy(i)

        # Calculate the hue.
        hue = (x + y + (step / 20)) / 8
        hue = hue - int(hue)
        hue = hue - math.floor(hue)

        # Convert the hue to RGB values.
        r, g, b = hsv_to_rgb(hue, 1, 1)

        # Display it on the key!
        if i == active or states[i]:
            keys[i].set_led(r, g, b)
        else:
            keys[i].set_led(int(r / 10.0), int(g / 10.0), int(b / 10.0))
