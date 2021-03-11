# SPDX-FileCopyrightText: 2021 Sandy Macdonald
#
# SPDX-License-Identifier: MIT

# This example demonstrates how to light keys when pressed.

# Drop the keybow2040.py file into your `lib` folder on your `CIRCUITPY` drive.

import board
from keybow2040 import Keybow2040

# Set up Keybow
i2c = board.I2C()
keybow = Keybow2040(i2c)
keys = keybow.keys

# Use cyan as the colour.
rgb = (0, 255, 255)

while True:
    # Always remember to call keybow.update() on every iteration of your loop!
    keybow.update()

    # Loop through the keys and set the LED to cyan if pressed, otherwise turn
    # it off (set it to black).
    for key in keys:
        if key.pressed:
            key.set_led(*rgb)
        else:
            key.set_led(0, 0, 0)