# lcd.py

import smbus2 as smbus
import time

LCD_CMD = 0
LCD_DAT = 1

# LCD commands
LCD_CLEARDISPLAY = 0x01
LCD_RETURNHOME = 0x02
LCD_ENTRYMODESET = 0x04
LCD_BACKLIGHT = 0x08
LCD_FUNCTIONSET = 0x20
LCD_SETDDRAMADDR = 0x80

# LCD flags for display entry mode
LCD_ENTRYLEFT = 0x02
LCD_ENTRYSHIFTDECREMENT = 0x00

# LCD flags for display on/off control
LCD_DISPLAYON = 0x04
LCD_CURSOROFF = 0x00
LCD_BLINKOFF = 0x00

# LCD flags for function set
LCD_2LINE = 0x08
LCD_5X8DOTS = 0x00


class LCD:
    def __init__(self, i2c_address):
        self.bus = smbus.SMBus(1)  # Use I2C bus number 1
        self.i2c_address = i2c_address

        self.bus.write_byte(self.i2c_address, 0x03)
        self.bus.write_byte(self.i2c_address, 0x03)
        self.bus.write_byte(self.i2c_address, 0x03)
        self.bus.write_byte(self.i2c_address, 0x02)

        # Initialize the LCD module
        self._send_command(
            LCD_FUNCTIONSET |
            LCD_2LINE |
            LCD_5X8DOTS)
        self._send_command(
            LCD_BACKLIGHT |
            LCD_DISPLAYON)
        self._send_command(LCD_CLEARDISPLAY)
        self._send_command(
            LCD_ENTRYMODESET |
            LCD_ENTRYLEFT)
        time.sleep(0.2)

    def _send_command(self, cmd):
        # Send a command to the LCD
        self.bus.write_byte_data(self.i2c_address, LCD_CMD, cmd)
        time.sleep(0.01)

    def _send_data(self, data):
        # Send data to the LCD
        self.bus.write_byte_data(self.i2c_address, LCD_DAT, data)
        time.sleep(0.01)

    def clear(self):
        # Clear the LCD display
        self._send_command(LCD_CLEARDISPLAY)

    def home(self):
        # Return the cursor to the home position
        self._send_command(LCD_RETURNHOME)

    def set_cursor(self, col, row):
        # Set the cursor position
        position = col + (0x40 * row)
        self._send_command(LCD_SETDDRAMADDR | position)

    def write(self, message):
        # Write a message to the LCD
        for char in message:
            self._send_data(ord(char))

    def write_line(self, message, row):
        # Write a message to a specific line on the LCD
        self.set_cursor(0, row)
        self.write(message)
