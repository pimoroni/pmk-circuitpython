import board
from keybow2040 import Keybow2040

import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
from adafruit_hid.keycode import Keycode

i2c = board.I2C()
keybow = Keybow2040(i2c)
keys = keybow.keys

keyboard = Keyboard(usb_hid.devices)
layout = KeyboardLayoutUS(keyboard)

keymap =    [Keycode.ZERO,
             Keycode.ONE,
             Keycode.TWO,
             Keycode.THREE,
             Keycode.FOUR,
             Keycode.FIVE,
             Keycode.SIX,
             Keycode.SEVEN,
             Keycode.EIGHT,
             Keycode.NINE,
             Keycode.A,
             Keycode.B,
             Keycode.C,
             Keycode.D,
             Keycode.E,
             Keycode.F]

for key in keys:
    @keybow.on_press(key)
    def press_handler(key):
        keycode = keymap[key.number]
        keyboard.send(keycode)

while True:
    keybow.update()
