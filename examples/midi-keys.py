# SPDX-FileCopyrightText: 2021 Sandy Macdonald
#
# SPDX-License-Identifier: MIT

# Demonstrates how to send MIDI notes by attaching handler functions to key
# presses with decorators.

# You'll need to connect Keybow 2040 to a computer running a DAW like Ableton,
# or other software synth, or to a hardware synth that accepts USB MIDI.

# Drop the keybow2040.py file into your `lib` folder on your `CIRCUITPY` drive.

# NOTE! Requires the adafruit_midi CircuitPython library also!

import time
import board
from keybow2040 import Keybow2040

import usb_midi
import adafruit_midi
from adafruit_midi.note_off import NoteOff
from adafruit_midi.note_on import NoteOn

# Set up Keybow
i2c = board.I2C()
keybow = Keybow2040(i2c)
keys = keybow.keys

# Set USB MIDI up on channel 0.
midi = adafruit_midi.MIDI(midi_out=usb_midi.ports[1], out_channel=0)

# The colour to set the keys when pressed.
rgb = (0, 255, 50)

# Initial values for MIDI note and velocity.
start_note = 36
velocity = 127

# Loop through keys and attach decorators.
for key in keys:
    # If pressed, send a MIDI note on command and light key.
    @keybow.on_press(key)
    def press_handler(key):
        note = start_note + key.number
        key.set_led(*rgb)
        midi.send(NoteOn(note, velocity))

    # If released, send a MIDI note off command and turn off LED.
    @keybow.on_release(key)
    def release_handler(key):
        note = start_note + key.number
        key.set_led(0, 0, 0)
        midi.send(NoteOff(note, 0))

while True:
    # Always remember to call keybow.update()!
    keybow.update()
