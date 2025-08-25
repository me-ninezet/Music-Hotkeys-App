import logging
import flet as ft
from flet.core.types import MainAxisAlignment
from hotkeys import hotkeys, inic_cfg, restart_controller
global_app = None


def set_global_app(app):
    """
    Sets the global application instance for cross-module access.

    This function provides a centralized way to store and access the main
    application instance from different modules without circular imports.
    """
    global global_app
    global_app = app

def change_cfg(action, new_key, act, page):
    logging.info('Changing cfg')
    with open("config.txt", "r") as file:
        lines = file.readlines()

    new_lines = []
    for line in lines:
        if line.strip() and '=' in line:
            key, value = line.split('=', 1)
            if key.strip() == action:
                new_lines.append(f"{action}={new_key}\n")
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)


    with open("config.txt", "w") as file:
        file.writelines(new_lines)


    act.text = f"{new_key}"
    page.update()
    # logging.info('cfg changed')
    restart_controller()


def design(page: ft.Page):
    """
     Main application UI design and event handling for music hotkeys configuration.

    Creates a responsive interface for managing media control hotkeys with:
    - Interactive button grid for six media control functions
    - Modal dialog for key reassignment
    - System tray minimization functionality
    - Real-time keyboard event capture for key mapping
    """
    waiting_for_input = False
    page.title = "Music Hotkeys"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    dlg_modal = ft.AlertDialog(
        # Modal dialog for capturing keyboard input during hotkey reassignment.
        modal=True,
        actions=[
            ft.TextButton("Отмена", on_click=lambda e: close_dialog(e))
        ],
        title=ft.Text("Нажмите подходящую клавишу"),
        content=ft.Text(""),
        actions_alignment=ft.MainAxisAlignment.END,
    )

    def close_dialog(e: None):
        nonlocal waiting_for_input
        waiting_for_input = False
        page.close(dlg_modal)
        page.update()

    def button_clicked(e):
        global button_text
        button_text = e.control
        global data
        data = e.control.data
        nonlocal waiting_for_input
        waiting_for_input = True
        page.update()
        dlg_modal.content = ft.Text(f"Текущая клавиша: {hotkeys.get(e.control.data)}")
        page.open(dlg_modal)
        page.update()

    def on_keyboard(e: ft.KeyboardEvent):
        nonlocal waiting_for_input

        if waiting_for_input:
            waiting_for_input = False
            page.close(dlg_modal)
            change_cfg(data, e.key, button_text, page)
            page.update()


    page.on_keyboard_event = on_keyboard

    def minimize_to_tray(e):
        page.window.visible = False
        page.update()

    # Creating UI
    page.add(ft.Row(
        controls=[
            ft.Text("Выберите удобные вам горячие клавиши", size=24),
            ft.IconButton(
                icon=ft.Icons.MINIMIZE,
                tooltip="Свернуть в трей",
                on_click=minimize_to_tray
            )
        ],
        alignment=MainAxisAlignment.SPACE_BETWEEN
    ))
    # page.add(ft.Row(controls=[ft.Text("Выберите удобные вам горячие клавиши", size=24)], alignment=MainAxisAlignment.CENTER))
    page.add(ft.Row(controls=
        [ft.Column(controls=[ft.Icon(name=ft.Icons.KEYBOARD_DOUBLE_ARROW_LEFT, size = 50),
            ft.ElevatedButton(text=hotkeys.get('prev'), on_click=button_clicked, data="prev")], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        ft.Column(controls=[ft.Icon(name=ft.Icons.PAUSE, size=50),
                            ft.ElevatedButton(hotkeys.get('pause'), on_click=button_clicked, data='pause')], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        ft.Column(controls=[ft.Icon(name = ft.Icons.KEYBOARD_DOUBLE_ARROW_RIGHT, size = 50),
                            ft.ElevatedButton(hotkeys.get('next'), on_click=button_clicked, data='next')], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        ft.Column(controls=[ft.Icon(name=ft.Icons.VOLUME_DOWN, size = 50),
                            ft.ElevatedButton(hotkeys.get('volume_down'), on_click=button_clicked, data='volume_down')], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        ft.Column(controls=[ft.Icon(name=ft.Icons.VOLUME_OFF, size = 50),
                            ft.ElevatedButton(hotkeys.get('mute'), on_click=button_clicked, data='mute')], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        ft.Column(controls=[ft.Icon(name=ft.Icons.VOLUME_UP, size = 50),
                            ft.ElevatedButton(hotkeys.get('volume_up'), on_click=button_clicked, data='volume_up')], horizontal_alignment=ft.CrossAxisAlignment.CENTER)],
        spacing=70,
        alignment=ft.MainAxisAlignment.CENTER
    ))


    if global_app:
        """
        Stores reference to the current page in the global application instance.
    
        This enables cross-module access to the page object for window management
        operations such as showing/hiding the application window from the system tray.
        """
        global_app.page = page

