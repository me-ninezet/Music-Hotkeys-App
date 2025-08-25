from time import sleep
from threading import Event
from pyautogui import press
from keyboard import add_hotkey, remove_hotkey
from os.path import dirname, join, abspath
import logging

hotkeys = {}
'''Finding a config path'''
def get_config_path():
    script_dir = dirname(abspath(__file__))
    config_path = join(script_dir, "config.txt")
    if not abspath(config_path).startswith(abspath(script_dir)):
        logging.error("Invalid config path!")
        return None
    return config_path

'''
Getting a config file(config.txt)

Config file format (default keys):
    next=pageup
    prev=pagedown
    pause=home
    mute=end
    volume_down=ins
    volume_up=del
'''

def inic_cfg():
    try:
        with open(get_config_path(), "r") as f:
            for line in f:
                line = line.strip()
                if line and '=' in line:
                    key, value = line.split('=', 1)
                    hotkeys[key.strip()] = value.strip()
        logging.info('Config created')
    except Exception as ex:
        logging.error(ex)
        logging.error("Cant create cfg")


'''
Media hotkeys controller for Yandex Music (or other media players).
    
This class provides system-wide hotkey functionality to control media playback
using simulated key presses.
'''

class YaMusicControl:
    def __init__(self):
        self.is_running = False
        self.handlers = {}
        self._stop_event = Event()

    def next_command(self):
        try:
            # logging.info('Switch to next track')
            press('nexttrack')
            sleep(0.2)
        except Exception as ex:
            logging.error(ex)

    def prev_command(self):
        try:
            # logging.info('Switch to prev track')
            press('prevtrack')
            sleep(0.2)
        except Exception as ex:
            logging.error(ex)

    def playpause_command(self):
        try:
            # logging.info('Play / Pause')
            press('playpause')
            sleep(0.2)
        except Exception as ex:
            logging.error(ex)

    def mute_command(self):
        try:
            # logging.info('Mute')
            press('volumemute')
            sleep(0.2)
        except Exception as ex:
            logging.error(ex)

    def volumeup_command(self):
        try:
            # logging.info('Volume+')
            press('volumeup')
        except Exception as ex:
            logging.error(ex)

    def volumedown_command(self):
        try:
            # logging.info('Volume-')
            press('volumedown')
        except Exception as ex:
            logging.error(ex)

    def setup_hotkeys(self):
        self.remove_hotkeys()
        try:
            self.handlers['next'] = add_hotkey(
                hotkeys.get('next'), self.next_command
            )
            self.handlers['prev'] = add_hotkey(
                hotkeys.get('prev'), self.prev_command
            )
            self.handlers['pause'] = add_hotkey(
                hotkeys.get('pause'), self.playpause_command
            )
            self.handlers['mute'] = add_hotkey(
                hotkeys.get('mute'), self.mute_command
            )
            self.handlers['volume_down'] = add_hotkey(
                hotkeys.get('volume_down'), self.volumedown_command
            )
            self.handlers['volume_up'] = add_hotkey(
                hotkeys.get('volume_up'), self.volumeup_command
            )
            logging.info('Hotkeys setup completed')
        except Exception as e:
            logging.error(f"Error setting up hotkeys: {e}")

    def remove_hotkeys(self):
        for handler in self.handlers.values():
            try:
                remove_hotkey(handler)
            except Exception as ex:
                logging.ERROR(f"An error with removing hotkeys: {ex}")
        self.handlers.clear()
        logging.info('Hotkeys removed')

    def start(self):
        if self.is_running:
            return

        self.is_running = True
        self._stop_event.clear()
        inic_cfg()
        self.setup_hotkeys()
        logging.info('Program started')

        while not self._stop_event.is_set():
            sleep(0.1)

        self.remove_hotkeys()
        self.is_running = False
        logging.info('Program stopped')

    def stop(self):
        self._stop_event.set()
        logging.info('Stop signal sent')

    def restart(self):
        self.stop()
        sleep(0.3)
        self.start()

"""Object of YaMusicControl"""
control = YaMusicControl()


def start_controller():
    control.start()


def stop_controller():
    control.stop()


def restart_controller():
    stop_controller()
    sleep(0.2)
    logging.info('Restarting program')
    start_controller()
