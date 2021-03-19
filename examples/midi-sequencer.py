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
# keys on the row above. The currently focussed track's track select key (on the
# second bottom row) is highlighted in a brighter colour.

# A track can be toggled on or off (no notes are sent from that track, but notes
# are not deleted) by tapping the track's track select key. The track select LED
# for a track toggled off will not be lit.

# The sequencer is started and stopped by tapping the bottom right key, which is
# red when the sequencer is stopped, and green when it is playing.

# The sequencer can be cleared by holding the track selector key (orange, bottom
# left) and then holding the start/stop key (red/green, bottom right).

# A single track can be cleared by holding the track selector key, the track
# select key (on the second bottom row) for the track you want to clear, and
# then holding the start/stop key.

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

# Tracks' notes are sent on MIDI channels 1-4.

# Drop the keybow2040.py file into your `lib` folder on your `CIRCUITPY` drive,
# and then save this code in the `code.py` file.

# NOTE! Requires the adafruit_midi CircuitPython library also!

import time
import board
from keybow2040 import Keybow2040

import usb_midi
import adafruit_midi
from adafruit_midi.note_off import NoteOff
from adafruit_midi.note_on import NoteOn


## CONSTANTS. Change these to change the look and feel of the sequencer.

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
HIGH_BRIGHTNESS = 1.0
MID_BRIGHTNESS = 0.2
LOW_BRIGHTNESS = 0.05

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

        # These keys select and change the current track.
        self.track_select_keys = []

        for i in range(len(TRACK_SELECTOR_KEYS)):
            track_select_key = self.keys[TRACK_SELECTOR_KEYS[i]]
            track_select_key.rgb = TRACK_COLOURS[i]
            self.track_select_keys.append(track_select_key)

        self.track_select_keys_held = [False, False, False, False]
        self.track_select_active = False

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
        self.start_stop_held = False

        # The track selector key.
        self.track_selector = self.keys[TRACK_SELECTOR]
        self.track_selector.set_led(*TRACK_SELECTOR_COLOUR)

        # Set the key hold time for all the keys. A little shorter than the 
        # default for Keybow. Makes controlling the sequencer a bit more fluid.
        for key in self.keys:
            key.hold_time = KEY_HOLD_TIME

        # Attach step_select function to keys in track steps. If pressed it
        # toggles the state of the step.
        for key in self.track_keys:
            @self.on_release(key)
            def step_select(key):
                if self.tracks[self.current_track].active:
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

                        self.update_track_select_keys(True)

            # When step held, toggle on the note and velocity up/down keys.
            @self.on_hold(key)
            def step_change(key):
                if self.tracks[self.current_track].active:
                    self.steps_held.append(key.index)
                    self.note_down.set_led(*NOTE_DOWN_COLOUR)
                    self.note_up.set_led(*NOTE_UP_COLOUR)
                    self.velocity_down.set_led(*VELOCITY_DOWN_COLOUR)
                    self.velocity_up.set_led(*VELOCITY_UP_COLOUR)

                self.update_track_select_keys(False)

        # Attach hold function to track selector key that sets it active and
        # lights the track select keys.
        @self.on_hold(self.track_selector)
        def track_selector_hold(key):
            self.track_select_active = True

            for track in self.tracks:
                track.update_track_select_key = True

        # Attach release function to track selector key that sets it inactive
        # and turns track select LEDs off.
        @self.on_release(self.track_selector)
        def track_selector_release(key):
            self.track_select_active = False
            self.update_track_select_keys(True)

        # Handles track select/mute, tempo down/up, note down/up.
        #
        # If the tempo selector key (second from left, blue, on the bottom row)
        # is held, pressing the tempo keys (the left two keys on the second
        # bottom row, lit blue and pink) shifts the tempo down or up by
        # 5 bpm each time it is pressed, with a lower limit of 5 BPM and upper
        # limit of 200 BPM.
        #
        # If notes are held, then the four track select keys allow the held 
        # notes MIDI note number to be shifted down/up (track select keys 0
        # and 1 respectively), or MIDI velocity to be shifted down/up (track
        # select keys 2 and 3 respectively).
        #
        # If the track selector is not held, tapping this track button toggles
        #the track on/off.
        for key in self.track_select_keys:

            @self.on_press(key)
            def track_select_press(key):
                index = TRACK_SELECTOR_KEYS.index(key.number)
                if self.track_select_active:
                    self.current_track = index
                elif self.tempo_select_active:
                    if index == 0:
                        if self.bpm > 5:
                            self.bpm -= 5
                    elif index == 1:
                        if self.bpm < 200:
                            self.bpm += 5
                elif len(self.steps_held):
                    for i in self.steps_held:
                        step = self.tracks[self.current_track].steps[i]
                        if index == 0 or index == 1:
                            step.last_notes.append(step.note)
                            step.note_changed = True
                            if index == 0:
                                if step.note > 0:
                                    step.note -= 1
                            elif index == 1:
                                if step.note < MAX_NOTE:
                                    step.note += 1
                        elif index == 2:
                            if step.velocity > 0 + VELOCITY_STEP:
                                step.velocity -= VELOCITY_STEP
                        elif index == 3:
                            if step.velocity <= MAX_VELOCITY - VELOCITY_STEP:
                                step.velocity += VELOCITY_STEP
                else:
                    self.tracks[index].active = not self.tracks[index].active
                    self.tracks[index].update_track_select_key = True

        # Handlers to hold held states of track select keys.
        for key in self.track_select_keys:
            @self.on_hold(key)
            def track_select_key_hold(key):
                index = TRACK_SELECTOR_KEYS.index(key.number)
                self.track_select_keys_held[index] = True

            @self.on_release(key)
            def track_select_key_release(key):
                index = TRACK_SELECTOR_KEYS.index(key.number)
                self.track_select_keys_held[index] = False

        # Attach press function to start/stop key that toggles whether the 
        # sequencer is running and toggles its colour between green (running)
        # and red (not running).
        @self.on_press(self.start_stop)
        def start_stop_toggle(key):
            if not self.track_select_active:
                if self.running:
                    self.running = False
                    key.set_led(*STOP_COLOUR)
                else:
                    self.running = True
                    key.set_led(*START_COLOUR)

        # Attach hold function, so that when the track selector key is held and
        # the start/stop key is also held, clear all of the steps on all of the
        # tracks. If a track select key is held, then clear just that track.
        @self.on_hold(self.start_stop)
        def start_stop_hold(key):
            self.start_stop_held = True

            if self.track_select_active:
                if not any(self.track_select_keys_held):
                    self.clear_tracks()
                    for track in self.tracks:
                        track.midi_panic()
                else:
                    for i, state in enumerate(self.track_select_keys_held):
                        if state:
                            self.tracks[i].clear_steps()

        @self.on_release(self.start_stop)
        def start_stop_release(key):
            self.start_stop_held = False

        # Attach hold function that lights the tempo down/up keys when the
        # tempo selector key is held.
        @self.on_hold(self.tempo_selector)
        def tempo_selector_hold(key):
            self.tempo_select_active = True
            self.tempo_down.set_led(*TEMPO_DOWN_COLOUR)
            self.tempo_up.set_led(*TEMPO_UP_COLOUR)
            self.track_select_keys[2].led_off()
            self.track_select_keys[3].led_off()
            self.update_track_select_keys(False)

        # Attach release function that furns off the tempo down/up LEDs.
        @self.on_release(self.tempo_selector)
        def tempo_selector_release(key):
            self.tempo_select_active = False
            self.tempo_down.led_off()
            self.tempo_up.led_off()
            self.update_track_select_keys(True)

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

                    # If track is not active, send note off for last note and this note.
                    else:
                        last_note = track.steps[self.last_step_num].note
                        this_note = track.steps[self.this_step_num].note
                        self.midi_channels[track.channel].send(NoteOff(last_note, 0))
                        self.midi_channels[track.channel].send(NoteOff(this_note, 0))

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

    def update_track_select_keys(self, state):
        # Updates all of the track select keys' states in one go.
        for track in self.tracks:
            track.update_track_select_key = state


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
        self.update_track_leds = False
        self.update_track_select_key = True
        self.select_key = self.sequencer.track_select_keys[self.index]

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

        r, g, b = TRACK_COLOURS[self.index]

        # Only update these keys if required, as it affects the BPM when 
        # constantly updating them. Light the focussed track in a bright colour.
        # Turn the LED off for tracks that aren't active.
        if self.update_track_select_key:
            if not self.sequencer.track_select_active:
                if self.active:
                    if not self.focussed:
                        r, g, b = rgb_with_brightness(r, g, b, brightness=LOW_BRIGHTNESS)
                        self.select_key.set_led(r, g, b)
                    else:
                        r, g, b = rgb_with_brightness(r, g, b, brightness=HIGH_BRIGHTNESS)
                        self.select_key.set_led(r, g, b)
                else:
                    self.select_key.led_off()
                self.update_track_select_key = False
            else:
                r, g, b = rgb_with_brightness(r, g, b, brightness=HIGH_BRIGHTNESS)
                self.select_key.set_led(r, g, b)
                self.update_track_select_key = False


    def update_steps(self):
        # Update a tracks steps.
        for step in self.steps:
            step.update()

    def clear_steps(self):
        # Clear a track's steps by setting them all to inactive.
        for step in self.steps:
            step.active = False

    def midi_panic(self):
        # Send note off messages for every note on this track's channel.
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
                if self.track.active:
                    # Make an active step that is currently being played full
                    # brightness.
                    if self.playing and self.active:
                        self.set_led(r, g, b, HIGH_BRIGHTNESS)

                    # Make an inactive step that is "playing" (the current step)
                    # the dimmest brightness, but bright enough to indicate the
                    # step the sequencer is on.
                    if self.playing and not self.active:
                        self.set_led(r, g, b, LOW_BRIGHTNESS)

                    # Make an active step that is not playing a low-medium 
                    # brightness to indicate that it is toggled active.
                    if not self.playing and self.active:
                        self.set_led(r, g, b, MID_BRIGHTNESS)

                    # Turn not playing, not active steps off.
                    if not self.playing and not self.active:
                        self.set_led(0, 0, 0, 0)
                else:
                    self.set_led(0, 0, 0, 0)

            # If the sequencer is not running, still show the active steps.
            elif not self.sequencer.running:
                if self.active:
                    self.set_led(r, g, b, 0.3)
                else:
                    self.set_led(0, 0, 0, 0)


def rgb_with_brightness(r, g, b, brightness=1.0):
    # Allows an RGB value to be altered with a brightness
    # value from 0.0 to 1.0.
    r, g, b = (int(c * brightness) for c in (r, g, b))
    return r, g, b


# Set up Keybow's I2C bus.
i2c = board.I2C()

# Instantiate the sequencer.
sequencer = Sequencer(i2c)

while True:
    # Always remember to call sequencer.update() on every iteration of the main
    # loop, otherwise NOTHING WILL WORK!
    sequencer.update()