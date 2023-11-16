from . import Settings
from ..pressed_keys import PressedKeys
import pynput


class HotkeySettings(Settings):
    def __init__(self, settings_file_location="hotkey_settings.json"):
        super().__init__(settings_file_location=settings_file_location)

    def create(self):
        # Each hotkey is a PressedKey object
        next_hotkey = PressedKeys()
        next_hotkey.add_modifier(pynput.keyboard.Key.up)
        previous_hotkey = PressedKeys()
        previous_hotkey.add_modifier(pynput.keyboard.Key.down)
        mute_hotkey = PressedKeys()
        mute_hotkey.add_modifier(pynput.keyboard.Key.left)
        settings = {
            "next": next_hotkey.hashed,
            "previous": previous_hotkey.hashed,
            "mute": mute_hotkey.hashed
        }
        return settings

    def set_hotkey(self, which, hotkey: PressedKeys):
        self.settings[which] = hotkey.hashed

    def get_next_hotkey(self):
        return PressedKeys(self.settings["next"])

    def get_previous_hotkey(self):
        return PressedKeys(self.settings["previous"])

    def get_mute_hotkey(self):
        return PressedKeys(self.settings["mute"])
