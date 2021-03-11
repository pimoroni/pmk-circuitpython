# SPDX-FileCopyrightText: 2021 Sandy Macdonald
#
# SPDX-License-Identifier: MIT

# Demonstrates how to send MIDI notes by attaching handler functions to key
# presses with decorators.

# You'll need to connect Keybow 2040 to a computer running a DAW like Ableton,
# or other software synth, or to a hardware synth that accepts USB MIDI.

# NOTE! Requires the adafruit_midi CircuitPython library!

import time
import board
import random
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
midi = adafruit_midi.MIDI(midi_out=usb_midi.ports[1], out_channel=5)

# The colour to set the keys when pressed.
rgb = (255, 50, 0)

# MIDI velocity.
start_note = 60
velocity = 127

# Arpeggio style:
# 0 = up
# 1 = down
# 2 = up down
arp_style = 2

if arp_style == 0 or arp_style == 2:
    direction = 1
elif arp_style == 1:
    direction = -1

last_played = None
last_pressed = []
speed = 5

# Loop through keys and attach decorators.
for key in keys:
    # If pressed, turn on LED.
    @keybow.on_press(key)
    def press_handler(key):
        key.set_led(*rgb)

    # If released, turn off LED.
    @keybow.on_release(key)
    def release_handler(key):
        key.set_led(0, 0, 0)

while True:
    # Always remember to call keybow.update()!
    keybow.update()

    if keybow.any_pressed():
        pressed = keybow.get_pressed()

        if pressed != last_pressed:
            notes = [start_note + k for k in pressed]
            last_pressed = pressed

            if arp_style == 0 or arp_style == 2:
                this_note = 0
            elif arp_style == 1:
                this_note = len(notes) - 1

            midi.send(NoteOn(notes[this_note], velocity))
            print(notes[this_note])

            last_played = time.monotonic()
            elapsed = 0
            last_note = this_note
            this_note += direction

        else:
            if notes != []:
                elapsed = time.monotonic() - last_played

                if elapsed > 1 / speed:
                    if this_note == len(notes) and direction == 1:
                        this_note = 0
                    elif this_note < 0:
                        this_note = len(notes) - 1

                    midi.send(NoteOff(notes[last_note], 0))
                    midi.send(NoteOn(notes[this_note], velocity))
                    print(notes[this_note])

                    last_played = time.monotonic()
                    last_note = this_note

                    if arp_style == 2 and this_note == len(notes) -1:
                        direction = -1
                    elif arp_style == 2 and this_note == 0:
                        direction = 1

                    this_note += direction

    elif len(last_pressed) and keybow.none_pressed():
        for note in range(128):
            midi.send(NoteOff(note, 0))

        last_pressed = []