# Implements a HD44780 character LCD connected via PCF8574 on I2C.
# Extended version: Try to display an extended character set, that is offered by the Japanese version of
# HD44780 (ROM Code: A00) and by the 6 remaining custom characters.
#   --> .define_char() is not available anymore.
#
# Should work with ESP8266 and (tested) Pyboard 1.1.
#
# Derived from https://github.com/dhylands/python_lcd by rkompass 2022,
#    (put everything in one file, removed constants, simplified....) --> ~1.8 K memory consumption,
#    (new newline logic, added scroll and wrap options)  --> ~2.7 K memory consumption.
#    (corrected '\\' and '~' characters)  --> ~2.7 K memory consumption.
#    (extended character set)  --> ~3.2 K memory consumption.

# Included from available ROM fonts:
# degree alpha  beta  epsilon  mu   sigma   rho   theta  Omega    pi   Sigma  auml  ouml  uuml szlig divide  bull  radic  yen   rarr   larr
#  °      α      β      ε      μ      σ      ρ      θ      Ω      π      Σ     ä     ö     ü     ß     ÷      •      √     ¥     →      ←
# 0xb0  0x3b1  0x3b2  0x3b5  0x3bc  0x3c3  0x3c1  0x3b8  0x3a9  0x3c0  0x3a3  0xe4  0xf6  0xfc  0xdf  0xf7  0x2022 0x221a 0xa5 0x2192 0x2190  <-- unicode
# 0xdf   0xe0   0xe2   0xe3   0xe4   0xe5   0xe6   0xf2   0xf2   0xf7   0xf6  0xe1  0xef  0xf5  0xe2  0xfd   0xa5   0xe8  0x5c  0xfe   0xff   <-- ROM code

# Included as custom characters:
# acute   sect   para  pound   euro  plusmn                                  #   ne    Delta   <-- not chosen
#   ´      §       ¶     £      €      ±                                     #   ≠       Δ
#  0xb4   0xa7   0xb6   0xa3  0x20ac  0xb1       <-- unicode                 #  0x2260  0x394
# chr(0) chr(1) chr(2) chr(3) chr(4) chr(5)      <-- internal code     

try:
    from time import sleep_us
except ImportError:              # Circuitpython does not have sleep_ms(), sleep_us(), we use sleep() for that
    from time import sleep
    def sleep_us(us):
        sleep(us/1000000)

# Driver class.
class I2cLcd:

    def __init__(self, i2c, i2c_addr=0x27, dim=(16, 2), scroll=True):  # default address of PCF8574 is 0x27
        self.i2c = i2c
        self.i2c_addr = i2c_addr
        if not isinstance(dim, (tuple, list)) or len(dim) != 2:
            raise ValueError('I2cLcd: dim argument should be tuple or list, e.g. (16, 2)')
        self.nx = min(dim[0], 40)
        self.ny = min(dim[1], 4)
        self.scroll = scroll
        if scroll:        # Create list of lines 1..ny that will store previously written chars to be rewritten 1 line higher at scrolling
            self.lines = [bytearray(32 for _ in range(self.nx)) for l in range(self.ny -1)]  # 32 <-- ord(' ')
        self.backl = 0x08
        self.i2c.writeto(self.i2c_addr, bytearray([0]))          # Init I2C
        sleep_us(20000)                                             # Allow LCD time to powerup
        for _ in range(3):                                       # Send reset 3 times
            self.i2c.writeto(self.i2c_addr, bytearray((0x34, 0x30))) # LCD_FUNCTION_RESET
            sleep_us(5000)                                          # Need to delay at least 4.1 msec
        self.i2c.writeto(self.i2c_addr, bytearray((0x24, 0x20))) # LCD_FUNCTION, put LCD into 4 bit mode
        sleep_us(1000)
        self.set_display(False)
        self.clear()     # Sets class variables: self.x = 0; self.y = 0; self.nl = False; self.impl_nl = False
        self._wr(0x06)                           # LCD_ENTRY_MODE | LCD_ENTRY_INC
        self.set_cursor(False)
        self.set_display(True)                   # We might include a backlight option here
        self._wr(0x28 if self.ny > 1 else 0x20)  # LCD_FUNCTION_2LINES if ny > 1 else LCD_FUNCTION
        self._idefc(0, b'\x02\x04\x08\x00\x00\x00\x00\x00')  # acute:     ´
        self._idefc(1, b'\x06\x09\x04\x0a\x04\x12\x0c\x00')  # sect:      §
        self._idefc(2, b'\x0f\x13\x13\x0f\x03\x03\x03\x00')  # para:      ¶
        self._idefc(3, b'\x06\x08\x08\x1c\x08\x09\x16\x00')  # pound:     £
        self._idefc(4, b'\x06\x09\x1c\x08\x1c\x09\x06\x00')  # euro:      €
        self._idefc(5, b'\x04\x04\x1f\x04\x04\x00\x1f\x00')  # plusmn:    ±
        self._idefc(6, b'\x00\x10\x08\x04\x02\x01\x00\x00')  # backslash: \, which was Yen in Japanese ROM
        self._idefc(7, b'\x00\x00\x00\x0d\x12\x00\x00\x00')  # tilde:     ~, which was right arrow
        self.move_to(self.x, self.y)
        self._ucodes = '£¥§°±´¶ß÷äöü•€←→√ΣΩαβεθμπρσ'
        self._rcodes = b'\x03\x5c\x01\xdf\x05\x00\x02\xe2\xfd\xe1\xef\xf5\xa5\x04\x7f\x7e\xe8\xf6\xf4\xe0\xe2\xe3\xf2\xe4\xf7\xe6\xe5'

    # Clears the LCD display and moves the cursor to the top left.
    def clear(self):
        self._wr(0x01)        # LCD_CLR
        self._wr(0x02)        # LCD_HOME
        self.x = 0
        self.y = 0
        self.nl = False       # linefeed
        self.impl_nl = False  # implicit newline, to suppress an extra nl when a character in rightmost position is followed by \n
        if self.scroll:       # in scroll mode also empty line buffer
            for i in range(self.ny-1):
                self.lines[i][:] = bytes(32 for _ in range(self.nx))  # 32 <-- ord(' ')

    # Causes the cursor to be made visible if show or even blink.
    def set_cursor(self, show=False, blink=False):
        self._wr(0x0f if blink else (0x0e if show else 0x0c))  # LCD_ON_CTRL | LCD_ON_DISPLAY | (LCD_ON_CURSOR) 

    # Turns the LCD on (unblanks) or off, optionally sets backlight.
    def set_display(self, on=True, backl=None):
        self._wr(0x0c if on else 0x08)     # LCD_ON_CTRL | LCD_ON_DISPLAY
        if backl is not None:
            self.backl = 0x08 if backl else 0x00
            self.i2c.writeto(self.i2c_addr, bytearray((self.backl,)))

    # Moves the cursor to the indicated position, if cl_cpy: Delete rest of line or write from given buffer into line.
    def move_to(self, x, y, cl_cpy=False):
        self.x = x                                     # The cursor position is zero based (x == 0 -> first column)
        self.y = y
        self.nl = False                                # No active newline anymore
        if not cl_cpy:                                 # If we just moved then also an implicit newline is no longer valid
            self.impl_nl = False                       #    but if we moved inside write()s scrolling it has to be preserved
        pos_c = 0x80 | x & 0x3f | (y & 1) << 6         # HD44780 position code.  y & 1 << 6   <-- Lines 1 & 3 add 0x40
        if y & 2:                                      # Lines 2 & 3 add number of columns
            pos_c += self.nx
        self._wr(pos_c)           # LCD_DDRAM | ..
        if cl_cpy == True:
            for _ in range(self.nx - x):
                self._wr(32, 1)   # 32 <-- ord(' ')    # Clear the line that we moved to till the end
            self._wr(pos_c)                            #   and go back to the position that we moved to
        elif isinstance(cl_cpy, (bytes, bytearray)):
            for i in range(min(len(cl_cpy), self.nx-x)):
                self._wr(cl_cpy[i], 1)                 # Write buffer from position till the end of line
            self._wr(pos_c)                            #   and go back to the position that we moved to

    # Writes the string at the current cursor pos and advances cursor.
    # Trailing newlines (also implicit) happen at writes of following character to better use the limited number of lines.
    # May be used to write a single character with .write(c, end='').
    # A .write() (without argument) results in a newline.
    def write(self, string='', end='\n', wrap=True):
        for c in ''.join((string, end)):
            if c == '\n' and self.impl_nl:
                self.impl_nl = False          # Consume nl if a character written in rightmost position already elicited an implicit nl
                continue
            if self.nl or wrap and self.x >= self.nx:  # In case of a new wrap (prev. write with wrap=False) and overdue nl: newline before writing
                if self.y < self.ny-1:                 # We were above the last line:
                    self.move_to(0, self.y+1, True)    #    Clear next line and start from there
                elif not self.scroll:                  # We were on the last line:
                    self.move_to(0, 0, True)           #    Clear first line and start from there, if no scroll
                else:
                    for i, l in enumerate(self.lines):
                        self.move_to(0, i, l)          # Write line buffer contents to upper lines
                    self.move_to(0, self.ny-1, True)   #    and clear last line and start from there, if scroll
                    l = self.lines.pop(0)              # Shift line buffer one line up
                    l[:] = bytes(32 for _ in range(self.nx)) # 32 <-- ord(' ')
                    self.lines.append(l)               #   and delete top line and append it below
                self.nl = False
            if c == '\n':
                self.nl = True                # nl will be executed when next character arrives
                continue
            if self.x < self.nx:
                self.impl_nl = False          # Other character than \n after implicit newline makes it invalid
                oc = ord(c)
                if 15 < oc < 127:
                    if oc ==  92: oc = 6       # select a better sign for \, which was yen, now defined as custom character 6
                    if oc == 126: oc = 7       # select a sign for ~, which was right arrow, now defined as custom character 7
                elif c in self._ucodes:
                    oc = self._rcodes[self._ucodes.find(c)]
                else:
                    oc = 127
                self._wr(oc, 1)
                if self.scroll and self.y > 0:
                    self.lines[self.y-1][self.x] = oc
                self.x += 1
            if wrap and self.x >= self.nx:
                self.nl = True                # We signal the newline, but it is implicit
                self.impl_nl = True

    # Here (extended driver) only internal function: write a character to one of the first 8 CGRAM locations, available as chr(0) through chr(7)
    def _idefc(self, loc, cmap):                              #  we define characters \ and ~ by them
        self._wr(0x40 | (loc << 3))  # LCD_CGRAM | ..
        sleep_us(40)
        for i in range(8):
            self._wr(cmap[i], 1)
            sleep_us(40)

    # Write to the LCD; dbit: 0..command, 1..data.
    def _wr(self, data, dbit=0):
        b0 = dbit | self.backl | data & 0xf0
        b1 = dbit | self.backl | ((data & 0x0f) << 4)
        self.i2c.writeto(self.i2c_addr, bytearray((b0 | 0x04, b0, b1 | 0x04, b1)))
        if not dbit and data <= 3:            # The home and clear commands require a worst case delay of 4.1 msec
            sleep_us(5000)
