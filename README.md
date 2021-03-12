# Keybow 2040 CircuitPython

This CircuitPython library is for the RP2040-powered Keybow 2040 from Pimoroni,
a 16-key mini mechanical keyboard with RGB backlit keys. Find out more about 
Keybow 2040 at the link below.

[Learn more about Keybow 2040 at pimoroni.com](https://shop.pimoroni.com/products/keybow-2040)

The library abstracts away most of the complexity of having to check pin states,
and interact with the IS31FL3731 LED driver library, and exposes classes for
individual keys and the whole Keybow (a collection of Key instances).

![Keybow 2040 with backlit keys on marble background](keybow-2040-github-1.jpg)

## Getting started quickly!

You'll need to grab the latest version of Adafruit's Keybow 2040-flavoured
CircuitPython, from the link below.

[Download the Adafruit CircuitPython binary for Keybow 2040](https://circuitpython.org/board/pimoroni_keybow2040/)

Unplug your Keybow 2040's USB-C cable, press and hold the button on the top edge
of Keybow 2040 while plugging the USB-C cable back into your computer to mount
it as a drive (it should show up as `RPI-RP2` or something similar).

Drag and drop the `adafruit-circuitpython-pimoroni_keybow2040-en_US-XXXXX.uf2`
file that you downloaded onto the drive and it should reboot and load the 
CircuitPython firmware. The drive should now show up as `CIRCUITPY`.

The Adafruit IS31FL3731 LED driver library for CircuitPython is a prequisite for
this Keybow 2040 library, so you'll need to download it from GitHub at the link
below, and then drop the `adafruit_is31fl3731` folder into the `lib` folder on
your `CIRCUITPY` drive.

[Download the Adafruit IS31FL3731 CircuitPython library](https://github.com/adafruit/Adafruit_CircuitPython_IS31FL3731)

Finally, drop the `keybow2040.py` file from this library into the `lib` folder
on your `CIRCUITPY` drive also, and you're all set!

Pick one of the [examples](examples) (I'd suggest the 
[reactive.press.py](examples/reactive-press.py) example to begin), copy the 
code, and save it in the `code.py` file on your `CIRCUITPY` drive using your 
favourite text editor. As soon as you save the `code.py` file, or make any other
changes, then it should load up and run the code!

## Basics

## Imports and setup

All of your programs will need to start with the following:

```
import board
from keybow2040 import Keybow2040

i2c = board.I2C()
keybow = Keybow2040(i2c)
```

First, this imports the `board` module which contains all of the pin objects for
the Keybow 2040 board, including `board.I2C`, a quick way to set up the I2C bus, 
which is needed for the IS31FL3731 LED driver library used in this Keybow 2040
library.

The `Keybow2040()` class, imported from the `keybow2040` module, is instantiated
and passed the i2c bus object. Instantiating this sets up all of the pins, keys,
and LEDs, and provides access to all of the attributes and methods associated 
with it.

## The Keybow class

The Keybow class exposes a number of handy attributes and methods. The main one
you'll be interested in is the `.keys` attribute, which is a list of `Key` 
class instances, one for each key.

```
keys = keybow.keys
```

The indices of the keys in that list correspond to their position on the keypad,
staring from the bottom left corner (when the USB connector is at the top), 
which is key 0, going upwards in columns, and ending at the top right corner,
which is key 15.

More about the `Key` class later...

A **super** important method of the `Keybow` class is `.update()` method. It 
updates all of the keys, key states, and other attributes like the time of the
last key press, and sleep state of the LEDs.

**You need to call this method on your `Keybow` class at the very start of each
iteration of your program's main loop, as follows:**

```
while True:
    keybow.update()
```

## An interlude on timing!

Another **super** important thing is **not to include any `time.sleep()`s in 
your main loop!** Doing so will ruin the latency and mean that you'll miss key
press events. Just don't do it.

If you need introduce timed events, then you have to go about it in a slightly
(!!) roundabout fashion, by using `time.monotonic()` a constantly incremented
count of seconds elapsed, and use it to check the time elapsed since your last
event, for example:

```
time_interval = 10

# An event just happened!

time_last_fired = time.monotonic()
time_elapsed = 0

# ... some iterations later

time_elapsed = time.monotonic() - time_last_fired

if time_elapsed > time_interval:
    # Fire your event again!
```

There's a handy `keybow.time_of_last_press` attribute that allows you to quickly
check if a certain amount of time has elapsed since any key press, and that
attribute gets updated every time `keybow.update()` is called.

## Key presses

There are a few ways that you can go about detecting key presses, some
global methods on the `Keybow` class instance, and some on the `Key` class
instances themselves.

### Keybow class methods for detecting presses and key states

`keybow.get_states()` will return a list of the state of all of the keys, in 
order, with a state of `0` being not pressed, and `1` being pressed. You can
then loop through that list to do whatever you like.

`keybow.get_pressed()` will return a list of the key numbers (indices in the 
list of keys) that are currently pressed. If you only care about key presses,
then this is an efficient way to do things, especially since you have all the
key numbers in a list.

`keybow.any_pressed()` returns a Boolean (`True`/`False`) that tells you whether
any keys are currently being pressed. Handy if you want to attach a behaviour to
all of the keys, which this is effectively a proxy for.

`keybow.none_pressed()` is similar to `.any_pressed()`, in that it returns a 
Boolean also, but... you guessed it, it returns `True` if no keys are being
pressed, and `False` if any keys are pressed.

### Key class methods for detecting key presses

If we want to check whether key 0 is pressed, we can do so as follows:

```
keys = keybow.keys()

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

```
keys = keybow.keys()

if keys[0].pressed:
    # Do something!

if keys[0].held:
    # Do something else!
```

## LEDs!

LEDs can be set either globally for all keys, using the `Keybow` class instance,
or on a per-key basis, either through the `Keybow` class, or using a `Key` class
instance.

To set all of the keys to the same colour, you can use the `.set_all()` method
of the `Keybow` class, to which you pass three 0-255 integers for red, green, 
and blue. For example, to set all of the keys to magenta:

```
keybow.set_all(255, 0, 255)
```

To set an individal key through your `Keybow` class instance, you can do as
follows, to set key 0 to white:

```
keybow.set_led(0, 255, 255, 255)
```

To set the colour on the key itself, you could do as follows, again to set key
0 to white:

```
keybow.keys[0].set_led(255, 255, 255)
```

A key retains its RGB value, even if it is turned off, so once a key has its 
colour set with `key.rgb = (255, 0, 0)` for example, you can turn it off using
`key.led_off()` or even `key.set_led(0, 0, 0)` and then when you turn it back on
with `key.led_on()`, then it will still be red when it comes back on.

As a convenience, and to avoid having to check `key.lit`, there is a 
`key.toggle_led()` method that will toggle the current state of the key's LED 
(on to off, and _vice versa_).

There's a handy `hsv_to_rgb()` function that can be imported from the 
`keybow2040` module to convert an HSV colour (a tuple of floats from 0.0 to 1.0)
to an RGB colour (a tuple of integers from 0 to 255), as follows:

```
from keybow2040 import hsv_to_rgb

h = 0.5  # Hue
s = 1.0  # Saturation
v = 1.0  # Value

r, g, b = hsv_to_rgb(h, s, v)
```

## Attaching functions to keys with decorators

There are three decorators that can be attached to functions to link that 
function to, i) a key press, ii) a key release, or iii) a key hold.

Here's an example of how you could attach a decorator to a function that lights
up that key yellow when it is pressed, turns all of the LEDs on when held, and 
turns them all off when released:

```
import board
from keybow2040 import Keybow2040

i2c = board.I2C()
keybow = Keybow2040(i2c)
keys = keybow.keys

key = keys[0]
rgb = (255, 255, 0)
key.rgb = rgb

@keybow.on_press(key)
def press_handler(key):
    key.led_on()

@keybow.on_release(key)
def release_handler(key):
    keybow.set_all(0, 0, 0)

@keybow.on_hold(key)
def hold_handler(key):
    keybow.set_all(*rgb)

while True:
    keybow.update()
```