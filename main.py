#!/usr/bin/python3

import json
from time import sleep
from RPLCD.i2c import CharLCD
import pyudev
import RPi.GPIO as GPIO
from sys import exit
from datetime import datetime

lcd_address = 0x27
lcd_port = 1
clk = 27
dt = 22
sw = 21
index = 0
clk_last_state = None
selection = None


def rotary_callback(channel):
    global index
    global clk_last_state
    global boards

    clk_state = GPIO.input(clk)
    dt_state = GPIO.input(dt)
    
    if clk_state != clk_last_state:
        if dt_state != clk_state:
            index = (index + 1) % len(boards.keys())
        else:
            index = (index - 1) % len(boards.keys())

        lcd.clear()
        lcd.write_string(list(boards)[index])

        print(datetime.now().timestamp(), index, list(boards)[index])

    clk_last_state = clk_state


def select_microcontroller(device):
    global selection
    global current_index

    vid = device.get('ID_VENDOR_ID')
    pid = device.get('ID_MODEL_ID')

    for board_name, board_data in boards.items():
        if board_data['vid'] == vid and board_data['pid'] == pid:
            return device

    lcd.clear()
    lcd.write_string("Select a MC:")
    lcd.cursor_pos = (1, 0)
    lcd.write_string(list(boards)[current_index])

    GPIO.add_event_detect(
            PIN_B,
            GPIO.FALLING,
            callback=update_list_callback,
            bouncetime=50)

    GPIO.add_event_detect(
            PIN_BUTTON,
            GPIO.RISING,
            callback=select_list_item_callback)

    while selection is None:
        pass

    GPIO.remove_event_detect(PIN_B)
    GPIO.remove_event_detect(PIN_BUTTON)

    # Provide a list of available boards and prompt the user to select one
    print("Available microcontroller boards:")
    for i, board_name in enumerate(boards.keys()):
        print(f"{i+1}. {board_name}")

    try:
        index = int(selection) - 1
        board_name = list(boards.keys())[index]
        return board_name
    except (ValueError, IndexError):
        print("Invalid selection.")
        return None


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

    try:
        GPIO.add_event_detect(clk, GPIO.FALLING, callback=rotary_callback, bouncetime=250)
        while True:
            sleep(1)
    finally:
        GPIO.cleanup()
        lcd.clear()

    context = pyudev.Context()
    monitor = pyudev.Monitor.from_netlink(context)
    monitor.filter_by(subsystem="usb")

    observer = pyudev.MonitorObserver(monitor, blink_reset)
    observer.start()

    while True:
        pass


if __name__ == '__main__':
    main()
