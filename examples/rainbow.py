# SPDX-FileCopyrightText: 2021 Sandy Macdonald
#
# SPDX-License-Identifier: MIT

# This example displays a rainbow animation on Keybow 2040's keys.

# Drop the `pmk` folder
# into your `lib` folder on your `CIRCUITPY` drive.

import math
from pmk import PMK, number_to_xy, hsv_to_rgb
from pmk.platform.keybow2040 import Keybow2040 as Hardware          # for Keybow 2040
# from pmk.platform.rgbkeypadbase import RGBKeypadBase as Hardware  # for Pico RGB Keypad Base

# Set up Keybow
keybow = PMK(Hardware())
keys = keybow.keys

# Increment step to shift animation across keys.
step = 0

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
        keys[i].set_led(r, g, b)
