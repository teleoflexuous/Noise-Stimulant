import os
import json
import pynput
from .pressed_keys import PressedKeys
import shutil


# Classes for settings component of the program


class Settings:
    def __init__(self, settings_file_location):
        self.settings_file_location = settings_file_location
        self.settings = self.load_or_create()
        self.save()

    def load_or_create(self):
        try:
            settings = self.load()
        except FileNotFoundError:
            settings = self.create()
        except json.decoder.JSONDecodeError:
            settings = self.create()
        return settings

    def load(self):
        with open(self.settings_file_location, "r") as f:
            settings = json.load(f)
        return settings

    def save(self):
        with open(self.settings_file_location, "w") as f:
            json.dump(self.settings, f, indent=4, sort_keys=True)

    def create(self):
        pass


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


class InternalSettings(Settings):
    def __init__(self, settings_file_location="internal_settings.json"):
        super().__init__(settings_file_location=settings_file_location)
        self.sounds_dir = self.settings["sounds_dir"]
        self.presets_dir = self.settings["presets_dir"]

    def create(self):
        settings = {
            # 2 folders in 'stimulant_noise' folder
            "sounds_dir": "sounds",
            "presets_dir": "presets"
        }
        return settings


class PresetSettings(Settings):
    def __init__(self, settings_file_location=None, internal_settings=None):
        if settings_file_location is None:
            settings_file_location = os.path.join(internal_settings.presets_dir,
                                                  f"Preset_{len(os.listdir(internal_settings.presets_dir))}.json")
        self.name = os.path.splitext(os.path.basename(settings_file_location))[0]
        if internal_settings is None:
            internal_settings = InternalSettings()
        self.internal_settings = internal_settings
        super().__init__(settings_file_location=settings_file_location)

    def create(self):
        settings = {
            "name": self.name,
            "volume": 50,
            "mute": True,
            "sounds": {
            },
        }
        return settings

    def add_sound(self, path, volume=0.5, mute=True):
        sound_name = os.path.basename(path)
        if sound_name in self.settings["sounds"]:
            raise Exception("Sound already exists")
        self.settings["sounds"][sound_name] = {
            "path": path,
            "volume": volume,
            "mute": mute,
        }
        return sound_name

    def remove_sound(self, sound_name):
        if sound_name not in self.settings["sounds"]:
            raise Exception("Sound does not exist")
        del self.settings["sounds"][sound_name]
        return self.settings["sounds"]

    def set_volume(self, volume):
        self.settings["volume"] = volume
        return volume

    def set_mute(self, mute):
        self.settings["mute"] = mute
        return mute

    def set_name(self, name):
        self.settings["name"] = name
        return name

    def set_sound_volume(self, sound_name, volume):
        if sound_name not in self.settings["sounds"]:
            return False
        self.settings["sounds"][sound_name]["volume"] = volume
        return True

    def set_sound_mute(self, sound_name, mute):
        if sound_name not in self.settings["sounds"]:
            return False
        self.settings["sounds"][sound_name]["mute"] = mute
        return True


class PresetsManagerSettings(Settings):
    def __init__(self, settings_file_location="presets_settings.json", internal_settings=None):
        if internal_settings is None:
            internal_settings = InternalSettings()
        self.internal_settings = internal_settings
        super().__init__(settings_file_location=settings_file_location)

    def create(self):
        settings = {
            "presets": {
                # "preset_name": preset_path
            },
            "presets_order": [],
            "current_preset": "None",
        }
        # Check if the presets directory exists. If not, create it.
        if not os.path.exists(self.internal_settings.presets_dir):
            os.mkdir(self.internal_settings.presets_dir)
        # Check if the directory is empty. If so, create a default preset.
        if len(os.listdir(self.internal_settings.presets_dir)) == 0:
            PresetSettings(internal_settings=self.internal_settings)

        for preset in os.listdir(self.internal_settings.presets_dir):
            preset_path = os.path.join(self.internal_settings.presets_dir, preset)
            preset_name = PresetSettings(preset_path, internal_settings=self.internal_settings).settings["name"]
            settings["presets"][preset_name] = preset_path
            settings["presets_order"].append(preset_name)

        settings["current_preset"] = settings["presets_order"][0]

        return settings

    def add_preset(self, preset_name, to_order=True):
        if preset_name in self.settings["presets"]:
            raise ValueError("Preset with name {} already exists".format(preset_name))
        preset_path = os.path.join(self.internal_settings.presets_dir, preset_name + ".json")
        PresetSettings(preset_path, internal_settings=self.internal_settings)
        self.settings["presets"][preset_name] = preset_path
        if to_order:
            self.settings["presets_order"].append(preset_name)

    def remove_preset(self, preset_name):
        os.remove(self.settings["presets"][preset_name])
        del self.settings["presets"][preset_name]
        self.settings["presets_order"].remove(preset_name)

    def set_current_preset(self, preset_name):
        if preset_name not in self.settings["presets"].keys():
            raise ValueError("Preset does not exist")
        self.settings["current_preset"] = preset_name
        return self.settings["current_preset"]

    def change_preset_order(self, preset_name, after_preset_name):
        if preset_name not in self.settings["presets"]:
            raise ValueError("Preset does not exist")
        if after_preset_name not in self.settings["presets"]:
            raise ValueError("Preset does not exist")
        self.settings["presets_order"].remove(preset_name)
        self.settings["presets_order"].insert(self.settings["presets_order"].index(after_preset_name) + 1, preset_name)
        return self.settings["presets_order"]

    def change_preset_name(self, preset_name, new_preset_name):
        if preset_name not in self.settings["presets"]:
            raise ValueError("Preset does not exist")
        if new_preset_name in self.settings["presets"]:
            raise ValueError(f"Preset with name {new_preset_name} already exists")
        if preset_name == self.settings["current_preset"]:
            self.settings["current_preset"] = new_preset_name
        preset_path = self.settings["presets"][preset_name]
        shutil.copy(preset_path, os.path.join(self.internal_settings.presets_dir, new_preset_name + ".json"))
        preset_index = self.settings["presets_order"].index(preset_name)
        self.remove_preset(preset_name)
        new_preset_settings = PresetSettings(os.path.join(self.internal_settings.presets_dir,
                                                          new_preset_name + ".json"),
                                             internal_settings=self.internal_settings)
        new_preset_settings.set_name(new_preset_name)
        new_preset_settings.save()
        self.settings["presets"][new_preset_name] = os.path.join(self.internal_settings.presets_dir,
                                                                 new_preset_name + ".json")

        self.settings["presets_order"].insert(preset_index, new_preset_name)
        return new_preset_name
