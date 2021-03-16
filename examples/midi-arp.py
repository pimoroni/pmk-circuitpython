# SPDX-FileCopyrightText: 2021 Sandy Macdonald
#
# SPDX-License-Identifier: MIT

# A MIDI arpeggiator, with three different styles: up, down, or up-down. BPM and
# note length are both configurable, and LEDs cycle with the currently-played
# key/note to give some visual feedback.

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
midi = adafruit_midi.MIDI(midi_out=usb_midi.ports[1], out_channel=5)

# The colour to set the keys when pressed, orange-y.
rgb = (255, 50, 0)

# MIDI velocity.
start_note = 36
velocity = 100

# Beats per minute
bpm = 80

# Play 16th notes
note_length = 1/16

# Assumes BPM is calculated on quarter notes
note_time = 60 / bpm * (note_length * 4)

# Arpeggio style:
# 0 = up
# 1 = down
# 2 = up-down
arp_style = 2

# Start the arp in a forwards direction (1) if the style is up or up-down, or
# or backwards (-1) if the style is down.
if arp_style == 0 or arp_style == 2:
    direction = 1
elif arp_style == 1:
    direction = -1

# Keep track of time of last note played and last keys pressed
last_played = None
last_pressed = []

while True:
    # Always remember to call keybow.update()!
    keybow.update()

    # If any keys are pressed, go through shenanigans
    if keybow.any_pressed():
        # Fetch a list of pressed keys
        pressed = keybow.get_pressed()

        # If the keys pressed have changed...
        if pressed != last_pressed:
            # Keys that were pressed, but are no longer
            missing = [k for k in last_pressed if k not in pressed]

            # Any keys that were pressed, but are no longer, turn LED off
            # and send MIDI note off for the respective note.
            for k in missing:
                note = start_note +k
                midi.send(NoteOff(note, 0))
                keys[k].set_led(0, 0, 0)

            # Calculate MIDI note numbers
            notes = [start_note + k for k in pressed]
            last_pressed = pressed

            # If going forward (up or starting up-down), start at 0,
            # otherwise start at the end of the list of notes.
            if arp_style == 0 or arp_style == 2:
                this_note = 0
            elif arp_style == 1:
                this_note = len(notes) - 1

            # Send MIDI note on message for current note and turn LED on
            midi.send(NoteOn(notes[this_note], velocity))
            keys[pressed[this_note]].set_led(*rgb)

            # Update last_played time, set elapsed to 0, and update current and
            # last note indices.
            last_played = time.monotonic()
            elapsed = 0
            last_note = this_note
            this_note += direction

        # If the currently pressed notes are the same as the last loop, then...
        else:
            if notes != []:
                # Check time elapsed since last note played
                elapsed = time.monotonic() - last_played

                # If the note time has elapsed, then...
                if elapsed > note_time:
                    # Reset at the end or start of the notes list
                    if this_note == len(notes) and direction == 1:
                        this_note = 0
                    elif this_note < 0:
                        this_note = len(notes) - 1

                    # Send a MIDI note off for the last note, turn off LED
                    midi.send(NoteOff(notes[last_note], 0))
                    keys[pressed[last_note]].set_led(0, 0, 0)

                    # Send a MIDI note on for the next note, turn on LED
                    midi.send(NoteOn(notes[this_note], velocity))
                    keys[pressed[this_note]].set_led(*rgb)

                    # Update time last_played, make this note last note
                    last_played = time.monotonic()
                    last_note = this_note

                    # For the up-down style, switch direction at either end
                    if arp_style == 2 and this_note == len(notes) -1:
                        direction = -1
                    elif arp_style == 2 and this_note == 0:
                        direction = 1

                    # Increment note
                    this_note += direction

    # If nothing is now pressed, but was last time, then send MIDI  note off
    # for every note, and turn all the LEDs off.
    elif len(last_pressed) and keybow.none_pressed():
        for note in range(128):
            midi.send(NoteOff(note, 0))
        for key in keys:
            key.set_led(0, 0, 0)

        # Nothing is pressed, so reset last_pressed list
        last_pressed = []