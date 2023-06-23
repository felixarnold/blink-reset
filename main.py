#!/usr/bin/python3

import json
from time import sleep
from RPLCD.i2c import CharLCD
import pyudev
import RPi.GPIO as GPIO
from sys import exit

lcd_address = 0x27
lcd_port = 1
clk = 22
dt = 27
sw = 17
index = 0
selection = None


def rotary_callback(channel):
    global index
    global clk_last_state
    global boards

    clk_state = GPIO.input(clk)
    dt_state = GPIO.input(dt)
    
    if clk_state == 0:
        if dt_state == 1:
            index = (index + 1) % len(boards.keys())
        else:
            index = (index - 1) % len(boards.keys())

        lcd.clear()
        lcd.write_string(list(boards)[index])


def sw_callback(channel):
    global boards
    global index
    global selection

    print(list(boards)[index])
    selection = boards.values()[index]


def select_microcontroller(device):
    global selection
    global index

    vid = device.get('ID_VENDOR_ID')
    pid = device.get('ID_MODEL_ID')

    for board_name, board_data in boards.items():
        if board_data['vid'] == vid and board_data['pid'] == pid:
            return device

    lcd.clear()
    lcd.write_string("Select a MC:")
    lcd.cursor_pos = (1, 0)
    lcd.write_string(list(boards)[index])

    GPIO.add_event_detect(clk, GPIO.FALLING, callback=rotary_callback, bouncetime=50)
    GPIO.add_event_detect(sw, GPIO.FALLING, callback=sw_callback, bouncetime=300)

    while selection is None:
        sleep(1)

    GPIO.remove_event_detect(clk)
    GPIO.remove_event_detect(sw)

    exit()


def flash_microcontroller_board(board_name):
    # Implement the code to flash the microcontroller board with the desired software
    # This can involve communication through USB, UART, SPI, I2C, or other protocols

    # Placeholder code
    print(f"Flashing microcontroller board: {board_name}")


def blink_reset(action, device):
    global boards

    lcd.backlight_enabled = True
    lcd.write_string("Hello")

    if device is None:
        print("No microcontroller boards detected.")
        lcd.clear()
        lcd.write_string("No MC connected")
        sleep(3)
        return

    selected_board = select_microcontroller(device)

    if selected_board is None:
        print("Exiting...")
        lcd.clear()
        lcd.write_string("Exiting...")
        sleep(2)
        return

    # Flash the selected microcontroller board
    flash_microcontroller_board(selected_board)

    lcd.backlight_enabled = False


def main():
    global boards
    global lcd

    with open('boards.json', 'r') as file:
        boards = json.load(file)

    try:
        lcd = CharLCD(
            i2c_expander='PCF8574',
            address=lcd_address,
            port=lcd_port,
            cols=16,
            rows=2)
    except OSError:
        print("Error initializing the LCD display. Please check your I2C bus and address settings.")
        exit(1)

    lcd.backlight_enabled = False

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(clk, GPIO.IN)
    GPIO.setup(dt, GPIO.IN)
    GPIO.setup(sw, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    context = pyudev.Context()
    monitor = pyudev.Monitor.from_netlink(context)
    monitor.filter_by(subsystem="usb")

    observer = pyudev.MonitorObserver(monitor, blink_reset)
    observer.start()

    while True:
        pass


if __name__ == '__main__':
    main()
