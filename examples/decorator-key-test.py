# SPDX-FileCopyrightText: 2021 Philip Howard
#
# SPDX-License-Identifier: MIT

# This example allows you to test each key and LED in turn
# 1. At startup all LEDs should be white
# 2. Press a key and it will turn blue
# 3. Release that key and it will turn white
# 4. *Hold* a key and it will turn red
# 5. Release a *held* key and it will turn green.
# If you can turn all your keys blue -> red -> green, they're good!

# Drop the `pmk` folder
# into your `lib` folder on your `CIRCUITPY` drive.

from pmk import PMK
from pmk.platform.keybow2040 import Keybow2040 as Hardware         # for Keybow 2040
# from pmk.platform.rgbkeypadbase import RGBKeypadBase as Hardware # for Pico RGB Keypad Base
import time

keybow = PMK(Hardware())
keys = keybow.keys

keybow.set_all(64, 64, 64)

for key in keys:
    @keybow.on_press(key)
    def press_handler(key):
        print("Key {} pressed".format(key.number))
        key.set_led(0, 0, 255)

    @keybow.on_release(key)
    def release_handler(key):
        print("Key {} released".format(key.number))
        if key.rgb == [255, 0, 0]:
            key.set_led(0, 255, 0)
        else:
            key.set_led(64, 64, 64)

    @keybow.on_hold(key)
    def hold_handler(key):
        print("Key {} held".format(key.number))
        key.set_led(255, 0, 0)

while True:
    keybow.update()
    time.sleep(1.0 / 60)
