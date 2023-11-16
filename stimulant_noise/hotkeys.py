import pynput

from .preset import PresetsManager
from .pressed_keys import PressedKeys
from .settings.hotkeys import HotkeySettings

import queue


class Hotkeys:

    def __init__(self, settings: HotkeySettings, presets_manager: PresetsManager, main_queue: queue.Queue):
        self.settings = settings
        self.pressed_keys = PressedKeys()
        self.next = PressedKeys(hashed=self.settings.settings['next'])
        self.previous = PressedKeys(hashed=self.settings.settings['previous'])
        self.mute = PressedKeys(hashed=self.settings.settings['mute'])

        self.presets_manager = presets_manager
        self.main_queue = main_queue

        self.which = False

    def run(self):
        with pynput.keyboard.Listener(on_press=self.on_press, on_release=self.on_release) as self.listener:
            self.listener.join()

    def on_press(self, key):
        if self.which:
            self.on_press_change(key)
        else:
            self.on_press_default(key)

    def on_release(self, key):
        if self.which:
            self.on_release_change(key)
        else:
            self.on_release_default(key)

    def on_press_default(self, key):
        try:
            if key.value is not None:
                self.pressed_keys.add_modifier(key)
        except AttributeError:
            self.pressed_keys.set_key(key)
        if self.pressed_keys.hashed == self.next.hashed:
            self.presets_manager.next_preset()
            self.main_queue.put({
                'name': 'next_preset'
            })
        elif self.pressed_keys.hashed == self.previous.hashed:
            self.presets_manager.previous_preset()
            self.main_queue.put({
                'name': 'previous_preset'
            })
        elif self.pressed_keys.hashed == self.mute.hashed:
            self.presets_manager.mute_current_preset()
            self.main_queue.put({
                'name': 'mute_preset'
            })
        else:
            pass

    def on_press_change(self, key):
        try:
            if key == pynput.keyboard.Key.esc:
                self.which = False
                return False
            if key.value is not None:
                self.pressed_keys.add_modifier(key)
        except AttributeError as e:
            if "'KeyCode' object has no attribute 'value'" in str(e):
                self.pressed_keys.set_key(key)
            else:
                raise e

    def on_release_default(self, key):
        try:
            if key.value is not None:
                self.pressed_keys.remove_modifier(key)
        except AttributeError as e:
            if "'KeyCode' object has no attribute 'value'" in str(e):
                self.pressed_keys.remove_key()
        except KeyError:
            pass

    def on_release_change(self, key):
        try:
            if key.value is not None:
                try:
                    self.pressed_keys.remove_modifier(key)
                except KeyError:
                    pass
        except AttributeError as e:
            if "'KeyCode' object has no attribute 'value'" in str(e):
                if self.which == 'next':
                    self.settings.set_hotkey('next', self.pressed_keys)
                    self.next = PressedKeys(hashed=self.settings.settings['next'])
                    self.which = False
                elif self.which == 'previous':
                    self.settings.set_hotkey('previous', self.pressed_keys)
                    self.previous = PressedKeys(hashed=self.settings.settings['previous'])
                    self.which = False
                elif self.which == 'mute':
                    self.settings.set_hotkey('mute', self.pressed_keys)
                    self.mute = PressedKeys(hashed=self.settings.settings['mute'])
                    self.which = False
            else:
                raise e

    def set_which(self, which):
        self.which = which
