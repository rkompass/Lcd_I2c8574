# Lcd_I2c8574

Micropython drivers for dot matrix character LCD displays with HD44780 controller
(also called LCD 1602 . . LCD 2004 ). 

The drivers are for displays that are connected via I2C to a PCF8574 backpack that drives the HD44780 controller.

The drivers are a rework of Dave Hylands drivers on https://github.com/dhylands/python_lcd.

### Reworking the drivers attempted at

- Simplicity of installation: Copy and import 1 file.
- Maximal hardware-independence: Only import is `from time import sleep_ms, sleep_us`.
  Uses I2C-object at instantiation of the lcd class.
- Memory savings: Removed C-style constant definitions. Combined and simplified functions.
- Improved handling of '\n': Corrected a bug. Introduced an optional end argument (like in `print()` with default newline). Delayed linefeed at next character. Delete new line at linefeed.
- Optional scrolling of lines (i.e. more similarity to `print()`).
- Correction and extension of the character set (based on Japanese HD44780 ROM version).

### There are currently 3 versions of the driver

- **lcd_i2c8574.py**:   Standard driver.  Includes scrolling.
  Corrected '\\\\\' and '~' characters, so that all ASCII characters from chr(32) . . chr(126) are displayed.  Only 6 custom characters.
  Consumes ~2.7 K of RAM.
- **lcd_i2c8574_m.py**:   Minimal driver.  No scrolling.
  All ASCII characters from chr(32) . . chr(126). Only 6 custom characters.
  Consumes ~1.8 K of RAM.
- **lcd_i2c8574_x.py**:   Extended driver.  Added the following characters to standard driver:
  `'£¥€ §¶ °´• √±÷ äöüß ←→ αβεθμπρσ ΣΩ'`.  No custom characters as they are used for some of these.  Consumes ~3.2 K of RAM.

The drivers are synchronous. The API is slightly changed (see below).

There is an extensive test script for each driver version (**lcd_i2c8574_test.py**, **lcd_i2c8574_x_test.py** and **lcd_i2c8574_m_test.py**). In case the following API description is not sufficient have a look there.

### Installation and API

1. Copy one of the above files to your device.

2. Setup I2C:
   Pyboard: Wire I2C accordingly and then put in your script something like:
   `from machine import I2C`
   `i2c = I2C('Y', freq=100000)`
   Depending on your hardware you may have to use another id for I2C, specify scl and/or sda pins or use machine.SoftI2C (instead of machine.I2C which is hard I2C). See https://docs.micropython.org/en/latest/library/machine.I2C.html for more info.
   If you are not sure your I2C is set up correctly, test it with a scan.
   If you encounter problems: I2C needs pull-up resistors which are activated automatically with the above command, but may not suffice (internal pull-up resistors are not very strong, i.e have large Ω values) so you perhaps have to add extra ones in the range 3.3-10 kΩ.

3. Import the driver and instantiate the lcd class:
   `from lcd_i2c8574 import I2cLcd`
   `lcd = I2cLcd(i2c, 0x27, (20, 4))`
   Of course you use `lcd_i2c8574_x` or `lcd_i2c8574_m` for another driver version.
   `0x27` is the I2C device address of the PCF8574 backpack chip. It may be set to other values by soldering. `i2c_addr=0x27` is the default and can be omitted. `(20, 4)` are the dimensions of my LCD: 20 charaters x 4 lines.
   Depending on your display you may need (8, 2), (16, 1), (16, 2), (16, 4), (20, 2), (40, 1) or (40, 2). `dim=(16, 2)` is the default and can be omitted
   Optionally you may specify `scroll=False` in the standard and extended driver to prevent scrolling. This saves some memory (for storage of written lines).

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

For more information have a look at the test scripts **lcd_i2c8574_test.py**, **lcd_i2c8574_x_test.py** and **lcd_i2c8574_m_test.py** and at Dave Hylands site https://github.com/dhylands/python_lcd.
Note however that the API here is slightly changed compared to python_lcd:

- The LCD dimension now is given as a tuple, e.g. `(20, 4)`.
- Instead of `lcd.putchar()` and `lcd.putstring()` there is only `lcd.write()` with its default `end='\n'`.
- `lcd.custom_char()` was renamed to `lcd.define_char()`.
- The functions for brightness and cursor were reduced and combined.
- We have more arguments and more default arguments, as described above.

