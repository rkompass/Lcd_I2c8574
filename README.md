# Lcd_I2c8574

Micropython drivers for dot matrix character LCD displays with HD44780 controller
(also called LCD 1602 . . LCD 2004 ). 

The drivers are for displays that are connected via I2C to a PCF8574 (or PCF8574A) backpack that drives the HD44780 controller.

The drivers are a rework of Dave Hylands drivers on https://github.com/dhylands/python_lcd.

### Reworking the drivers attempted at

- Simplicity of installation: Copy and import 1 file.
- Maximal hardware-independence:
  Only import is `from time import sleep_us` (or `sleep` with Circuitpython)
  Uses I2C-object at instantiation of the lcd class.
- Memory savings: Removed C-style constant definitions. Combined and simplified functions.
- Improved handling of '\n': Corrected a bug. Introduced an optional end argument (like in `print()` with default newline). Delayed linefeed at next character. Delete new line at linefeed.
- Optional scrolling of lines (i.e. more similarity to `print()`).
- Correction and extension of the character set (based on Japanese HD44780 ROM version).

### There are currently 3 versions of the driver

- **lcd_i2c8574_m.py**:   Minimal driver.  No scrolling.
  All ASCII characters from chr(32) . . chr(126). Only 6 custom characters.
  Consumes 1.8-1.9 K of RAM (in Micropython, ??-2.5 K in Circuitpython).
- **lcd_i2c8574.py**:   Standard driver.  Includes scrolling.
  Corrected '\\\\\' and '~' characters, so that all ASCII characters from chr(32) . . chr(126) are displayed.  Only 6 custom characters.
  Consumes 2.7-3.3 K of RAM (in Micropython, ??-3.6 K in Circuitpython).
- **lcd_i2c8574_x.py**:   Extended driver.  Added the following characters to standard driver:
  `'£¥€ §¶ °´• √±÷ äöüß ←→ αβεθμπρσ ΣΩ'`.  No custom characters as they are used for some of these.  Consumes 3.2-3.8 K of RAM (in Micropython, ??-4.1 K in Circuitpython).

The drivers work with Micropython and Circuitpython.

The drivers are synchronous.

There is a **common extensive test script** for all driver versions (**lcd_i2c8574_test.py**) which you may adapt to your needs mostly by adjusting comments.
In case the following API description is not sufficient have a look there.

### Installation and API

1. Copy one (or all three) of the above files to your device.

2. Setup I2C:

   ##### Pyboard, Micropython:

   Wire I2C accordingly (see the Fritzing schema for pyboard) and then put in your script something like:
   `from machine import I2C`
   `i2c = I2C('Y', freq=100000)`

   ##### Raspberry Pi Pico, Micropython:

   After wiring like in the Fritzing schema for Pico include the following into you script:

   `from machine import I2C,  Pin          # Raspberry Pi Pico, Micropython`
   `i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=100000)`

   ##### Raspberry Pi Pico, Circuitpython:

   After wiring like in the Fritzing schema for Pico include the following into you script:
   `import board                         # Raspberry Pi Pico, Circuitpython`
   `from busio import I2C`
   `i2c = I2C(sda=board.GP0, scl=board.GP1)`
   `while i2c.try_lock():  # CP requires I2C bus locking`
   `    pass`

   The above statements are in the test script, you activate them by selective commenting in/out.
   Depending on your hardware you may have to use another id for I2C (e.g. 'X' for pyboard), specify scl and/or sda pins or use `machine.SoftI2C` (instead of `machine.I2C` which is hard I2C). See https://docs.micropython.org/en/latest/library/machine.I2C.html for more info.
   It is recommended to test your I2C setup with a scan.

   The test script includes a verbose I2C scan that you may use.

   If you encounter problems (e.g. no device responding to the scan): Check the I2C channel, try another one if available. Check the pins. Pin numbers on the board may be different to those of the MCU (if in doubt, try them out with LED blinking).  I2C needs pull-up resistors which are activated automatically with the above commands, but may not suffice (MCU-internal pull-up resistors are not very strong, i.e have large Ω values) so you perhaps have to add extra ones in the range 3.3-10 kΩ.
   If your I2C scan returns one or more devices you are almost finished. Find out which one (i.e. which address) is the one of your LCD backpack. If you have a PCF8574 on your backpack then the address is in the range 0x20..0x27 (which is 32..39 decimal) - depending on the soldering of 3 solder-connections (A0, A1 and A2, see PCF8574 image) on the board. By default (no soldering) it's 0x27.
   With a PCF8574A the address range is 0x38..0x3F (i.e. 56..63 decimal), 0x3F by default.

3. Import the driver and instantiate the lcd class:
   `from lcd_i2c8574 import I2cLcd`
   `lcd = I2cLcd(i2c, 0x27, (20, 4))`
   Of course you use `lcd_i2c8574_x` or `lcd_i2c8574_m` for another driver version.
   Instead of`0x27` you may have to use another number as the I2C device address of your backpack chip as noted above. Note that `i2c_addr=0x27` is a default of the I2cLcd class and can be omitted.
   `(20, 4)` are the dimensions of my LCD: 20 charaters x 4 lines. Depending on your display you may need other numbers like (8, 2), (16, 1), (16, 2), (16, 4), (20, 2), (40, 1) or (40, 2). `dim=(16, 2)` is the default and again may be omitted
   Optionally you may specify `scroll=False` in the standard and extended driver to prevent scrolling. This saves some memory.

4. Optionally set light and cursor:
   `lcd.set_display(backl=False)` switches backlight off.
   `lcd.set_display(backl=True`) switches it on again (which is on by default).
    If you have problems here (e.g. no difference by this, no characters): Note that there is a potentiometer on the LCD backpack which has to be set to a suitable value to recognize the characters. In the extremes you only see white/bright or all 5x8 character pixels. Find an intermediate poti setting.
   `lcd.set_cursor(blink=True)` shows a blinking cursor.
   `lcd.set_cursor(show=True)` shows a cursor bar.
   `lcd.set_cursor(show=False)` hides the cursor, which is the default.

5. Write to the display, perhaps move position:
   `lcd.write('Hello, here we have a first very long line, which is 72 characters long.'` writes a text over several lines. It automatically adds a newline in the end, which is not displayed directly, so that you may read as much as possible and dont see unnecessary blank lines. The newline will appear as soon as the next character is written to the display.
   `lcd.write('a', end='')` writes a single character without following newline.
   If this character was the last in the line it will make a newline pending however, which may be removed by setting the writing position directly with
   `lcd.move_to(0, 2)` for example, which moves to the beginning (x=0) of the third line.
   `lcd.write('First long line, at least a bit long.', wrap=False)` will write the line to the display but not wrap it to the following lines. This option is not available in the minimal driver.

6. Clear the LCD:
   `lcd.clear()` if necessary, clears the display and moves to (0, 0).

7. Define custom characters and write them (not available in extended driver):
   `lcd.define_char(0, b'\x00\x0a\x1f\x1f\x0e\x04\x00\x00')    # Heart`
   `lcd.define_char(1, b'\x01\x03\x05\x09\x09\x0b\x1b\x18')    # Notes`
   define two custom characters. 0 and 1 are the RAM slots. We have 7 of them, but slot 6 and 7 are already used to define '\\\\\' and '~'.  Note: All slots are used already in the extended driver.
   The second argument may be a bytes object (like in the above code) or a bytearray. It defines the character pixels bit by bit from top to bottom:
   `lcd.write(chr(0))` writes the character in the 0-th slot, a heart in our case.

   ```
   Heart (where .=0, #=1)
   ..... == 0b00000 == 0x00
   .#.#. == 0b01010 == 0x0a
   ##### == 0b11111 == 0x1f
   ##### == 0b11111 == 0x1f
   .###. == 0b01110 == 0x0e
   ..#.. == 0b01110 == 0x04
   ..... == 0b00000 == 0x00
   ..... == 0b00000 == 0x00
   ```

For more information have a look at the test script **lcd_i2c8574_test.py** 
and perhaps at Dave Hylands site https://github.com/dhylands/python_lcd.
Note however that the API here is slightly changed compared to python_lcd:

- The LCD dimension now is given as a tuple, e.g. `(20, 4)`.
- Instead of `lcd.putchar()` and `lcd.putstring()` there is only `lcd.write()` with its default `end='\n'`.
- `lcd.custom_char()` was renamed to `lcd.define_char()`.
- The functions for brightness and cursor were reduced and combined.
- We have more arguments and more default arguments, as described above.

