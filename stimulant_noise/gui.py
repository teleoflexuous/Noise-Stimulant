from typing import Any, Optional, Union
import flet as ft
from flet.alignment import Alignment
from flet.border import Border
from flet.control import Control, OptionalNumber
from flet.gradients import Gradient
from flet.ref import Ref
from flet.types import AnimationValue, BlendMode, BorderRadiusValue, BoxShape, ClipBehavior, ImageFit, ImageRepeat, MarginValue, OffsetValue, PaddingValue, ResponsiveNumber, RotateValue, ScaleValue

from .hotkeys import Hotkeys
from .preset import PresetsManager


class SideBar:
    def __init__(self, presets_manager: PresetsManager) -> None:
        self.presets_manager: PresetsManager = presets_manager

    def build(self):

        presets = self.presets_manager.presets_manager_settings.groups.groups[self.presets_manager.presets_manager_settings.groups.current_group]

        preset_buttons = []

        for preset_name in presets:
            preset_button = ft.ElevatedButton(text=preset_name, on_click=lambda _: self.presets_manager.set_current_preset(preset_name))
            preset_buttons.append(preset_button)

        next_preset_button = ft.FilledTonalButton(text='Down', icon=ft.icons.KEYBOARD_ARROW_DOWN_ROUNDED,
                                                  style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
                                                  on_click=self.next_preset, width=100)
        previous_preset_button = ft.FilledTonalButton(text='Up', icon=ft.icons.KEYBOARD_ARROW_UP_ROUNDED,
                                                      style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
                                                      on_click=self.previous_preset, width=100)

        container = ft.Container(ft.Column([
            ft.Text(self.presets_manager.current_preset.name),
            next_preset_button,
            *preset_buttons,
            previous_preset_button,
            ft.FilledTonalButton(text="Lower", icon=ft.icons.KEYBOARD_ARROW_DOWN_ROUNDED),
            ft.FilledTonalButton(text="Higher", icon=ft.icons.KEYBOARD_ARROW_UP_ROUNDED),
            ft.FilledTonalButton(text="Add new preset", icon=ft.icons.PLUS_ONE),

        ]))

        return container


class GUI:
    def __init__(self,
                 presets_manager: PresetsManager,
                 hotkeys: Hotkeys,
                 queue
                 ):

        self.presets_manager = presets_manager
        self.hotkeys = hotkeys

        self.queue = queue

        self.current_preset = self.presets_manager.get_current_preset()

        self.page = None

    def main(self, page: ft.Page):
        self.page = page
        self.build_page()
        self.build_container()

    def build_page(self):
        self.page.title = "Noise Generator"
        self.page.update()
        self.page.theme_mode = "system"
        self.page.theme = ft.Theme(color_scheme_seed="deepPurple50", font_family="Roboto Bold Italic")
        self.page.window_width = 800
        self.page.window_resizeable = False
        self.page.scroll = ft.ScrollMode.ADAPTIVE
        self.page.on_disconnect = lambda _: self.queue.put({'name': 'close_all'})

    def build_container(self):
        left_column = self.build_left_column()
        left_container = ft.Container(content=left_column,
                                      margin=4,
                                      padding=4,
                                      width=500,
                                      border_radius=10,
                                      )
        right_column = self.build_right_column()
        right_container = ft.Container(content=right_column,
                                       margin=4,
                                       padding=4,
                                       width=200,
                                       border_radius=10,
                                       alignment=ft.alignment.top_center
                                       )

        rows = ft.Row(controls=[left_container, right_container],
                      vertical_alignment=ft.CrossAxisAlignment.START,
                      )
        self.page.controls = [rows]
        self.page.update()

    def build_left_column(self):
        pick_files_dialog = ft.FilePicker(on_result=self.add_sounds)
        self.page.overlay.append(pick_files_dialog)
        add_sound_button = ft.FloatingActionButton(text='Add sounds',
                                                   icon=ft.icons.ADD_CIRCLE,
                                                   on_click=lambda _: pick_files_dialog.pick_files(
                                                       allow_multiple=True,
                                                   ))
        change_preset_name_button = ft.FloatingActionButton(text='Change preset name',
                                                            icon=ft.icons.EDIT,
                                                            height=30,
                                                            on_click=self.display_change_current_preset_name_dialog)
        remove_preset_button = ft.FloatingActionButton(text='Remove preset',
                                                       icon=ft.icons.DELETE,
                                                       height=30,
                                                       on_click=self.remove_preset)
        volume_slider = ft.Slider(
            value=self.current_preset.volume,
            min=0,
            max=100,
            on_change=lambda e: self.set_preset_volume(e),
            width=300,
            height=30,
        )

        preset_mute_toggle = ft.Checkbox(label='Mute', value=self.current_preset.mute,
                                         on_change=lambda e: self.mute_current_preset(e))

        slider_row = ft.Row(controls=[ft.Text('Volume'), volume_slider, preset_mute_toggle])

        options_row = ft.Row(controls=[change_preset_name_button, remove_preset_button])

        preset_options_row = ft.ResponsiveRow(controls=[slider_row, options_row])

        left_column = ft.Column(
            controls=[ft.Text(self.current_preset.name, size=20, weight='w600'),
                      preset_options_row, self.build_sounds_column(), add_sound_button],
            spacing=10, scroll='auto'
        )
        return left_column

    def build_right_column(self):
        self.presets_manager.load_presets()
        
        return SideBar(self.presets_manager).build()

    def set_dark_mode(self, e):
        self.page.theme_mode = self.page.theme_mode == "dark" and "light" or "dark"
        self.page.update()

    def build_sounds_column(self):
        names = []
        sliders = []
        toggles = []
        remove_buttons = []
        for sound_name, sound_settings in self.current_preset.sounds.items():
            sound_container = self.build_sound_row(sound_name, sound_settings)
            names.append(sound_container[0])
            sliders.append(sound_container[1])
            toggles.append(sound_container[2])
            remove_buttons.append(sound_container[3])

        names_column = ft.Column(controls=names, spacing=10)
        sliders_column = ft.Column(controls=sliders, spacing=10)
        toggles_column = ft.Column(controls=toggles, spacing=10)
        remove_buttons_column = ft.Column(controls=remove_buttons, spacing=10)
        sounds_row = ft.Row(controls=[names_column, sliders_column, toggles_column, remove_buttons_column], spacing=5)
        return sounds_row

    def next_preset(self, e):
        self.current_preset = self.presets_manager.next_preset()
        self.build_container()

    def previous_preset(self, e):
        self.current_preset = self.presets_manager.previous_preset()
        self.build_container()

    def add_sounds(self, e: ft.FilePickerResultEvent):
        sounds = []
        for file in e.files:
            print(f'Adding sound {file.name}, path: {file.path}, size: {file.size}')
            sounds.append(file.path)
        print(f'Adding sounds: {sounds}')
        self.presets_manager.add_sounds(sounds)
        self.build_container()

    def build_sound_row(self, sound_file_name, sound_settings):
        sound_name = ft.Text(sound_file_name.split('.')[0])
        sound_name_container = ft.Container(content=sound_name, padding=2, height=50, border_radius=10)
        volume_slider = ft.Slider(
            min=0,
            max=100,
            value=sound_settings['volume'],
            on_change=lambda e: self.set_sound_volume(sound_file_name, e)
        )
        volume_slider_container = ft.Container(content=volume_slider, padding=2, height=50, border_radius=10)
        mute_button = ft.Checkbox(label='Mute', value=sound_settings['mute'],
                                  on_change=lambda e: self.mute_sound(sound_file_name, e))
        mute_button_container = ft.Container(content=mute_button, padding=2, height=50, border_radius=10)
        remove_button = ft.FloatingActionButton(text='Remove',
                                                icon=ft.icons.REMOVE_CIRCLE,
                                                on_click=lambda _: self.remove_sound(sound_file_name),
                                                width=100,
                                                height=30,
                                                shape=ft.RoundedRectangleBorder(radius=10))
        remove_button_container = ft.Container(content=remove_button, padding=2, height=50, border_radius=10)
        return sound_name_container, volume_slider_container, mute_button_container, remove_button_container

    def set_sound_volume(self, sound_name, e):
        volume = e.control.value
        self.presets_manager.set_sound_volume(sound_name, volume)
        if self.current_preset.sounds[sound_name]['mute']:
            self.set_mute_from_slider(sound_name, False)

    def set_mute_from_slider(self, sound_name, mute):
        self.presets_manager.set_sound_mute(sound_name, mute)
        columns_count = len(self.page.controls[0].controls[0].content.controls[2].controls[0].controls)
        for column_id in range(columns_count):
            if self.page.controls[0].controls[0].content.controls[2].controls[0].controls[column_id].\
                    content.value == sound_name.split('.')[0]:
                self.page.controls[0].controls[0].content.controls[2].controls[2].controls[column_id].\
                    content.value = mute
                break
        self.page.update()

    def mute_current_preset(self, e):
        self.presets_manager.mute_current_preset()

    def mute_sound(self, sound_name, e):
        mute = e.control.value
        self.presets_manager.set_sound_mute(sound_name, mute)

    def remove_sound(self, sound_name):
        self.presets_manager.remove_sound(sound_name)
        self.build_container()

    def build_presets_column(self):
        rows = []
        for preset_name in self.presets_manager.presets_order:
            preset_button = ft.ElevatedButton(
                text=preset_name,
                on_click=lambda e: self.change_preset(e.control.text)
            )
            rows.append(preset_button)
        column = ft.Column(controls=rows, spacing=5, width=200, height=350, scroll="auto")
        container = ft.Container(content=column, padding=ft.padding.all(5))
        return container

    def change_preset(self, preset_name):
        self.current_preset = self.presets_manager.set_current_preset(preset_name)
        self.build_container()

    def display_new_preset_dialog(self):
        user_input_dialog = ft.TextField(label="Name", on_submit=lambda e: self.add_preset(e.control.value))
        submit_button = ft.ElevatedButton(text='Create New Preset',
                                          on_click=lambda _: self.add_preset(user_input_dialog.value))
        dialog_container = ft.Container(
            content=ft.Column(controls=[user_input_dialog, submit_button], spacing=10),
            height=200,
            border_radius=10,
            margin=ft.margin.all(10)
        )
        bottom_sheet = ft.BottomSheet(content=dialog_container)
        self.page.dialog = bottom_sheet
        bottom_sheet.open = True
        self.page.update()

    def close_dialog(self):
        self.page.dialog.open = False

    def add_preset(self, preset_name):
        try:
            self.presets_manager.add_preset(preset_name, after_preset_name=self.current_preset.name)
        except Exception as e:
            if 'already exists' in str(e):
                self.page.dialog.content.content.controls[1].error_text = 'Preset with this name already exists'
                self.page.update()
                return
        self.close_dialog()
        self.current_preset = self.presets_manager.set_current_preset(preset_name)
        self.build_container()

    def remove_preset(self, e):
        current_preset_name = self.current_preset.name
        self.current_preset = self.presets_manager.previous_preset()
        self.presets_manager.remove_preset(current_preset_name)
        self.build_container()

    def set_preset_volume(self, e):
        self.presets_manager.set_preset_volume(self.current_preset.name, float(e.control.value))
        self.page.controls[0].controls[0].content.controls[1].controls[0].controls[2].value = False
        self.page.update()

    def display_change_current_preset_name_dialog(self, e):
        new_preset_text = ft.Text(f'Change {self.current_preset.name} name to:')
        user_input_dialog = ft.TextField(label="Name")
        submit_button = ft.ElevatedButton(text='Change name',
                                          on_click=lambda _: self.change_preset_name(user_input_dialog.value))
        dialog_container = ft.Container(
            content=ft.Column(controls=[new_preset_text, user_input_dialog, submit_button], spacing=10),
            height=200,
            border_radius=10,
        )
        bottom_sheet = ft.BottomSheet(content=dialog_container)
        self.page.dialog = bottom_sheet
        bottom_sheet.open = True
        self.page.update()

    def change_preset_name(self, preset_name):
        self.presets_manager.change_preset_name(self.current_preset.name, preset_name)
        self.current_preset = self.presets_manager.set_current_preset(preset_name)
        self.build_left_column()
        self.close_dialog()
        self.build_container()

    def display_change_hotkeys_dialog(self):
        dialog_container = self.build_change_hotkeys_dialog()
        bottom_sheet = ft.BottomSheet(content=dialog_container,
                                      on_dismiss=lambda e: self.finish_hotkey_change(e),
                                      open=True)
        self.page.dialog = bottom_sheet
        self.page.update()

    def build_change_hotkeys_dialog(self):
        previous_hotkey_row = self.build_hotkey_row('previous')
        next_hotkey_row = self.build_hotkey_row('next')
        mute_hotkey_row = self.build_hotkey_row('mute')

        hotkeys_column = ft.Column(controls=[previous_hotkey_row, next_hotkey_row, mute_hotkey_row],
                                   alignment='center', spacing=10)

        dialog_container = ft.Container(
            content=ft.Column(controls=[hotkeys_column], spacing=10), height=150,
            border_radius=10, alignment=ft.alignment.center, margin=ft.margin.all(10),
        )
        return dialog_container

    def build_hotkey_row(self, hotkey_name):
        hotkey_name_formatted = hotkey_name.capitalize()
        if hotkey_name == 'previous':
            current_hotkey = self.hotkeys.previous
            icon = ft.Icon(name=ft.icons.KEYBOARD_ARROW_UP_ROUNDED)
        elif hotkey_name == 'next':
            current_hotkey = self.hotkeys.next
            icon = ft.Icon(name=ft.icons.KEYBOARD_ARROW_DOWN_ROUNDED)
        elif hotkey_name == 'mute':
            current_hotkey = self.hotkeys.mute
            icon = ft.Icon(name=ft.icons.VOLUME_OFF_ROUNDED)
        else:
            raise ValueError(f'Unknown hotkey name {hotkey_name}')

        hotkey_text = ft.Text(f'{hotkey_name_formatted}', weight='w600')
        hotkey_row = ft.Row(controls=[hotkey_text, icon], alignment='spaceAround')
        text_container = ft.Container(content=hotkey_row, width=100, border_radius=5, border=ft.border.all(1))

        readable_hotkey = current_hotkey.human_readable

        change_hotkey_button = ft.ElevatedButton(text='Change',
                                                 on_click=lambda e_: self.activate_hotkey_change(hotkey_name))
        button_container = ft.Container(content=change_hotkey_button, width=100, alignment=ft.alignment.center)
        hotkey_display = ft.Text(readable_hotkey, size=20)

        display_container = ft.Container(content=hotkey_display, width=250, border_radius=10, border=ft.border.all(3),
                                         alignment=ft.alignment.center)

        hotkey_row = ft.Row(controls=[text_container, display_container, button_container],
                            alignment='spaceEvenly', vertical_alignment="center", spacing=10)
        return hotkey_row

    def activate_hotkey_change(self, hotkey_name):
        self.hotkeys.set_which(hotkey_name)
        while self.page.dialog.open:
            if hotkey_name == 'previous':
                self.page.dialog.content.content.controls[0].controls[0].controls[1].content.value = self.hotkeys.previous.human_readable
            elif hotkey_name == 'next':
                self.page.dialog.content.content.controls[0].controls[1].controls[1].content.value = self.hotkeys.next.human_readable
            elif hotkey_name == 'mute':
                self.page.dialog.content.content.controls[0].controls[2].controls[1].content.value = self.hotkeys.mute.human_readable
            self.page.update()

    def finish_hotkey_change(self, e):
        self.hotkeys.set_which(False)
        self.hotkeys.settings.save()

    def rebuild_on_hotkey(self):
        self.current_preset = self.presets_manager.get_current_preset()
        self.build_container()

    def run(self):
        ft.app(target=self.main)
