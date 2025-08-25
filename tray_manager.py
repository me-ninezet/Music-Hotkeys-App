import pystray
from PIL import Image, ImageDraw
import logging
import os


"""
    System tray icon manager for the music hotkeys application.
    
    Provides a persistent tray icon with menu controls for managing the application
    window and exit functionality. The tray icon remains active even when the main
    window is hidden, allowing background operation.
"""

class TrayIconManager:
    def __init__(self, app_instance):
        self.app = app_instance
        self.icon = None
        self.is_running = True

    def create_icon_image(self, size=32):
        """Creating an image"""
        image = Image.new('RGB', (size, size), color=(70, 130, 180))
        dc = ImageDraw.Draw(image)
        dc.text((size // 2, size // 2), "M", fill="white", anchor="mm")
        return image

    def on_show(self, icon, item):
        """Showing window"""
        logging.info("Show the window")
        if self.app and hasattr(self.app, 'show_window'):
            self.app.show_window()

    def on_hide(self, icon, item):
        """Hiding window"""
        logging.info("Hide the window")
        if self.app and hasattr(self.app, 'hide_window'):
            self.app.hide_window()

    def on_exit(self, icon, item):
        """Clean exit from app"""
        logging.info("Clean exit from app...")

        # 1. Stop trey icon
        if self.icon:
            try:
                self.icon.stop()
            except:
                pass

        # 2. Trying to clean exit
        if self.app and hasattr(self.app, 'clean_exit'):
            self.app.clean_exit()
        else:
            # Emergency exit
            os._exit(0)


    def run(self):
        """Start icon in tray"""
        try:
            image = self.create_icon_image()

            menu = pystray.Menu(
                pystray.MenuItem('Показать окно', self.on_show),
                pystray.MenuItem('Скрыть в трей', self.on_hide),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem('Выход', self.on_exit)
            )

            self.icon = pystray.Icon(
                "music_hotkeys",
                image,
                "Music Hotkeys Controller",
                menu
            )

            logging.info("Trey icon started")
            self.icon.run()

        except Exception as e:
            logging.error(f"Trey error: {e}")

    def stop(self):
        """Stop the icon"""
        self.is_running = False
        if self.icon:
            try:
                self.icon.stop()
                logging.info("Trey icon stopped")
            except Exception as e:
                logging.error(f"Icon stopped error: {e}")