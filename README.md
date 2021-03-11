# Keybow 2040 CircuitPython

This CircuitPython library is for the RP2040-powered Keybow 2040 from Pimoroni,
a 16-key mini mechanical keyboard with RGB backlit keys. Find out more about 
Keybow 2040 at the link below.

[Keybow 2040 at pimoroni.com](https://shop.pimoroni.com/products/keybow-2040)

![Keybow 2040 with backlit keys on marble background](keybow-2040-github-1.jpg)

The library abstracts away most of the complexity of having to check pin states,
and interact with the IS31FL3731 LED driver library, and exposes classes for
individual keys and the whole Keybow (a collection of Key instances).

## Getting started quickly!

You'll need to grab the latest version of Adafruit's Keybow 2040-flavoured
CircuitPython, from the link below.

[Adafruit CircuitPython binary for Keybow 2040](https://circuitpython.org/board/pimoroni_keybow2040/)

Unplug your Keybow 2040's USB-C cable, press and hold the button on the top edge
of Keybow 2040 while plugging the USB-C cable back into your computer to mount
it as a drive (it should show up as `RPI-RP2` or something similar).

Drag and drop the `xxxxxxxx.uf2` file that you downloaded onto the drive and it
should reboot and load the CircuitPython firmware. The drive should now show up
as `CIRCUITPY`.

The Adafruit IS31FL3731 LED driver library for CircuitPython is a prequisite for
this Keybow 2040 library, so you'll need to download it from GitHub at the link
below, and then drop the `adafruit_is31fl3731` folder into the `lib` folder on
your `CIRCUITPY` drive.

[Adafruit IS31FL3731 CircuitPython library](https://github.com/adafruit/Adafruit_CircuitPython_IS31FL3731)

Finally, drop the `keybow2040.py` file from this library into the `lib` folder
on your `CIRCUITPY` drive also, and you're all set!

Pick one of the [examples](examples) (I'd suggest the 
[reactive.press.py](examples/reactive-press.py) example to begin), copy the 
code, and save it in the `code.py` file on your `CIRCUITPY` drive using your 
favourite text editor. As soon as you save the `code.py` file, or make any other
changes, then it should load up and run the code!