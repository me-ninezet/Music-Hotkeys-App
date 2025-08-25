import logging
import flet as ft
from hotkeys import inic_cfg, start_controller, stop_controller
from design import design
from tray_manager import TrayIconManager
import threading
import time
import os

# Logging settings
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='music_app.log',
    filemode='w'
    # handlers=[
    #     logging.FileHandler("music_app.log"),
    #     # logging.StreamHandler()
    # ]
)


class MusicApp:
    def __init__(self):
        self.page = None
        self.tray_manager = None
        self.is_running = True
        self.app_started = False
        self.gui_closed = threading.Event()

    def show_window(self):
        """Showing the window"""
        try:
            if self.page and hasattr(self.page, 'window'):
                self.page.window.visible = True
                self.page.window.to_front()
                self.page.update()
                return True
        except Exception as e:
            logging.error(f"Error with showing the window: {e}")
        return False

    def hide_window(self):
        """Hiding the window"""
        try:
            if self.page and hasattr(self.page, 'window'):
                self.page.window.visible = False
                self.page.update()
                return True
        except Exception as e:
            logging.error(f"Error with hiding the window: {e}")
        return False

    def design_wrapper(self, page: ft.Page):
        """
        Design with support trey icon
        """
        self.page = page

        # Window settings
        page.window.width = 800
        page.window.height = 600
        page.window.visible = True

        # window closing handler(dont work now)
        def window_event(e):
            if e.data == "close":
                logging.info("Окно закрыто, сворачиваем в трей")
                self.hide_window()
                e.page.window.destroy = False

        page.on_window_event = window_event

        # Start main design
        design(page)

        logging.info("GUI started")
        self.app_started = True

        # Wait for closing GUI
        while not self.gui_closed.is_set():
            time.sleep(0.1)

    def stop_controller(self):
        """Stop media controller"""
        try:
            stop_controller()
        except Exception as e:
            logging.error(f"Error with stopping controller: {e}")

    def start_controller(self):
        """Starts the media controller in a personal thread"""

        def controller_thread():
            try:
                start_controller()
                # logging.info("Медиа контроллер запущен")

                # Wait for app
                while self.is_running:
                    time.sleep(0.1)

            except Exception as e:
                logging.error(f"Error with controler starting: {e}")

        thread = threading.Thread(target=controller_thread, daemon=True)
        thread.start()
        return thread

    def setup_tray(self):
        """Setup tray icon"""
        try:
            self.tray_manager = TrayIconManager(self)
            # Start trey in a personal thread
            tray_thread = threading.Thread(target=self.tray_manager.run, daemon=True)
            tray_thread.start()
            # logging.info("Tray manager started")
            return True
        except Exception as e:
            logging.error(f"Error with trey icon setup: {e}")
            return False

    def start(self):
        """Starting app"""
        # logging.info("Запуск приложения...")

        # Initiation cfg
        # inic_cfg()

        try:
            # Start media controller
            controller_thread = self.start_controller()

            # Start trey
            self.setup_tray()

            # Waiting for trey starting
            time.sleep(0.15)

            # Start GUI in main thread
            logging.info("GUI Started")
            ft.app(target=self.design_wrapper)

        except KeyboardInterrupt:
            logging.info("App closed by user")
        except Exception as ex:
            logging.error(f"Starting error: {ex}")
        finally:
            self.clean_exit()

    def clean_exit(self):
        # Clean exit from app
        logging.info("Start clean exit")
        self.is_running = False
        try:
            stop_controller()
            # logging.info("Контроллер остановлен")
        except Exception as e:
            logging.error(f"Controller stop error: {e}")

        # Closing all processes
        self.close_processes()

        # Exit
        logging.info("App closed")
        os._exit(0)  # Forced exit


    def close_processes(self):
        try:
            import gc
            gc.collect()
            logging.info("Garbage collection completed")
        except Exception as ex:
            logging.error(f"Error with closing processes: {ex}")

    # def stop(self):
    #     """Останавливает приложение"""
    #     self.is_running = False
    #     self.gui_closed.set()
    #     logging.info("Остановка приложения...")
    #     self.stop_controller()
    #     if self.tray_manager:
    #         self.tray_manager.stop()
    #     logging.info("Приложение остановлено")


def main():
    app = MusicApp()
    app.start()


if __name__ == "__main__":
    main()