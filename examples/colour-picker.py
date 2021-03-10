# SPDX-FileCopyrightText: 2021 Sandy Macdonald
#
# SPDX-License-Identifier: MIT

# This example demonstrates the use of a modifier key to pick the colour of the 
# keys' LEDs, as well as the LED sleep functionality.

import time
import board
import random
from keybow2040 import Keybow2040, number_to_xy

MODIFIER_KEY = 0

def hsv_to_rgb(h, s, v):
    # Convert an HSV (0.0-1.0) colour to RGB (0-255)
    if s == 0.0:
        rgb = [v, v, v]
    
    i = int(h * 6.0)

    f = (h*6.)-i; p,q,t = v*(1.-s), v*(1.-s*f), v*(1.-s*(1.-f)); i%=6
    
    if i == 0:
        rgb = [v, t, p]
    if i == 1:
        rgb = [q, v, p]
    if i == 2:
        rgb = [p, v, t]
    if i == 3:
        rgb = [p, q, v]
    if i == 4:
        rgb = [t, p, v]
    if i == 5:
        rgb = [v, p, q]

    rgb = [int(c * 255) for c in rgb]

    return rgb

# Set up Keybow
i2c = board.I2C()
keybow = Keybow2040(i2c)
keys = keybow.keys

# Enable LED sleep and set a time of 5 seconds before the LEDs turn off.
# They'll turn back on with a tap of any key!
keybow.led_sleep_enabled = True
keybow.led_sleep_time = 5

# Set up the modifier key. It's 0, or the bottom left key.
modifier_key = keys[MODIFIER_KEY]
modifier_key.modifier = True

# The starting colour (black/off)
rgb = (0, 0, 0)

while True:
    # Always remember to call keybow.update()!
    keybow.update()

    # If the modifier key and any other key are pressed, then set all the
    # keys to the selected colour. The second key pressed picks the colour.
    if modifier_key.held and keybow.any_pressed:
        if len(keybow.get_pressed()) > 1:
            hue = max(keybow.get_pressed()) / 15.0
            rgb = hsv_to_rgb(hue, 1.0, 1.0)

    keybow.set_all(*rgb)
