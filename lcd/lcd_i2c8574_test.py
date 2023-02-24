"""Tests of I2cLcd (in lcd_i2c8574.py, lcd_i2c8574_m.py or lcd_i2c8574_x.py)
   which implements a HD44780 character LCD connected via PCF8574 on I2C."""

# Memory Consumptions:
#  1904, 3312, 3840  Bytes with Rpi Pico, Micropython
#  2528, 3616, 4144  Bytes with Rpi Pico, Circuitpython

# ------- I2C  Address -----
I2C_Addr = 0x27 #  address may be changed by soldering connections on PCF8574 backpack

# ------- LCD Dimension ----
LCD_Dim = (20, 4)

# ------- Driver Version ---
# _Driver_Version = 'Normal'
# _Driver_Version = 'Minimal'
_Driver_Version = 'Extended'

# --- I2C - Setup: Depends on Board and Micropython vs. Circuitpython choice ------

from machine import I2C              # Pyboard, Micropython
i2c = I2C('Y', freq=100000)

# from machine import I2C,  Pin          # Raspberry Pi Pico, Micropython
# i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=100000)
# 
# import board                         # Raspberry Pi Pico, Circuitpython
# from busio import I2C
# i2c = I2C(sda=board.GP0, scl=board.GP1)
# while i2c.try_lock():  # CP requires I2C bus locking
#     pass

# from machine import I2C,  Pin          # ESP32 NodeMCU, Micropython
# i2c = I2C(0, sda=Pin(21), scl=Pin(22), freq=100000)

# ----------------- Test Options -------------------
_Intro_and_Memory     = True
_Light_and_Cursor     = True
_Present_Characters   = True
_Custom_Characters    = True
_Move_to_Position     = False
_Write_in_Scroll_Mode = False   # Ignored in minimal Version: No Scroll Mode
_Write_without_Scroll = False
_Write_Test_1 = True           # Short lines
_Write_Test_2 = True           # Long lines
_Write_Test_3 = True           # Lines with 20 characters
_Write_Test_4 = True           # '\n\n\n', end='' and long line after move_to


# ------------ Do a I2C Scan and check Address -------------------

print('--- Scanning I2C Bus ---\n')
devices = i2c.scan()
print('  \\  ', end='')
for j in range(0x10):
    print(f'...{j:01x} ', end='')
print()
for i in range(0x8):
    print(f'0x{i:01x}. ', end='')
    for j in range(0x10):
        k = i*16+j
        if k < 4:
            print('     ', end='')
        elif k in devices:
            print(f'0x{k:02x} ', end='')
        else:
            print('---- ', end='')
    print()
print()

pcf8574_devices = [i for i in range(0x20, 0x28) if i in devices]
pcf8574A_devices = [i for i in range(0x38, 0x40) if i in devices]

if pcf8574_devices:
    print(f'The following device addresses could be from a PCF8574 LCD Backpack: {', '.join([hex(d) for d in pcf8574_devices])}')
if pcf8574A_devices:
    print(f'The following device addresses could be from a PCF8574A LCD Backpack: {', '.join([hex(d) for d in pcf8574A_devices])}')
if I2C_Addr in pcf8574_devices + pcf8574A_devices:
    i2c_Addr_match = True
else:
    i2c_Addr_match = False
print(f'You selected I2C Address 0x{I2C_Addr:02x}:  {'Fine' if i2c_Addr_match else 'Wrong'}')
if not i2c_Addr_match:
    raise SystemExit
print()

# ------- Import Driver and Measure Memory Consumption --------

import gc
from time import sleep

print('--- Importing I2cLcd Driver ---\n')
gc.collect(); mfree0 = gc.mem_free()
if _Driver_Version == 'Normal':
    from lcd_i2c8574 import I2cLcd
elif _Driver_Version == 'Minimal':
    from lcd_i2c8574_m import I2cLcd
elif _Driver_Version == 'Extended':
    from lcd_i2c8574_x import I2cLcd

lcd = I2cLcd(i2c, I2C_Addr, LCD_Dim)
gc.collect(); mfree1 = gc.mem_free()


# Used twice: With and without scrolling.
def write_tests():
    if _Write_Test_1:
        lcd.write('Several short lines')
        sleep(1.5)
        for i in range(1,8):
            lcd.write(f'Short line {i}')
            sleep(1)
        sleep(1)
        lcd.write('Short lines with ..')
        lcd.write(" .. end='' option")
        sleep(1.5)
        lcd.write('Short', end='')
        sleep(1.5)
        lcd.write('..short', end='')
        sleep(1.5)
        lcd.write('..fine!')
        sleep(2)
    if _Write_Test_2:
        lcd.write('Two long lines')
        sleep(1.5)
        lcd.write('First long line, 40 characters (!) long.')
        sleep(1.5)
        lcd.write('Second long line, also a bit long.')
        sleep(1.5)
        lcd.write('Same lines with ..')
        lcd.write('.. wrap=False option')
        sleep(1.5)
        lcd.write('First long line, at least a bit long.', wrap=False)
        sleep(1.5)
        lcd.write('Second long line, also a bit long.', wrap=False)
        sleep(2)
    if _Write_Test_3:
        lcd.write('Lines with 20 ..')
        lcd.write('.. characters.')
        sleep(1.5)
        for i in range(1,4):
            lcd.write(f'--20 char line No {i}-')
            sleep(1)
        sleep(1)
        lcd.write('Lines with 20 chars.')
        sleep(1)
        lcd.write('.. followed by ..')
        sleep(1)
        lcd.write('.. empty lines')
        sleep(1.5)
        for i in range(1,4):
            lcd.write(f'--20 char line No {i}-')
            lcd.write()
            sleep(1.5)
        sleep(1.5)
    if _Write_Test_4:
        lcd.write("'\\n\\n\\n', end=''")  # Use a character that is somewhat similar to backslash, as backslash --> Yen symbol (in my Japanese ROM-Code A00)
        sleep(1.5)
        lcd.write('\n\n\n', end='')
        sleep(1.5)
        lcd.write('Long line after ..')
        lcd.write('.. move to (4,2)')
        sleep(2.5)
        lcd.move_to(4, 2)
        lcd.write('Long long line, again a bit boring..')  # 36 characters, stops at x=20, 
        sleep(1.5)


# ------------------- The Tests start here --------------------


# ------- Introduction and Memory Usage ------------
if _Intro_and_Memory:
    print('--- Testing Lcd Driver ---')
    lcd.write('-Testing LCD Driver-')  # 20 Characters, should elicit implicit newline
    print(f'--- Version: {_Driver_Version:s} ---\n')
    lcd.write(f'-Version: {_Driver_Version:s}-')
    sleep(1.5)
    print('-- Memory usage --')
    lcd.write('-- Memory usage --')
    sleep(1.5)
    print('Free mem:', mfree1, '. I2cLcd driver used:', mfree0-mfree1)
    lcd.write(f'Mem used: {mfree0-mfree1} Bytes')
    sleep(3)

# ---------- Backlight and Cursor Modes ------------
if _Light_and_Cursor:
    print('-- Light and Cursor --')
    lcd.write('-Light and Cursor-')
    sleep(1.5)
    print('Backlight off')
    lcd.write('Backlight off')
    sleep(1)
    lcd.set_display(backl=False)
    sleep(1.5)
    lcd.set_display(backl=True)
    print('Backlight on')
    lcd.write('Backlight on')
    sleep(1.5)
    print('Cursor blink on')
    lcd.write('Cursor blink on')
    lcd.set_cursor(blink=True)
    sleep(1.5)
    print("Cursor blink off")
    lcd.write('Cursor blink off')
    lcd.set_cursor(show=True)
    sleep(1.5)
    print('Cursor hide')
    lcd.write('Cursor hide')
    lcd.set_cursor(show=False);
    sleep(1.5)
    print('Clear Display..')
    lcd.write('Clear Display..')
    lcd.clear()
    sleep(2)

# ---- Present available Characters ----------
if _Present_Characters:
    print('-- Present Characters --')
    lcd.write('-Present Characters-')
    sleep(2)
    lcd.write(' !"#$%&\'()*+,-./')
    sleep(3)
    lcd.write('0123456789:;<=>?')
    sleep(3)
    lcd.write('@ABCDEFGHIJKLMNO')
    sleep(3)
    lcd.write('PQRSTUVWXYZ[\]^_')
    sleep(3)
    lcd.write('`abcdefghijklmno')
    sleep(3)
    lcd.write('pqrstuvwxyz{|}~')
    sleep(3)
    if _Driver_Version == 'Extended': 
        print('£¥€ §¶ °´• √±÷ äöüß')
        lcd.write('£¥€ §¶ °´• √±÷ äöüß')
        sleep(3)
        print('←→ αβεθμπρσ ΣΩ')
        lcd.write('←→ αβεθμπρσ ΣΩ')
        sleep(3)

# -------- Define and Display Custom Characters ----------
if _Custom_Characters and _Driver_Version != 'Extended': # No custom chars in extended driver
    print('-- Custom Characters --')
    lcd.write('-Custom Characters-')
    sleep(1.5)

    lcd.define_char(0, b'\x00\x0a\x1f\x1f\x0e\x04\x00\x00')    # Heart
    lcd.define_char(1, b'\x01\x03\x05\x09\x09\x0b\x1b\x18')    # Notes
    lcd.define_char(2, b'\x0e\x11\x11\x1f\x1b\x1b\x1f\x00')    # Lock
    lcd.define_char(3, b'\x04\x0e\x0e\x0e\x1f\x00\x04\x00')    # Bell           
    lcd.define_char(4, b'\x01\x03\x0f\x0f\x03\x01\x00\x00')    # Speaker
    # lcd.define_char(5, b'\x00\x0a\x0a\x00\x11\x0e\x00\x00')    # Smile
    lcd.define_char(5, b'\x06\x09\x1c\x08\x1c\x09\x06\x00')    # Euro

    # We have only 6 custom characters available in standard driver, because chr(6) and chr(7) are used by the driver for \ and ~
    for i in range(6):   # We have only 6 custom characters available because chr(6) and chr(7) are used by the driver for \ and ~
        print(' .', end='')
        lcd.write(f' {chr(i)}', end='')
        sleep(0.2)
    print()
    lcd.write()
    sleep(2)

# ------ Move to (x, y) Position ----------
if _Move_to_Position:
    print('-- Write at (x,y) --')
    lcd.write('-- Write at (x,y) --')
    sleep(1.5)
    lcd.clear()
    lcd.move_to(2, 0)
    print('Moved to (2,0)')
    lcd.write('Moved to (2,0)')
    sleep(1.5)
    lcd.move_to(5, 3)
    print('Moved to (5,3)')
    lcd.write('Moved to (5,3)')
    sleep(2)
    lcd.clear()

# ------ Write Functionality in Scoll Mode ----------
if _Write_in_Scroll_Mode and _Driver_Version in ('Normal', 'Extended'):
    print('-- Write in Scroll Mode --')
    lcd.write('Write in Scroll Mode')    # Line with 20 characters
    sleep(1.5)
    write_tests()

# ------ Write Functionality without Scoll Mode ----------
if _Write_without_Scroll: 
    del lcd
    lcd = I2cLcd(i2c, 0x27, (20,4), scroll=False)   # 0x27 <-- i2c address, may be changed by soldering connections
    print('-- Write without scroll --')
    lcd.write('Write without scroll')    # Line with 20 characters
    sleep(1.5)
    write_tests()


