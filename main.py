#!/usr/bin/python3

import json
from time import sleep
from RPLCD.i2c import CharLCD
import pyudev
import RPi.GPIO as GPIO

boards = None
current_index = 0
selection = None

LCD_ADDRESS = 0x27
LCD_PORT = 1
lcd = CharLCD(
    i2c_expander='PCF8574',
    address=LCD_ADDRESS,
    port=LCD_PORT,
    cols=16,
    rows=2)

PIN_BUTTON = 21
PIN_A = 22
PIN_B = 23

GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN_BUTTON, GPIO.IN)
GPIO.setup(PIN_A, GPIO.IN)
GPIO.setup(PIN_B, GPIO.IN)


def update_list_callback(channel):
    global current_index

    if GPIO.input(PIN_A):
        # clockwise
        current_index = (current_index + 1) % len(boards.keys())
    else:
        # counter-clockwise
        current_index = (current_index - 1) % len(boards.keys())

    lcd.cursor_pos(1, 0)
    lcd.write_string(boards.keys()[current_index])
    pass


def select_list_item_callback(channel):
    global current_index
    global selection

    selection = boards[current_index]
    pass


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

    GPIO.add_event_detect(
            PIN_B,
            GPIO.RISING,
            callback=update_list_callback,
            bouncetime=50)

    GPIO.add_event_detect(
            PIN_BUTTON,
            GPIO.RISING,
            callback=select_list_item_callback)

    while selection is None:
        lcd.cursor_pos(1, 0)
        text = boards.keys()[current_index]
        lcd.write_string(text)
        sleep(.5)

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

    lcd.backlight_enabled = False

    with open('boards.json', 'r') as file:
        boards = json.load(file)

    context = pyudev.Context()
    monitor = pyudev.Monitor.from_netlink(context)
    monitor.filter_by(subsystem="usb")

    observer = pyudev.MonitorObserver(monitor, blink_reset)
    observer.start()

    while True:
        pass


if __name__ == '__main__':
    main()
