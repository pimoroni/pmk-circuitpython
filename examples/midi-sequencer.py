# SPDX-FileCopyrightText: 2021 Sandy Macdonald
#
# SPDX-License-Identifier: MIT

# A MIDI step sequencer, with four tracks and eight steps per track.

# The eight steps are on the top two rows of keys. Steps can be toggled on by 
# tapping a step's key. Active steps are indicated with a brighter LED, and the
# currently playing step in the sequence is shown with a moving LED across the
# eight steps.

# Each track is colour-coded: track 1 is orange, track 2 blue, track 3 is pink,
# and track 4 is green. Tracks can be selected by pressing and holding the 
# bottom left orange track select key and then tapping one of the four track
# keys on the row above.

# The sequencer is started and stopped by tapping the bottom right key, which is
# red when the sequencer is stopped, and green when it is playing.

# The sequencer can be cleared by holding the track selector key (orange, bottom
# left) and then holding the start/stop key (red/green, bottom right).

# Tempo can be increased or decreased by holding the tempo selector key (blue,
# second from left, on the bottom row) and then tapping blue key on the row 
# above to shift tempo down, or the pink key to shift it up. Tempo is increased/
# decreased by 5 BPM on each press.

# If an active step is held down, the second bottom row of keys lights to allow
# the note to be shifted down/up (the left two keys, decremented/incremented by
# one each time) and the note velocity to be shifted down/up (the right two keys
# decremented/incremented by four each time).

# You'll need to connect Keybow 2040 to a computer running a DAW like Ableton,
# or other software synth, or to a hardware synth that accepts USB MIDI.

# Currently, all of the notes are C3 with a velocity of 127.

# Tracks' notes are sent on MIDI channels 1-4.

# Drop the keybow2040.py file into your `lib` folder on your `CIRCUITPY` drive,
# and then save this code in the `code.py` file 

# NOTE! Requires the adafruit_midi CircuitPython library also!

import time
import board
from keybow2040 import Keybow2040

import usb_midi
import adafruit_midi
from adafruit_midi.note_off import NoteOff
from adafruit_midi.note_on import NoteOn

# These are the key numbers that represent each step in a track (the top two
# rows of four keys)
TRACK_KEYS = [3, 7, 11, 15, 2, 6, 10, 14]

ORANGE = (255, 255, 0)
BLUE = (0, 255, 175)
PINK = (255, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# The colours for the LEDs on each track: orange, blue, pink, green
TRACK_COLOURS = [ORANGE, BLUE, PINK, GREEN]

# The MIDI channels for each track in turn: 1, 2, 3, 4
MIDI_CHANNELS = [0, 1, 2, 3]

# The bottom left key, orange. When pressed, it brings up the track selector
# keys, the four keys on the row above it.
TRACK_SELECTOR = 0
TRACK_SELECTOR_KEYS = [1, 5, 9, 13]
TRACK_SELECTOR_COLOUR = ORANGE

# The bottom right key. When pressed, it toggles the sequencer on or off. Green
# indicates that it is currently playing, red that it is stopped.
START_STOP = 12
START_COLOUR = GREEN
STOP_COLOUR = RED

# The key second from left on the bottom row, blue. When pressed, it brings up
# the tempo down/up buttons on the row above it. The left blue key shifts the 
# tempo down, the right pink key shifts the tempo up.
TEMPO_SELECTOR = 4
TEMPO_SELECTOR_COLOUR = BLUE
TEMPO_DOWN = 1
TEMPO_DOWN_COLOUR = BLUE
TEMPO_UP = 5
TEMPO_UP_COLOUR = PINK

NOTE_DOWN = 1
NOTE_DOWN_COLOUR = BLUE
NOTE_UP = 5
NOTE_UP_COLOUR = PINK

# When an active step is held down, the second bottom row of keys lights to
# allow the note to be shifted down/up (the left two keys) and the note velocity
# to be shifted down/up (the right two keys).
VELOCITY_DOWN = 9
VELOCITY_DOWN_COLOUR = BLUE
VELOCITY_UP = 13
VELOCITY_UP_COLOUR = PINK

# The default starting BPM.
BPM = 85
MAX_BPM = 200

# Dictates the time after which a key is "held".
KEY_HOLD_TIME = 0.25

# LED brightness settings for the track steps.
PLAY_BRIGHTNESS = 1.0
ACTIVE_BRIGHTNESS = 0.2
STEP_BRIGHTNESS = 0.05

# Start on middle C and a reasonably high velocity.
DEFAULT_NOTE = 60
DEFAULT_VELOCITY = 99
MAX_VELOCITY = 127
MAX_NOTE = 127
VELOCITY_STEP = 4

class Sequencer(Keybow2040):
    """
    Represents the sequencer, with a set of Track instances, which in turn have
    a set of Step instances. This class is a subclass of the Keybow2040 class,
    so it inherits all of its methods and key methods.

    :param i2c: the I2C bus for Keybow 2040
    """
    def __init__(self, *args, **kwargs):
        super(Sequencer, self).__init__(*args, **kwargs)

        # Holds the list of MIDI channels for the tracks.
        self.midi_channels = []

        # Set the MIDI channels up.
        for channel in MIDI_CHANNELS:
            midi = adafruit_midi.MIDI(midi_out=usb_midi.ports[1], out_channel=channel)
            self.midi_channels.append(midi)

        # These keys represent the steps on the tracks.
        self.track_keys = []

        for i in range(len(TRACK_KEYS)):
            track_key = self.keys[TRACK_KEYS[i]]
            track_key.index = i
            self.track_keys.append(track_key)

        # Holds the list of tracks, a set of Track instances.
        self.tracks = []

        # Set the tracks up.
        for i in range(4):
            track = Track(self, i, i, TRACK_COLOURS[i])
            self.tracks.append(track)

        # Speed attributes.
        self.bpm = BPM
        self.tempo_selector = self.keys[TEMPO_SELECTOR]
        self.tempo_selector.set_led(*TEMPO_SELECTOR_COLOUR)
        self.tempo_select_active = False
        self.tempo_down = self.keys[TEMPO_DOWN]
        self.tempo_up = self.keys[TEMPO_UP]

        # Step related stuff
        self.num_steps = 8
        self.this_step_num = 0
        self.last_step_num = 0
        self.steps_held = []

        # Note change  attributes.
        self.note_down = self.keys[NOTE_DOWN]
        self.note_up = self.keys[NOTE_UP]
        self.velocity_down = self.keys[VELOCITY_DOWN]
        self.velocity_up = self.keys[VELOCITY_UP]

        # Is the sequencer running?
        self.running = False

        # Step time assumes the BPM is based on quarter notes.
        self.step_time = 60.0 / self.bpm / (self.num_steps / 2)
        self.last_step_time = time.monotonic()

        # Set the default starting track to track 0
        self.current_track = 0

        # The start stop key.
        self.start_stop = self.keys[START_STOP]
        self.start_stop.set_led(*STOP_COLOUR)

        # The track selector key.
        self.track_selector = self.keys[TRACK_SELECTOR]
        self.track_selector.set_led(*TRACK_SELECTOR_COLOUR)
        self.track_selector_active = False

        # These keys select and change the current track.
        self.track_select_keys = []

        for i in range(len(TRACK_SELECTOR_KEYS)):
            track_select_key = self.keys[TRACK_SELECTOR_KEYS[i]]
            track_select_key.rgb = TRACK_COLOURS[i]
            self.track_select_keys.append(track_select_key)

        # Set the key hold time for all the keys. A little shorter than the 
        # default for Keybow. Makes controlling the sequencer a bit more fluid.
        for key in self.keys:
            key.hold_time = KEY_HOLD_TIME

        # Attach step_select function to keys in track steps. If pressed it
        # toggles the state of the step.
        for key in self.track_keys:
            @self.on_release(key)
            def step_select(key):
                if not key.held:
                    step = self.tracks[self.current_track].steps[key.index]
                    step.toggle()
                    if not step.active:
                        current_note = step.note
                        self.midi_channels[track.channel].send(NoteOff(current_note, 0))
                        step.note = DEFAULT_NOTE
                        step.velocity = DEFAULT_VELOCITY
                else:
                    self.steps_held.remove(key.index)
                    self.note_down.led_off()
                    self.note_up.led_off()
                    self.velocity_down.led_off()
                    self.velocity_up.led_off()

            # When step held, toggle on the note and velocity up/down keys.
            @self.on_hold(key)
            def step_change(key):
                self.steps_held.append(key.index)
                self.note_down.set_led(*NOTE_DOWN_COLOUR)
                self.note_up.set_led(*NOTE_UP_COLOUR)
                self.velocity_down.set_led(*VELOCITY_DOWN_COLOUR)
                self.velocity_up.set_led(*VELOCITY_UP_COLOUR)

        # Attach hold function to track selector key that sets it active and
        # lights the track select keys.
        @self.on_hold(self.track_selector)
        def track_selector_hold(key):
            self.track_selector_active = True

            for k in range(len(self.track_select_keys)):
                key = self.track_select_keys[k]
                key.set_led(*TRACK_COLOURS[k])
                key.led_on()

        # Attach release function to track selector key that sets it inactive
        # and turns track select LEDs off.
        @self.on_release(self.track_selector)
        def track_selector_release(key):
            self.track_selector_active = False

            for key in self.track_select_keys:
                key.led_off()

        # Handles track 0 select, tempo down, note down.
        # Pressing the tempo down key shifts the tempo down by
        # 5 bpm each time it is pressed, with a lower limit of 5 BPM.
        # If notes are held, then tapping this key decrements the MIDI note 
        # number by one.
        @self.on_press(self.track_select_keys[0])
        def track_select_0_press(key):
            if self.track_selector_active:
                self.current_track = 0
            elif self.tempo_select_active:
                if self.bpm > 5:
                    self.bpm -= 5
            elif len(self.steps_held):
                for i in self.steps_held:
                    step = self.tracks[self.current_track].steps[i]
                    step.last_notes.append(step.note)
                    step.note_changed = True
                    if step.note > 0:
                        step.note -= 1

        # Handles track 1 select, tempo up, note up.
        # Pressing the tempo up key shifts the tempo up by
        # 5 bpm each time it is pressed, with an upper limit of 200 BPM.
        # If notes are held, then tapping this key increments the MIDI note 
        # number by one.
        @self.on_press(self.track_select_keys[1])
        def track_select_1_press(key):
            if self.track_selector_active:
                self.current_track = 1
            elif self.tempo_select_active:
                if self.bpm < 200:
                    self.bpm += 5
            elif len(self.steps_held):
                for i in self.steps_held:
                    step = self.tracks[self.current_track].steps[i]
                    step.last_notes.append(step.note)
                    step.note_changed = True
                    if step.note < MAX_NOTE:
                        step.note += 1

        # Handles track 2 select, velocity down.
        # If notes are held, then tapping this key decrements the velocity by
        # four.
        @self.on_press(self.track_select_keys[2])
        def track_select_2_press(key):
            if self.track_selector_active:
                self.current_track = 2
            elif len(self.steps_held):
                for i in self.steps_held:
                    step = self.tracks[self.current_track].steps[i]
                    if step.velocity > 0 + VELOCITY_STEP:
                        step.velocity -= VELOCITY_STEP

        # Handles track 3 select, velocity up.
        # If notes are held, then tapping this key increments the velocity by 
        # four.
        @self.on_press(self.track_select_keys[3])
        def track_select_3_press(key):
            if self.track_selector_active:
                self.current_track = 3
            elif len(self.steps_held):
                for i in self.steps_held:
                    step = self.tracks[self.current_track].steps[i]
                    if step.velocity <= MAX_VELOCITY - VELOCITY_STEP:
                        step.velocity += VELOCITY_STEP

        # Attach press function to start/stop key that toggles whether the 
        # sequencer is running and toggles its colour between green (running)
        # and red (not running).
        @self.on_press(self.start_stop)
        def start_stop_toggle(key):
            if not self.track_selector_active:
                if self.running:
                    self.running = False
                    key.set_led(*STOP_COLOUR)
                else:
                    self.running = True
                    key.set_led(*START_COLOUR)

        # Attach hold function, so that when the track selector key is held and
        # the start/stop key is also held, clear all of the steps on all of the
        # tracks.
        @self.on_hold(self.start_stop)
        def start_stop_hold(key):
            if self.track_selector_active:
                self.clear_tracks()
                for track in self.tracks:
                    track.midi_panic()

        # Attach hold function that lights the tempo down/up keys when the
        # tempo selector key is held.
        @self.on_hold(self.tempo_selector)
        def tempo_selector_hold(key):
            self.tempo_select_active = True
            self.tempo_down.set_led(*TEMPO_DOWN_COLOUR)
            self.tempo_up.set_led(*TEMPO_UP_COLOUR)
            self.track_select_keys[2].led_off()
            self.track_select_keys[3].led_off()

        # Attach release function that furns off the tempo down/up LEDs.
        @self.on_release(self.tempo_selector)
        def tempo_selector_release(key):
            self.tempo_select_active = False
            self.tempo_down.led_off()
            self.tempo_up.led_off()

    def update(self):
        # Update the superclass (Keybow2040).
        super(Sequencer, self).update()

        if self.running:
            # Keep track of current time.
            current_time = time.monotonic()

            # If a step has elapsed...
            if current_time - self.last_step_time > self.step_time:
                for track in self.tracks:
                    if track.active:
                        # Turn last step off.
                        last_step = track.steps[self.last_step_num]
                        last_step.playing = False
                        last_step.update()
                        last_note = last_step.note
 
                        # Helps prevent stuck notes.
                        if last_step.note_changed:
                            for note in last_step.last_notes:
                                self.midi_channels[track.channel].send(NoteOff(note, 0))
                            last_step.note_changed = False
                            last_step.last_notes = []

                        # If last step is active, send MIDI note off message.
                        if last_step.active:
                            self.midi_channels[track.channel].send(NoteOff(last_note, 0))

                        # Turn this step on.
                        this_step = track.steps[self.this_step_num]
                        this_step.playing = True
                        this_step.update()
                        this_note = this_step.note
                        this_vel = this_step.velocity

                        # Helps prevent stuck notes
                        if this_step.note_changed:
                            for note in this_step.last_notes:
                                self.midi_channels[track.channel].send(NoteOff(note, 0))
                            this_step.note_changed = False
                            this_step.last_notes = []

                        # If this step is active, send MIDI note on message.
                        if this_step.active:
                            self.midi_channels[track.channel].send(NoteOn(this_note, this_vel))

                # This step is now the last step!
                last_step = this_step
                self.last_step_num = self.this_step_num
                self.this_step_num += 1

                # If we get to the end of the sequence, go back to the start.
                if self.this_step_num == self.num_steps:
                    self.this_step_num = 0

                # Keep track of last step time.
                self.last_step_time = current_time

        # Update the tracks.
        for track in self.tracks:
            track.update()

        # Update the step_time, in case the BPM has been changed.
        self.step_time = 60.0 / self.bpm / (self.num_steps / 2)

    def clear_tracks(self):
        # Clears the steps on all tracks.
        for track in self.tracks:
            track.clear_steps()


class Track:
    """
    Represents a track on the sequencer.

    :param sequencer: the parent sequencer instance
    :param index: the index of the track, integer
    :param channel: the MIDI channel, integer
    :param rgb: the RGB colour of the track, tuple of R, G, B, 0-255.
    """
    def __init__(self, sequencer, index, channel, rgb):
        self.index = index
        self.rgb = rgb
        self.channel = channel
        self.steps = []
        self.sequencer = sequencer
        self.track_keys = self.sequencer.track_keys

        # For each key in the track, create a Step instance and add to 
        # self.steps.
        for i, key in enumerate(self.track_keys):
            step = Step(i, key, self)
            self.steps.append(step)

        # Default to having the track active.
        self.active = True
        self.focussed = False

    def set_on(self):
        # Toggle the track on.
        self.active = True

    def set_off(self):
        # Toggle the track off.
        self.active = False

    def update(self):
        # Make the current track focussed and update its steps.
        if sequencer.current_track == self.index:
            self.focussed = True
            self.update_steps()
        else:
            self.focussed = False

    def update_steps(self):
        # Update a tracks steps.
        for step in self.steps:
            step.update()

    def clear_steps(self):
        # Clear a track's steps by setting them all to inactive.
        for step in self.steps:
            step.active = False

    def midi_panic(self):
        for i in range(128):
            self.sequencer.midi_channels[self.channel].send(NoteOff(i, 0))


class Step:
    """
    Represents a step on a track.

    :param index: the index of the step, integer
    :param key: the key attached to this step, integer
    :param track: the track this step belongs to, Track instance.
    """
    def __init__(self, index, key, track):
        self.index = index
        self.key = key
        self.track = track
        self.active = False
        self.playing = False
        self.held = False
        self.velocity = DEFAULT_VELOCITY
        self.note = DEFAULT_NOTE
        self.last_notes = []
        self.note_changed = False
        self.rgb = self.track.rgb
        self.sequencer = self.track.sequencer

    def toggle(self):
        # Toggle the step between active and inactive.
        self.active = not self.active

    def state(self):
        # Returns the state of the track (active/inactve).
        return self.active

    def set_led(self, r, g, b, brightness):
        # Set the step's LED. Has an additional brightness parameter from 0.0
        # (off) to 1.0 (full brightness for the colour).
        r, g, b = [int(c * brightness) for c in (r, g, b)]
        self.key.set_led(r, g, b)

    def update(self):
        # Update the step. Pretty much just handles the LEDs.
        r, g, b = self.rgb

        # If this step's track is focussed...
        if self.track.focussed:
            # Only update the LEDs when the sequencer is running.
            if self.sequencer.running:
                # Make an active step that is currently being played full
                # brightness.
                if self.playing and self.active:
                    self.set_led(r, g, b, PLAY_BRIGHTNESS)

                # Make an inactive step that is "playing" (the current step)
                # the dimmest brightness, but bright enough to indicate the
                # step the sequencer is on.
                if self.playing and not self.active:
                    self.set_led(r, g, b, STEP_BRIGHTNESS)

                # Make an active step that is not playing a low-medium 
                # brightness to indicate that it is toggled active.
                if not self.playing and self.active:
                    self.set_led(r, g, b, ACTIVE_BRIGHTNESS)

                # Turn not playing, not active steps off.
                if not self.playing and not self.active:
                    self.set_led(0, 0, 0, 0)

            # If the sequencer is not running, still show the active steps.
            elif not self.sequencer.running:
                if self.active:
                    self.set_led(r, g, b, 0.3)
                else:
                    self.set_led(0, 0, 0, 0)

# Set up Keybow
i2c = board.I2C()

# Instatiate the sequencer.
sequencer = Sequencer(i2c)

while True:
    # Always remember to call sequencer.update() on every iteration of the main
    # loop, otherwise NOTHING WILL WORK!
    sequencer.update()