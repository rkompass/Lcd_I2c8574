"""Tests of I2cLcd (in lcd_i2c8574.py) which implements a HD44780 character LCD connected via PCF8574 on I2C.
   This code should work for at least esp8266 and (tested) Pyboard"""

# ------- Test Options -----
_Intro_and_Memory     = True
_Light_and_Cursor     = True
_Present_Characters   = True
_Custom_Characters    = True
_Move_to_Position     = True
_Write                = True
_Write_Test_1 = True           # Short lines
_Write_Test_2 = True           # Long lines
_Write_Test_3 = True           # Lines with 20 characters


# ---------- Import and Measure Memory Consumption ------------
import gc
from time import sleep_ms
from machine import I2C
gc.collect(); mfree0 = gc.mem_free()
from lcd_i2c8574_m import I2cLcd

i2c = I2C('Y', freq=100000)


lcd = I2cLcd(i2c, 0x27, (20,4))   # 0x27 <-- i2c address, may be changed by soldering connections
gc.collect(); mfree1 = gc.mem_free()

if _Intro_and_Memory:
    print('--- Testing Lcd Driver ---')
    lcd.write('-Testing LCD Driver-')    # 20 Characters, should elicit implicit newline
    sleep_ms(1500)
    print('-- Memory usage --')
    lcd.write('-- Memory usage --')
    sleep_ms(1500)
    print('Free mem:', mfree1, '. I2cLcd driver used:', mfree0-mfree1)
    lcd.write(f'Mem used: {mfree0-mfree1} Bytes')
    sleep_ms(3000)

if _Light_and_Cursor:
    # ---------- Backlight and Cursor Modes ------------
    print('-- Light and Cursor --')
    lcd.write('-Light and Cursor-')
    sleep_ms(1500)
    print('Backlight off')
    lcd.write('Backlight off')
    sleep_ms(1000)
    lcd.set_display(backl=False)
    sleep_ms(1500)
    lcd.set_display(backl=True)
    print('Backlight on')
    lcd.write('Backlight on')
    sleep_ms(1500)
    print('Cursor blink on')
    lcd.write('Cursor blink on')
    lcd.set_cursor(blink=True)
    sleep_ms(1500)
    print("Cursor blink off")
    lcd.write('Cursor blink off')
    lcd.set_cursor(show=True)
    sleep_ms(1500)
    print('Cursor hide')
    lcd.write('Cursor hide')
    lcd.set_cursor(show=False);
    sleep_ms(1500)
    print('Clear Display..')
    lcd.write('Clear Display..')
    lcd.clear()
    sleep_ms(2000)

if _Present_Characters:
    # ---- Present available Characters ----------
    print('-- Present Characters --')
    lcd.write('-Present Characters-')
    sleep_ms(1500)
    print(' !"#$%&\'()*+,-./')
    lcd.write(' !"#$%&\'()*+,-./')
    sleep_ms(2500)
    print('0123456789:;<=>?')
    lcd.write('0123456789:;<=>?')
    sleep_ms(2500)
    print('@ABCDEFGHIJKLMNO')
    lcd.write('@ABCDEFGHIJKLMNO')
    sleep_ms(2500)
    print('PQRSTUVWXYZ[\]^_')
    lcd.write('PQRSTUVWXYZ[\]^_')
    sleep_ms(2500)
    print('`abcdefghijklmno')
    lcd.write('`abcdefghijklmno')
    sleep_ms(2500)
    print('pqrstuvwxyz{|}~')
    lcd.write('pqrstuvwxyz{|}~')
    sleep_ms(2500)
    

if _Custom_Characters:
    # -------- Define and Display Custom Characters ----------
    print('-- Custom Characters --')
    lcd.write('-Custom Characters-')
    sleep_ms(1500)

    lcd.define_char(0, b'\x00\x0a\x1f\x1f\x0e\x04\x00\x00')    # Heart
    lcd.define_char(1, b'\x01\x03\x05\x09\x09\x0b\x1b\x18')    # Notes
    lcd.define_char(2, b'\x0e\x11\x11\x1f\x1b\x1b\x1f\x00')    # Lock
    lcd.define_char(3, b'\x04\x0e\x0e\x0e\x1f\x00\x04\x00')    # Bell           
    lcd.define_char(4, b'\x01\x03\x0f\x0f\x03\x01\x00\x00')    # Speaker
    lcd.define_char(5, b'\x06\x09\x1c\x08\x1c\x09\x06\x00')    # Euro
    lcd.define_char(6, b'\x00\x10\x08\x04\x02\x01\x00\x00')    # Character for '\\', which was Yen in Japanese ROM
    lcd.define_char(7, b'\x00\x00\x00\x0d\x12\x00\x00\x00')    # Character for '~', which was right arrow

    for i in range(8):
        print(' .', end='')
        lcd.write(f' {chr(i)}', end='')
        sleep_ms(200)
    print()
    lcd.write('\n')
    sleep_ms(2000)

if _Move_to_Position:
    # ------ Move to (x, y) Position ----------
    print('-- Write at (x,y) --')
    lcd.write('-- Write at (x,y) --')
    sleep_ms(1500)
    lcd.clear()
    lcd.move_to(2, 0)
    print('Moved to (2,0)')
    lcd.write('Moved to (2,0)')
    sleep_ms(1500)
    lcd.move_to(5, 3)
    print('Moved to (5,3)')
    lcd.write('Moved to (5,3)')
    sleep_ms(2000)
    lcd.clear()


if _Write:
    # ------ Write Functionality without Scoll Mode ----------
    print('-- Write --')
    lcd.write('\n-- Write --')
    sleep_ms(1500)
    if _Write_Test_1:
        lcd.write('Several short lines')
        sleep_ms(1500)
        for i in range(1,8):
            lcd.write(f'Short line {i}')
            sleep_ms(1000)
        sleep_ms(1000)
        lcd.write('Short lines wo newl')
        sleep_ms(1500)
        lcd.write('Short', end='')
        sleep_ms(1500)
        lcd.write('..short', end='')
        sleep_ms(1500)
        lcd.write('..fine!')
        sleep_ms(2000)
    if _Write_Test_2:
        lcd.write('Two long lines')
        sleep_ms(1500)
        lcd.write('First long line, 40 characters (!) long.')
        sleep_ms(1500)
        lcd.write('Second long line, also a bit long.')
        sleep_ms(1500)
    if _Write_Test_3:
        lcd.write('Lines with 20 ..')
        lcd.write('.. characters.')
        sleep_ms(1500)
        for i in range(1,4):
            lcd.write(f'--20 char line No {i}-')
            sleep_ms(1000)
        sleep_ms(1000)
        lcd.write('Lines with 20 chars,')
        sleep_ms(1000)
        lcd.write('.. followed by ..')
        sleep_ms(1000)
        lcd.write('.. empty lines.')
        sleep_ms(1500)
        for i in range(1,4):
            lcd.write(f'--20 char line No {i}-')
            lcd.write()
            sleep_ms(1500)
        sleep_ms(1500)




