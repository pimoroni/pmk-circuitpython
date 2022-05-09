# PMK - Pimoroni Mechanical/Mushy Keypad - CircuitPython <!-- omit in toc -->

The library abstracts away most of the complexity of having to check pin states,
and interact with the LED driver library, and exposes classes for
individual keys and the whole PMK class (a collection of Key instances).

## Supported Devices

* The [RP2040-powered Keybow 2040 from Pimoroni](https://shop.pimoroni.com/products/keybow-2040),
a 16-key mini mechanical keyboard with RGB backlit keys.
* A Raspberry Pi Pico mounted on the [RGB Keypad Base from Pimoroni](https://shop.pimoroni.com/products/pico-rgb-keypad-base)
a 16-key mini rubber keyboard with RGB backlit keys.

![Keybow 2040 with backlit keys on marble background](keybow-2040-github-1.jpg)

# Index <!-- omit in toc -->

- [Getting started quickly!](#getting-started-quickly)
  - [Preparing Your Device](#preparing-your-device)
    - [Keybow 2040](#keybow-2040)
    - [Pico RGB Keypad](#pico-rgb-keypad)
  - [Installing PMK](#installing-pmk)
- [Library functionality](#library-functionality)
  - [Imports and setup](#imports-and-setup)
  - [The PMK class](#the-pmk-class)
  - [An interlude on timing!](#an-interlude-on-timing)
  - [Key presses](#key-presses)
    - [PMK class methods for detecting presses and key states](#pmk-class-methods-for-detecting-presses-and-key-states)
    - [Key class methods for detecting key presses](#key-class-methods-for-detecting-key-presses)
  - [LEDs!](#leds)
  - [LED sleep](#led-sleep)
  - [Attaching functions to keys with decorators](#attaching-functions-to-keys-with-decorators)
  - [Key combos](#key-combos)
- [USB HID](#usb-hid)
  - [Setup](#setup)
  - [Sending key presses](#sending-key-presses)
  - [Sending strings of text](#sending-strings-of-text)
- [USB MIDI](#usb-midi)
  - [Setup](#setup-1)
  - [Sending MIDI notes](#sending-midi-notes)

# Getting started quickly!

For a more verbose installation guide with screenshots, check out our Learn guide:

[CircuitPython and Keybow 2040](https://learn.pimoroni.com/article/circuitpython-and-keybow-2040)

## Preparing Your Device

### Keybow 2040

You'll need to grab the latest version of Adafruit's Keybow 2040-flavoured
CircuitPython, from the link below.

[Download the Adafruit CircuitPython binary for Keybow 2040](https://circuitpython.org/board/pimoroni_keybow2040/)

Unplug your Keybow 2040's USB-C cable, press and hold the BOOTSEL button while plugging the USB-C cable back into your computer to mount
it as a drive (it should show up as `RPI-RP2` or something similar). The BOOTSEL button is to the right of the USB-C port, assuming your Keybow is oriented with keys pointing upwards and with the USB-C port at the top edge.

Drag and drop the `adafruit-circuitpython-pimoroni_keybow2040-en_US-XXXXX.uf2`
file that you downloaded onto the drive and it should reboot and load the
CircuitPython firmware. The drive should now show up as `CIRCUITPY`.

The Adafruit IS31FL3731 LED driver library for CircuitPython is a prerequisite for
this Keybow 2040 library, so you'll need to download it from GitHub at the link
below, and then drop the `adafruit_is31fl3731` folder into the `lib` folder on
your `CIRCUITPY` drive.

[Download the Adafruit IS31FL3731 CircuitPython library](https://github.com/adafruit/Adafruit_CircuitPython_IS31FL3731)

### Pico RGB Keypad

You'll need to grab the latest version of Adafruit's Raspberry Pi Pico-flavoured
CircuitPython, from the link below.

[Download the Adafruit CircuitPython binary for Raspberry Pi Pico](https://circuitpython.org/board/raspberry_pi_pico/)

Unplug your Pi Pico's micro USB cable, press and hold the BOOTSEL button on the top
of Pi Pico while plugging the micro USB cable back into your computer to mount
it as a drive (it should show up as `RPI-RP2` or something similar).

Drag and drop the `adafruit-circuitpython-raspberry_pi_pico-en_US-XXXXX.uf2`
file that you downloaded onto the drive and it should reboot and load the
CircuitPython firmware. The drive should now show up as `CIRCUITPY`.

The Adafruit DotStar LED driver library for CircuitPython is a prerequisite for
this Keybow 2040 library, so you'll need to download it from GitHub at the link
below, and then drop the `adafruit_dotstar.py` file into the `lib` folder on
your `CIRCUITPY` drive.

[Download the Adafruit DotStar CircuitPython library](https://github.com/adafruit/Adafruit_CircuitPython_DotStar)

## Installing PMK

Drop the `lib` contents (the `pmk` folder) from this library into the `lib` folder
on your `CIRCUITPY` drive also, and you're all set!

Pick one of the [examples](examples) (I'd suggest the
[reactive.press.py](examples/reactive-press.py) example to begin), copy the
code, and save it in the `code.py` file on your `CIRCUITPY` drive using your
favourite text editor. As soon as you save the `code.py` file, or make any other
changes, then it should load up and run the code!

Examples are by default using Keybow 2040 hardware, if you want to run them
on Pico RGB Keypad, you need to change the hardware. Comment out the line:

```
from pmk.platform.keybow2040 import Keybow2040 as Hardware
```

and uncomment the line:

```
from pmk.platform.rgbkeypadbase import RGBKeypadBase as Hardware
```

# Library functionality

This section covers most of the functionality of the library itself, without
delving into additional functions like USB MIDI or HID (they're both covered
later!)

## Imports and setup

All of your programs will need to start with the following:

```python
from pmk.platform.keybow2040 import Keybow2040 as Hardware
from pmk import PMK

hardware = Hardware()
pmk = PMK(hardware)
```

First, this imports a hardware object representing the board. A hardware object
hides technical details on how keys and LEDs are connected and exposes them
via uniform interface. You need to choose the correct hardware object for
your hardware. If you're curious, hardware differences are explained below,
but all you need to know is that for Keybow 2040 you need an import:

```python
from pmk.platform.keybow2040 import Keybow2040 as Hardware
```

and for Pico RGB Keypad Base:

```python
from pmk.platform.rgbkeypadbase import RGBKeypadBase as Hardware
```

On Keybow 2040 (`Keybow2040`) keys are read directly via GPIO, and LEDs are set
via IS31FL3731 LED driver connected over I2C bus.

On Pico RGB Keypad Base (`RGBKeypadBase`) keys are connected via TCA9555 GPIO extender
connected over I2C bus and LEDs are DotStar LEDs connected via SPI bus.

Since both boards use I2C bus, hardware object also exposes it in case you
need to access it (Keybow 2040 has even I2C connecting pads exposed):
i2c = hardware.i2c()

In the rest of this file examples of the code will use `Keybow2040` hardware object.
If you're running them on Pico RGB Keypad Base, don't forget to change it accordingly.

The `PMK()` class, imported from the `pmk` module, is instantiated
and passed the hardware object. Instantiating this sets up all of the pins, keys,
and LEDs, and provides access to all of the attributes and methods associated
with it.

## The PMK class

The PMK class exposes a number of handy attributes and methods. The main one
you'll be interested in is the `.keys` attribute, which is a list of `Key`
class instances, one for each key.

```python
keys = pmk.keys
```

The indices of the keys in that list correspond to their position on the keypad,
staring from the bottom left corner (when the USB connector is at the top),
which is key 0, going upwards in columns, and ending at the top right corner,
which is key 15.

More about the `Key` class later...

A **super** important method of the `PMK` class is `.update()` method. It
updates all of the keys, key states, and other attributes like the time of the
last key press, and sleep state of the LEDs.

**You need to call this method on your `PMK` class at the very start of each
iteration of your program's main loop, as follows:**

```python
while True:
    pmk.update()
```

## An interlude on timing!

Another **super** important thing is **not to include any `time.sleep()`s in
your main loop!** Doing so will ruin the latency and mean that you'll miss key
press events. Just don't do it.

If you need introduce timed events, then you have to go about it in a slightly
(!!) roundabout fashion, by using `time.monotonic()` a constantly incremented
count of seconds elapsed, and use it to check the time elapsed since your last
event, for example you could do this inside your `while True` loop:

```python
time_interval = 10

# An event just happened!

time_last_fired = time.monotonic()
time_elapsed = 0

# ... some iterations later

time_elapsed = time.monotonic() - time_last_fired

if time_elapsed > time_interval:
    # Fire your event again!
```

There's a handy `pmk.time_of_last_press` attribute that allows you to quickly
check if a certain amount of time has elapsed since any key press, and that
attribute gets updated every time `pmk.update()` is called.

## Key presses

There are a few ways that you can go about detecting key presses, some
global methods on the `PMK` class instance, and some on the `Key` class
instances themselves.

### PMK class methods for detecting presses and key states

`pmk.get_states()` will return a list of the state of all of the keys, in
order, with a state of `0` being not pressed, and `1` being pressed. You can
then loop through that list to do whatever you like.

`pmk.get_pressed()` will return a list of the key numbers (indices in the
list of keys) that are currently pressed. If you only care about key presses,
then this is an efficient way to do things, especially since you have all the
key numbers in a list.

`pmk.any_pressed()` returns a Boolean (`True`/`False`) that tells you whether
any keys are currently being pressed. Handy if you want to attach a behaviour to
all of the keys, which this is effectively a proxy for.

`pmk.none_pressed()` is similar to `.any_pressed()`, in that it returns a
Boolean also, but... you guessed it, it returns `True` if no keys are being
pressed, and `False` if any keys are pressed.

### Key class methods for detecting key presses

If we want to check whether key 0 is pressed, we can do so as follows:

```python
keys = pmk.keys()

while True:
    pmk.update()

    if keys[0].pressed:
        # Do something!
```

The `.pressed` attribute returns a Boolean that is `True` if the key is pressed
and `False` if it is not pressed.

`key.state` is another way to check the state of a key. It will equal `1` if the
key is pressed and `0` if it is not pressed.

If you want to attach an additional behaviour to your key, you can use
`key.held` to check if a key is being key rather than being pressed and released
quickly. It returns `True` if the key is held and `False` if it is not.

The default hold time (after which `key.held` is `True`) for all of the keys is
0.75 seconds, but you can change `key.hold_time` to adjust this to your liking,
on a per key basis.

This means that we could extend the example above to be:

```python
keys = pmk.keys()

while True:
    pmk.update()

    if keys[0].pressed:
        # Do something!

    if keys[0].held:
        # Do something else!
```

The [reactive-press.py example](examples/reactive-press.py) shows in more detail
how to handle key presses.

## LEDs!

LEDs can be set either globally for all keys, using the `PMK` class instance,
or on a per-key basis, either through the `PMK` class, or using a `Key` class
instance.

To set all of the keys to the same colour, you can use the `.set_all()` method
of the `PMK` class, to which you pass three 0-255 integers for red, green,
and blue. For example, to set all of the keys to magenta:

```
pmk.set_all(255, 0, 255)
```

To set an individual key through your `PMK` class instance, you can do as
follows, to set key 0 to white:

```
pmk.set_led(0, 255, 255, 255)
```

To set the colour on the key itself, you could do as follows, again to set key
0 to white:

```
pmk.keys[0].set_led(255, 255, 255)
```

A key retains its RGB value, even if it is turned off, so once a key has its
colour set with `key.rgb = (255, 0, 0)` for example, you can turn it off using
`key.led_off()` or even `key.set_led(0, 0, 0)` and then when you turn it back on
with `key.led_on()`, then it will still be red when it comes back on.

As a convenience, and to avoid having to check `key.lit`, there is a
`key.toggle_led()` method that will toggle the current state of the key's LED
(on to off, and _vice versa_).

There's a handy `hsv_to_rgb()` function that can be imported from the
`pmk` module to convert an HSV colour (a tuple of floats from 0.0 to 1.0)
to an RGB colour (a tuple of integers from 0 to 255), as follows:

```
from pmk import hsv_to_rgb

h = 0.5  # Hue
s = 1.0  # Saturation
v = 1.0  # Value

r, g, b = hsv_to_rgb(h, s, v)
```

The [rainbow.py example](examples/rainbow.py) shows a more complex example of
how to animate the keys' LEDs, including the use of the `hsv_to_rgb()` function.

## LED sleep

The `PMK` class has an `.led_sleep_enabled` attribute that is disabled (set to
`False`) by default, and an `.led_sleep_time` attribute (set to 60 seconds by
default) that determines how many seconds need to elapse before LED sleep is
triggered and the LEDs turn off.

The time elapsed since the last key press is constantly updated when
`pmk.update()` is called in your main loop, and if the `.led_sleep_time` is
exceeded then LED sleep is triggered.

Because keys retain their RGB values when toggled off, when asleep, a tap on any
key will wake all of the LEDs up at their last state before sleep.

Enabling LED sleep with a sleep time of 10 seconds could be done as simply as:

```python
pmk.led_sleep_enabled = True
pmk.led_sleep_time = 10
```

There's also a `.sleeping` attribute that returns a Boolean, that you can check
to see whether the LEDs are sleeping or not.

## Attaching functions to keys with decorators

There are three decorators that can be attached to functions to link that
function to, i) a key press, ii) a key release, or iii) a key hold.

Here's an example of how you could attach a decorator to a function that lights
up that key yellow when it is pressed, turns all of the LEDs on when held, and
turns them all off when released:

```python
from pmk.platform.keybow2040 import Keybow2040 as Hardware
from pmk import PMK

pmk = PMK(Hardware())
keys = pmk.keys

key = keys[0]
rgb = (255, 255, 0)
key.rgb = rgb

@pmk.on_press(key)
def press_handler(key):
    key.led_on()

@pmk.on_release(key)
def release_handler(key):
    pmk.set_all(0, 0, 0)

@pmk.on_hold(key)
def hold_handler(key):
    pmk.set_all(*rgb)

while True:
    pmk.update()
```

The [decorators.py example](examples/decorators.py) has another example of how
to use the `.on_hold()` decorator to toggle LEDs on and off when a key is held.

## Key combos

Key combos can provide a way to add additional behaviours to keys that only get
triggered if a combination of keys is pressed. The best way to achieve this is
using the `.held` attribute of a key, meaning that the key can also have a
`.pressed` behaviour too.

Here's a brief example of how you could do this inside your main loop, with key
0 as the modifier key, and key 1 as the action key:

```
keys = pmk.keys

modifier_key = keys[0]
action_key = keys[1]

while True:
    pmk.update()

    if modifier_key.held and action_key.pressed:
        # Do something!
```

Of course, you could chain these together, to require two modifer keys to be
held and a third to be pressed, and so on...

The [colour-picker.py example](examples/colour-picker.py) has an example of
using a modifier key to change the hue of the keys.

# USB HID

This covers setting up a USB HID keyboard and linking physical key presses to
keyboard key presses on a connected computer.

## Setup

USB HID requires the `adafruit_hid` CircuitPython library. Download it from the
link below and drop the `adafruit_hid` folder into the `lib` folder on your
`CIRCUITPY` drive.

[Download the Adafruit HID CircuitPython library](https://github.com/adafruit/Adafruit_CircuitPython_HID)

You'll need to connect your Keybow or Pico + RGB Keypad  Base to a computer using a USB cable, just like
you would with a regular USB keyboard.

## Sending key presses

Here's an example of setting up a keyboard object and sending a `0` key press
when key 0 is pressed, using an `.on_press()` decorator:

```python
from pmk.platform.keybow2040 import Keybow2040 as Hardware
from pmk import PMK

import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
from adafruit_hid.keycode import Keycode

pmk = PMK(Hardware())
keys = pmk.keys

keyboard = Keyboard(usb_hid.devices)
layout = KeyboardLayoutUS(keyboard)

key = keys[0]

@pmk.on_press(key)
def press_handler(key):
    keyboard.send(Keycode.ZERO)

while True:
    pmk.update()
```

You can find a list of all of the keycodes available at the
[HID CircuitPython library documentation here](https://circuitpython.readthedocs.io/projects/hid/en/latest/api.html#adafruit-hid-keycode-keycode).

If you wanted to take this a bit further and make a full keymap for your
keyboard, then you could create a list of 16 different keycodes and then use the
number of the key press registered by the `press_handler` function as an index
into your keymap to get the keycode to send for each key.

```python
from pmk.platform.keybow2040 import Keybow2040 as Hardware
from pmk import PMK

import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
from adafruit_hid.keycode import Keycode

pmk = PMK(Hardware())
keys = pmk.keys

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
    @pmk.on_press(key)
    def press_handler(key):
        keycode = keymap[key.number]
        keyboard.send(keycode)

while True:
    pmk.update()
```

This code is available in the
[hid-keys-simple.py example](examples/hid-keys-simple.py).

As well as sending a single keypress, you can send multiple keypresses at once,
simply by adding them as additional arguments to `keyboard.send()`, e.g.
`keyboard.send(Keycode.A, Keycode.B)` and so on.

## Sending strings of text

Rather than the inconvenience of sending multiple keycodes using
`keyboard.send()`, there's a different method to send whole strings of text at
once, using the `layout` object we created.

```python
from pmk.platform.keybow2040 import Keybow2040 as Hardware
from pmk import PMK

import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
from adafruit_hid.keycode import Keycode

pmk = PMK(Hardware())
keys = pmk.keys

keyboard = Keyboard(usb_hid.devices)
layout = KeyboardLayoutUS(keyboard)

key = keys[0]

@pmk.on_press(key)
def press_handler(key):
    layout.write("Pack my box with five dozen liquor jugs.")

while True:
    pmk.update()
```

A press of key 0 will send that whole string of text at once!

Be aware that strings sent like that take a little while to  virtually "type",
so you might want to incorporate a delay using  `pmk.time_of_last_press`,
and then check against a `time_elapsed` variable created with
`time_elapsed = time.monotonic() - pmk.time_of_last_press`.

Also, be aware that the Adafruit HID CircuitPython library only currently
supports US Keyboard layouts, so you'll have to work around that and map any
keycodes that differ from their US counterpart to whatever your is.

# USB MIDI

This covers basic MIDI note messages and how to link them to key presses.

## Setup

USB MIDI requires the `adafruit_midi` CircuitPython library. Download it from
the link below and then drop the `adafruit_midi` folder into the `lib` folder on
your `CIRCUITPY` drive.

[Download the Adafruit MIDI CircuitPython library](https://github.com/adafruit/Adafruit_CircuitPython_MIDI)

You'll need to connect your Keybow 2040 with a USB cable to a computer running a
software synth or DAW like Ableton Live, to a hardware synth that accepts USB
MIDI, or through a MIDI interface that will convert the USB MIDI messages to
regular serial MIDI through a DIN connector.

Using USB MIDI, Keybow 2040 shows up as a device with the name
`Keybow 2040 (CircuitPython usb midi.ports[1])`

In my testing, Keybow 2040 works with the Teenage Engineering OP-Z quite nicely.

## Sending MIDI notes

Here's a complete, minimal example of how to send a single MIDI note (middle C,
or MIDI note number 60) when key 0 is pressed, sending a note on message when
pressed and a note off message when released.

```python
from pmk.platform.keybow2040 import Keybow2040 as Hardware
from pmk import PMK

import usb_midi
import adafruit_midi
from adafruit_midi.note_off import NoteOff
from adafruit_midi.note_on import NoteOn

pmk = PMK(Hardware())
keys = pmk.keys

midi = adafruit_midi.MIDI(midi_out=usb_midi.ports[1], out_channel=0)

key = keys[0]
note = 60
velocity = 127

was_pressed = False

while True:
    pmk.update()

    if key.pressed:
        midi.send(NoteOn(note, velocity))
        was_pressed = True
    elif not key.pressed and was_pressed:
        midi.send(NoteOff(note, 0))
        was_pressed = False
```

There'a more complete example of how to set up all of Keybow's keys with
associated MIDI notes using decorators in the
[midi-keys.py example](examples/midi-keys.py).

The example above, and the `midi-keys.py` example both send notes on MIDI
channel 0 (all channels), but you can set this to a specific channel, if you
like, by changing `out_channel=` when you instantiate your `midi` object.
