"""Tests of I2cLcd (in lcd_i2c8574_x.py) which implements a HD44780 character LCD connected via PCF8574 on I2C.
   This code should work for at least esp8266 and (tested) Pyboard"""

# ------- Test Options -----
_Intro_and_Memory     = True
_Light_and_Cursor     = False
_Present_Characters   = True
_Move_to_Position     = False
_Write_in_Scroll_Mode = False
_Write_without_Scroll = False
_Write_Test_1 = False           # Short lines
_Write_Test_2 = False           # Long lines
_Write_Test_3 = False           # Lines with 20 characters
_Write_Test_4 = True            # '\n\n\n', end='' and long line after move_to

def write_tests():
    if _Write_Test_1:
        lcd.write('Several short lines')
        sleep_ms(1500)
        for i in range(1,8):
            lcd.write(f'Short line {i}')
            sleep_ms(1000)
        sleep_ms(1000)
        lcd.write('Short lines with ..')
        lcd.write(" .. end='' option")
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
        lcd.write('Same lines with ..')
        lcd.write('.. wrap=False option')
        sleep_ms(1500)
        lcd.write('First long line, at least a bit long.', wrap=False)
        sleep_ms(1500)
        lcd.write('Second long line, also a bit long.', wrap=False)
        sleep_ms(2000)
    if _Write_Test_3:
        lcd.write('Lines with 20 ..')
        lcd.write('.. characters.')
        sleep_ms(1500)
        for i in range(1,4):
            lcd.write(f'--20 char line No {i}-')
            sleep_ms(1000)
        sleep_ms(1000)
        lcd.write('Lines with 20 chars.')
        sleep_ms(1000)
        lcd.write('.. followed by ..')
        sleep_ms(1000)
        lcd.write('.. empty lines')
        sleep_ms(1500)
        for i in range(1,4):
            lcd.write(f'--20 char line No {i}-')
            lcd.write()
            sleep_ms(1500)
        sleep_ms(1500)
    if _Write_Test_4:
        lcd.write("'\\n\\n\\n', end=''")  # Use a character that is somewhat similar to backslash, as backslash --> Yen symbol (in my Japanese ROM-Code A00)
        sleep_ms(1500)
        lcd.write('\n\n\n', end='')
        sleep_ms(1500)
        lcd.write('Long line after ..')
        lcd.write('.. move to (4,2)')
        sleep_ms(2500)
        lcd.move_to(4, 2)
        lcd.write('Long long line, again a bit boring..')  # 36 characters, stops at x=20, 
        sleep_ms(1500)



# ---------- Import and Measure Memory Consumption ------------
import gc
from time import sleep_ms
from machine import I2C
gc.collect(); mfree0 = gc.mem_free()
from lcd_i2c8574_x import I2cLcd

i2c = I2C('Y', freq=100000)


lcd = I2cLcd(i2c, 0x27, (20,4))   # 0x27 <-- i2c address, may be changed by soldering connections
gc.collect(); mfree1 = gc.mem_free()

if _Intro_and_Memory:
    print('--- Testing Lcd Driver ---')
    lcd.write('-Testing LCD Driver-')  # 20 Characters, should elicit implicit newline
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
    sleep_ms(3000)
    print('0123456789:;<=>?')
    lcd.write('0123456789:;<=>?')
    sleep_ms(3000)
    print('@ABCDEFGHIJKLMNO')
    lcd.write('@ABCDEFGHIJKLMNO')
    sleep_ms(3000)
    print('PQRSTUVWXYZ[\]^_')
    lcd.write('PQRSTUVWXYZ[\]^_')
    sleep_ms(3000)
    print('`abcdefghijklmno')
    lcd.write('`abcdefghijklmno')
    sleep_ms(3000)
    print('pqrstuvwxyz{|}~')
    lcd.write('pqrstuvwxyz{|}~')
    sleep_ms(3000)
    print('--New in _x Driver--')
    lcd.write('--New in _x Driver--')
    sleep_ms(3000)
    print('£¥€ §¶ °´• √±÷ äöüß')
    lcd.write('£¥€ §¶ °´• √±÷ äöüß')
    sleep_ms(3000)
    print('←→ αβεθμπρσ ΣΩ')
    lcd.write('←→ αβεθμπρσ ΣΩ')
    sleep_ms(3000)

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

if _Write_in_Scroll_Mode:
    # ------ Write Functionality in Scoll Mode ----------
    print('-- Write in Scroll Mode --')
    lcd.write('Write in Scroll Mode')    # Line with 20 characters
    sleep_ms(1500)
    write_tests()

if _Write_without_Scroll:
    # ------ Write Functionality without Scoll Mode ----------
    del lcd
    lcd = I2cLcd(i2c, 0x27, (20,4), scroll=False)   # 0x27 <-- i2c address, may be changed by soldering connections
    lcd.clear()
    print('-- Write without scroll --')
    lcd.write('Write without scroll')    # Line with 20 characters
    sleep_ms(1500)
    write_tests()


