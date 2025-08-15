import subprocess
import time
import pyautogui
import config

def send_with_gui(mb4_path):
    subprocess.Popen([config.ROBOLauncher])
    time.sleep(config.ROBO_OPEN_TIMEOUT)

    pyautogui.click(*config.COORD_OPEN_BUTTON)
    time.sleep(0.8)
    pyautogui.click(*config.COORD_FILENAME_INPUT)
    pyautogui.hotkey('ctrl', 'a')
    pyautogui.typewrite(mb4_path)
    pyautogui.press('enter')
    time.sleep(1.0)
    pyautogui.click(*config.COORD_SEND_BUTTON)
    time.sleep(2.0)
