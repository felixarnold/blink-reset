#!/usr/bin/python3
# main.py

# import usb.core
# import usb.util
import json
from time import sleep
from RPLCD.i2c import CharLCD
import pyudev
from ui.rotary_encoder import RotaryEncoder

boards_data = None

LCD_ADDRESS = 0x27
LCD_PORT = 1
lcd = CharLCD(
    i2c_expander='PCF8574',
    address=LCD_ADDRESS,
    port=LCD_PORT,
    cols=16,
    rows=2)

PIN_A = 4
PIN_B = 17
PIN_BUTTON = 27
re = RotaryEncoder(PIN_A, PIN_B, PIN_BUTTON)


def initialize_re():
    re.setup_rotary_encoder()


def select_microcontroller(device):
    vid = device.get('ID_VENDOR_ID')
    pid = device.get('ID_MODEL_ID')
    print(vid)
    print(pid)

    for board_name, board_data in boards_data.items():
        print(board_data['vid'])
        print(board_data['pid'])
        if board_data['vid'] == vid and board_data['pid'] == pid:
            return device

    # Provide a list of available boards and prompt the user to select one
    print("Available microcontroller boards:")
    for i, board_name in enumerate(boards_data.keys()):
        print(f"{i+1}. {board_name}")

    selection = input("Enter the number of the board you want to select: ")

    try:
        index = int(selection) - 1
        board_name = list(boards_data.keys())[index]
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
    global boards_data
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
    global boards_data

    lcd.backlight_enabled = False

    with open('boards.json', 'r') as file:
        boards_data = json.load(file)

    context = pyudev.Context()
    monitor = pyudev.Monitor.from_netlink(context)
    monitor.filter_by(subsystem="usb")

    observer = pyudev.MonitorObserver(monitor, blink_reset)
    observer.start()

    initialize_re()

    while True:
        pass


if __name__ == '__main__':
    main()
